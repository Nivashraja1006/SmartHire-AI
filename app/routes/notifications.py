from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.models import ActivityLog, Notification, Role
from app.utils.decorators import role_required


bp = Blueprint('notifications', __name__)


def _serialize(notification):
    return {
        'id': notification.id, 'title': notification.title,
        'message': notification.message, 'notification_type': notification.notification_type,
        'is_read': notification.is_read, 'created_at': notification.created_at.isoformat(),
    }


@bp.route('/api/notifications')
@login_required
def list_notifications():
    rows = current_user.notifications.order_by(Notification.created_at.desc()).limit(30).all()
    return jsonify({'notifications': [_serialize(row) for row in rows], 'unread_count': current_user.notifications.filter_by(is_read=False).count()})


@bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    notification = current_user.notifications.filter_by(id=notification_id).first_or_404()
    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True, 'id': notification.id})


@bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    current_user.notifications.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@bp.route('/api/recruiter/dashboard')
@role_required(Role.RECRUITER)
def dashboard_data():
    from app.models import Application, CandidateScore, Job
    jobs = Job.query.filter_by(recruiter_id=current_user.id)
    job_ids = [job.id for job in jobs.all()]
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []
    scores = [application.score for application in applications if application.score]
    return jsonify({
        'total_jobs': len(job_ids),
        'active_jobs': sum(job.status == Job.STATUS_ACTIVE for job in jobs.all()),
        'total_candidates': len({application.candidate_id for application in applications}),
        'analyzed_candidates': len(scores),
        'shortlisted_candidates': sum(application.is_shortlisted for application in applications),
        'average_match_score': round(sum(score.overall_score for score in scores) / len(scores), 1) if scores else 0,
        'recent_activity': [
            {'activity_type': row.activity_type, 'description': row.description, 'created_at': row.created_at.isoformat()}
            for row in ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(12).all()
        ],
    })