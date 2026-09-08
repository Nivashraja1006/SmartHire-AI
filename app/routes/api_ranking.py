"""
REST API endpoints for the AI-based ranking system.

Endpoints:
- POST /api/ranking/upload-resume - Upload and parse resume
- POST /api/ranking/analyze-jd - Analyze job description
- POST /api/ranking/match - Match candidate to job
- GET /api/ranking/results - Get ranking results
- GET /api/ranking/candidates - Get candidates with filters
- POST /api/ranking/generate-report - Generate PDF report
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.ai.jd_analyzer import analyze
from app.ai.ranking_engine import rank_candidates_for_job
from app.ai.resume_parser import parse_resume
from app.models import Application, Candidate, CandidateScore, Job, Resume, Skill
from app.services.matching_service import match_candidate_to_job
from app.utils.file_extraction import save_resume_upload
from app.realtime.events import emit_recruiter_event

logger = logging.getLogger(__name__)

bp = Blueprint('api_ranking', __name__, url_prefix='/api/ranking')


def json_response(data=None, error=None, status=200):
    """Helper to create JSON responses."""
    response = {
        'success': error is None,
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
    }
    if error:
        response['error'] = error
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def handle_api_errors(f):
    """Decorator to handle common API errors."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return json_response(error=str(e), status=400)
        except PermissionError as e:
            return json_response(error=str(e), status=403)
        except Exception as e:
            logger.error(f'API Error: {str(e)}', exc_info=True)
            return json_response(error='Internal server error', status=500)
    return wrapper


# ==================== RESUME HANDLING ====================

@bp.route('/upload-resume', methods=['POST'])
@login_required
@handle_api_errors
def upload_resume():
    """
    Upload and parse a resume file.
    
    Expected:
    - file: Resume file (PDF, DOCX)
    - candidate_id: Optional candidate ID (create new if not provided)
    
    Returns:
    - Parsed resume data with extracted information
    """
    if 'file' not in request.files:
        return json_response(error='No file provided', status=400)
    
    upload = request.files['file']
    if not upload or upload.filename == '':
        return json_response(error='No file selected', status=400)
    
    # Validate file type
    allowed_extensions = {'pdf', 'docx', 'doc'}
    if not upload.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        return json_response(error='Only PDF and DOCX files are allowed', status=400)
    
    # Get or create candidate
    candidate_id = request.form.get('candidate_id', type=int)
    if candidate_id:
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            return json_response(error='Candidate not found', status=404)
    else:
        # Create new candidate
        name = request.form.get('name', 'Unknown').strip()
        email = request.form.get('email', f'candidate_{datetime.utcnow().timestamp()}@example.com').strip()
        candidate = Candidate(full_name=name, email=email)
        db.session.add(candidate)
        db.session.flush()
    
    # Process upload
    try:
        original, stored, path, extension, text = save_resume_upload(upload)
        
        # Mark previous resumes as not current
        previous_resumes = Resume.query.filter_by(candidate_id=candidate.id, is_current=True).all()
        for resume in previous_resumes:
            resume.is_current = False
        
        # Create new resume record
        version = max((r.version for r in candidate.resumes.all()), default=0) + 1
        resume = Resume(
            candidate=candidate,
            original_filename=original,
            stored_filename=stored,
            file_path=path,
            file_type=extension,
            extracted_text=text,
            processing_status=Resume.STATUS_PROCESSING,
            version=version,
            is_current=True,
        )
        db.session.add(resume)
        db.session.flush()
        
        # Parse resume
        skills = Skill.query.all()
        parsed_data = parse_resume(text, skills)
        
        # Update resume and candidate with parsed data
        resume.parsed_data = parsed_data
        resume.processing_status = Resume.STATUS_COMPLETED
        
        # Update candidate info from parsed data
        if parsed_data.get('email'):
            candidate.email = parsed_data['email'].lower()
        if parsed_data.get('phone'):
            candidate.phone = parsed_data['phone']
        if parsed_data.get('total_experience') is not None:
            candidate.total_experience = parsed_data['total_experience']
        
        db.session.commit()
        
        logger.info(f'Resume uploaded and parsed: {resume.id}')
        
        return json_response({
            'resume_id': resume.id,
            'candidate_id': candidate.id,
            'candidate_name': candidate.full_name,
            'parsed_data': parsed_data,
            'message': 'Resume uploaded and parsed successfully',
        }, status=201)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Resume processing error: {str(e)}')
        return json_response(error=f'Failed to process resume: {str(e)}', status=400)


# ==================== JOB DESCRIPTION HANDLING ====================

