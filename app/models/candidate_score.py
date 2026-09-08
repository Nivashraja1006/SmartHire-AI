from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import validates
from sqlalchemy import JSON

from app import db


class CandidateScore(db.Model):
    __tablename__ = 'candidate_scores'
    __table_args__ = (
        db.Index('ix_candidate_scores_application_id', 'application_id', unique=True),
        db.Index('ix_candidate_scores_overall_score', 'overall_score'),
    )

    REC_HIRE = 'Strong Hire'
    REC_SHORTLIST = 'Shortlist'
    REC_REVIEW = 'Review'
    REC_REJECT = 'Reject'
    REC_EXCELLENT = 'Excellent Match'
    REC_STRONG = 'Strong Match'
    REC_GOOD = 'Good Match'
    REC_MODERATE = 'Moderate Match'
    REC_LOW = 'Low Match'
    RECOMMENDATIONS = (REC_HIRE, REC_SHORTLIST, REC_REVIEW, REC_REJECT,
                       REC_EXCELLENT, REC_STRONG, REC_GOOD, REC_MODERATE, REC_LOW)

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id', ondelete='CASCADE',
                      name='fk_candidate_scores_application_id'),
        nullable=False,
        unique=True,
    )
    overall_score = db.Column(db.Float, nullable=False, default=0.0)
    skill_score = db.Column(db.Float, nullable=False, default=0.0)
    experience_score = db.Column(db.Float, nullable=False, default=0.0)
    project_score = db.Column(db.Float, nullable=False, default=0.0)
    education_score = db.Column(db.Float, nullable=False, default=0.0)
    certification_score = db.Column(db.Float, nullable=False, default=0.0)
    semantic_score = db.Column(db.Float, nullable=False, default=0.0)
    recommendation = db.Column(db.String(40), nullable=True)
    matched_skills = db.Column(JSON, nullable=True)
    missing_skills = db.Column(JSON, nullable=True)
    partial_skills = db.Column(JSON, nullable=True)
    explanation = db.Column(JSON, nullable=True)
    calculated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=db.func.now(),
    )

    application = db.relationship('Application', back_populates='score')

    @validates(
        'overall_score', 'skill_score', 'experience_score',
        'project_score', 'education_score', 'certification_score', 'semantic_score',
    )
    def _validate_score(self, key, value):
        value = 0.0 if value is None else float(value)
        if value < 0:
            raise ValueError(f'{key} cannot be negative')
        if value > 100:
            raise ValueError(f'{key} cannot exceed 100')
        return value

    @validates('recommendation')
    def _validate_recommendation(self, _key, value):
        if value and value not in CandidateScore.RECOMMENDATIONS:
            raise ValueError(f'Invalid recommendation {value!r}')
        return value

    def __repr__(self) -> str:
        return (
            f'<CandidateScore application_id={self.application_id}'
            f' overall={self.overall_score} rec={self.recommendation!r}>'
        )
