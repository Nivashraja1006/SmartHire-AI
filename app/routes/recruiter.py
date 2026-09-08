from __future__ import annotations

import os
import re
import uuid
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename

from app import db
from app.ai.jd_analyzer import analyze
from app.models import ActivityLog, Job, JobSkill, Notification, Role, Skill
from app.realtime.events import create_notification, emit_recruiter_event, log_activity
from app.utils.decorators import role_required
from app.utils.file_extraction import validate_file_signature
from app.services.ai_audit_service import audit_ai_operation


bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')
ALLOWED_JD_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_JD_BYTES = 10 * 1024 * 1024


def _owned_job(job_id):
    return Job.query.filter_by(id=job_id, recruiter_id=current_user.id).first_or_404()


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as exc:
        raise ValueError('Application deadline must be a valid date.') from exc


def _float_value(value, label):
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f'{label} must be a number.') from exc
    if parsed < 0:
        raise ValueError(f'{label} cannot be negative.')
    return parsed


def _extract_text(path, extension):
    if extension == 'pdf':
        try:
            import fitz
        except ImportError as exc:
            raise ValueError('PDF analysis requires PyMuPDF. Install the project requirements first.') from exc
        with fitz.open(path) as document:
            return '\n'.join(page.get_text() for page in document)
    if extension == 'docx':
        try:
            from docx import Document
        except ImportError as exc:
            raise ValueError('DOCX analysis requires python-docx. Install the project requirements first.') from exc
        return '\n'.join(paragraph.text for paragraph in Document(path).paragraphs)
    with open(path, 'r', encoding='utf-8', errors='replace') as file:
        return file.read()


def _save_and_extract(upload):
    original = secure_filename(upload.filename or '')
    extension = original.rsplit('.', 1)[-1].lower() if '.' in original else ''
    if not original or extension not in ALLOWED_JD_EXTENSIONS:
        raise ValueError('Upload a PDF, DOCX, or TXT job description.')
    upload.stream.seek(0, os.SEEK_END)
    size = upload.stream.tell()
    upload.stream.seek(0)
    if size == 0:
        raise ValueError('The uploaded job description is empty.')
    if size > MAX_JD_BYTES:
        raise ValueError('Job descriptions must be 10 MB or smaller.')

    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'job_descriptions')
    os.makedirs(folder, exist_ok=True)
    stored = f'{uuid.uuid4().hex}.{extension}'
    path = os.path.join(folder, stored)
    upload.save(path)
    try:
        validate_file_signature(path, extension)
        text = re.sub(r'\s+', ' ', _extract_text(path, extension)).strip()
    except Exception as exc:
        os.remove(path)
        raise ValueError('The uploaded file could not be read.') from exc
    if not text:
        os.remove(path)
        raise ValueError('No readable text was found in the uploaded file.')
    return original, stored, path, text


def _skill_ids(field):
    values = set()
    for value in request.form.getlist(field):
        try:
            values.add(int(value))
        except ValueError:
            continue
    return values


def _form_values(job=None):
    return {
        'title': request.form.get('title', job.title if job else ''),
        'company_name': request.form.get('company_name', job.company_name if job else ''),
        'location': request.form.get('location', job.location if job else ''),
        'employment_type': request.form.get('employment_type', job.employment_type if job else Job.TYPE_FULL_TIME),
        'description': request.form.get('description', job.description if job else ''),
        'min_experience': request.form.get('min_experience', job.min_experience if job and job.min_experience is not None else ''),
        'max_experience': request.form.get('max_experience', job.max_experience if job and job.max_experience is not None else ''),
        'required_education': request.form.get('required_education', job.required_education if job else ''),
        'application_deadline': request.form.get('application_deadline', job.application_deadline.isoformat() if job and job.application_deadline else ''),
        'status': request.form.get('status', job.status if job else Job.STATUS_DRAFT),
    }


def _render_editor(template, job=None, analysis=None, extracted_text=''):
    selected = {skill.skill_id: skill.importance for skill in job.job_skills.all()} if job else {}
    return render_template(
        template,
        title='Edit job' if job else 'Create job',
        job=job,
        values=_form_values(job),
        skills=Skill.query.order_by(Skill.name).all(),
        selected_skills=selected,
        analysis=analysis,
        extracted_text=extracted_text,
        employment_types=Job.EMPLOYMENT_TYPES,
        statuses=Job.STATUSES,
    )


def _apply_job_form(job):
    values = _form_values(job)
    if not values['title'] or not values['company_name']:
        raise ValueError('Job title and company name are required.')
    min_experience = _float_value(values['min_experience'], 'Minimum experience')
    max_experience = _float_value(values['max_experience'], 'Maximum experience')
    if min_experience is not None and max_experience is not None and max_experience < min_experience:
        raise ValueError('Maximum experience cannot be less than minimum experience.')
    if values['employment_type'] not in Job.EMPLOYMENT_TYPES:
        raise ValueError('Choose a valid employment type.')
    if values['status'] not in Job.STATUSES:
        raise ValueError('Choose a valid job status.')

    job.title = values['title']
    job.company_name = values['company_name']
    job.location = values['location'] or None
    job.employment_type = values['employment_type']
    job.description = values['description'] or None
    job.min_experience = min_experience
    job.max_experience = max_experience
    job.required_education = values['required_education'] or None
    job.application_deadline = _parse_date(values['application_deadline'])
    job.status = values['status']
    mandatory = _skill_ids('mandatory_skill_ids')
    preferred = _skill_ids('preferred_skill_ids') - mandatory
    if job.id:
        db.session.query(JobSkill).filter_by(job_id=job.id).delete(synchronize_session=False)
    for skill_id in mandatory:
        if Skill.query.get(skill_id):
            db.session.add(JobSkill(job=job, skill_id=skill_id, importance=JobSkill.IMPORTANCE_MANDATORY))
    for skill_id in preferred:
        if Skill.query.get(skill_id):
            db.session.add(JobSkill(job=job, skill_id=skill_id, importance=JobSkill.IMPORTANCE_PREFERRED))


