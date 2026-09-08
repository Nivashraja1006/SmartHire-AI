from __future__ import annotations

import logging

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import or_

from app import db
from app.ai.ranking_engine import MIN_MATCH_THRESHOLD, rank_candidates_for_job
from app.ai.scoring_engine import DEFAULT_WEIGHTS
from app.models import ActivityLog, Application, Candidate, Job, Notification, Role
from app.realtime.events import create_notification, emit_job_event, log_activity
from app.services.matching_service import match_candidate_to_job
from app.services.ai_audit_service import audit_ai_operation
from app.utils.decorators import role_required


logger = logging.getLogger(__name__)
bp = Blueprint('recruiter_ranking', __name__)


def _owned_job(job_id):
    return Job.query.filter_by(id=job_id, recruiter_id=current_user.id).first_or_404()


def _serialize(item):
    score = item['score']
    component_values = {
        'skill': score.skill_score if score else 0,
        'experience': score.experience_score if score else 0,
        'semantic': score.semantic_score if score else 0,
        'project': score.project_score if score else 0,
        'education': score.education_score if score else 0,
        'certification': score.certification_score if score else 0,
    }
    return {
        'rank': item['rank'],
        'candidate_id': item['candidate'].id,
        'candidate_name': item['candidate'].full_name,
        'email': item['candidate'].email,
        'overall_score': score.overall_score if score else None,
        'skill_score': score.skill_score if score else None,
        'experience_score': score.experience_score if score else None,
        'semantic_score': score.semantic_score if score else None,
        'project_score': score.project_score if score else None,
        'education_score': score.education_score if score else None,
        'certification_score': score.certification_score if score else None,
        'recommendation': score.recommendation if score else 'Pending Resume',
        'mandatory_coverage': item['mandatory_coverage'],
        'below_threshold': item['below_threshold'],
        'resume_status': item['resume'].processing_status if item['resume'] else 'Pending',
        'shortlisted': bool(item['application'] and item['application'].is_shortlisted),
        'matched_skills': score.matched_skills if score else [],
        'missing_skills': score.missing_skills if score else [],
        'partial_skills': score.partial_skills if score else [],
        'explanation': score.explanation if score else {},
        'score_trace': [{'component': key.title(), 'score': value, 'weight': DEFAULT_WEIGHTS[key], 'contribution': round(value * DEFAULT_WEIGHTS[key] / 100, 1)} for key, value in component_values.items()] if score else [],
    }


def _filtered(items):
    search = request.args.get('q', '').strip().casefold()
    level = request.args.get('level', '').strip().casefold()
    skill = request.args.get('skill', '').strip().casefold()
    minimum = request.args.get('minimum', type=float)
    experience = request.args.get('experience', '').strip()
    mandatory = request.args.get('mandatory', '').strip().casefold()
    status = request.args.get('resume_status', '').strip().casefold()
    sort = request.args.get('sort', 'best')
    output = []
    for item in items:
        data = _serialize(item)
        if search and search not in data['candidate_name'].casefold() and search not in data['email'].casefold():
            continue
        if level and level not in (data['recommendation'] or '').casefold():
            continue
        if minimum is not None and (data['overall_score'] is None or data['overall_score'] < minimum):
            continue
        if skill and not any(skill in str(entry).casefold() for entry in data['matched_skills'] + data['partial_skills']):
            continue
        if status and status not in data['resume_status'].casefold():
            continue
        if mandatory == 'matched' and data['mandatory_coverage']['percent'] < 100:
            continue
        if mandatory == 'partial' and not (0 < data['mandatory_coverage']['percent'] < 100):
            continue
        if mandatory == 'missing' and data['mandatory_coverage']['matched'] != 0:
            continue
        years = item['candidate'].total_experience or 0
        if experience == '0-1' and not 0 <= years <= 1:
            continue
        if experience == '1-3' and not 1 < years <= 3:
            continue
        if experience == '3-5' and not 3 < years <= 5:
            continue
        if experience == '5+' and years <= 5:
            continue
        output.append((item, data))
    if sort == 'lowest':
        output.sort(key=lambda pair: pair[1]['overall_score'] if pair[1]['overall_score'] is not None else -1)
    elif sort == 'skill':
        output.sort(key=lambda pair: pair[1]['skill_score'] if pair[1]['skill_score'] is not None else -1, reverse=True)
    elif sort == 'experience':
        output.sort(key=lambda pair: pair[1]['experience_score'] if pair[1]['experience_score'] is not None else -1, reverse=True)
    elif sort == 'semantic':
        output.sort(key=lambda pair: pair[1]['semantic_score'] if pair[1]['semantic_score'] is not None else -1, reverse=True)
    elif sort == 'project':
        output.sort(key=lambda pair: pair[1]['project_score'] if pair[1]['project_score'] is not None else -1, reverse=True)
    return output


@bp.route('/recruiter/jobs/<int:job_id>/ranking')
@role_required(Role.RECRUITER)
def ranking(job_id):
    job = _owned_job(job_id)
    results = rank_candidates_for_job(job.id)
    filtered = _filtered(results)
    serialized = [data for _, data in filtered]
    scored = [item for item in serialized if item['overall_score'] is not None]
    summary = {
        'total': len(results), 'analyzed': len(scored),
        'excellent': sum(item['recommendation'] == 'Excellent Match' for item in scored),
        'strong': sum(item['recommendation'] == 'Strong Match' for item in scored),
        'average': round(sum(item['overall_score'] for item in scored) / len(scored), 1) if scored else 0,
        'below_threshold': sum(item['below_threshold'] for item in serialized),
    }
    return render_template('recruiter/ranking.html', title='AI Candidate Ranking', job=job, rows=serialized, summary=summary, threshold=MIN_MATCH_THRESHOLD)


