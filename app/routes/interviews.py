from __future__ import annotations

from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from app import db
from app.models import ActivityLog, Application, Interview, Job, Notification, Role
from app.realtime.events import create_notification, emit_job_event, log_activity
from app.utils.decorators import role_required

bp = Blueprint('interviews', __name__)


def _application(application_id):
    return Application.query.join(Job).filter(Application.id == application_id, Job.recruiter_id == current_user.id).first_or_404()


def _parse_schedule(form):
    try:
        interview_date = date.fromisoformat((form.get('interview_date') or '').strip())
        interview_time = time.fromisoformat((form.get('interview_time') or '').strip())
        duration = int(form.get('duration_minutes') or 60)
    except (TypeError, ValueError):
        raise ValueError('Provide a valid interview date, time, and duration.')
    if interview_date < date.today():
        raise ValueError('Interview date cannot be in the past.')
    if duration <= 0 or duration > 480:
        raise ValueError('Duration must be between 1 and 480 minutes.')
    return interview_date, interview_time, duration


def _when(interview):
    return datetime.combine(interview.interview_date, interview.interview_time)


def _conflict(application, interview_date, interview_time, duration, exclude_id=None):
    start = datetime.combine(interview_date, interview_time)
    end = start + timedelta(minutes=duration)
    recruiter_interviews = Interview.query.join(Application).join(Job).filter(Job.recruiter_id == current_user.id, Interview.status.in_((Interview.STATUS_SCHEDULED, Interview.STATUS_RESCHEDULED))).all()
    candidate_interviews = Interview.query.join(Application).filter(Application.candidate_id == application.candidate_id, Interview.status.in_((Interview.STATUS_SCHEDULED, Interview.STATUS_RESCHEDULED))).all()
    seen = {row.id: row for row in recruiter_interviews + candidate_interviews}
    for existing in seen.values():
        if exclude_id and existing.id == exclude_id:
            continue
        if not existing.interview_date or not existing.interview_time:
            continue
        existing_start = _when(existing)
        existing_end = existing_start + timedelta(minutes=existing.duration_minutes or 60)
        if start < existing_end and end > existing_start:
            return existing
    return None


def _serialize(interview):
    application = interview.application
    return {
        'id': interview.id,
        'application_id': application.id,
        'candidate': application.candidate.full_name,
        'candidate_id': application.candidate_id,
        'job': application.job.title,
        'job_id': application.job_id,
        'date': interview.interview_date.isoformat() if interview.interview_date else None,
        'time': interview.interview_time.isoformat() if interview.interview_time else None,
        'duration_minutes': interview.duration_minutes,
        'interview_type': interview.interview_type,
        'meeting_link': interview.meeting_link,
        'location': interview.location,
        'status': interview.status,
        'notes': interview.notes,
    }


def _save_event(interview, activity_type, title, message, event_name):
    application = interview.application
    application.status = Application.STATUS_INTERVIEW_SCHEDULED if interview.status in (Interview.STATUS_SCHEDULED, Interview.STATUS_RESCHEDULED) else application.status
    log_activity(current_user.id, activity_type, message, {'interview_id': interview.id, 'job_id': application.job_id, 'candidate_id': application.candidate_id})
    create_notification(current_user.id, title, message, Notification.TYPE_INTERVIEW, application.job_id, application.candidate_id)
    if application.candidate.user_id:
        create_notification(application.candidate.user_id, title, message, Notification.TYPE_INTERVIEW, application.job_id, application.candidate_id)
    db.session.commit()
    emit_job_event(application.job_id, event_name, _serialize(interview), application.job.recruiter_id)


@bp.route('/recruiter/interviews')
@role_required(Role.RECRUITER)
def list_interviews():
    rows = Interview.query.join(Application).join(Job).filter(Job.recruiter_id == current_user.id).order_by(Interview.interview_date, Interview.interview_time).paginate(page=request.args.get('page', 1, type=int), per_page=20, error_out=False)
    return render_template('recruiter/interviews.html', title='Interview Management', interviews=rows)


