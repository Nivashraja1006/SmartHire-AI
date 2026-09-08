from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import validates

from app import db


class Skill(db.Model):
    __tablename__ = 'skills'
    __table_args__ = (
        db.Index('ix_skills_category', 'category'),
    )

    CAT_PROGRAMMING = 'Programming Language'
    CAT_FRONTEND = 'Frontend'
    CAT_BACKEND = 'Backend'
    CAT_DATABASE = 'Database'
    CAT_CLOUD = 'Cloud'
    CAT_DEVOPS = 'DevOps'
    CAT_AI_ML = 'AI/ML'
    CAT_TESTING = 'Testing'
    CAT_TOOLS = 'Tools'
    CATEGORIES = (
        CAT_PROGRAMMING, CAT_FRONTEND, CAT_BACKEND, CAT_DATABASE,
        CAT_CLOUD, CAT_DEVOPS, CAT_AI_ML, CAT_TESTING, CAT_TOOLS,
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    category = db.Column(db.String(64), nullable=False, default=CAT_TOOLS)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )

    job_skills = db.relationship(
        'JobSkill', back_populates='skill',
        cascade='all, delete-orphan', lazy='dynamic',
    )
    candidate_skills = db.relationship(
        'CandidateSkill', back_populates='skill',
        cascade='all, delete-orphan', lazy='dynamic',
    )

    @validates('name')
    def _normalize_name(self, _key, value):
        value = (value or '').strip()
        if not value:
            raise ValueError('Skill name cannot be empty')
        return value

    @validates('category')
    def _validate_category(self, _key, value):
        if value and value not in Skill.CATEGORIES:
            raise ValueError(
                f'Invalid category {value!r}. Expected one of {Skill.CATEGORIES}'
            )
        return value or Skill.CAT_TOOLS

    def __repr__(self) -> str:
        return f'<Skill #{self.id} {self.name!r} [{self.category}]>'
