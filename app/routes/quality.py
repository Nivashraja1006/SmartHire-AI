from __future__ import annotations

from flask import Blueprint, jsonify, render_template
from flask_login import current_user

from app.ai.hiring_insights import generate_hiring_insights
from app.ai.job_quality_analyzer import analyze_job_quality
from app.ai.resume_quality_analyzer import analyze_resume_quality
from app.models import Application, AIAudit, Job, Resume, Role
from app.services.ai_audit_service import audit_ai_operation
from app.utils.decorators import role_required

bp = Blueprint('quality', __name__)


@bp.route('/api/recruiter/insights/<int:job_id>')
@role_required(Role.RECRUITER)
def hiring_insights(job_id):
    result = generate_hiring_insights(job_id, current_user.id)
    if result is None:
        return jsonify({'success': False, 'error': 'Job not found.'}), 404
    audit_ai_operation('hiring_insights', 'job', job_id)
    return jsonify({'success': True, 'insights': result})


@bp.route('/api/recruiter/jobs/<int:job_id>/quality')
@role_required(Role.RECRUITER)
def job_quality(job_id):
    job = Job.query.filter_by(id=job_id, recruiter_id=current_user.id).first_or_404()
    result = analyze_job_quality(job.description, [item.skill for item in job.job_skills.all()], job.min_experience, job.required_education)
    audit_ai_operation('job_quality', 'job', job.id)
    return jsonify({'success': True, 'quality': result})


@bp.route('/api/recruiter/resumes/<int:resume_id>/quality')
@role_required(Role.RECRUITER)
def resume_quality(resume_id):
    resume = Resume.query.join(Resume.candidate).filter(Resume.id == resume_id).first_or_404()
    if not Application.query.join(Job).filter(Job.recruiter_id == current_user.id, Application.candidate_id == resume.candidate_id).first():
        return jsonify({'success': False, 'error': 'Resume access denied.'}), 403
    result = analyze_resume_quality(resume.parsed_data, resume.extracted_text)
    audit_ai_operation('resume_quality', 'resume', resume.id)
    return jsonify({'success': True, 'quality': result})


@bp.route('/admin/system-health')
@role_required(Role.ADMIN)
def system_health():
    from app import db, socketio
    import os
    checks = {}
    try:
        db.session.execute(db.text('SELECT 1'))
        checks['database'] = {'status': 'Healthy', 'detail': 'Connected'}
    except Exception:
        checks['database'] = {'status': 'Error', 'detail': 'Unavailable'}
    upload_folder = __import__('flask').current_app.config['UPLOAD_FOLDER']
    checks['file_storage'] = {'status': 'Healthy' if os.access(upload_folder, os.W_OK) else 'Warning', 'detail': 'Writable' if os.access(upload_folder, os.W_OK) else 'Not writable'}
    checks['application'] = {'status': 'Healthy', 'detail': 'Running'}
    checks['socket_io'] = {'status': 'Healthy' if socketio.server else 'Warning', 'detail': 'Initialized' if socketio.server else 'Unavailable'}
    checks['ai_engine'] = {'status': 'Healthy', 'detail': 'Local rule-based engine'}
    return render_template('admin/system_health.html', title='System Health', checks=checks)


@bp.route('/api/admin/ai-audits')
@role_required(Role.ADMIN)
def ai_audits():
    rows = AIAudit.query.order_by(AIAudit.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'audits': [{'operation': row.operation, 'input_type': row.input_type, 'entity_id': row.entity_id, 'status': row.status, 'engine_version': row.engine_version, 'duration_ms': row.duration_ms, 'created_at': row.created_at.isoformat()} for row in rows]})
