import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IS_VERCEL = bool(os.getenv('VERCEL'))
IS_PRODUCTION = IS_VERCEL or os.getenv('FLASK_ENV') == 'production'

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or ('development-only-change-me' if not IS_PRODUCTION else None)
    DATABASE = BASE_DIR / 'database' / 'rivolic.db'
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    FRONTEND_ORIGINS = [origin.strip().rstrip('/') for origin in os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173').split(',') if origin.strip()]
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'None' if IS_PRODUCTION else 'Lax')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true' if IS_PRODUCTION else 'false').lower() == 'true'
    JSON_SORT_KEYS = False

def validate_production_config(app):
    if not IS_PRODUCTION:
        return
    missing = []
    if not app.config['SECRET_KEY']:
        missing.append('SECRET_KEY')
    if not app.config['DATABASE_URL']:
        missing.append('DATABASE_URL')
    if not os.getenv('FRONTEND_ORIGIN'):
        missing.append('FRONTEND_ORIGIN')
    if missing:
        raise RuntimeError('Missing required production environment variables: ' + ', '.join(missing))