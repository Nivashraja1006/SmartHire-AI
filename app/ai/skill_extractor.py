from __future__ import annotations

import re


SKILLS = {}
for _category, _names in {
    'Programming Language': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Kotlin', 'Swift'],
    'Frontend': ['HTML', 'CSS', 'React', 'Angular', 'Vue', 'Next.js', 'Bootstrap', 'Tailwind CSS'],
    'Backend': ['Flask', 'Django', 'FastAPI', 'Node.js', 'Express.js', 'Spring Boot', '.NET'],
    'Database': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle'],
    'AI/ML': ['Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'OpenCV'],
    'Cloud': ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes'],
    'Tools': ['Git', 'GitHub', 'GitLab', 'Jira', 'Postman', 'VS Code'],
}.items():
    for _name in _names:
        SKILLS[_name] = _category
ALIASES = {
    'js': 'JavaScript', 'javascript es6': 'JavaScript', 'reactjs': 'React',
    'node': 'Node.js', 'nodejs': 'Node.js', 'postgres': 'PostgreSQL',
    'ml': 'Machine Learning', 'dl': 'Deep Learning', 'cv': 'Computer Vision',
    'tf': 'TensorFlow', 'k8s': 'Kubernetes', 'scikit learn': 'Scikit-learn',
}


def canonicalize(name: str) -> str:
    value = re.sub(r'\s+', ' ', (name or '').strip()).casefold()
    for alias, canonical in ALIASES.items():
        if value == alias.casefold():
            return canonical
    for skill in SKILLS:
        if value == skill.casefold():
            return skill
    return name.strip()


def extract_skills(text: str) -> list[dict]:
    found = {}
    normalized = (text or '').casefold()
    terms = list(SKILLS) + list(ALIASES)
    terms.sort(key=len, reverse=True)
    for term in terms:
        if re.search(r'(?<!\w)' + re.escape(term.casefold()) + r'(?!\w)', normalized):
            canonical = canonicalize(term)
            found[canonical.casefold()] = {
                'name': canonical,
                'category': SKILLS.get(canonical, 'Tools'),
                'source': 'text',
                'match_type': 'alias' if term.casefold() in {key.casefold() for key in ALIASES} else 'exact',
            }
    return sorted(found.values(), key=lambda item: item['name'].casefold())