from __future__ import annotations

from app.ai.skill_extractor import ALIASES, canonicalize


RELATED_SKILLS = {
    'django': {'flask', 'fastapi'}, 'flask': {'django', 'fastapi'},
    'react': {'vue', 'angular'}, 'vue': {'react', 'angular'},
    'mysql': {'postgresql', 'oracle'}, 'postgresql': {'mysql', 'oracle'},
    'aws': {'azure', 'google cloud'}, 'azure': {'aws', 'google cloud'},
}


def match_skills(required, candidate):
    candidate_names = {canonicalize(item).casefold(): item for item in candidate}
    matched, partial, missing = [], [], []
    total_weight = sum(float(item.get('weight') or (1.0 if item.get('importance') == 'Mandatory' else .5)) for item in required) or 1.0
    earned = 0.0
    for item in required:
        required_name = canonicalize(item['name'])
        key = required_name.casefold()
        weight = float(item.get('weight') or (1.0 if item.get('importance') == 'Mandatory' else .5))
        if key in candidate_names:
            kind = 'Alias Match' if candidate_names[key].casefold() != item['name'].casefold() else 'Exact Match'
            matched.append({'skill': required_name, 'candidate_skill': candidate_names[key], 'type': kind, 'weight': weight})
            earned += weight
        elif key in RELATED_SKILLS and RELATED_SKILLS[key].intersection(candidate_names):
            related = sorted(RELATED_SKILLS[key].intersection(candidate_names))[0]
            partial.append({'skill': required_name, 'candidate_skill': candidate_names[related], 'type': 'Related Match', 'weight': weight, 'credit': .5})
            missing.append({'skill': required_name, 'importance': item.get('importance', 'Preferred'), 'weight': weight, 'reason': 'No exact match; related skill found.'})
            earned += weight * .5
        else:
            missing.append({'skill': required_name, 'importance': item.get('importance', 'Preferred'), 'weight': weight})
    return {'skill_score': round(100 * earned / total_weight, 1), 'matched_skills': matched, 'partial_skills': partial, 'missing_skills': missing}