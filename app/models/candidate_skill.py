from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint, Index

from app import db


class CandidateSkill(db.Model):
    __tablename__ = 'candidate_skills'
    __table_args__ = (
        UniqueConstraint(
            'candidate_id', 'skill_id', name='uq_candidate_skills_candidate_skill',
        ),
        Index('ix_candidate_skills_candidate_id', 'candidate_id'),
        Index('ix_candidate_skills_skill_id', 'skill_id'),
        Index('ix_candidate_skills_proficiency', 'proficiency_level'),
    )

    PROF_BEGINNER = 'Beginner'
    PROF_INTERMEDIATE = 'Intermediate'
    PROF_ADVANCED = 'Advanced'
    PROFICIENCIES = (PROF_BEGINNER, PROF_INTERMEDIATE, PROF_ADVANCED)

    SRC_RESUME = 'Resume'
    SRC_MANUAL = 'Manual'
    SRC_PROFILE = 'Profile'
    SOURCES = (SRC_RESUME, SRC_MANUAL, SRC_PROFILE)

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidates.id', ondelete='CASCADE',
                      name='fk_candidate_skills_candidate_id'),
        nullable=False,
    )
    skill_id = db.Column(
        db.Integer,
        db.ForeignKey('skills.id', ondelete='CASCADE',
                      name='fk_candidate_skills_skill_id'),
        nullable=False,
    )
    proficiency_level = db.Column(db.String(32), nullable=False, default=PROF_INTERMEDIATE)
    source = db.Column(db.String(32), nullable=False, default=SRC_RESUME)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )

    candidate = db.relationship('Candidate', back_populates='candidate_skills')
    skill = db.relationship('Skill', back_populates='candidate_skills')

    @validates('proficiency_level')
    def _validate_proficiency(self, _key, value):
        if value and value not in CandidateSkill.PROFICIENCIES:
            raise ValueError(f'Invalid proficiency_level {value!r}')
        return value or CandidateSkill.PROF_INTERMEDIATE

    @validates('source')
    def _validate_source(self, _key, value):
        if value and value not in CandidateSkill.SOURCES:
            raise ValueError(f'Invalid source {value!r}')
        return value or CandidateSkill.SRC_RESUME

    def __repr__(self) -> str:
        return (
            f'<CandidateSkill candidate_id={self.candidate_id}'
            f' skill_id={self.skill_id} proficiency={self.proficiency_level}'
            f' src={self.source}>'
        )
