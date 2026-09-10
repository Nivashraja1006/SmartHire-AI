from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import current_user

from app.ai.scoring_engine import DEFAULT_WEIGHTS
from app.routes.api_recruiter_matching import match_api as match_api_view
from app.models import Candidate, Job, Role
from app.utils.decorators import role_required


bp = Blueprint('recruiter_matching', __name__, url_prefix='/recruiter')

bp.add_url_rule(
    '/jobs/<int:job_id>/match/<int:candidate_id>',
    endpoint='match_api',
    view_func=match_api_view,
    methods=['POST'],
)


def _owned_job(job_id):
    return Job.query.filter_by(id=job_id, recruiter_id=current_user.id).first_or_404()


@bp.route('/jobs/<int:job_id>/matches')
@role_required(Role.RECRUITER)
def matches(job_id):
    job = _owned_job(job_id)
    candidates = Candidate.query.order_by(Candidate.updated_at.desc()).all()
    return render_template('recruiter/matches.html', title='Analyze candidates', job=job, candidates=candidates)


@bp.route('/jobs/<int:job_id>/candidates/<int:candidate_id>/match')
@role_required(Role.RECRUITER)
def match_page(job_id, candidate_id):
    job = _owned_job(job_id)
    candidate = Candidate.query.filter_by(id=candidate_id).first_or_404()
    return render_template('recruiter/match.html', title='AI candidate match', job=job, candidate=candidate, weights=DEFAULT_WEIGHTS)
