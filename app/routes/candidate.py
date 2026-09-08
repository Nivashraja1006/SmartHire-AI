import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user

from app import db
from app.models import Application, Candidate, Resume, Role
from app.utils.decorators import role_required
from app.routes.recruiter_candidates import _process_upload


bp = Blueprint('candidate', __name__, url_prefix='/candidate')


@bp.route('/dashboard')
@role_required(Role.CANDIDATE)
def dashboard():
    candidate = Candidate.query.filter_by(user_id=current_user.id).first()
    applications = Application.query.filter_by(candidate_id=candidate.id).order_by(Application.applied_at.desc()).limit(8).all() if candidate else []
    scores = [application.score for application in applications if application.score]
    return render_template(
        'dashboard.html',
        title='Candidate dashboard',
        role=Role.CANDIDATE,
        candidate=candidate,
        applications=applications,
        average_match_score=round(sum(score.overall_score for score in scores) / len(scores), 1) if scores else 0,
    )


def _profile():
    return Candidate.query.filter_by(user_id=current_user.id).first_or_404()


@bp.route('/resumes')
@role_required(Role.CANDIDATE)
def resumes():
    candidate = _profile()
    return render_template('candidate/resumes.html', title='My resumes', candidate=candidate, resumes=candidate.resumes.order_by(Resume.uploaded_at.desc()).all())


@bp.route('/resumes/upload', methods=['POST'])
@role_required(Role.CANDIDATE)
def upload_resume():
    candidate = _profile()
    try:
        upload = request.files.get('resume')
        if not upload or not upload.filename:
            raise ValueError('Choose a resume file first.')
        _process_upload(candidate, upload)
        db.session.commit()
        flash('Resume uploaded and processed locally.', 'success')
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), 'error')
    return redirect(url_for('candidate.resumes'))


@bp.route('/resumes/<int:resume_id>/download')
@role_required(Role.CANDIDATE)
def download_resume(resume_id):
    resume = Resume.query.join(Candidate).filter(Resume.id == resume_id, Candidate.user_id == current_user.id).first_or_404()
    path = os.path.abspath(os.path.join(current_app.root_path, '..', resume.file_path))
    return send_file(path, download_name=resume.original_filename, as_attachment=True)