from __future__ import annotations

from datetime import datetime, date, time

from sqlalchemy.orm import validates

from app import db


class Interview(db.Model):
    __tablename__ = 'interviews'
    __table_args__ = (
        db.Index('ix_interviews_application_id', 'application_id'),
        db.Index('ix_interviews_status', 'status'),
        db.Index('ix_interviews_interview_date', 'interview_date'),
        db.Index('ix_interviews_created_by', 'created_by'),
    )

    TYPE_ONLINE = 'Online'
    TYPE_OFFLINE = 'Offline'
    TYPE_TECHNICAL = 'Technical'
    TYPE_HR = 'HR'
    TYPES = (TYPE_ONLINE, TYPE_OFFLINE, TYPE_TECHNICAL, TYPE_HR)

    STATUS_SCHEDULED = 'Scheduled'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'
    STATUS_NO_SHOW = 'No Show'
    STATUS_RESCHEDULED = 'Rescheduled'
    STATUSES = (
        STATUS_SCHEDULED, STATUS_COMPLETED, STATUS_CANCELLED,
        STATUS_NO_SHOW, STATUS_RESCHEDULED,
    )

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id', ondelete='CASCADE',
                      name='fk_interviews_application_id'),
        nullable=False,
    )
    interview_date = db.Column(db.Date, nullable=True)
    interview_time = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60, server_default='60')
    interview_type = db.Column(db.String(32), nullable=False, default=TYPE_TECHNICAL)
    meeting_link = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(32), nullable=False, default=STATUS_SCHEDULED)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=db.func.now(),
    )

    application = db.relationship('Application', back_populates='interviews')
    creator = db.relationship('User', foreign_keys=[created_by])

    @validates('duration_minutes')
    def _validate_duration(self, _key, value):
        value = 60 if value is None else int(value)
        if value <= 0 or value > 480:
            raise ValueError('duration_minutes must be between 1 and 480')
        return value

    @validates('interview_type')
    def _validate_type(self, _key, value):
        if value and value not in Interview.TYPES:
            raise ValueError(f'Invalid interview_type {value!r}')
        return value or Interview.TYPE_TECHNICAL

    @validates('status')
    def _validate_status(self, _key, value):
        if value and value not in Interview.STATUSES:
            raise ValueError(f'Invalid interview status {value!r}')
        return value or Interview.STATUS_SCHEDULED

    def __repr__(self) -> str:
        return (
            f'<Interview #{self.id} application_id={self.application_id}'
            f' date={self.interview_date} type={self.interview_type}'
            f' status={self.status!r}>'
        )
