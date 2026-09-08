from __future__ import annotations

import re


EDUCATION_ALIASES = {'be': 'B.E', 'b e': 'B.E', 'btech': 'B.Tech', 'b tech': 'B.Tech', 'bsc': 'B.Sc', 'bca': 'BCA', 'mca': 'MCA', 'mtech': 'M.Tech', 'msc': 'M.Sc', 'mba': 'MBA', 'phd': 'PhD', 'diploma': 'Diploma'}


def normalize_education(value):
    text = (value or '').casefold()
    for alias, canonical in EDUCATION_ALIASES.items():
        if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', text):
            return canonical
    return value or ''


def match_education(candidate_data, required):
    candidate_items = candidate_data if isinstance(candidate_data, list) else []
    candidate_text = ' '.join(item.get('degree', '') for item in candidate_items)
    if not required:
        return {'education_score': 100.0, 'candidate_education': candidate_text or 'Not detected', 'required_education': 'Not specified', 'explanation': 'No education requirement specified.'}
    score = 100.0 if normalize_education(required).casefold() in normalize_education(candidate_text).casefold() else 0.0
    return {'education_score': score, 'candidate_education': candidate_text or 'Not detected', 'required_education': required, 'explanation': 'Required education matched.' if score else 'Required education was not detected.'}