from __future__ import annotations

from datetime import datetime
from sqlalchemy import UniqueConstraint

from app import db


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = (
        UniqueConstraint('name', name='uq_roles_name'),
    )

    ADMIN = 'Admin'
    RECRUITER = 'Recruiter'
    CANDIDATE = 'Candidate'
    _ALL = (ADMIN, RECRUITER, CANDIDATE)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )

    users = db.relationship(
        'User',
        back_populates='role',
        cascade='save-update, merge',
        lazy='dynamic',
    )

    def __repr__(self) -> str:
        return f'<Role #{self.id} name={self.name!r}>'