@bp.route('/recruiter/interviews/create', methods=['GET', 'POST'])
@role_required(Role.RECRUITER)
def create_interview():
    applications = Application.query.join(Job).filter(Job.recruiter_id == current_user.id).order_by(Application.id.desc()).all()
    if request.method == 'POST':
        try:
            application = _application(int(request.form.get('application_id')))
            interview_date, interview_time, duration = _parse_schedule(request.form)
            conflict = _conflict(application, interview_date, interview_time, duration)
            if conflict:
                raise ValueError('Scheduling conflict detected.')
            interview = Interview(application=application, created_by=current_user.id, interview_date=interview_date, interview_time=interview_time, duration_minutes=duration, interview_type=request.form.get('interview_type') or Interview.TYPE_TECHNICAL, meeting_link=request.form.get('meeting_link') or None, location=request.form.get('location') or None, notes=request.form.get('notes') or None)
            db.session.add(interview)
            db.session.flush()
            _save_event(interview, ActivityLog.TYPE_INTERVIEW_CREATED, 'Interview scheduled', f'Interview scheduled with {application.candidate.full_name} for {application.job.title}.', 'interview_created')
            flash('Interview scheduled.', 'success')
            return redirect(url_for('interviews.list_interviews'))
        except (TypeError, ValueError) as exc:
            db.session.rollback()
            flash(str(exc), 'error')
    return render_template('recruiter/interview_form.html', title='Schedule Interview', interview=None, applications=applications, interview_types=Interview.TYPES)


@bp.route('/recruiter/interviews/<int:interview_id>/edit', methods=['GET', 'POST'])
@role_required(Role.RECRUITER)
def edit_interview(interview_id):
    interview = Interview.query.join(Application).join(Job).filter(Interview.id == interview_id, Job.recruiter_id == current_user.id).first_or_404()
    if request.method == 'POST':
        try:
            interview_date, interview_time, duration = _parse_schedule(request.form)
            conflict = _conflict(interview.application, interview_date, interview_time, duration, interview.id)
            if conflict:
                raise ValueError('Scheduling conflict detected.')
            interview.interview_date, interview.interview_time, interview.duration_minutes = interview_date, interview_time, duration
            interview.interview_type = request.form.get('interview_type') or interview.interview_type
            interview.meeting_link, interview.location, interview.notes = request.form.get('meeting_link') or None, request.form.get('location') or None, request.form.get('notes') or None
            interview.status = Interview.STATUS_RESCHEDULED
            _save_event(interview, ActivityLog.TYPE_INTERVIEW_RESCHEDULED, 'Interview rescheduled', f'Interview with {interview.application.candidate.full_name} was rescheduled.', 'interview_rescheduled')
            flash('Interview rescheduled.', 'success')
            return redirect(url_for('interviews.list_interviews'))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), 'error')
    return render_template('recruiter/interview_form.html', title='Edit Interview', interview=interview, applications=[interview.application], interview_types=Interview.TYPES)


@bp.route('/api/recruiter/interviews/<int:interview_id>/<string:action>', methods=['POST'])
@role_required(Role.RECRUITER)
def update_status(interview_id, action):
    interview = Interview.query.join(Application).join(Job).filter(Interview.id == interview_id, Job.recruiter_id == current_user.id).first_or_404()
    statuses = {'complete': (Interview.STATUS_COMPLETED, ActivityLog.TYPE_INTERVIEW_COMPLETED, 'interview_completed'), 'cancel': (Interview.STATUS_CANCELLED, ActivityLog.TYPE_INTERVIEW_CANCELLED, 'interview_cancelled'), 'no-show': (Interview.STATUS_NO_SHOW, ActivityLog.TYPE_INTERVIEW_UPDATED, 'interview_updated')}
    if action not in statuses:
        return jsonify({'success': False, 'error': 'Unsupported interview action.'}), 400
    status, activity_type, event_name = statuses[action]
    interview.status = status
    _save_event(interview, activity_type, f'Interview {status.lower()}', f'Interview with {interview.application.candidate.full_name} marked {status.lower()}.', event_name)
    if status == Interview.STATUS_COMPLETED:
        interview.application.status = Application.STATUS_INTERVIEW_COMPLETED
        db.session.commit()
    return jsonify({'success': True, 'interview': _serialize(interview)})
