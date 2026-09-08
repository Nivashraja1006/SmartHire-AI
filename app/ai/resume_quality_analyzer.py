from __future__ import annotations


def analyze_resume_quality(parsed_data, extracted_text=''):
    parsed = parsed_data or {}
    text = extracted_text or ''
    checks = {
        'contact information': bool(parsed.get('email') or parsed.get('phone')),
        'skills section': bool(parsed.get('skills')),
        'education': bool(parsed.get('education')),
        'experience': bool(parsed.get('experience') or parsed.get('total_experience')),
        'projects': bool(parsed.get('projects')),
        'certifications': bool(parsed.get('certifications')),
    }
    strong = [label.title() for label, present in checks.items() if present]
    needs = [label.title() for label, present in checks.items() if not present]
    if len(text.split()) < 80:
        needs.append('More resume detail')
    if text and any(text.casefold().count(word) > 5 for word in set(text.casefold().split())):
        needs.append('Repeated keywords')
    score = round(sum(checks.values()) / len(checks) * 80 + (20 if len(text.split()) >= 80 else 0))
    return {'score': min(score, 100), 'strong': strong, 'needs_improvement': needs, 'checks': checks}
