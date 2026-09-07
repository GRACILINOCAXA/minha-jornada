import os
from datetime import timedelta

try:
    from .resource_paths import get_database_path, is_frozen
except ImportError:
    from resource_paths import get_database_path, is_frozen

# Limites de upload
MAX_METHOD_PDF_SIZE = 50 * 1024 * 1024  # 50 MB para método personalizado

class Config:
    """Configuração base"""
    DEFAULT_DATABASE_URL = f'sqlite:///{get_database_path().as_posix()}'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = 'local-dev-secret-key-change-in-production'

    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.getenv('SESSION_LIFETIME_DAYS', '7')))
    MAX_METHOD_PDF_SIZE = MAX_METHOD_PDF_SIZE

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    if not os.getenv('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY is required in production. Set it in the environment before deploy.')

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
