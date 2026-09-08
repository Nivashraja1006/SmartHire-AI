from flask import Blueprint, redirect, url_for

from app.models import Role
from app.utils.decorators import role_required


bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/dashboard')
@role_required(Role.ADMIN)
def dashboard():
    return redirect(url_for('analytics.admin_analytics'))