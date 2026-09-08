from __future__ import annotations

import json
import os
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user
from sqlalchemy import or_

from app import db
from app.ai.resume_parser import parse_resume
from app.models import ActivityLog, Candidate, CandidateSkill, Notification, Resume, Role, Skill
from app.realtime.events import create_notification, emit_recruiter_event, log_activity
from app.utils.decorators import role_required
from app.utils.file_extraction import save_resume_upload
from app.utils.rate_limit import local_rate_limit
from app.services.ai_audit_service import audit_ai_operation


bp = Blueprint('recruiter_candidates', __name__, url_prefix='/recruiter/candidates')
PAGE_SIZE = 10


def _candidate(candidate_id):
    return Candidate.query.filter(Candidate.id == candidate_id).first_or_404()


def _resume_owner(resume_id):
    return Resume.query.join(Candidate).filter(Resume.id == resume_id).first_or_404()


def _apply_candidate_form(candidate):
    name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    if not name or not email or '@' not in email:
        raise ValueError('Full name and a valid email are required.')
    try:
        experience = float(request.form.get('total_experience') or 0)
    except ValueError as exc:
        raise ValueError('Total experience must be a number.') from exc
    if experience < 0:
        raise ValueError('Total experience cannot be negative.')
    candidate.full_name = name
    candidate.email = email
    candidate.phone = request.form.get('phone', '').strip() or None
    candidate.current_location = request.form.get('current_location', '').strip() or None
    candidate.total_experience = experience
    candidate.profile_summary = request.form.get('profile_summary', '').strip() or None
    candidate.linkedin_url = request.form.get('linkedin_url', '').strip() or None
    candidate.github_url = request.form.get('github_url', '').strip() or None
    candidate.portfolio_url = request.form.get('portfolio_url', '').strip() or None


def _save_parsed_skills(candidate, parsed):
    for item in parsed.get('skills', []):
        skill = Skill.query.filter_by(name=item.get('name')).first()
        if not skill:
            continue
        existing = CandidateSkill.query.filter_by(candidate_id=candidate.id, skill_id=skill.id).first()
        if existing:
            existing.proficiency_level = item.get('proficiency_level', CandidateSkill.PROF_INTERMEDIATE)
            existing.source = CandidateSkill.SRC_RESUME
        else:
            db.session.add(CandidateSkill(
                candidate=candidate, skill=skill,
                proficiency_level=item.get('proficiency_level', CandidateSkill.PROF_INTERMEDIATE),
                source=CandidateSkill.SRC_RESUME,
            ))


def _process_upload(candidate, upload):
    original, stored, path, extension, text = save_resume_upload(upload)
    current = Resume.query.filter_by(candidate_id=candidate.id, is_current=True).all()
    for resume in current:
        resume.is_current = False
    version = (max((resume.version for resume in candidate.resumes.all()), default=0) + 1)
    resume = Resume(
        candidate=candidate, original_filename=original, stored_filename=stored,
        file_path=path, file_type=extension, extracted_text=text,
        processing_status=Resume.STATUS_PROCESSING, version=version, is_current=True,
    )
    db.session.add(resume)
    db.session.flush()
    try:
        parsed = parse_resume(text, Skill.query.all())
        audit_ai_operation('resume_parsing', 'resume', resume.id, algorithm='regex local resume parser')
        resume.parsed_data = parsed
        resume.processing_status = Resume.STATUS_COMPLETED
        if parsed.get('email'):
            candidate.email = parsed['email'].lower()
        if parsed.get('phone'):
            candidate.phone = parsed['phone']
        if parsed.get('total_experience') is not None:
            candidate.total_experience = parsed['total_experience']
        _save_parsed_skills(candidate, parsed)
    except Exception as exc:
        resume.processing_status = Resume.STATUS_FAILED
        resume.processing_error = str(exc)[:500]
    return resume


@bp.route('')
@role_required(Role.RECRUITER)
def candidates():
    query = Candidate.query
    search = request.args.get('q', '').strip()
    if search:
        term = f'%{search}%'
        query = query.filter(or_(Candidate.full_name.ilike(term), Candidate.email.ilike(term), Candidate.current_location.ilike(term)))
    sort = request.args.get('sort', 'updated')
    query = query.order_by(Candidate.full_name.asc() if sort == 'name' else Candidate.updated_at.desc())
    page = query.paginate(page=request.args.get('page', 1, type=int), per_page=PAGE_SIZE, error_out=False)
    return render_template('recruiter/candidates.html', title='Candidates', candidates=page, search=search, sort=sort)


