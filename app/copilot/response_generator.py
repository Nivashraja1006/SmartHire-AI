from __future__ import annotations


def _candidate_line(item):
    score = item['score']
    if not score:
        return f"{item['candidate'].full_name} — resume analysis pending"
    return f"{item['candidate'].full_name} — {score.overall_score:.1f}% — {score.recommendation}"


def generate(intent, context):
    if intent == 'FAIRNESS':
        return {
            'response': 'I can only evaluate candidates using job-relevant criteria such as skills, experience, education, certifications, projects, and the existing matching score.',
            'data': {},
        }
    if intent == 'HELP':
        return {'response': 'I can explain rankings, summarize jobs or candidates, find skill matches, analyze gaps, compare candidates, recommend a shortlist, and report recruitment, interview, and job performance statistics.', 'data': {}}
    if intent == 'INTERVIEW_STATISTICS':
        stats = context['analytics']['interviews']; return {'response': f"There are {stats['upcoming']} scheduled interviews and {stats['total']} total interviews in your recruiter workspace.", 'data': stats}
    if intent == 'JOB_QUALITY':
        quality = context.get('quality') or {}; return {'response': f"This job description has a quality score of {quality.get('score', 0)}/100. " + (' '.join(quality.get('issues', [])) if quality.get('issues') else 'No major quality issues were detected.'), 'data': quality}
    if intent == 'HIRING_INSIGHTS':
        insights = context.get('hiring_insights') or {}; return {'response': '\n'.join(insights.get('insights', [])) or context['no_data'], 'data': insights}
    if intent == 'ANALYTICS_SUMMARY':
        stats = context['analytics']['summary']; return {'response': f"You have {stats['total_applications']} applications, {stats['shortlisted']} shortlisted candidates, and a {stats['shortlist_rate']}% shortlist rate. Average match score is {stats['average_match_score']}%.", 'data': stats}
    if intent == 'JOB_PERFORMANCE':
        jobs = sorted(context['analytics']['jobs'], key=lambda item: item['applications'], reverse=True); return {'response': f"{jobs[0]['title']} has the most applicants with {jobs[0]['applications']}." if jobs else context['no_data'], 'data': {'jobs': jobs}}
    if intent == 'SKILL_GAP_STATISTICS':
        gaps = context['analytics']['skill_gaps']; return {'response': 'Most common missing skills:\n' + '\n'.join(f"- {item['skill']} — missing in {item['missing_percent']}% of candidates" for item in gaps) if gaps else context['no_data'], 'data': {'skill_gaps': gaps}}
    if intent == 'TOP_CANDIDATES':
        rows = context.get('rows', [])
        if not rows:
            return {'response': context['no_data'], 'data': {}}
        lines = '\n'.join(f'{index}. {_candidate_line(item)}' for index, item in enumerate(rows, 1))
        return {'response': f"Top candidates for {context['job'].title}:\n{lines}", 'data': {'candidates': [context['serialize'](item) for item in rows]}}
    if intent == 'MATCH_EXPLANATION':
        item = context.get('candidate_item') or (context.get('rows') or [None])[0]
        if not item or not item['score']:
            return {'response': context['no_data'], 'data': {}}
        score = item['score']; explanation = score.explanation or {}
        strengths = explanation.get('strengths', [])
        weaknesses = explanation.get('weaknesses', [])
        response = f"{item['candidate'].full_name} is scored at {score.overall_score:.1f}% ({score.recommendation}).\n\nMain reasons:\n" + '\n'.join(f'- {value}' for value in strengths[:6])
        if weaknesses:
            response += '\n\nPotential gaps:\n' + '\n'.join(f'- {value}' for value in weaknesses[:6])
        return {'response': response, 'data': {'candidate': context['serialize'](item)}}
    if intent == 'CANDIDATE_SUMMARY':
        item = context.get('candidate_item')
        if not item:
            return {'response': context['no_data'], 'data': {}}
        candidate = item['candidate']; parsed = (item['resume'].parsed_data if item['resume'] else {}) or {}; skills = [skill.skill.name for skill in candidate.candidate_skills.all()]
        response = f"{candidate.full_name} has {candidate.total_experience or 'not detected'} years of experience.\n\nTop skills: {', '.join(skills) or 'Not detected'}.\nCurrent match: {item['score'].overall_score:.1f}%" if item['score'] else f"{candidate.full_name} has no analyzed job match yet."
        return {'response': response, 'data': {'candidate': context['serialize'](item), 'education': parsed.get('education', []), 'projects': parsed.get('projects', []), 'certifications': parsed.get('certifications', [])}}
    if intent == 'SKILL_GAP':
        item = context.get('candidate_item')
        if item and item['score']:
            missing = [value.get('skill') for value in item['score'].missing_skills or []]
            partial = [value.get('skill') for value in item['score'].partial_skills or []]
            return {'response': f"Missing skills for {item['candidate'].full_name}:\n" + '\n'.join(f'- {value}' for value in missing) + ('\n\nRelated skills:\n' + '\n'.join(f'- {value}' for value in partial) if partial else ''), 'data': {'missing_skills': missing, 'partial_skills': partial}}
        gaps = context.get('gaps', [])
        return {'response': 'Most common missing skills:\n' + '\n'.join(f"{index}. {item['skill']} — missing in {item['count']} candidates" for index, item in enumerate(gaps, 1)) if gaps else context['no_data'], 'data': {'skill_gaps': gaps}}
    if intent == 'CANDIDATE_COMPARISON':
        rows = context.get('rows', [])
        if len(rows) < 2:
            return {'response': 'Please provide at least two candidates in the current job context to compare.', 'data': {}}
        lines = '\n'.join(f"{item['candidate'].full_name}: {item['score'].overall_score:.1f}%" for item in rows if item['score'])
        best = max((item for item in rows if item['score']), key=lambda item: item['score'].overall_score, default=None)
        response = f"Candidate comparison:\n{lines}\n\nBased on the current scoring model, {best['candidate'].full_name} has the stronger job match." if best else context['no_data']
        return {'response': response, 'data': {'candidates': [context['serialize'](item) for item in rows]}}
    if intent == 'SHORTLIST_RECOMMENDATION':
        rows = [item for item in context.get('rows', []) if item['score'] and item['score'].overall_score >= 75 and item['mandatory_coverage']['percent'] >= 50][:5]
        return {'response': 'Suggested shortlist:\n' + '\n'.join(f'{index}. {_candidate_line(item)}' for index, item in enumerate(rows, 1)) if rows else context['no_data'], 'data': {'candidates': [context['serialize'](item) for item in rows]}}
    if intent == 'STATISTICS':
        stats = context.get('statistics')
        if not stats or not stats['analyzed']:
            return {'response': context['no_data'], 'data': {}}
        response = f"Applicants: {stats['applicants']}\nAnalyzed: {stats['analyzed']}\nExcellent: {stats['excellent']}\nStrong: {stats['strong']}\nGood: {stats['good']}\nModerate: {stats['moderate']}\nLow: {stats['low']}\nAverage match score: {stats['average_score']}%"
        return {'response': response, 'data': {'statistics': stats}}
    if intent == 'JOB_SUMMARY':
        summary = context.get('job_summary')
        if not summary:
            return {'response': context['no_data'], 'data': {}}
        job = summary['job']; return {'response': f"{job.title} at {job.company_name}.\nExperience: {job.min_experience or 'Any'}–{job.max_experience or 'open'} years.\nMandatory skills: {', '.join(summary['mandatory']) or 'None'}.\nPreferred skills: {', '.join(summary['preferred']) or 'None'}.\nCandidates: {summary['candidate_count']}. Average score: {summary['average_score'] or 'Not available'}%", 'data': {'job': {'id': job.id, 'title': job.title}, 'summary': summary}}
    if intent == 'CANDIDATE_SEARCH':
        rows = context.get('rows', [])
        return {'response': '\n'.join(f'{index}. {_candidate_line(item)}' for index, item in enumerate(rows, 1)) if rows else context['no_data'], 'data': {'candidates': [context['serialize'](item) for item in rows]}}
    return {'response': 'I can answer questions about the current job, candidate scores, skill gaps, rankings, comparisons, and recruitment statistics. Try one of the suggested questions.', 'data': {}}