@bp.route('/analyze-jd', methods=['POST'])
@login_required
@handle_api_errors
def analyze_jd():
    """
    Analyze a job description and extract requirements.
    
    Expected JSON:
    - jd_text: Job description text
    - job_id: Optional job ID to update
    
    Returns:
    - Extracted job requirements (skills, education, experience, etc.)
    """
    data = request.get_json() or {}
    jd_text = data.get('jd_text', '').strip()
    
    if not jd_text:
        return json_response(error='Job description text is required', status=400)
    
    if len(jd_text) < 50:
        return json_response(error='Job description is too short (minimum 50 characters)', status=400)
    
    try:
        # Analyze JD
        analysis = analyze(jd_text, Skill.query.all())
        
        job_id = data.get('job_id', type=int)
        if job_id:
            job = Job.query.get(job_id)
            if job and job.recruiter_id == current_user.id:
                job.description = jd_text
                db.session.commit()
        
        return json_response({
            'extracted_requirements': analysis,
            'jd_text_length': len(jd_text),
            'message': 'Job description analyzed successfully',
        })
        
    except Exception as e:
        logger.error(f'JD analysis error: {str(e)}')
        return json_response(error=f'Failed to analyze job description: {str(e)}', status=400)


# ==================== MATCHING & RANKING ====================

@bp.route('/match', methods=['POST'])
@login_required
@handle_api_errors
def match_candidate():
    """
    Match a candidate to a job and calculate scores.
    
    Expected JSON:
    - candidate_id: Candidate ID
    - job_id: Job ID
    
    Returns:
    - Match score and detailed matching results
    """
    data = request.get_json() or {}
    candidate_id = data.get('candidate_id', type=int)
    job_id = data.get('job_id', type=int)
    
    if not candidate_id or not job_id:
        return json_response(error='candidate_id and job_id are required', status=400)
    
    candidate = Candidate.query.get(candidate_id)
    job = Job.query.get(job_id)
    
    if not candidate:
        return json_response(error='Candidate not found', status=404)
    if not job:
        return json_response(error='Job not found', status=404)
    
    if job.recruiter_id != current_user.id:
        return json_response(error='You do not have permission to access this job', status=403)
    
    try:
        # Run matching algorithm
        result = match_candidate_to_job(candidate_id, job_id)
        
        return json_response({
            'candidate_id': candidate_id,
            'candidate_name': candidate.full_name,
            'job_id': job_id,
            'job_title': job.title,
            'overall_score': result.get('overall_score'),
            'recommendation': result.get('recommendation'),
            'component_scores': result.get('component_scores'),
            'matched_skills': result.get('matched_skills'),
            'missing_skills': result.get('missing_skills'),
            'explanation': result.get('explanation'),
        })
        
    except Exception as e:
        logger.error(f'Matching error: {str(e)}')
        return json_response(error=f'Failed to match candidate: {str(e)}', status=400)


@bp.route('/rank', methods=['POST'])
@login_required
@handle_api_errors
def rank_candidates():
    """
    Rank all candidates for a specific job.
    
    Expected JSON:
    - job_id: Job ID
    - force: Optional boolean to force recalculation
    
    Returns:
    - Ranked list of candidates with scores
    """
    data = request.get_json() or {}
    job_id = data.get('job_id', type=int)
    force = data.get('force', False, type=bool)
    
    if not job_id:
        return json_response(error='job_id is required', status=400)
    
    job = Job.query.get(job_id)
    if not job:
        return json_response(error='Job not found', status=404)
    
    if job.recruiter_id != current_user.id:
        return json_response(error='You do not have permission to access this job', status=403)
    
    try:
        # Rank candidates
        ranked_results = rank_candidates_for_job(job_id, force=force)
        
        # Format results
        formatted_results = []
        for item in ranked_results:
            score = item['score']
            formatted_results.append({
                'rank': item['rank'],
                'candidate_id': item['candidate'].id,
                'candidate_name': item['candidate'].full_name,
                'candidate_email': item['candidate'].email,
                'overall_score': score.overall_score if score else 0,
                'skill_score': score.skill_score if score else 0,
                'experience_score': score.experience_score if score else 0,
                'matched_skills': score.matched_skills if score else [],
                'missing_skills': score.missing_skills if score else [],
                'recommendation': score.recommendation if score else 'Not Assessed',
                'below_threshold': item['below_threshold'],
            })
        
        return json_response({
            'job_id': job_id,
            'job_title': job.title,
            'total_candidates': len(formatted_results),
            'ranked_candidates': formatted_results,
            'message': f'Successfully ranked {len(formatted_results)} candidates',
        })
        
    except Exception as e:
        logger.error(f'Ranking error: {str(e)}')
        return json_response(error=f'Failed to rank candidates: {str(e)}', status=400)


# ==================== RESULTS & RETRIEVAL ====================

