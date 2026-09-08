from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint, Index

from app import db


class JobSkill(db.Model):
    __tablename__ = 'job_skills'
    __table_args__ = (
        UniqueConstraint('job_id', 'skill_id', name='uq_job_skills_job_skill'),
        Index('ix_job_skills_job_id', 'job_id'),
        Index('ix_job_skills_skill_id', 'skill_id'),
        Index('ix_job_skills_importance', 'importance'),
    )

    IMPORTANCE_MANDATORY = 'Mandatory'
    IMPORTANCE_PREFERRED = 'Preferred'
    IMPORTANCES = (IMPORTANCE_MANDATORY, IMPORTANCE_PREFERRED)

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id', ondelete='CASCADE', name='fk_job_skills_job_id'),
        nullable=False,
    )
    skill_id = db.Column(
        db.Integer,
        db.ForeignKey('skills.id', ondelete='CASCADE', name='fk_job_skills_skill_id'),
        nullable=False,
    )
    importance = db.Column(db.String(32), nullable=False, default=IMPORTANCE_MANDATORY)
    weight = db.Column(db.Float, nullable=True, default=1.0)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )

    job = db.relationship('Job', back_populates='job_skills')
    skill = db.relationship('Skill', back_populates='job_skills')

    @validates('importance')
    def _validate_importance(self, _key, value):
        if value and value not in JobSkill.IMPORTANCES:
            raise ValueError(f'Invalid importance {value!r}')
        return value or JobSkill.IMPORTANCE_MANDATORY

    @validates('weight')
    def _validate_weight(self, _key, value):
        if value is None:
            return 1.0
        if value <= 0:
            raise ValueError('weight must be positive')
        return value

    def __repr__(self) -> str:
        return (
            f'<JobSkill job_id={self.job_id} skill_id={self.skill_id}'
            f' importance={self.importance} weight={self.weight}>'
        )
