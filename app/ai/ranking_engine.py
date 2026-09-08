from __future__ import annotations

from datetime import datetime

from app import db
from app.models import Application, Candidate, CandidateScore, Job
from app.services.matching_service import match_candidate_to_job


MIN_MATCH_THRESHOLD = 40.0


def _score_is_stale(candidate, job, score):
    if score is None:
        return True
    resume = candidate.resumes.filter_by(is_current=True).first()
    if resume is None or resume.processing_status != 'Completed':
        return False
    return bool(
        resume.uploaded_at and score.calculated_at and resume.uploaded_at > score.calculated_at
    ) or bool(job.updated_at and score.calculated_at and job.updated_at > score.calculated_at)


def _mandatory_coverage(job, score):
    required = [item for item in job.job_skills.all() if item.importance == 'Mandatory']
    matched = {item.get('skill', '').casefold() for item in (score.matched_skills or [])}
    total = len(required)
    covered = sum(1 for item in required if item.skill.name.casefold() in matched)
    return {
        'total': total,
        'matched': covered,
        'percent': round(100 * covered / total, 1) if total else 100.0,
    }


def _rank_key(item):
    score = item['score']
    applied = item['application'].applied_at if item['application'] else datetime.max
    return (
        -(score.overall_score if score else 0),
        -item['mandatory_coverage']['percent'],
        -(score.skill_score if score else 0),
        -(score.experience_score if score else 0),
        -(score.semantic_score if score else 0),
        -(score.project_score if score else 0),
        applied,
    )


def rank_candidates_for_job(job_id, force=False):
    job = db.session.get(Job, job_id)
    if not job:
        raise ValueError('Job not found.')
    results = []
    candidates = Candidate.query.order_by(Candidate.updated_at.desc()).all()
    for candidate in candidates:
        application = Application.query.filter_by(candidate_id=candidate.id, job_id=job.id).first()
        score = application.score if application else None
        resume = candidate.resumes.filter_by(is_current=True).first()
        if resume and resume.processing_status == 'Completed' and (force or _score_is_stale(candidate, job, score)):
            try:
                match_candidate_to_job(candidate.id, job.id)
            except ValueError:
                db.session.rollback()
            application = Application.query.filter_by(candidate_id=candidate.id, job_id=job.id).first()
            score = application.score if application else None
        coverage = _mandatory_coverage(job, score) if score else {'total': sum(1 for item in job.job_skills.all() if item.importance == 'Mandatory'), 'matched': 0, 'percent': 0.0}
        results.append({
            'candidate': candidate,
            'application': application,
            'score': score,
            'resume': resume,
            'mandatory_coverage': coverage,
            'below_threshold': score is None or score.overall_score < MIN_MATCH_THRESHOLD,
        })
    results.sort(key=_rank_key)
    for rank, item in enumerate(results, 1):
        item['rank'] = rank
    return results