from __future__ import annotations

from flask import Blueprint, jsonify
from flask_login import current_user

from app.models import Candidate, Job, Role
from app.services.matching_service import match_candidate_to_job
from app.utils.decorators import role_required
from app.utils.rate_limit import local_rate_limit


bp = Blueprint('api_recruiter_matching', __name__, url_prefix='/api/recruiter')


def _owned_job(job_id):
    return Job.query.filter_by(id=job_id, recruiter_id=current_user.id).first_or_404()


@bp.route('/jobs/<int:job_id>/match/<int:candidate_id>', methods=['POST'])
@role_required(Role.RECRUITER)
@local_rate_limit(20)
def match_api(job_id, candidate_id):
    job = _owned_job(job_id)
    if not Candidate.query.filter_by(id=candidate_id).first():
        return jsonify({'success': False, 'error': 'Candidate not found.'}), 404
    try:
        result = match_candidate_to_job(candidate_id, job.id)
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400
    return jsonify({
        'success': True,
        'candidate': result['candidate'],
        'job': result['job'],
        'scores': {
            'overall': result['overall_score'],
            'skill': result['skill_score'],
            'experience': result['experience_score'],
            'education': result['education_score'],
            'certification': result['certification_score'],
            'project': result['project_relevance_score'],
            'semantic': result['semantic_score'],
        },
        'matched_skills': result['matched_skills'],
        'partial_skills': result['partial_skills'],
        'missing_skills': result['missing_skills'],
        'recommendation': result['recommendation'],
        'explanation': result['explanation'],
        'relevant_projects': result['relevant_projects'],
        'experience_analysis': {
            'candidate_experience': result['candidate_experience'],
            'required_experience': result['required_experience'],
            'explanation': result['experience_explanation'],
        },
    })
