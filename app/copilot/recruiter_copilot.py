from __future__ import annotations

import re

from app.copilot import intent_detector, query_engine, response_generator


NO_DATA = query_engine.NO_DATA


def serialize(item):
    score = item.get('score')
    return {
        'candidate_id': item['candidate'].id,
        'candidate_name': item['candidate'].full_name,
        'overall_score': score.overall_score if score else None,
        'recommendation': score.recommendation if score else 'Pending Resume',
        'skill_score': score.skill_score if score else None,
        'experience_score': score.experience_score if score else None,
        'mandatory_coverage': item.get('mandatory_coverage'),
        'shortlisted': bool(item.get('application') and item['application'].is_shortlisted),
    }


def _find_candidate(job_id, names):
    if not names:
        return None
    rows = query_engine.ranking(job_id)
    for item in rows:
        candidate_name = item['candidate'].full_name.casefold()
        if any(name.casefold() in candidate_name for name in names):
            return item
    return None


def answer(user_id, message, job_id=None, candidate_id=None):
    message = (message or '').strip()
    if not message:
        return {'intent': 'UNKNOWN', 'response': 'Please ask a recruitment question.', 'data': {}}
    intent = intent_detector.detect_intent(message)
    context = {'no_data': NO_DATA, 'serialize': serialize}
    if intent in ('INTERVIEW_STATISTICS', 'ANALYTICS_SUMMARY', 'JOB_PERFORMANCE', 'SKILL_GAP_STATISTICS'):
        context['analytics'] = {
            'interviews': query_engine.interview_statistics(user_id),
            'summary': query_engine.analytics_summary(user_id),
            'jobs': query_engine.job_performance(user_id),
            'skill_gaps': query_engine.skill_gap_statistics(user_id),
        }
        result = response_generator.generate(intent, context)
        result['intent'] = intent
        return result
    if job_id is None:
        jobs = [job for job in __import__('app.models', fromlist=['Job']).Job.query.filter_by(recruiter_id=user_id).all()]
        if len(jobs) == 1:
            job_id = jobs[0].id
    if job_id is None:
        return {'intent': intent, 'response': 'Which job would you like me to analyze?', 'data': {}}
    job = query_engine.owned_job(user_id, job_id)
    if not job:
        return {'intent': intent, 'response': 'I could not access that job from your recruiter account.', 'data': {}}
    context['job'] = job
    if intent in ('JOB_QUALITY', 'HIRING_INSIGHTS'):
        context['quality'] = query_engine.job_quality(user_id, job.id)
        context['hiring_insights'] = query_engine.hiring_insights(user_id, job.id)
        result = response_generator.generate(intent, context)
        result['intent'] = intent
        return result
    rows = query_engine.ranking(job.id)
    context['rows'] = rows
    names = intent_detector.extract_names(message)
    item = query_engine.candidate_score(job.id, candidate_id) if candidate_id else _find_candidate(job.id, names)
    context['candidate_item'] = item
    if intent in ('CANDIDATE_SUMMARY', 'SKILL_GAP', 'MATCH_EXPLANATION') and not item and candidate_id:
        return {'intent': intent, 'response': 'I could not find that candidate in the selected job context.', 'data': {}}
    if intent == 'SKILL_GAP' and not item and not any(word in message.casefold() for word in ('most', 'common', 'often')):
        return {'intent': intent, 'response': 'Which candidate should I analyze for skill gaps?', 'data': {}}
    if intent == 'CANDIDATE_COMPARISON' and names:
        context['rows'] = [candidate for candidate in rows if any(name.casefold() in candidate['candidate'].full_name.casefold() for name in names)][:3]
    if intent == 'CANDIDATE_SEARCH':
        skills = intent_detector.extract_skills(message, job.job_skills.all())
        context['rows'] = query_engine.search_candidates(job.id, skills, _experience_from_message(message))
    if intent == 'STATISTICS':
        context['statistics'] = query_engine.statistics(job.id)
    if intent == 'JOB_SUMMARY':
        context['job_summary'] = query_engine.job_summary(job.id)
    if intent == 'SKILL_GAP' and not item:
        context['gaps'] = query_engine.skill_gaps(job.id)
    result = response_generator.generate(intent, context)
    result['intent'] = intent
    return result


def _experience_from_message(message):
    match = re.search(r'(?:more than|over|at least)\s+(\d+(?:\.\d+)?)\s+years?', message.casefold())
    return float(match.group(1)) if match else None
