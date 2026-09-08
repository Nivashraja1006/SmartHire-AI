from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import validates

from app import db


class Candidate(db.Model):
    __tablename__ = 'candidates'
    __table_args__ = (
        db.Index('ix_candidates_email', 'email'),
        db.Index('ix_candidates_user_id', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL', name='fk_candidates_user_id'),
        nullable=True,
    )
    full_name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), nullable=True)
    current_location = db.Column(db.String(200), nullable=True)
    total_experience = db.Column(db.Float, nullable=True, default=0.0)
    profile_summary = db.Column(db.Text, nullable=True)
    linkedin_url = db.Column(db.String(512), nullable=True)
    github_url = db.Column(db.String(512), nullable=True)
    portfolio_url = db.Column(db.String(512), nullable=True)
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

    user = db.relationship('User', back_populates='candidate_profiles', foreign_keys=[user_id])
    resumes = db.relationship(
        'Resume', back_populates='candidate',
        cascade='all, delete-orphan', lazy='dynamic',
    )
    candidate_skills = db.relationship(
        'CandidateSkill', back_populates='candidate',
        cascade='all, delete-orphan', lazy='dynamic',
    )
    applications = db.relationship(
        'Application', back_populates='candidate',
        cascade='all, delete-orphan', lazy='dynamic',
    )

    @validates('email')
    def _normalize_email(self, _key, value):
        value = (value or '').strip().lower()
        if not value:
            raise ValueError('Candidate email cannot be empty')
        return value

    @validates('full_name')
    def _normalize_name(self, _key, value):
        value = (value or '').strip()
        if not value:
            raise ValueError('Candidate full_name cannot be empty')
        return value

    def __repr__(self) -> str:
        return f'<Candidate #{self.id} {self.full_name!r} {self.email!r}>'
