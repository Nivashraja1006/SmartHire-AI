from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta

from sqlalchemy import case, distinct, func

from app import db
from app.models import (
    Application,
    Candidate,
    CandidateScore,
    CandidateSkill,
    Interview,
    Job,
    JobSkill,
    Resume,
    Role,
    Skill,
    User,
)


def _percent(value, total):
    return round((value / total) * 100, 1) if total else 0.0


def _date_range(days=30, start_date=None, end_date=None):
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=days - 1))
    if start > end:
        raise ValueError('start_date must be on or before end_date')
    return start, end


def _job_ids(recruiter_id=None):
    query = db.select(Job.id)
    if recruiter_id is not None:
        query = query.where(Job.recruiter_id == recruiter_id)
    return query


def get_recruitment_overview(recruiter_id=None):
    job_ids = _job_ids(recruiter_id)
    application_filter = Application.job_id.in_(job_ids)
    jobs = db.session.scalar(db.select(func.count(Job.id)).where(Job.id.in_(job_ids))) or 0
    active_jobs = db.session.scalar(db.select(func.count(Job.id)).where(Job.id.in_(job_ids), Job.status == Job.STATUS_ACTIVE)) or 0
    candidates = db.session.scalar(db.select(func.count(distinct(Application.candidate_id))).where(application_filter)) or 0
    applications = db.session.scalar(db.select(func.count(Application.id)).where(application_filter)) or 0
    analyzed = db.session.scalar(db.select(func.count(CandidateScore.id)).join(Application).where(application_filter)) or 0
    shortlisted = db.session.scalar(db.select(func.count(Application.id)).where(application_filter, Application.is_shortlisted.is_(True))) or 0
    interviews = db.session.scalar(db.select(func.count(Interview.id)).join(Application).where(application_filter)) or 0
    selected = db.session.scalar(db.select(func.count(Application.id)).where(application_filter, Application.status == Application.STATUS_SELECTED)) or 0
    average = db.session.scalar(db.select(func.avg(CandidateScore.overall_score)).join(Application).where(application_filter))
    score_rows = db.session.execute(
        db.select(CandidateScore.overall_score).join(Application).where(application_filter)
    ).scalars().all()
    distribution = {'excellent': 0, 'strong': 0, 'good': 0, 'moderate': 0, 'low': 0}
    for score in score_rows:
        bucket = 'excellent' if score >= 85 else 'strong' if score >= 70 else 'good' if score >= 55 else 'moderate' if score >= 40 else 'low'
        distribution[bucket] += 1
    return {
        'total_jobs': jobs,
        'active_jobs': active_jobs,
        'total_candidates': candidates,
        'total_applications': applications,
        'analyzed_candidates': analyzed,
        'shortlisted': shortlisted,
        'interviews': interviews,
        'selected': selected,
        'average_match_score': round(float(average), 1) if average is not None else 0.0,
        'shortlist_rate': _percent(shortlisted, applications),
        'interview_rate': _percent(interviews, applications),
        'selection_rate': _percent(selected, applications),
        'hiring_conversion_rate': _percent(selected, applications),
        **distribution,
    }


def get_application_funnel(job_id, recruiter_id=None):
    job_query = db.select(Job.id).where(Job.id == job_id)
    if recruiter_id is not None:
        job_query = job_query.where(Job.recruiter_id == recruiter_id)
    if db.session.scalar(job_query) is None:
        return None
    base = Application.job_id == job_id
    applications = db.session.scalar(db.select(func.count(Application.id)).where(base)) or 0
    analyzed = db.session.scalar(db.select(func.count(CandidateScore.id)).join(Application).where(base)) or 0
    strong = db.session.scalar(db.select(func.count(CandidateScore.id)).join(Application).where(base, CandidateScore.overall_score >= 70)) or 0
    shortlisted = db.session.scalar(db.select(func.count(Application.id)).where(base, Application.is_shortlisted.is_(True))) or 0
    interviewed = db.session.scalar(db.select(func.count(distinct(Interview.application_id))).join(Application).where(base)) or 0
    selected = db.session.scalar(db.select(func.count(Application.id)).where(base, Application.status == Application.STATUS_SELECTED)) or 0
    return {
        'candidates': db.session.scalar(db.select(func.count(distinct(Application.candidate_id))).where(base)) or 0,
        'applications': applications,
        'analyzed': analyzed,
        'strong_matches': strong,
        'shortlisted': shortlisted,
        'interviewed': interviewed,
        'selected': selected,
    }


def get_job_analytics(job_id, recruiter_id=None):
    funnel = get_application_funnel(job_id, recruiter_id)
    if funnel is None:
        return None
    job = db.session.get(Job, job_id)
    average = db.session.scalar(db.select(func.avg(CandidateScore.overall_score)).join(Application).where(Application.job_id == job_id))
    return {
        'job_id': job.id,
        'title': job.title,
        **funnel,
        'average_match_score': round(float(average), 1) if average is not None else 0.0,
        'shortlist_rate': _percent(funnel['shortlisted'], funnel['applications']),
        'interview_rate': _percent(funnel['interviewed'], funnel['applications']),
        'selection_rate': _percent(funnel['selected'], funnel['applications']),
    }


