from __future__ import annotations

import re


INTENTS = (
    'TOP_CANDIDATES', 'CANDIDATE_SUMMARY', 'CANDIDATE_COMPARISON',
    'SKILL_GAP', 'MATCH_EXPLANATION', 'JOB_SUMMARY', 'CANDIDATE_SEARCH',
    'SHORTLIST_RECOMMENDATION', 'STATISTICS', 'INTERVIEW_STATISTICS',
    'ANALYTICS_SUMMARY', 'JOB_PERFORMANCE', 'SKILL_GAP_STATISTICS',
    'JOB_QUALITY', 'RESUME_QUALITY', 'HIRING_INSIGHTS', 'SYSTEM_HELP',
    'RANKING_STATUS', 'HELP', 'UNKNOWN',
)
PROTECTED_TERMS = ('gender', 'religion', 'caste', 'race', 'ethnicity', 'marital', 'appearance', 'photograph', 'young', 'old')


def detect_intent(message: str) -> str:
    text = (message or '').casefold()
    if any(term in text for term in PROTECTED_TERMS):
        return 'FAIRNESS'
    if re.search(r'\b(compare|versus| vs\.?|and)\b', text) and ('candidate' in text or len(re.findall(r'\b[A-Z][a-z]+\b', message or '')) >= 2):
        return 'CANDIDATE_COMPARISON'
    if any(term in text for term in ('top candidates', 'best candidates', 'highest score', 'ranked', 'ranking')):
        return 'TOP_CANDIDATES' if 'why' not in text else 'MATCH_EXPLANATION'
    if any(term in text for term in ('missing skill', 'skill gap', 'skills missing', 'skills is', 'gap')):
        return 'SKILL_GAP_STATISTICS' if any(term in text for term in ('most', 'common', 'often')) else 'SKILL_GAP'
    if any(term in text for term in ('job has the most', 'highest average', 'job performance', 'most applicants')):
        return 'JOB_PERFORMANCE'
    if any(term in text for term in ('interviews scheduled', 'interview statistics', 'interviewed', 'interviews this week')):
        return 'INTERVIEW_STATISTICS'
    if any(term in text for term in ('job description', 'job quality', 'quality of this job')):
        return 'JOB_QUALITY'
    if any(term in text for term in ('resume quality', 'how good is this resume')):
        return 'RESUME_QUALITY'
    if any(term in text for term in ('recruitment insights', 'hiring insights', 'major insights')):
        return 'HIRING_INSIGHTS'
    if any(term in text for term in ('shortlist rate', 'conversion rate', 'recruitment summary', 'analytics summary')):
        return 'ANALYTICS_SUMMARY'
    if any(term in text for term in ('why is', 'why was', 'ranked first', 'explain')):
        return 'MATCH_EXPLANATION'
    if any(term in text for term in ('summarize this job', 'job summary', 'requirements for this job')):
        return 'JOB_SUMMARY'
    if any(term in text for term in ('summarize', 'strengths of', 'profile of')):
        return 'CANDIDATE_SUMMARY'
    if any(term in text for term in ('shortlist', 'should i shortlist', 'who should')):
        return 'SHORTLIST_RECOMMENDATION'
    if any(term in text for term in ('how many', 'average score', 'statistics', 'excellent matches', 'strong matches', 'applied')):
        return 'STATISTICS'
    if any(term in text for term in ('find candidates', 'show candidates', 'candidates with', 'developers with')):
        return 'CANDIDATE_SEARCH'
    if any(term in text for term in ('help', 'what can you do', 'try asking')):
        return 'HELP'
    return 'UNKNOWN'


def extract_names(message: str) -> list[str]:
    quoted = re.findall(r'["\']([^"\']+)["\']', message or '')
    return quoted + re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', message or '')


def extract_skills(message: str, known_skills) -> list[str]:
    text = (message or '').casefold()
    return [skill.name for skill in known_skills if re.search(r'(?<!\w)' + re.escape(skill.name.casefold()) + r'(?!\w)', text)]
