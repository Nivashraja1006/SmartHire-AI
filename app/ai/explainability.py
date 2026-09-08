from __future__ import annotations


def explain(result):
    matched = result.get('matched_skills', [])
    partial = result.get('partial_skills', [])
    missing = result.get('missing_skills', [])
    strengths = [f"{item['skill']} matched" for item in matched]
    strengths.extend(f"{item['candidate_skill']} relates to {item['skill']}" for item in partial)
    if result.get('experience_score', 0) >= 75:
        strengths.append(result.get('experience_explanation', 'Experience requirement met.'))
    if result.get('education_score', 0) >= 75:
        strengths.append('Required education matched.')
    weaknesses = [f"{item['skill']} missing" for item in missing]
    weaknesses.extend(result.get('missing_certifications', []))
    overall = result.get('overall_score', 0)
    if strengths:
        summary = 'Candidate is a strong match because ' + ', '.join(strengths[:3]).lower() + '.'
    else:
        summary = 'Candidate has limited matching evidence in the available profile and resume data.'
    return {'strengths': strengths, 'weaknesses': weaknesses, 'summary': summary, 'score_reason': f'Match score is {overall:.1f} based on weighted, explainable signals.'}