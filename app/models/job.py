from __future__ import annotations

from datetime import datetime, date

from sqlalchemy.orm import validates

from app import db


class Job(db.Model):
    __tablename__ = 'jobs'
    __table_args__ = (
        db.Index('ix_jobs_recruiter_id', 'recruiter_id'),
        db.Index('ix_jobs_status', 'status'),
        db.Index('ix_jobs_location', 'location'),
        db.Index('ix_jobs_employment_type', 'employment_type'),
    )

    STATUS_DRAFT = 'Draft'
    STATUS_ACTIVE = 'Active'
    STATUS_CLOSED = 'Closed'
    STATUSES = (STATUS_DRAFT, STATUS_ACTIVE, STATUS_CLOSED)

    TYPE_FULL_TIME = 'Full-Time'
    TYPE_PART_TIME = 'Part-Time'
    TYPE_CONTRACT = 'Contract'
    TYPE_INTERNSHIP = 'Internship'
    TYPE_FREELANCE = 'Freelance'
    TYPE_REMOTE = 'Remote'
    TYPE_HYBRID = 'Hybrid'
    TYPE_ON_SITE = 'On-site'
    EMPLOYMENT_TYPES = (
        TYPE_FULL_TIME, TYPE_PART_TIME, TYPE_CONTRACT,
        TYPE_INTERNSHIP, TYPE_FREELANCE, TYPE_REMOTE, TYPE_HYBRID,
        TYPE_ON_SITE,
    )

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE', name='fk_jobs_recruiter_id'),
        nullable=False,
    )
    title = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=False, default='')
    location = db.Column(db.String(200), nullable=True)
    employment_type = db.Column(db.String(32), nullable=False, default=TYPE_FULL_TIME)
    description = db.Column(db.Text, nullable=True)
    jd_original_filename = db.Column(db.String(255), nullable=True)
    jd_stored_filename = db.Column(db.String(255), nullable=True)
    jd_file_path = db.Column(db.String(512), nullable=True)
    min_experience = db.Column(db.Float, nullable=True)
    max_experience = db.Column(db.Float, nullable=True)
    required_education = db.Column(db.String(120), nullable=True)
    application_deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(32), nullable=False, default=STATUS_DRAFT)
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

    recruiter = db.relationship('User', back_populates='jobs', foreign_keys=[recruiter_id])
    job_skills = db.relationship(
        'JobSkill', back_populates='job',
        cascade='all, delete-orphan', lazy='dynamic',
    )
    applications = db.relationship(
        'Application', back_populates='job',
        cascade='all, delete-orphan', lazy='dynamic',
    )

    @validates('status')
    def _validate_status(self, _key, value):
        if value and value not in Job.STATUSES:
            raise ValueError(f'Invalid job status {value!r}')
        return value or Job.STATUS_DRAFT

    @validates('employment_type')
    def _validate_employment_type(self, _key, value):
        if value and value not in Job.EMPLOYMENT_TYPES:
            raise ValueError(f'Invalid employment_type {value!r}')
        return value or Job.TYPE_FULL_TIME

    @validates('title')
    def _normalize_title(self, _key, value):
        value = (value or '').strip()
        if not value:
            raise ValueError('Job title cannot be empty')
        return value

    @validates('min_experience', 'max_experience')
    def _validate_experience(self, key, value):
        if value is None:
            return value
        if value < 0:
            raise ValueError(f'{key} cannot be negative')
        return value

    def __repr__(self) -> str:
        return f'<Job #{self.id} {self.title!r} status={self.status}>'
