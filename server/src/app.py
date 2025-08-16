"""
LPR Server Application Factory

This module provides the application factory pattern for creating Flask applications
with proper dependency injection and service registration.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_socketio import SocketIO
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from config import get_config

# Initialize extensions - use the same db instance as models
from core.models import db
socketio = SocketIO()

def setup_logging(app):
    """
    Setup application logging with rotation and proper formatting.
    
    Args:
        app: Flask application instance
    """
    if not app.debug:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Setup file handler with rotation
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        # Setup formatter
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Add handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        
        app.logger.info('LPR Server startup')

def create_app(config_class=None):
    """
    Application factory pattern for creating Flask applications.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../web/static')
    
    # Use provided config class or get from environment
    if config_class is None:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions with app
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    try:
        from web.blueprints.main import main_bp
        from web.blueprints.api import api_bp
        from web.blueprints.health import health_bp
        from web.blueprints.aicamera import aicamera_bp
        from web.blueprints.detection import detection_bp
        from web.blueprints.map import map_bp
        from web.blueprints.system import system_bp
        from web.blueprints.user import user_bp
        from web.blueprints.report import report_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(health_bp, url_prefix='/health')
        app.register_blueprint(aicamera_bp)
        app.register_blueprint(detection_bp)
        app.register_blueprint(map_bp)
        app.register_blueprint(system_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(report_bp)
        
        app.logger.info("All blueprints registered successfully")
    except ImportError as e:
        app.logger.warning(f"Some blueprints could not be loaded: {e}")
    
    # Create database tables
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")
    
    # Initialize services with app context
    with app.app_context():
        _initialize_services(app)
    
    app.logger.info("LPR Server application created successfully")
    return app

def create_socketio_app(config_class=None):
    """
    Create SocketIO app for WebSocket server.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Tuple of (socketio, app)
    """
    app = create_app(config_class)
    return socketio, app

def _initialize_services(app):
    """
    Initialize all services with proper dependencies.
    
    Args:
        app: Flask application instance
    """
    try:
        # Register services with dependency container
        from core.dependency_container import register_services, container
        register_services()
        
        # Get services from container
        websocket_service = container.get('websocket_service')
        blacklist_service = container.get('blacklist_service')
        health_service = container.get('health_service')
        database_service = container.get('database_service')
        
        # Initialize services with app context
        websocket_service.initialize(socketio, db.session)
        blacklist_service.initialize(db.session)
        health_service.initialize(db.session, socketio)
        database_service.initialize(db.session, app.config)
        
        app.logger.info("All services initialized successfully")
        
    except Exception as e:
        app.logger.error(f"Service initialization failed: {str(e)}")
        # Don't raise exception to allow app to start even if some services fail