@bp.route('/dashboard')
@role_required(Role.RECRUITER)
def dashboard():
    return render_template('dashboard.html', title='Recruiter dashboard', role=Role.RECRUITER)


@bp.route('/jobs')
@role_required(Role.RECRUITER)
def jobs():
    job_list = Job.query.filter_by(recruiter_id=current_user.id).order_by(Job.created_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=20, error_out=False)
    return render_template('recruiter/jobs.html', title='Manage jobs', jobs=job_list)


@bp.route('/jobs/create', methods=['GET', 'POST'])
@role_required(Role.RECRUITER)
def create_job():
    if request.method == 'POST':
        try:
            if request.form.get('action') == 'analyze':
                extracted = request.form.get('description', '')
                upload = request.files.get('job_description_file')
                if upload and upload.filename:
                    _, _, _, extracted = _save_and_extract(upload)
                analysis = analyze(extracted, Skill.query.all())
                audit_ai_operation('jd_analysis', 'job_description', None, algorithm='regex local JD analyzer')
                db.session.commit()
                return _render_editor('recruiter/job_form.html', analysis=analysis, extracted_text=extracted)
            job = Job(recruiter_id=current_user.id)
            _apply_job_form(job)
            upload = request.files.get('job_description_file')
            if upload and upload.filename:
                original, stored, path, text = _save_and_extract(upload)
                job.jd_original_filename, job.jd_stored_filename = original, stored
                job.jd_file_path, job.description = os.path.relpath(path), text
            db.session.add(job)
            db.session.commit()
            flash('Job created successfully.', 'success')
            return redirect(url_for('recruiter.view_job', job_id=job.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), 'error')
    return _render_editor('recruiter/job_form.html')


@bp.route('/jobs/<int:job_id>')
@role_required(Role.RECRUITER)
def view_job(job_id):
    return render_template('recruiter/job_view.html', title='Job details', job=_owned_job(job_id))


@bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@role_required(Role.RECRUITER)
def edit_job(job_id):
    job = _owned_job(job_id)
    if request.method == 'POST':
        try:
            if request.form.get('action') == 'analyze':
                extracted = request.form.get('description', '')
                upload = request.files.get('job_description_file')
                if upload and upload.filename:
                    _, _, _, extracted = _save_and_extract(upload)
                return _render_editor('recruiter/job_form.html', job, analyze(extracted, Skill.query.all()), extracted)
            _apply_job_form(job)
            upload = request.files.get('job_description_file')
            if upload and upload.filename:
                original, stored, path, text = _save_and_extract(upload)
                job.jd_original_filename, job.jd_stored_filename = original, stored
                job.jd_file_path, job.description = os.path.relpath(path), text
            db.session.commit()
            flash('Job updated successfully.', 'success')
            return redirect(url_for('recruiter.view_job', job_id=job.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), 'error')
    return _render_editor('recruiter/job_form.html', job)


@bp.route('/jobs/<int:job_id>/analyze')
@role_required(Role.RECRUITER)
def analyze_job(job_id):
    job = _owned_job(job_id)
    suggestions = analyze(job.description or '', Skill.query.all())
    audit_ai_operation('jd_analysis', 'job', job.id, algorithm='regex local JD analyzer')
    db.session.commit()
    return _render_editor('recruiter/job_form.html', job, suggestions, job.description or '')


@bp.route('/jobs/<int:job_id>/toggle', methods=['POST'])
@role_required(Role.RECRUITER)
def toggle_job(job_id):
    job = _owned_job(job_id)
    job.status = Job.STATUS_DRAFT if job.status == Job.STATUS_ACTIVE else Job.STATUS_ACTIVE
    db.session.commit()
    payload = {'job_id': job.id, 'status': job.status, 'title': job.title}
    emit_recruiter_event(current_user.id, 'job_status_changed', payload)
    log_activity(current_user.id, ActivityLog.TYPE_JOB_CREATED, f'{job.title} status changed to {job.status}.', payload)
    create_notification(current_user.id, 'Job status updated', f'{job.title} is now {job.status}.', Notification.TYPE_JOB, job.id)
    db.session.commit()
    flash(f'Job is now {job.status.lower()}.', 'success')
    return redirect(url_for('recruiter.jobs'))


@bp.route('/jobs/<int:job_id>/archive', methods=['POST'])
@role_required(Role.RECRUITER)
def archive_job(job_id):
    job = _owned_job(job_id)
    job.status = Job.STATUS_CLOSED
    db.session.commit()
    flash('Job archived.', 'success')
    return redirect(url_for('recruiter.jobs'))


@bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@role_required(Role.RECRUITER)
def delete_job(job_id):
    job = _owned_job(job_id)
    if job.applications.count():
        flash('This job has applications and cannot be deleted. Archive it instead.', 'error')
    else:
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted.', 'success')
    return redirect(url_for('recruiter.jobs'))
