"""Small, local job-description analyzer for Phase 4.

The analyzer intentionally uses the seeded Skill dictionary and regular
expressions so it works offline and remains easy for recruiters to review.
"""
from __future__ import annotations

import re


EDUCATION_PATTERNS = (
    r"(?:bachelor(?:'s|s)?|master(?:'s|s)?|ph\.?d\.?|b\.?tech|m\.?tech|mba|degree)",
)
EXPERIENCE_PATTERN = re.compile(
    r"(?P<min>\d+)\s*(?:-|to)\s*(?P<max>\d+)\s*(?:years?|yrs?)|"
    r"(?P<single>\d+)\+?\s*(?:years?|yrs?)",
    re.IGNORECASE,
)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def analyze(text: str, skills=None) -> dict:
    """Return editable requirement suggestions from plain text."""
    cleaned = _clean_text(text)
    lowered = cleaned.casefold()
    detected = []
    for skill in skills or ():
        if re.search(r"(?<!\w)" + re.escape(skill.name.casefold()) + r"(?!\w)", lowered):
            detected.append({
                'name': skill.name,
                'category': skill.category,
                'importance': 'Mandatory' if re.search(
                    r"(?:required|must have|mandatory|essential).{0,100}" +
                    re.escape(skill.name.casefold()), lowered
                ) else 'Preferred',
            })

    experience_min = None
    experience_max = None
    match = EXPERIENCE_PATTERN.search(cleaned)
    if match:
        if match.group('min'):
            experience_min = float(match.group('min'))
            experience_max = float(match.group('max'))
        else:
            experience_min = float(match.group('single'))

    education = None
    for pattern in EDUCATION_PATTERNS:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            education = match.group(0)
            break

    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned)]
    responsibilities = [
        sentence for sentence in sentences
        if re.search(r"\b(build|develop|design|lead|manage|create|maintain|work)\b", sentence, re.I)
    ][:8]
    keywords = sorted({word.lower() for word in re.findall(r"\b[A-Za-z][A-Za-z+#.-]{3,}\b", cleaned)})[:40]
    return {
        'skills': detected,
        'min_experience': experience_min,
        'max_experience': experience_max,
        'education': education,
        'keywords': keywords,
        'responsibilities': responsibilities,
        'cleaned_text': cleaned,
    }