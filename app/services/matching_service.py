from __future__ import annotations

import logging

from sqlalchemy import or_

from app import db
from app.ai.certification_matcher import match_certifications
from app.ai.education_matcher import match_education
from app.ai.experience_matcher import match_experience
from app.ai.explainability import explain
from app.ai.project_matcher import match_projects
from app.ai.scoring_engine import calculate_scores
from app.ai.semantic_matcher import semantic_similarity
from app.ai.skill_matcher import match_skills
from app.ai.skill_extractor import extract_skills
from app.models import Application, Candidate, CandidateScore, Job, Notification, Skill
from app.realtime.events import create_notification, emit_job_event, log_activity
from app.services.ai_audit_service import audit_ai_operation


logger = logging.getLogger(__name__)


def _resume_data(candidate):
    resume = candidate.resumes.filter_by(is_current=True).first()
    if not resume:
        raise ValueError('Candidate has no current resume.')
    if not resume.extracted_text:
        raise ValueError('Current resume has no extracted text.')
    return resume


def match_candidate_to_job(candidate_id, job_id):
    candidate = db.session.get(Candidate, candidate_id)
    job = db.session.get(Job, job_id)
    if not candidate or not job:
        raise ValueError('Candidate or job was not found.')
    resume = _resume_data(candidate)
    logger.info('MATCHING_STARTED candidate_id=%s job_id=%s', candidate_id, job_id)
    parsed = resume.parsed_data or {}
    candidate_skill_names = [item.skill.name for item in candidate.candidate_skills.all()]
    candidate_skill_names.extend(item['name'] for item in extract_skills(resume.extracted_text))
    required = [{'name': item.skill.name, 'importance': item.importance, 'weight': item.weight} for item in job.job_skills.all()]
    skills = match_skills(required, candidate_skill_names)
    experience = match_experience(candidate.total_experience if candidate.total_experience is not None else parsed.get('total_experience'), job.min_experience, job.max_experience)
    education = match_education(parsed.get('education', []), job.required_education)
    certification = match_certifications(parsed.get('certifications', []), job.description or '')
    project = match_projects(parsed.get('projects', []), job.description or '')
    semantic = {'semantic_score': semantic_similarity(job.description or '', resume.extracted_text)}
    parts = {**skills, **experience, **education, **certification, **project, **semantic}
    scored = calculate_scores(parts)
    result = {**parts, **scored}
    result['explanation'] = explain(result)
    application = Application.query.filter_by(candidate_id=candidate.id, job_id=job.id).first()
    if application is None:
        application = Application(candidate_id=candidate.id, job_id=job.id, status=Application.STATUS_UNDER_REVIEW)
        db.session.add(application)
        db.session.flush()
    score = application.score or CandidateScore(application=application)
    score.overall_score = scored['overall_score']
    score.skill_score = skills['skill_score']
    score.experience_score = experience['experience_score']
    score.education_score = education['education_score']
    score.certification_score = certification['certification_score']
    score.project_score = project['project_relevance_score']
    score.semantic_score = semantic['semantic_score']
    score.recommendation = scored['recommendation']
    score.matched_skills = skills['matched_skills']
    score.partial_skills = skills['partial_skills']
    score.missing_skills = skills['missing_skills']
    score.explanation = result['explanation']
    db.session.add(score)
    db.session.commit()
    audit_ai_operation('matching', 'candidate_job', application.id, algorithm='weighted local matching')
    db.session.commit()
    event = {
        'job_id': job.id, 'candidate_id': candidate.id,
        'candidate_name': candidate.full_name, 'score': score.overall_score,
        'recommendation': score.recommendation,
    }
    emit_job_event(job.id, 'candidate_score_updated', event, job.recruiter_id)
    log_activity(job.recruiter_id, 'Candidate Ranked', f'{candidate.full_name} scored {score.overall_score:.1f}% for {job.title}.', event)
    create_notification(job.recruiter_id, 'AI analysis completed', f'{candidate.full_name} scored {score.overall_score:.1f}% for {job.title}.', Notification.TYPE_MATCHING, job.id, candidate.id)
    db.session.commit()
    logger.info('MATCHING_COMPLETED candidate_id=%s job_id=%s score=%s', candidate_id, job_id, scored['overall_score'])
    result['candidate'] = {'id': candidate.id, 'name': candidate.full_name, 'email': candidate.email}
    result['job'] = {'id': job.id, 'title': job.title}
    return result