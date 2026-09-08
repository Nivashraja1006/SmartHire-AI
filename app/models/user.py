from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint, Index
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('email', name='uq_users_email'),
        Index('ix_users_role_id', 'role_id'),
        Index('ix_users_is_active', 'is_active'),
    )

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id', ondelete='RESTRICT', name='fk_users_role_id'),
        nullable=False,
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
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

    role = db.relationship('Role', back_populates='users', lazy='joined')
    jobs = db.relationship(
        'Job',
        back_populates='recruiter',
        foreign_keys='Job.recruiter_id',
        cascade='save-update, merge',
        lazy='dynamic',
    )
    candidate_profiles = db.relationship(
        'Candidate',
        back_populates='user',
        foreign_keys='Candidate.user_id',
        cascade='save-update, merge',
        lazy='dynamic',
    )
    activity_logs = db.relationship(
        'ActivityLog',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic',
    )
    notifications = db.relationship(
        'Notification', back_populates='user',
        cascade='all, delete-orphan', lazy='dynamic',
    )

    @validates('email')
    def _normalize_email(self, _key, value):
        value = (value or '').strip().lower()
        if not value:
            raise ValueError('User email cannot be empty')
        if '@' not in value:
            raise ValueError(f'Invalid email: {value!r}')
        return value

    @validates('full_name')
    def _normalize_name(self, _key, value):
        value = (value or '').strip()
        if not value:
            raise ValueError('User full_name cannot be empty')
        return value

    def set_password(self, raw_password: str) -> None:
        if not raw_password or not isinstance(raw_password, str):
            raise ValueError('Password cannot be empty')
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash or not raw_password:
            return False
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self) -> str:
        return f'<User #{self.id} {self.email!r} role_id={self.role_id}>'