@bp.route('/new', methods=['GET', 'POST'])
@role_required(Role.RECRUITER)
def create_candidate():
    candidate = Candidate(full_name='Pending', email='pending@example.com')
    if request.method == 'POST':
        try:
            _apply_candidate_form(candidate)
            db.session.add(candidate)
            db.session.flush()
            db.session.commit()
            emit_recruiter_event(current_user.id, 'candidate_created', {'candidate_id': candidate.id, 'candidate_name': candidate.full_name, 'email': candidate.email})
            upload = request.files.get('resume')
            if upload and upload.filename:
                _process_upload(candidate, upload)
            db.session.commit()
            flash('Candidate added successfully.', 'success')
            return redirect(url_for('recruiter_candidates.view_candidate', candidate_id=candidate.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), 'error')
    return render_template('recruiter/candidate_form.html', title='Add candidate', candidate=candidate, mode='create')


@bp.route('/<int:candidate_id>')
@role_required(Role.RECRUITER)
def view_candidate(candidate_id):
    candidate = _candidate(candidate_id)
    return render_template('recruiter/candidate_view.html', title=candidate.full_name, candidate=candidate, resumes=candidate.resumes.order_by(Resume.uploaded_at.desc()).all())


@bp.route('/<int:candidate_id>/edit', methods=['GET', 'POST'])
@role_required(Role.RECRUITER)
def edit_candidate(candidate_id):
    candidate = _candidate(candidate_id)
    if request.method == 'POST':
        try:
            _apply_candidate_form(candidate)
            db.session.commit()
            flash('Candidate profile updated.', 'success')
            return redirect(url_for('recruiter_candidates.view_candidate', candidate_id=candidate.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), 'error')
    return render_template('recruiter/candidate_form.html', title='Edit candidate', candidate=candidate, mode='edit')


@bp.route('/<int:candidate_id>/resume', methods=['POST'])
@role_required(Role.RECRUITER)
@local_rate_limit(10)
def upload_resume(candidate_id):
    candidate = _candidate(candidate_id)
    try:
        upload = request.files.get('resume')
        if not upload or not upload.filename:
            raise ValueError('Choose a resume file first.')
        emit_recruiter_event(current_user.id, 'resume_processing_started', {'candidate_id': candidate.id, 'candidate_name': candidate.full_name})
        _process_upload(candidate, upload)
        db.session.commit()
        emit_recruiter_event(current_user.id, 'resume_processing_completed', {'candidate_id': candidate.id, 'candidate_name': candidate.full_name, 'status': 'Completed'})
        log_activity(current_user.id, ActivityLog.TYPE_RESUME_UPLOADED, f'Resume uploaded for {candidate.full_name}.', {'candidate_id': candidate.id})
        create_notification(current_user.id, 'Resume processed', f'Resume processed for {candidate.full_name}.', Notification.TYPE_RESUME, related_candidate_id=candidate.id)
        db.session.commit()
        flash('Resume uploaded and processed locally.', 'success')
    except ValueError as exc:
        db.session.rollback()
        emit_recruiter_event(current_user.id, 'resume_processing_failed', {'candidate_id': candidate.id, 'candidate_name': candidate.full_name, 'error': str(exc)})
        flash(str(exc), 'error')
    return redirect(url_for('recruiter_candidates.view_candidate', candidate_id=candidate.id))


@bp.route('/<int:candidate_id>/resume/<int:resume_id>/review', methods=['POST'])
@role_required(Role.RECRUITER)
def review_resume(candidate_id, resume_id):
    candidate = _candidate(candidate_id)
    resume = Resume.query.filter_by(id=resume_id, candidate_id=candidate.id).first_or_404()
    try:
        parsed = json.loads(request.form.get('parsed_json', '{}'))
        if not isinstance(parsed, dict):
            raise ValueError
        resume.parsed_data = parsed
        resume.reviewed_at = datetime.utcnow()
        if parsed.get('full_name'):
            candidate.full_name = str(parsed['full_name'])[:160]
        _save_parsed_skills(candidate, parsed)
        db.session.commit()
        flash('Resume extraction review saved.', 'success')
    except (ValueError, TypeError, json.JSONDecodeError):
        db.session.rollback()
        flash('Parsed resume data must be valid JSON.', 'error')
    return redirect(url_for('recruiter_candidates.view_candidate', candidate_id=candidate.id))


@bp.route('/resume/<int:resume_id>/download')
@role_required(Role.RECRUITER)
def download_resume(resume_id):
    resume = _resume_owner(resume_id)
    return send_file(os.path.abspath(os.path.join(current_app.root_path, '..', resume.file_path)), download_name=resume.original_filename, as_attachment=True)