@bp.route('/results/<int:job_id>', methods=['GET'])
@login_required
@handle_api_errors
def get_results(job_id):
    """
    Get ranking results for a specific job.
    
    Query parameters:
    - limit: Number of results to return (default: 50)
    - offset: Offset for pagination (default: 0)
    - min_score: Minimum score filter
    - max_score: Maximum score filter
    
    Returns:
    - Ranked candidates with detailed scores
    """
    job = Job.query.get(job_id)
    if not job:
        return json_response(error='Job not found', status=404)
    
    if job.recruiter_id != current_user.id:
        return json_response(error='You do not have permission', status=403)
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    min_score = request.args.get('min_score', 0, type=float)
    max_score = request.args.get('max_score', 100, type=float)
    
    # Query results
    query = (
        db.session.query(Candidate, CandidateScore, Application)
        .join(Application, Candidate.id == Application.candidate_id)
        .join(CandidateScore, Application.id == CandidateScore.application_id)
        .filter(Application.job_id == job_id)
        .filter(CandidateScore.overall_score.between(min_score, max_score))
        .order_by(CandidateScore.overall_score.desc())
    )
    
    total = query.count()
    results = query.limit(limit).offset(offset).all()
    
    formatted = []
    for candidate, score, application in results:
        formatted.append({
            'candidate_id': candidate.id,
            'candidate_name': candidate.full_name,
            'email': candidate.email,
            'phone': candidate.phone,
            'experience': candidate.total_experience,
            'overall_score': score.overall_score,
            'skill_score': score.skill_score,
            'experience_score': score.experience_score,
            'education_score': score.education_score,
            'recommendation': score.recommendation,
            'matched_skills': score.matched_skills,
            'missing_skills': score.missing_skills,
            'explanation': score.explanation,
        })
    
    return json_response({
        'job_id': job_id,
        'total_results': total,
        'returned': len(formatted),
        'offset': offset,
        'limit': limit,
        'candidates': formatted,
    })


# ==================== SEARCH & FILTER ====================

@bp.route('/candidates', methods=['GET'])
@login_required
@handle_api_errors
def search_candidates():
    """
    Search and filter candidates.
    
    Query parameters:
    - query: Search query (name, email)
    - skill: Filter by skill
    - min_experience: Minimum years of experience
    - max_experience: Maximum years of experience
    - limit: Results per page (default: 20)
    - offset: Pagination offset
    
    Returns:
    - List of matching candidates
    """
    query_text = request.args.get('query', '').strip()
    skill_filter = request.args.get('skill', '').strip()
    min_exp = request.args.get('min_experience', 0, type=float)
    max_exp = request.args.get('max_experience', 100, type=float)
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query_obj = Candidate.query
    
    # Text search
    if query_text:
        query_obj = query_obj.filter(
            db.or_(
                Candidate.full_name.ilike(f'%{query_text}%'),
                Candidate.email.ilike(f'%{query_text}%'),
            )
        )
    
    # Experience filter
    query_obj = query_obj.filter(
        Candidate.total_experience.between(min_exp, max_exp)
    )
    
    # Skill filter
    if skill_filter:
        skill = Skill.query.filter_by(name=skill_filter).first()
        if skill:
            from app.models import CandidateSkill
            query_obj = query_obj.join(
                CandidateSkill, Candidate.id == CandidateSkill.candidate_id
            ).filter(CandidateSkill.skill_id == skill.id)
    
    total = query_obj.count()
    candidates = query_obj.limit(limit).offset(offset).all()
    
    result = []
    for candidate in candidates:
        result.append({
            'id': candidate.id,
            'name': candidate.full_name,
            'email': candidate.email,
            'phone': candidate.phone,
            'experience': candidate.total_experience,
            'location': candidate.current_location,
        })
    
    return json_response({
        'total': total,
        'returned': len(result),
        'offset': offset,
        'limit': limit,
        'candidates': result,
    })


# ==================== STATISTICS & INSIGHTS ====================

@bp.route('/stats/<int:job_id>', methods=['GET'])
@login_required
@handle_api_errors
def get_statistics(job_id):
    """Get statistics and insights for a job posting."""
    job = Job.query.get(job_id)
    if not job:
        return json_response(error='Job not found', status=404)
    
    if job.recruiter_id != current_user.id:
        return json_response(error='Permission denied', status=403)
    
    applications = Application.query.filter_by(job_id=job_id).all()
    scores = CandidateScore.query.join(
        Application, CandidateScore.application_id == Application.id
    ).filter(Application.job_id == job_id).all()
    
    if not scores:
        avg_score = 0
        top_score = 0
        low_count = 0
    else:
        avg_score = sum(s.overall_score for s in scores) / len(scores)
        top_score = max(s.overall_score for s in scores)
        low_count = sum(1 for s in scores if s.overall_score < 40)
    
    return json_response({
        'job_id': job_id,
        'total_applications': len(applications),
        'total_scored': len(scores),
        'average_score': round(avg_score, 1),
        'top_score': top_score,
        'candidates_below_threshold': low_count,
        'recommendations': {
            'excellent': sum(1 for s in scores if s.overall_score >= 90),
            'strong': sum(1 for s in scores if 75 <= s.overall_score < 90),
            'good': sum(1 for s in scores if 60 <= s.overall_score < 75),
            'moderate': sum(1 for s in scores if 40 <= s.overall_score < 60),
            'low': sum(1 for s in scores if s.overall_score < 40),
        }
    })
