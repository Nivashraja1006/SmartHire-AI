from __future__ import annotations

from datetime import datetime
from sqlalchemy import JSON

from sqlalchemy.orm import validates

from app import db


class Resume(db.Model):
    __tablename__ = 'resumes'
    __table_args__ = (
        db.Index('ix_resumes_candidate_id', 'candidate_id'),
        db.Index('ix_resumes_processing_status', 'processing_status'),
        db.Index('ix_resumes_is_current', 'is_current'),
    )

    STATUS_UPLOADED = 'Uploaded'
    STATUS_PROCESSING = 'Processing'
    STATUS_COMPLETED = 'Completed'
    STATUS_FAILED = 'Failed'
    STATUSES = (STATUS_UPLOADED, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_FAILED)

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidates.id', ondelete='CASCADE',
                      name='fk_resumes_candidate_id'),
        nullable=False,
    )
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(16), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(JSON, nullable=True)
    version = db.Column(db.Integer, nullable=False, default=1, server_default='1')
    is_current = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    processing_error = db.Column(db.String(500), nullable=True)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    processing_status = db.Column(
        db.String(32), nullable=False, default=STATUS_UPLOADED,
    )
    uploaded_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )

    candidate = db.relationship('Candidate', back_populates='resumes')

    @validates('processing_status')
    def _validate_status(self, _key, value):
        if value and value not in Resume.STATUSES:
            raise ValueError(f'Invalid processing_status {value!r}')
        return value or Resume.STATUS_UPLOADED

    @validates('file_type')
    def _normalize_file_type(self, _key, value):
        value = (value or '').strip().lower()
        if not value:
            raise ValueError('file_type cannot be empty')
        return value

    def __repr__(self) -> str:
        return (
            f'<Resume #{self.id} candidate_id={self.candidate_id}'
            f' status={self.processing_status} file={self.original_filename!r}>'
        )
