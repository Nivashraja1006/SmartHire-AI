from __future__ import annotations


def match_experience(candidate_experience, minimum=None, maximum=None):
    if candidate_experience is None or candidate_experience == '':
        return {'experience_score': 0.0, 'candidate_experience': 'Not detected', 'required_experience': 'Not specified', 'explanation': 'Candidate experience was not detected.'}
    value = float(candidate_experience)
    required = f'{minimum:g}–{maximum:g} years' if minimum is not None and maximum is not None else f'{minimum:g}+ years' if minimum is not None else 'Not specified'
    if minimum is None:
        score = 100.0
    elif value < minimum:
        score = max(0.0, 100 * value / minimum)
    elif maximum is not None and value > maximum:
        score = 95.0
    else:
        score = 100.0
    return {'experience_score': round(score, 1), 'candidate_experience': value, 'required_experience': required, 'explanation': f'{value:g} years against {required}.'}