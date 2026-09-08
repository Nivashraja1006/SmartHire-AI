from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user

from app import db
from app.copilot.recruiter_copilot import answer
from app.copilot.intent_detector import detect_intent
from app.models import Application, CopilotConversation, CopilotMessage, Job, Role
from app.services.ai_audit_service import audit_ai_operation
from app.realtime.events import emit_recruiter_event
from app.utils.decorators import role_required
from app.utils.rate_limit import local_rate_limit


bp = Blueprint('copilot', __name__)


def _conversation(conversation_id):
    return CopilotConversation.query.filter_by(id=conversation_id, user_id=current_user.id).first_or_404()


@bp.route('/recruiter/copilot')
@role_required(Role.RECRUITER)
def page():
    return render_template('recruiter/copilot.html', title='SmartHire Copilot')


@bp.route('/api/recruiter/copilot/conversations')
@role_required(Role.RECRUITER)
def conversations():
    rows = CopilotConversation.query.filter_by(user_id=current_user.id).order_by(CopilotConversation.updated_at.desc()).limit(20).all()
    return jsonify({'conversations': [{'id': row.id, 'job_id': row.job_id, 'candidate_id': row.candidate_id, 'updated_at': row.updated_at.isoformat()} for row in rows]})


@bp.route('/api/recruiter/copilot/conversations/<int:conversation_id>')
@role_required(Role.RECRUITER)
def conversation(conversation_id):
    row = _conversation(conversation_id)
    return jsonify({'id': row.id, 'messages': [{'sender': message.sender, 'message': message.message, 'intent': message.intent, 'created_at': message.created_at.isoformat()} for message in row.messages.order_by(CopilotMessage.created_at.asc()).all()]})


@bp.route('/api/recruiter/copilot/chat', methods=['POST'])
@role_required(Role.RECRUITER)
@local_rate_limit(30)
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get('message', '')).strip()
    if not message:
        return jsonify({'success': False, 'error': 'Enter a question for the Copilot.'}), 400
    conversation_id = payload.get('conversation_id')
    job_id = payload.get('job_id')
    candidate_id = payload.get('candidate_id')
    if job_id is not None and not Job.query.filter_by(id=job_id, recruiter_id=current_user.id).first():
        return jsonify({'success': True, 'intent': detect_intent(message), 'response': 'I could not access that job from your recruiter account.', 'data': {}})
    if candidate_id is not None and not Application.query.join(Job).filter(Job.recruiter_id == current_user.id, Application.candidate_id == candidate_id).first():
        return jsonify({'success': True, 'intent': detect_intent(message), 'response': 'I could not access that candidate from your recruiter account.', 'data': {}})
    row = _conversation(conversation_id) if conversation_id else CopilotConversation(user_id=current_user.id, job_id=job_id, candidate_id=candidate_id)
    if not conversation_id:
        db.session.add(row)
        db.session.flush()
    if payload.get('job_id') is not None:
        row.job_id = job_id
    if payload.get('candidate_id') is not None:
        row.candidate_id = candidate_id
    db.session.add(CopilotMessage(conversation=row, sender='recruiter', message=message))
    db.session.commit()
    emit_recruiter_event(current_user.id, 'copilot_request_started', {'conversation_id': row.id})
    try:
        result = answer(current_user.id, message, row.job_id, row.candidate_id)
        audit_ai_operation('copilot_query', 'message', row.id, algorithm='rule-based local copilot')
        db.session.add(CopilotMessage(conversation=row, sender='copilot', message=result['response'], intent=result['intent']))
        db.session.commit()
        output = {'success': True, 'conversation_id': row.id, **result}
        emit_recruiter_event(current_user.id, 'copilot_response_ready', {'conversation_id': row.id, 'intent': result['intent']})
        return jsonify(output)
    except Exception:
        db.session.rollback()
        emit_recruiter_event(current_user.id, 'copilot_error', {'conversation_id': row.id})
        return jsonify({'success': False, 'error': 'I could not analyze the available recruitment data right now.'}), 500
