from __future__ import annotations

from collections import Counter

from app.ai.ranking_engine import rank_candidates_for_job
from app.models import Application, Candidate, CandidateSkill, Job, JobSkill, Skill
from app.services.analytics_service import get_interview_analytics, get_recruitment_overview, get_skill_gap_analytics
from app.ai.hiring_insights import generate_hiring_insights
from app.ai.job_quality_analyzer import analyze_job_quality


NO_DATA = "I couldn't find enough information in the available recruitment data."


def owned_job(user_id, job_id):
    return Job.query.filter_by(id=job_id, recruiter_id=user_id).first()


def owned_candidate(user_id, candidate_id, job_id=None):
    query = Candidate.query.filter_by(id=candidate_id)
    if job_id is not None:
        query = query.join(Application).filter(Application.job_id == job_id, Application.job_id.in_(
            [job.id for job in Job.query.filter_by(recruiter_id=user_id).all()]
        ))
    return query.first()


def ranking(job_id):
    return rank_candidates_for_job(job_id)


def top_candidates(job_id, limit=5):
    return ranking(job_id)[:limit]


def candidate_score(job_id, candidate_id):
    for item in ranking(job_id):
        if item['candidate'].id == candidate_id:
            return item
    return None


def job_summary(job_id):
    job = Job.query.get(job_id)
    if not job:
        return None
    mandatory = [item.skill.name for item in job.job_skills.all() if item.importance == JobSkill.IMPORTANCE_MANDATORY]
    preferred = [item.skill.name for item in job.job_skills.all() if item.importance == JobSkill.IMPORTANCE_PREFERRED]
    rows = ranking(job_id)
    scores = [item['score'].overall_score for item in rows if item['score']]
    return {'job': job, 'mandatory': mandatory, 'preferred': preferred, 'candidate_count': len(rows), 'average_score': round(sum(scores) / len(scores), 1) if scores else None}


def statistics(job_id):
    rows = ranking(job_id)
    scores = [item['score'].overall_score for item in rows if item['score']]
    tiers = Counter(item['score'].recommendation for item in rows if item['score'])
    return {'applicants': len(rows), 'analyzed': len(scores), 'excellent': tiers.get('Excellent Match', 0), 'strong': tiers.get('Strong Match', 0), 'good': tiers.get('Good Match', 0), 'moderate': tiers.get('Moderate Match', 0), 'low': tiers.get('Low Match', 0), 'below_threshold': sum(item['below_threshold'] for item in rows), 'average_score': round(sum(scores) / len(scores), 1) if scores else None}


def skill_gaps(job_id):
    counter = Counter()
    rows = ranking(job_id)
    for item in rows:
        if item['score']:
            for missing in item['score'].missing_skills or []:
                counter[missing.get('skill', 'Unknown')] += 1
    return [{'skill': skill, 'count': count} for skill, count in counter.most_common(10)]


def search_candidates(job_id, skills=None, minimum_experience=None):
    wanted = {value.casefold() for value in (skills or [])}
    results = []
    for item in ranking(job_id):
        candidate_skills = {skill.skill.name.casefold() for skill in item['candidate'].candidate_skills.all()}
        matched = wanted.intersection(candidate_skills)
        years = item['candidate'].total_experience or 0
        if wanted and matched != wanted:
            continue
        if minimum_experience is not None and years < minimum_experience:
            continue
        results.append(item)
    return results


def analytics_summary(user_id):
    return get_recruitment_overview(user_id)


def interview_statistics(user_id):
    return get_interview_analytics(user_id)


def job_performance(user_id):
    get_recruitment_overview(user_id)
    return [
        {'title': job.title, 'applications': job.applications.count(), 'average_match_score': round(sum(application.score.overall_score for application in job.applications if application.score) / max(sum(1 for application in job.applications if application.score), 1), 1)}
        for job in Job.query.filter_by(recruiter_id=user_id).all()
    ]


def skill_gap_statistics(user_id):
    output = []
    for job in Job.query.filter_by(recruiter_id=user_id).all():
        output.extend({'job': job.title, **gap} for gap in (get_skill_gap_analytics(job.id, user_id) or {}).get('gaps', []))
    output.sort(key=lambda item: (-item['missing_percent'], item['skill'].casefold()))
    return output[:10]


def hiring_insights(user_id, job_id):
    return generate_hiring_insights(job_id, user_id)


def job_quality(user_id, job_id):
    job = owned_job(user_id, job_id)
    return analyze_job_quality(job.description, [item.skill for item in job.job_skills.all()], job.min_experience, job.required_education) if job else None
