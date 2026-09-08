from urllib.parse import urljoin, urlparse

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.models import Candidate, Role, User
from app.utils.rate_limit import local_rate_limit


bp = Blueprint('auth', __name__)


def _safe_next_url(value):
    if not value:
        return None
    target = urlparse(urljoin(request.host_url, value))
    if target.netloc != request.host_url.rstrip('/').split('//', 1)[-1]:
        return None
    return target.path


def _dashboard_for(user):
    destinations = {
        Role.ADMIN: 'admin.dashboard',
        Role.RECRUITER: 'recruiter.dashboard',
        Role.CANDIDATE: 'candidate.dashboard',
    }
    return redirect(url_for(destinations[user.role.name]))


@bp.route('/login', methods=['GET', 'POST'])
@local_rate_limit(10)
def login():
    if current_user.is_authenticated:
        return _dashboard_for(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(email=email).first()

        if not email or not password:
            flash('Enter your email and password.', 'error')
        elif user is None or not user.check_password(password):
            flash('The email or password is incorrect.', 'error')
        elif not user.is_active:
            flash('This account is currently inactive.', 'error')
        else:
            login_user(user, remember=remember)
            next_url = _safe_next_url(request.args.get('next'))
            return redirect(next_url) if next_url else _dashboard_for(user)

    return render_template('auth/login.html', title='Sign in | SmartHire AI')


@bp.route('/register', methods=['GET', 'POST'])
@local_rate_limit(5)
def register():
    if current_user.is_authenticated:
        return _dashboard_for(current_user)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role_name = request.form.get('role', '').strip()
        error = None

        if not full_name or not email or not password or not confirm_password or not role_name:
            error = 'Complete all required fields.'
        elif len(full_name) > 160:
            error = 'Full name must be 160 characters or fewer.'
        else:
            try:
                email = validate_email(email, check_deliverability=False).normalized
            except EmailNotValidError:
                error = 'Enter a valid email address.'

        if error is None and len(password) < 8:
            error = 'Password must contain at least 8 characters.'
        elif error is None and password != confirm_password:
            error = 'Passwords do not match.'
        elif error is None and role_name not in (Role.RECRUITER, Role.CANDIDATE):
            error = 'Choose a valid account type.'
        elif error is None and User.query.filter_by(email=email).first() is not None:
            error = 'An account with this email already exists.'

        if error:
            flash(error, 'error')
        else:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                flash('Account roles are not configured yet. Run the seed command first.', 'error')
            else:
                user = User(full_name=full_name, email=email, role=role)
                user.set_password(password)
                db.session.add(user)
                if role.name == Role.CANDIDATE:
                    db.session.flush()
                    db.session.add(Candidate(
                        user_id=user.id,
                        full_name=full_name,
                        email=email,
                    ))
                db.session.commit()
                flash('Your account is ready. Sign in to continue.', 'success')
                return redirect(url_for('auth.login'))

    return render_template(
        'auth/register.html',
        title='Create account | SmartHire AI',
        roles=(Role.RECRUITER, Role.CANDIDATE),
    )


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))