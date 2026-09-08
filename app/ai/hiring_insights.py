from __future__ import annotations

from collections import Counter

from sqlalchemy import func

from app import db
from app.models import Application, CandidateSkill, CandidateScore, Job, JobSkill, Skill


def _percent(value, total):
    return round(value * 100 / total, 1) if total else 0.0


def generate_hiring_insights(job_id, recruiter_id=None):
    job = Job.query.filter_by(id=job_id, **({'recruiter_id': recruiter_id} if recruiter_id is not None else {})).first()
    if job is None:
        return None
    applications = Application.query.filter_by(job_id=job.id).all()
    scores = [application.score for application in applications if application.score]
    required = [item.skill.name for item in job.job_skills.all()]
    missing = Counter()
    available = Counter()
    for score in scores:
        for item in score.missing_skills or []:
            missing[item.get('skill', 'Unknown')] += 1
        for item in score.matched_skills or []:
            available[item.get('skill', 'Unknown')] += 1
    mandatory = [item.skill.name for item in job.job_skills.all() if item.importance == JobSkill.IMPORTANCE_MANDATORY]
    complete = sum(not (score.missing_skills or []) for score in scores)
    insights = []
    if missing:
        skill, count = missing.most_common(1)[0]
        insights.append(f'Most candidates are missing {skill} ({_percent(count, len(scores))}% of analyzed applicants).')
    if available:
        skill, count = available.most_common(1)[0]
        insights.append(f'{skill} has the highest observed candidate availability ({_percent(count, len(scores))}% of analyzed applicants).')
    if mandatory:
        insights.append(f'{_percent(complete, len(scores))}% of analyzed applicants satisfy all detected mandatory skills.')
    if scores:
        moderate = sum(40 <= score.overall_score < 60 for score in scores)
        if moderate:
            insights.append(f'Most applications for this role have moderate skill alignment ({_percent(moderate, len(scores))}%).')
    recommendations = []
    if missing:
        skill, count = missing.most_common(1)[0]
        if count / max(len(scores), 1) >= 0.5:
            recommendations.append(f'Consider reviewing whether {skill} should remain mandatory because it is missing in most analyzed applicants.')
    if job.min_experience is None:
        recommendations.append('Consider specifying a minimum experience requirement so candidate fit can be reviewed consistently.')
    if not job.required_education:
        recommendations.append('Consider specifying education requirements if they are relevant to this role.')
    return {'job_id': job.id, 'job_title': job.title, 'applicants': len(applications), 'analyzed': len(scores), 'insights': insights, 'recommendations': recommendations, 'missing_skills': [{'skill': name, 'count': count, 'percent': _percent(count, len(scores))} for name, count in missing.most_common(10)], 'mandatory_coverage_percent': _percent(complete, len(scores))}
