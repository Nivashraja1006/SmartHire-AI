from __future__ import annotations

from app.ai.semantic_matcher import semantic_similarity


def match_projects(projects, job_text):
    results = []
    for project in projects or []:
        text = ' '.join(str(project.get(key, '')) for key in ('name', 'description'))
        score = semantic_similarity(job_text, text) if text else 0.0
        results.append({'name': project.get('name', 'Unnamed project'), 'description': project.get('description', ''), 'relevance_score': score})
    results.sort(key=lambda item: item['relevance_score'], reverse=True)
    average = sum(item['relevance_score'] for item in results) / len(results) if results else 0.0
    return {'project_relevance_score': round(average, 1), 'relevant_projects': results[:5], 'project_explanation': 'Relevant project evidence was found.' if results and average else 'No project evidence was detected.'}