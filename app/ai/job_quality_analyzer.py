from __future__ import annotations

import re


def analyze_job_quality(description, detected_skills=None, min_experience=None, education=None):
    text = re.sub(r'\s+', ' ', description or '').strip()
    lowered = text.casefold()
    issues = []
    strengths = []
    skills = [skill.get('name', '') if isinstance(skill, dict) else getattr(skill, 'name', '') for skill in (detected_skills or [])]
    if not text:
        issues.append('Job description is empty.')
    if not skills:
        issues.append('No recognizable skills were detected.')
    else:
        strengths.append(f'{len(skills)} job-relevant skills detected.')
    if min_experience is None and not re.search(r'\b\d+\+?\s*(?:years?|yrs?)\b', lowered):
        issues.append('Experience requirement is not clearly specified.')
    else:
        strengths.append('Experience requirement is present.')
    if not education and not re.search(r'\b(?:bachelor|master|degree|mba|b\.tech|m\.tech|ph\.d)\b', lowered):
        issues.append('Education requirement is not clearly specified.')
    if not re.search(r'\b(?:build|develop|design|lead|manage|create|maintain|responsibilit)', lowered):
        issues.append('Responsibilities are not clearly described.')
    duplicates = sorted({word for word in re.findall(r'\b[A-Za-z][A-Za-z+#.-]{3,}\b', lowered) if lowered.count(word) > 2})
    if duplicates:
        issues.append('Some requirement terms are repeated: ' + ', '.join(duplicates[:5]) + '.')
    if len(text.split()) < 30:
        issues.append('Description may be too broad; add framework, database, experience, and responsibility details.')
    score = max(0, min(100, 100 - len(issues) * 15))
    return {'score': score, 'issues': issues, 'strengths': strengths, 'detected_skills': skills, 'needs_review': score < 70}
