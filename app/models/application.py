from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint, Index

from app import db


class Application(db.Model):
    __tablename__ = 'applications'
    __table_args__ = (
        UniqueConstraint(
            'candidate_id', 'job_id', name='uq_applications_candidate_job',
        ),
        Index('ix_applications_candidate_id', 'candidate_id'),
        Index('ix_applications_job_id', 'job_id'),
        Index('ix_applications_status', 'status'),
        Index('ix_applications_applied_at', 'applied_at'),
    )

    STATUS_APPLIED = 'Applied'
    STATUS_UNDER_REVIEW = 'Under Review'
    STATUS_SHORTLISTED = 'Shortlisted'
    STATUS_INTERVIEW_SCHEDULED = 'Interview Scheduled'
    STATUS_INTERVIEW_COMPLETED = 'Interview Completed'
    STATUS_SELECTED = 'Selected'
    STATUS_REJECTED = 'Rejected'
    STATUS_ON_HOLD = 'On Hold'
    STATUSES = (
        STATUS_APPLIED, STATUS_UNDER_REVIEW, STATUS_SHORTLISTED,
        STATUS_INTERVIEW_SCHEDULED, STATUS_INTERVIEW_COMPLETED,
        STATUS_SELECTED, STATUS_REJECTED, STATUS_ON_HOLD,
    )

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidates.id', ondelete='CASCADE',
                      name='fk_applications_candidate_id'),
        nullable=False,
    )
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id', ondelete='CASCADE',
                      name='fk_applications_job_id'),
        nullable=False,
    )
    status = db.Column(db.String(40), nullable=False, default=STATUS_APPLIED)
    is_shortlisted = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    applied_at = db.Column(
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

    candidate = db.relationship('Candidate', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    score = db.relationship(
        'CandidateScore',
        back_populates='application',
        uselist=False,
        cascade='all, delete-orphan',
    )
    interviews = db.relationship(
        'Interview', back_populates='application',
        cascade='all, delete-orphan', lazy='dynamic',
    )

    @validates('status')
    def _validate_status(self, _key, value):
        if value and value not in Application.STATUSES:
            raise ValueError(f'Invalid application status {value!r}')
        return value or Application.STATUS_APPLIED

    def __repr__(self) -> str:
        return (
            f'<Application #{self.id} candidate_id={self.candidate_id}'
            f' job_id={self.job_id} status={self.status!r}>'
        )
