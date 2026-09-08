from __future__ import annotations


DEFAULT_WEIGHTS = {
    'skill': 40, 'experience': 20, 'semantic': 15,
    'project': 10, 'education': 10, 'certification': 5,
}


def recommendation(score):
    if score >= 90: return 'Excellent Match'
    if score >= 75: return 'Strong Match'
    if score >= 60: return 'Good Match'
    if score >= 40: return 'Moderate Match'
    return 'Low Match'


def calculate_scores(parts, weights=None):
    weights = weights or DEFAULT_WEIGHTS
    if round(sum(weights.values()), 5) != 100:
        raise ValueError('Scoring weights must total 100.')
    scores = {
        'skill': float(parts.get('skill_score', 0)),
        'experience': float(parts.get('experience_score', 0)),
        'semantic': float(parts.get('semantic_score', 0)),
        'project': float(parts.get('project_relevance_score', 0)),
        'education': float(parts.get('education_score', 0)),
        'certification': float(parts.get('certification_score', 0)),
    }
    overall = round(sum(scores[key] * weights[key] / 100 for key in weights), 1)
    return {'overall_score': overall, 'recommendation': recommendation(overall), 'component_scores': scores, 'weights': weights}