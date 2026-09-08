from __future__ import annotations

from datetime import datetime

from app import db


class Notification(db.Model):
    __tablename__ = 'notifications'
    __table_args__ = (
        db.Index('ix_notifications_user_read', 'user_id', 'is_read'),
        db.Index('ix_notifications_created_at', 'created_at'),
    )

    TYPE_RESUME = 'RESUME'
    TYPE_MATCHING = 'MATCHING'
    TYPE_RANKING = 'RANKING'
    TYPE_SHORTLIST = 'SHORTLIST'
    TYPE_INTERVIEW = 'INTERVIEW'
    TYPE_JOB = 'JOB'
    TYPE_SYSTEM = 'SYSTEM'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    notification_type = db.Column(db.String(32), nullable=False, default=TYPE_SYSTEM)
    related_job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True)
    related_candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id', ondelete='SET NULL'), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=db.func.now())

    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification #{self.id} user_id={self.user_id} read={self.is_read}>'