@bp.route('/api/recruiter/jobs/<int:job_id>/ranking')
@role_required(Role.RECRUITER)
def ranking_api(job_id):
    job = _owned_job(job_id)
    return jsonify({'success': True, 'job': {'id': job.id, 'title': job.title}, 'candidates': [_serialize(item) for item in rank_candidates_for_job(job.id)]})


@bp.route('/api/recruiter/jobs/<int:job_id>/ranking/recalculate', methods=['POST'])
@role_required(Role.RECRUITER)
def recalculate(job_id):
    job = _owned_job(job_id)
    emit_job_event(job.id, 'ranking_started', {'job_id': job.id, 'total_candidates': Candidate.query.count()}, job.recruiter_id)
    rows = rank_candidates_for_job(job.id, force=True)
    serialized = [_serialize(item) for item in rows]
    scored = [item for item in serialized if item['overall_score'] is not None]
    payload = {'job_id': job.id, 'candidate_count': len(scored), 'average_score': round(sum(item['overall_score'] for item in scored) / len(scored), 1) if scored else 0}
    audit_ai_operation('ranking', 'job', job.id, algorithm='local weighted ranking engine')
    log_activity(current_user.id, ActivityLog.TYPE_CANDIDATE_RANKED, f'Ranking recalculated for {job.title}.', payload)
    create_notification(current_user.id, 'AI ranking completed', f'Ranking updated for {job.title}.', Notification.TYPE_RANKING, job.id)
    db.session.commit()
    emit_job_event(job.id, 'ranking_completed', payload, job.recruiter_id)
    return jsonify({'success': True, 'candidates': serialized})


@bp.route('/api/recruiter/jobs/<int:job_id>/ranking/candidate/<int:candidate_id>')
@role_required(Role.RECRUITER)
def ranking_candidate(job_id, candidate_id):
    job = _owned_job(job_id)
    candidate = Candidate.query.filter_by(id=candidate_id).first_or_404()
    try:
        result = match_candidate_to_job(candidate.id, job.id)
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400
    return jsonify({'success': True, 'candidate': result['candidate'], 'job': result['job'], 'scores': {key: result[source] for key, source in {'overall': 'overall_score', 'skill': 'skill_score', 'experience': 'experience_score', 'semantic': 'semantic_score', 'project': 'project_relevance_score', 'education': 'education_score', 'certification': 'certification_score'}.items()}, 'explanation': result['explanation'], 'matched_skills': result['matched_skills'], 'partial_skills': result['partial_skills'], 'missing_skills': result['missing_skills']})


@bp.route('/api/recruiter/jobs/<int:job_id>/shortlist/<int:candidate_id>', methods=['POST', 'DELETE'])
@role_required(Role.RECRUITER)
def shortlist(job_id, candidate_id):
    job = _owned_job(job_id)
    candidate = Candidate.query.filter_by(id=candidate_id).first_or_404()
    application = Application.query.filter_by(job_id=job.id, candidate_id=candidate.id).first()
    if application is None:
        application = Application(job=job, candidate=candidate, status=Application.STATUS_UNDER_REVIEW)
        db.session.add(application)
    application.is_shortlisted = request.method == 'POST'
    db.session.commit()
    event_name = 'candidate_shortlisted' if application.is_shortlisted else 'candidate_unshortlisted'
    event = {'job_id': job.id, 'candidate_id': candidate.id, 'candidate_name': candidate.full_name, 'shortlisted': application.is_shortlisted}
    emit_job_event(job.id, event_name, event, job.recruiter_id)
    log_activity(current_user.id, ActivityLog.TYPE_APPLICATION_UPDATED, f'{candidate.full_name} shortlist updated.', event)
    create_notification(current_user.id, 'Candidate shortlisted' if application.is_shortlisted else 'Candidate removed from shortlist', f'{candidate.full_name} shortlist status updated.', Notification.TYPE_SHORTLIST, job.id, candidate.id)
    db.session.commit()
    return jsonify({'success': True, 'shortlisted': application.is_shortlisted})


@bp.route('/api/recruiter/jobs/<int:job_id>/compare', methods=['POST'])
@role_required(Role.RECRUITER)
def compare(job_id):
    job = _owned_job(job_id)
    payload = request.get_json(silent=True) or {}
    candidate_ids = payload.get('candidate_ids', [])
    if not isinstance(candidate_ids, list) or len(candidate_ids) > 3 or not candidate_ids:
        return jsonify({'success': False, 'error': 'Select between one and three candidates.'}), 400
    rows = rank_candidates_for_job(job.id)
    by_id = {item['candidate'].id: item for item in rows}
    if any(candidate_id not in by_id for candidate_id in candidate_ids):
        return jsonify({'success': False, 'error': 'One or more candidates are not available.'}), 400
    return jsonify({'success': True, 'candidates': [_serialize(by_id[candidate_id]) for candidate_id in candidate_ids]})


@bp.route('/recruiter/jobs/<int:job_id>/shortlist/<int:candidate_id>', methods=['POST'])
@role_required(Role.RECRUITER)
def shortlist_page(job_id, candidate_id):
    job = _owned_job(job_id)
    candidate = Candidate.query.filter_by(id=candidate_id).first_or_404()
    application = Application.query.filter_by(job_id=job.id, candidate_id=candidate.id).first()
    if application is None:
        application = Application(job=job, candidate=candidate, status=Application.STATUS_UNDER_REVIEW)
        db.session.add(application)
    application.is_shortlisted = True
    db.session.commit()
    return redirect(url_for('recruiter_ranking.ranking', job_id=job.id))
