from __future__ import annotations

import re


def match_certifications(candidate_data, required_text=''):
    candidate = [item.get('name', '') for item in (candidate_data or [])]
    required = [part.strip() for part in (required_text or '').replace(';', ',').split(',') if part.strip()]
    if required and len(required) == 1:
        required = [match.group(0).strip() for match in re.finditer(
            r'(?i)(?:[A-Za-z0-9+#.-]+\s+)?(?:certified|certification|certificate)(?:\s+(?:in|for))?\s+[A-Za-z0-9+# .-]{2,50}',
            required[0],
        )]
    if not required:
        return {'certification_score': 100.0, 'matched_certifications': candidate, 'missing_certifications': [], 'explanation': 'No certification requirement specified.'}
    matched = [item for item in required if any(item.casefold() in value.casefold() or value.casefold() in item.casefold() for value in candidate)]
    missing = [item for item in required if item not in matched]
    return {'certification_score': round(100 * len(matched) / len(required), 1), 'matched_certifications': matched, 'missing_certifications': missing, 'explanation': f'{len(matched)} of {len(required)} required certifications matched.'}