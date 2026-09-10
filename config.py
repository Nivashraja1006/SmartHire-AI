import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-change-me'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')
    TESTING = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    UPLOAD_FOLDER = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))

    ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
    ALLOWED_JD_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}

    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')

    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS
    SOCKETIO_ASYNC_MODE = 'threading'

    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    LOGIN_VIEW = os.environ.get('FLASK_LOGIN_LOGIN_VIEW', 'auth.login')
    SESSION_PROTECTION = os.environ.get('FLASK_LOGIN_SESSION_PROTECTION', 'strong')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_TIME_LIMIT = 3600
    AI_ENGINE_VERSION = os.environ.get('AI_ENGINE_VERSION', '1.0.0')

    @staticmethod
    def _make_mysql_url():
        url = os.environ.get('DATABASE_URL')
        if url:
            return url
        host = os.environ.get('MYSQL_HOST', 'localhost')
        port = os.environ.get('MYSQL_PORT', '3306')
        user = os.environ.get('MYSQL_USER', 'root')
        pwd = os.environ.get('MYSQL_PASSWORD', '')
        db = os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB', 'smarthire_ai')
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

    SQLALCHEMY_DATABASE_URI = (
        Config._make_mysql_url()
        if os.environ.get('DATABASE_URL') or os.environ.get('USE_MYSQL', '').lower() in ('true', '1', 'yes')
        else 'sqlite:///' + os.path.join(basedir, 'dev.db')
    )

    SERVER_NAME = None
    PREFERRED_URL_SCHEME = 'http'


class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

    SQLALCHEMY_DATABASE_URI = Config._make_mysql_url()

    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True

    @classmethod
    def validate(cls):
        if cls.SECRET_KEY == 'dev-only-change-me':
            raise RuntimeError('SECRET_KEY must be configured in production.')
        if not os.environ.get('DATABASE_URL') and not os.environ.get('MYSQL_PASSWORD'):
            raise RuntimeError('DATABASE_URL or MYSQL_PASSWORD must be configured in production.')


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
