"""
Configuration Management for LPR Server v3

This module provides configuration classes for different environments
with support for environment variables and .env files.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///lprserver.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File storage configuration
    IMAGE_STORAGE_PATH = os.environ.get('IMAGE_STORAGE_PATH') or 'storage/images'
    MAX_IMAGE_SIZE = int(os.environ.get('MAX_IMAGE_SIZE', 10485760))  # 10MB default
    
    # WebSocket configuration
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'eventlet')
    WEBSOCKET_PORT = int(os.environ.get('WEBSOCKET_PORT', 8765))
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/lprserver.log')
    
    # Health monitoring configuration
    HEALTH_CHECK_INTERVAL_MINUTES = int(os.environ.get('HEALTH_CHECK_INTERVAL_MINUTES', 5))
    HEALTH_CHECK_RETENTION_DAYS = int(os.environ.get('HEALTH_CHECK_RETENTION_DAYS', 7))
    
    # Database cleanup configuration
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 30))
    
    # Pagination
    RECORDS_PER_PAGE = int(os.environ.get('RECORDS_PER_PAGE', 20))
    DB_MAX_PAGE_SIZE = 100
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security configuration
    SECRET_KEY_MIN_LENGTH = int(os.environ.get('SECRET_KEY_MIN_LENGTH', 32))
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))
    
    # Network configuration
    DEFAULT_HTTP_PORT = int(os.environ.get('DEFAULT_HTTP_PORT', 5000))
    DEFAULT_NGINX_PORT = int(os.environ.get('DEFAULT_NGINX_PORT', 80))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lprserver_dev.db'
    LOG_LEVEL = 'DEBUG'
    
    # Development-specific settings
    HEALTH_CHECK_INTERVAL_MINUTES = 1  # More frequent checks in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # Production-specific settings
    # Use environment variables for production settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Ensure secure settings for production
    # Only check if SECRET_KEY is provided
    if SECRET_KEY and len(SECRET_KEY) < Config.SECRET_KEY_MIN_LENGTH:
        raise ValueError(f"SECRET_KEY must be at least {Config.SECRET_KEY_MIN_LENGTH} characters long")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'DEBUG'
    
    # Testing-specific settings
    HEALTH_CHECK_INTERVAL_MINUTES = 1
    DATA_RETENTION_DAYS = 1

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    Get configuration based on environment.
    
    Returns:
        Configuration class for current environment
    """
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    return config.get(config_name, config['default'])
