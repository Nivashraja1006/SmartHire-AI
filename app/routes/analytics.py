from __future__ import annotations

import csv
import io
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, make_response, render_template, request
from flask_login import current_user

from app.models import Application, CandidateScore, Job, Role
from app.services.analytics_service import (
    get_admin_overview,
    get_application_funnel,
    get_job_analytics,
    get_recruitment_overview,
    get_recruiter_analytics,
    get_skill_gap_analytics,
    get_time_series_data,
)
from app.utils.decorators import role_required

bp = Blueprint('analytics', __name__)


def _owned_job(job_id):
    return Job.query.filter_by(id=job_id, recruiter_id=current_user.id).first_or_404()


def _days():
    value = request.args.get('days', default=30, type=int)
    if value not in (7, 30, 90):
        raise ValueError('days must be 7, 30, or 90')
    return value


@bp.route('/recruiter/analytics')
@role_required(Role.RECRUITER)
def recruiter_dashboard():
    return render_template('recruiter/analytics.html', title='Recruitment Analytics')


@bp.route('/api/recruiter/analytics/overview')
@role_required(Role.RECRUITER)
def recruiter_overview():
    return jsonify({'success': True, 'overview': get_recruiter_analytics(current_user.id)})


@bp.route('/api/recruiter/analytics/job/<int:job_id>')
@role_required(Role.RECRUITER)
def recruiter_job(job_id):
    data = get_job_analytics(job_id, current_user.id)
    if data is None:
        return jsonify({'success': False, 'error': 'Job not found.'}), 404
    return jsonify({'success': True, 'job': data})


@bp.route('/api/recruiter/analytics/skills/<int:job_id>')
@role_required(Role.RECRUITER)
def recruiter_skills(job_id):
    data = get_skill_gap_analytics(job_id, current_user.id)
    if data is None:
        return jsonify({'success': False, 'error': 'Job not found.'}), 404
    return jsonify({'success': True, 'skills': data})


@bp.route('/api/recruiter/analytics/funnel/<int:job_id>')
@role_required(Role.RECRUITER)
def recruiter_funnel(job_id):
    data = get_application_funnel(job_id, current_user.id)
    if data is None:
        return jsonify({'success': False, 'error': 'Job not found.'}), 404
    return jsonify({'success': True, 'funnel': data})


@bp.route('/api/recruiter/analytics/trends')
@role_required(Role.RECRUITER)
def recruiter_trends():
    try:
        start_value = request.args.get('start_date')
        end_value = request.args.get('end_date')
        if start_value or end_value:
            if not start_value or not end_value:
                raise ValueError('Both start_date and end_date are required.')
            start_date, end_date = date.fromisoformat(start_value), date.fromisoformat(end_value)
            data = get_time_series_data(current_user.id, max((end_date - start_date).days + 1, 1), start_date, end_date)
        else:
            data = get_time_series_data(current_user.id, _days())
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400
    return jsonify({'success': True, 'trends': data})


@bp.route('/api/recruiter/analytics/interviews')
@role_required(Role.RECRUITER)
def recruiter_interviews():
    from app.services.analytics_service import get_interview_analytics
    return jsonify({'success': True, 'interviews': get_interview_analytics(current_user.id)})


@bp.route('/api/recruiter/analytics/export/<string:report>')
@role_required(Role.RECRUITER)
def export_report(report):
    if report not in ('summary', 'jobs', 'ranking', 'skills', 'interviews'):
        return jsonify({'success': False, 'error': 'Unknown report.'}), 404
    output = io.StringIO()
    writer = csv.writer(output)
    if report == 'summary':
        data = get_recruitment_overview(current_user.id)
        writer.writerow(['Metric', 'Value'])
        writer.writerows((key.replace('_', ' ').title(), value) for key, value in data.items())
    elif report == 'jobs':
        data = get_recruiter_analytics(current_user.id)['jobs']
        writer.writerow(['Job', 'Applications', 'Analyzed', 'Average Match Score', 'Shortlisted', 'Interviews', 'Selected', 'Shortlist Rate', 'Interview Rate', 'Selection Rate'])
        for item in data:
            writer.writerow([item['title'], item['applications'], item['analyzed'], item['average_match_score'], item['shortlisted'], item['interviewed'], item['selected'], item['shortlist_rate'], item['interview_rate'], item['selection_rate']])
    elif report == 'interviews':
        writer.writerow(['Candidate', 'Job', 'Date', 'Time', 'Duration', 'Type', 'Status', 'Meeting Link', 'Location'])
        from app.models import Interview
        for interview in Interview.query.join(Application).join(Job).filter(Job.recruiter_id == current_user.id).all():
            writer.writerow([interview.application.candidate.full_name, interview.application.job.title, interview.interview_date, interview.interview_time, interview.duration_minutes, interview.interview_type, interview.status, interview.meeting_link or '', interview.location or ''])
    else:
        rows = Application.query.join(Job).filter(Job.recruiter_id == current_user.id).all()
        if report == 'ranking':
            writer.writerow(['Candidate', 'Job', 'Score', 'Skill Score', 'Experience Score', 'Recommendation', 'Shortlisted', 'Interview Status'])
            for application in rows:
                score = application.score
                writer.writerow([application.candidate.full_name, application.job.title, score.overall_score if score else '', score.skill_score if score else '', score.experience_score if score else '', score.recommendation if score else 'Pending', application.is_shortlisted, ', '.join(interview.status for interview in application.interviews.all())])
        else:
            writer.writerow(['Job', 'Skill', 'Missing Count', 'Missing Percent', 'Available Percent'])
            for job in Job.query.filter_by(recruiter_id=current_user.id).all():
                for gap in (get_skill_gap_analytics(job.id, current_user.id) or {}).get('gaps', []):
                    writer.writerow([job.title, gap['skill'], gap['missing_count'], gap['missing_percent'], gap['available_percent']])
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=smarthire-{report}-report.csv'
    return response


@bp.route('/admin/analytics')
@role_required(Role.ADMIN)
def admin_analytics():
    return render_template('admin/analytics.html', title='Admin Intelligence Dashboard')


@bp.route('/api/admin/analytics/overview')
@role_required(Role.ADMIN)
def admin_overview():
    return jsonify({'success': True, 'overview': get_admin_overview()})


@bp.route('/api/admin/analytics/users')
@role_required(Role.ADMIN)
def admin_users():
    overview = get_admin_overview()
    return jsonify({'success': True, 'users_by_role': overview['users_by_role']})


@bp.route('/api/admin/analytics/jobs')
@role_required(Role.ADMIN)
def admin_jobs():
    from app.models import Job
    rows = []
    for job in Job.query.order_by(Job.created_at.desc()).all():
        rows.append({'id': job.id, 'title': job.title, 'status': job.status, 'applications': job.applications.count(), 'average_match_score': round(sum(score.overall_score for application in job.applications for score in [application.score] if score) / max(sum(1 for application in job.applications if application.score), 1), 1)})
    return jsonify({'success': True, 'jobs': rows})


@bp.route('/api/admin/analytics/activity')
@role_required(Role.ADMIN)
def admin_activity():
    from app.models import ActivityLog
    rows = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(50).all()
    return jsonify({'success': True, 'activity': [{'activity_type': row.activity_type, 'description': row.description, 'created_at': row.created_at.isoformat()} for row in rows]})