def get_candidate_analytics(job_id, recruiter_id=None):
    return get_job_analytics(job_id, recruiter_id)


def get_skill_gap_analytics(job_id, recruiter_id=None):
    if get_application_funnel(job_id, recruiter_id) is None:
        return None
    required = db.session.execute(
        db.select(Skill.id, Skill.name).join(JobSkill).where(JobSkill.job_id == job_id)
    ).all()
    candidate_ids = db.select(Application.candidate_id).where(Application.job_id == job_id)
    total = db.session.scalar(db.select(func.count(distinct(Application.candidate_id))).where(Application.job_id == job_id)) or 0
    available_rows = db.session.execute(
        db.select(Skill.name, func.count(distinct(CandidateSkill.candidate_id)))
        .join(CandidateSkill, CandidateSkill.skill_id == Skill.id)
        .where(CandidateSkill.candidate_id.in_(candidate_ids), Skill.id.in_([row.id for row in required]))
        .group_by(Skill.name)
    ).all()
    available = {name: count for name, count in available_rows}
    gaps = [
        {'skill': name, 'missing_count': max(total - available.get(name, 0), 0), 'missing_percent': _percent(max(total - available.get(name, 0), 0), total), 'available_percent': _percent(available.get(name, 0), total)}
        for _, name in required
    ]
    gaps.sort(key=lambda item: (-item['missing_percent'], item['skill'].casefold()))
    return {'required_skills': len(required), 'candidates': total, 'gaps': gaps}


def get_interview_analytics(recruiter_id=None):
    query = db.select(Interview).join(Application).join(Job, Job.id == Application.job_id)
    if recruiter_id is not None:
        query = query.where(Job.recruiter_id == recruiter_id)
    rows = db.session.scalars(query).all()
    counts = Counter(row.status for row in rows)
    return {'total': len(rows), 'by_status': dict(counts), 'upcoming': counts.get(Interview.STATUS_SCHEDULED, 0)}


def get_time_series_data(recruiter_id=None, days=30, start_date=None, end_date=None):
    start, end = _date_range(days, start_date, end_date)
    job_ids = _job_ids(recruiter_id)
    applications = db.session.execute(
        db.select(func.date(Application.applied_at), func.count(Application.id))
        .where(Application.job_id.in_(job_ids), Application.applied_at >= start, Application.applied_at < end + timedelta(days=1))
        .group_by(func.date(Application.applied_at)).order_by(func.date(Application.applied_at))
    ).all()
    scores = db.session.execute(
        db.select(func.date(CandidateScore.calculated_at), func.avg(CandidateScore.overall_score))
        .join(Application).where(Application.job_id.in_(job_ids), CandidateScore.calculated_at >= start, CandidateScore.calculated_at < end + timedelta(days=1))
        .group_by(func.date(CandidateScore.calculated_at)).order_by(func.date(CandidateScore.calculated_at))
    ).all()
    return {
        'start_date': start.isoformat(), 'end_date': end.isoformat(),
        'applications': [{'date': str(day), 'count': count} for day, count in applications],
        'scores': [{'date': str(day), 'average': round(float(value), 1)} for day, value in scores],
    }


def get_recruiter_analytics(recruiter_id):
    overview = get_recruitment_overview(recruiter_id)
    jobs = db.session.scalars(db.select(Job).where(Job.recruiter_id == recruiter_id).order_by(Job.created_at.desc())).all()
    return {**overview, 'jobs': [get_job_analytics(job.id, recruiter_id) for job in jobs]}


def get_admin_overview():
    role_counts = dict(db.session.execute(db.select(Role.name, func.count(User.id)).join(User, User.role_id == Role.id).group_by(Role.name)).all())
    jobs = {status: db.session.scalar(db.select(func.count(Job.id)).where(Job.status == status)) or 0 for status in Job.STATUSES}
    resumes = {status: db.session.scalar(db.select(func.count(Resume.id)).where(Resume.processing_status == status)) or 0 for status in Resume.STATUSES}
    return {
        'total_users': db.session.scalar(db.select(func.count(User.id))) or 0,
        'users_by_role': role_counts,
        'total_jobs': sum(jobs.values()), 'jobs_by_status': jobs,
        'total_candidates': db.session.scalar(db.select(func.count(Candidate.id))) or 0,
        'total_applications': db.session.scalar(db.select(func.count(Application.id))) or 0,
        'total_interviews': db.session.scalar(db.select(func.count(Interview.id))) or 0,
        'shortlisted': db.session.scalar(db.select(func.count(Application.id)).where(Application.is_shortlisted.is_(True))) or 0,
        'resumes_by_status': resumes,
        'database_connected': True,
    }
