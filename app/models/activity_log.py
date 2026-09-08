from __future__ import annotations

from datetime import datetime

from app import db


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    __table_args__ = (
        db.Index('ix_activity_logs_user_id', 'user_id'),
        db.Index('ix_activity_logs_created_at', 'created_at'),
        db.Index('ix_activity_logs_activity_type', 'activity_type'),
    )

    TYPE_RESUME_UPLOADED = 'Resume Uploaded'
    TYPE_JOB_CREATED = 'Job Created'
    TYPE_CANDIDATE_RANKED = 'Candidate Ranked'
    TYPE_INTERVIEW_SCHEDULED = 'Interview Scheduled'
    TYPE_INTERVIEW_CREATED = 'Interview Created'
    TYPE_INTERVIEW_UPDATED = 'Interview Updated'
    TYPE_INTERVIEW_RESCHEDULED = 'Interview Rescheduled'
    TYPE_INTERVIEW_CANCELLED = 'Interview Cancelled'
    TYPE_INTERVIEW_COMPLETED = 'Interview Completed'
    TYPE_ANALYTICS_REPORT = 'Analytics Report Generated'
    TYPE_APPLICATION_UPDATED = 'Application Updated'
    TYPE_USER_LOGIN = 'User Login'
    TYPE_USER_LOGOUT = 'User Logout'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL',
                      name='fk_activity_logs_user_id'),
        nullable=True,
    )
    activity_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )

    user = db.relationship('User', back_populates='activity_logs')

    def __repr__(self) -> str:
        return (
            f'<ActivityLog #{self.id} user_id={self.user_id}'
            f' type={self.activity_type!r}>'
        )
