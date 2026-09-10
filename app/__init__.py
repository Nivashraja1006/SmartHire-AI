import os
import logging

from flask import Flask, jsonify, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFError, CSRFProtect
from dotenv import load_dotenv

from config import config_by_name

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    )

    config_cls = config_by_name.get(config_name, config_by_name['default'])
    if config_name == 'production':
        config_cls.validate()
    app.config.from_object(config_cls)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions'), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = app.config.get('LOGIN_VIEW', 'auth.login')
    login_manager.login_message = 'Please sign in to continue.'
    login_manager.login_message_category = 'info'

    @login_manager.unauthorized_handler
    def unauthorized():
        if request_wants_json():
            return jsonify({'success': False, 'error': 'Authentication required.'}), 401
        return redirect(url_for(login_manager.login_view, next=request.url))

    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get('SOCKETIO_CORS_ALLOWED_ORIGINS', '*'),
        async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading'),
    )

    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.recruiter import bp as recruiter_bp
    from app.routes.recruiter_candidates import bp as recruiter_candidates_bp
    from app.routes.recruiter_matching import bp as recruiter_matching_bp
    from app.routes.api_recruiter_matching import bp as api_recruiter_matching_bp
    from app.routes.recruiter_ranking import bp as recruiter_ranking_bp
    from app.routes.candidate import bp as candidate_bp
    from app.routes.notifications import bp as notifications_bp
    from app.routes.copilot import bp as copilot_bp
    from app.routes.analytics import bp as analytics_bp
    from app.routes.interviews import bp as interviews_bp
    from app.routes.quality import bp as quality_bp
    from app.routes.api_ranking import bp as api_ranking_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(recruiter_candidates_bp)
    app.register_blueprint(recruiter_matching_bp)
    app.register_blueprint(api_recruiter_matching_bp)
    app.register_blueprint(recruiter_ranking_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(copilot_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(interviews_bp)
    app.register_blueprint(quality_bp)
    app.register_blueprint(api_ranking_bp)

    from app.realtime import events  # noqa: F401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'Not found.'}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'success': False, 'error': 'Bad request.'}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'success': False, 'error': 'The uploaded request is too large.'}), 413

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({'success': False, 'error': 'The submitted data is invalid.'}), 422

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        return jsonify({'success': False, 'error': 'Your session token is invalid or expired. Refresh and try again.'}), 400

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'success': False, 'error': 'Access forbidden.'}), 403

    @app.errorhandler(500)
    def server_error(e):
        logging.getLogger(__name__).exception('Unhandled application error')
        return jsonify({'success': False, 'error': 'An internal server error occurred.'}), 500

    @app.after_request
    def add_api_cors_headers(response):
        origin = request.headers.get('Origin')
        allowed_origins = {
            item.strip()
            for item in app.config.get('CORS_ORIGINS', '').split(',')
            if item.strip()
        }
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response.headers.add('Vary', 'Origin')
        return response

    with app.app_context():
        try:
            from app import models
        except ImportError:
            pass

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    return app


def request_wants_json():
    return request.is_json or request.path.startswith('/api/')
