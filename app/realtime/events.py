from __future__ import annotations

from flask_login import current_user
from flask_socketio import join_room

from app import db, socketio
from app.models import ActivityLog, Notification, Role


def recruiter_room(user_id):
    return f'recruiter_{user_id}'


def job_room(job_id):
    return f'job_{job_id}'


def emit_recruiter_event(recruiter_id, event_name, payload):
    socketio.emit(event_name, payload, room=recruiter_room(recruiter_id))


def emit_job_event(job_id, event_name, payload, recruiter_id=None):
    socketio.emit(event_name, payload, room=job_room(job_id))
    if recruiter_id is not None:
        emit_recruiter_event(recruiter_id, event_name, payload)


def create_notification(user_id, title, message, notification_type=Notification.TYPE_SYSTEM, related_job_id=None, related_candidate_id=None):
    notification = Notification(
        user_id=user_id, title=title, message=message,
        notification_type=notification_type, related_job_id=related_job_id,
        related_candidate_id=related_candidate_id,
    )
    db.session.add(notification)
    db.session.flush()
    emit_recruiter_event(user_id, 'notification_created', {
        'id': notification.id, 'title': title, 'message': message,
        'notification_type': notification_type,
        'created_at': notification.created_at.isoformat(), 'unread': True,
    })
    return notification


def log_activity(user_id, activity_type, description, payload=None):
    activity = ActivityLog(user_id=user_id, activity_type=activity_type, description=description)
    db.session.add(activity)
    db.session.flush()
    event = {
        'id': activity.id, 'activity_type': activity_type,
        'description': description, 'created_at': activity.created_at.isoformat(),
    }
    if payload:
        event.update(payload)
    emit_recruiter_event(user_id, 'activity_created', event)
    emit_recruiter_event(user_id, 'analytics_updated', {'activity_type': activity_type})
    return activity


@socketio.on('join_recruiter_room')
def join_recruiter_room(_payload=None):
    if not current_user.is_authenticated or not current_user.role or current_user.role.name != Role.RECRUITER:
        return {'success': False, 'error': 'Authentication required.'}
    join_room(recruiter_room(current_user.id))
    return {'success': True, 'room': recruiter_room(current_user.id)}


@socketio.on('join_job_room')
def join_job_room(payload=None):
    if not current_user.is_authenticated or not current_user.role or current_user.role.name != Role.RECRUITER:
        return {'success': False, 'error': 'Authentication required.'}
    from app.models import Job
    job = db.session.get(Job, (payload or {}).get('job_id'))
    if not job or job.recruiter_id != current_user.id:
        return {'success': False, 'error': 'Job access denied.'}
    join_room(job_room(job.id))
    return {'success': True, 'room': job_room(job.id)}
