#!/usr/bin/env python3
"""
AI Camera v1.3 Flask Application

Main Flask application that integrates camera services and web interface
using absolute imports and existing blueprint structure.

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import os
import sys
from pathlib import Path
from typing import Tuple
from datetime import datetime

# Load environment variables from .env.production first
def load_env_file():
    """Load environment variables from .env.production file."""
    env_file = Path(__file__).parent.parent / '.env.production'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key.strip()] = value

# Load environment variables
load_env_file()

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO
import logging

# Import import helper first to setup paths
from v1_3.src.core.utils.import_helper import setup_import_paths, validate_imports
setup_import_paths()

from v1_3.src.core.utils.logging_config import setup_logging, get_logger
from v1_3.src.core.dependency_container import get_container, get_service
from v1_3.src.web.blueprints import register_blueprints
from v1_3.src.core.config import (
    AUTO_START_CAMERA, AUTO_START_DETECTION, AUTO_START_HEALTH_MONITOR, AUTO_START_WEBSOCKET_SENDER,
    AUTO_START_STORAGE_MONITOR, STARTUP_DELAY, HEALTH_MONITOR_STARTUP_DELAY, 
    WEBSOCKET_SENDER_STARTUP_DELAY, STORAGE_MONITOR_STARTUP_DELAY, STORAGE_MONITOR_INTERVAL
)


def _initialize_services(logger):
    """
    Initialize services in the correct order with modular architecture support.
    
    Modular Architecture:
    - Core modules (camera, detection, health) are essential and must work
    - Optional modules (websocket sender, storage) can be disabled without affecting core
    - Each phase is independent and can fail without stopping the system
    
    Args:
        logger: Logger instance
    """
    logger.info("🚀 Starting modular service initialization sequence...")
    
    # Track initialization results
    init_results = {
        'core_modules': {},
        'optional_modules': {},
        'errors': []
    }
    
    # === PHASE 1: Core Infrastructure ===
    logger.info("📋 Phase 1: Core Infrastructure")
    try:
        # Logger and config are already initialized by DI container
        logger.info("✅ Core infrastructure ready")
    except Exception as e:
        logger.error(f"❌ Core infrastructure failed: {e}")
        init_results['errors'].append(f"Core infrastructure: {e}")
        return False  # Core infrastructure failure is critical
    
    # === PHASE 2: Core Components ===
    logger.info("🔧 Phase 2: Core Components")
    
    # Camera Handler
    try:
        camera_handler = get_service('camera_handler')
        if camera_handler:
            logger.info("✅ Camera Handler available")
            init_results['core_modules']['camera_handler'] = True
        else:
            logger.error("❌ Camera Handler not available")
            init_results['core_modules']['camera_handler'] = False
            init_results['errors'].append("Camera Handler not available")
    except Exception as e:
        logger.error(f"❌ Camera Handler error: {e}")
        init_results['core_modules']['camera_handler'] = False
        init_results['errors'].append(f"Camera Handler: {e}")
    
    # Detection Processor
    try:
        detection_processor = get_service('detection_processor')
        if detection_processor:
            logger.info("✅ Detection Processor available")
            init_results['core_modules']['detection_processor'] = True
        else:
            logger.warning("⚠️ Detection Processor not available")
            init_results['core_modules']['detection_processor'] = False
    except Exception as e:
        logger.warning(f"⚠️ Detection Processor error: {e}")
        init_results['core_modules']['detection_processor'] = False
    
    # Database Manager
    try:
        database_manager = get_service('database_manager')
        if database_manager:
            logger.info("✅ Database Manager available")
            init_results['core_modules']['database_manager'] = True
        else:
            logger.error("❌ Database Manager not available")
            init_results['core_modules']['database_manager'] = False
            init_results['errors'].append("Database Manager not available")
    except Exception as e:
        logger.error(f"❌ Database Manager error: {e}")
        init_results['core_modules']['database_manager'] = False
        init_results['errors'].append(f"Database Manager: {e}")
    
    # Health Monitor
    try:
        health_monitor = get_service('health_monitor')
        if health_monitor:
            logger.info("✅ Health Monitor available")
            init_results['core_modules']['health_monitor'] = True
        else:
            logger.error("❌ Health Monitor not available")
            init_results['core_modules']['health_monitor'] = False
            init_results['errors'].append("Health Monitor not available")
    except Exception as e:
        logger.error(f"❌ Health Monitor error: {e}")
        init_results['core_modules']['health_monitor'] = False
        init_results['errors'].append(f"Health Monitor: {e}")
    
    # === PHASE 3: Core Services ===
    logger.info("⚙️ Phase 3: Core Services")
    
    # Camera Manager
    try:
        camera_manager = get_service('camera_manager')
        if camera_manager:
            success = camera_manager.initialize()
            if success:
                logger.info("✅ Camera Manager initialized successfully")
                init_results['core_modules']['camera_manager'] = True
                if AUTO_START_CAMERA:
                    logger.info("🎥 Camera auto-start enabled")
            else:
                logger.error("❌ Camera Manager initialization failed")
                init_results['core_modules']['camera_manager'] = False
                init_results['errors'].append("Camera Manager initialization failed")
        else:
            logger.error("❌ Camera Manager service not available")
            init_results['core_modules']['camera_manager'] = False
            init_results['errors'].append("Camera Manager service not available")
    except Exception as e:
        logger.error(f"❌ Camera Manager error: {e}")
        init_results['core_modules']['camera_manager'] = False
        init_results['errors'].append(f"Camera Manager: {e}")
    
    # Detection Manager
    try:
        detection_manager = get_service('detection_manager')
        if detection_manager:
            success = detection_manager.initialize()
            if success:
                logger.info("✅ Detection Manager initialized successfully")
                init_results['core_modules']['detection_manager'] = True
                if AUTO_START_DETECTION:
                    logger.info("🔍 Detection auto-start enabled")
            else:
                logger.warning("⚠️ Detection Manager initialization failed")
                init_results['core_modules']['detection_manager'] = False
        else:
            logger.warning("⚠️ Detection Manager service not available")
            init_results['core_modules']['detection_manager'] = False
    except Exception as e:
        logger.warning(f"⚠️ Detection Manager error: {e}")
        init_results['core_modules']['detection_manager'] = False
    
    # Health Service
    try:
        health_service = get_service('health_service')
        if health_service:
            success = health_service.initialize()
            if success:
                logger.info("✅ Health Service initialized successfully")
                init_results['core_modules']['health_service'] = True
                if AUTO_START_HEALTH_MONITOR:
                    logger.info("🏥 Health Monitor auto-start enabled")
            else:
                logger.error("❌ Health Service initialization failed")
                init_results['core_modules']['health_service'] = False
                init_results['errors'].append("Health Service initialization failed")
        else:
            logger.error("❌ Health Service not available")
            init_results['core_modules']['health_service'] = False
            init_results['errors'].append("Health Service not available")
    except Exception as e:
        logger.error(f"❌ Health Service error: {e}")
        init_results['core_modules']['health_service'] = False
        init_results['errors'].append(f"Health Service: {e}")
    
    # Video Streaming
    try:
        video_streaming = get_service('video_streaming')
        if video_streaming:
            logger.info("✅ Video Streaming available")
            init_results['core_modules']['video_streaming'] = True
        else:
            logger.warning("⚠️ Video Streaming not available")
            init_results['core_modules']['video_streaming'] = False
    except Exception as e:
        logger.warning(f"⚠️ Video Streaming error: {e}")
        init_results['core_modules']['video_streaming'] = False
    
    # === PHASE 4: Optional Components ===
    logger.info("🔌 Phase 4: Optional Components")
    
    # Storage Monitor (Optional)
    try:
        storage_monitor = get_service('storage_monitor')
        if storage_monitor:
            logger.info("✅ Storage Monitor available")
            init_results['optional_modules']['storage_monitor'] = True
        else:
            logger.info("ℹ️ Storage Monitor not available (optional)")
            init_results['optional_modules']['storage_monitor'] = False
    except Exception as e:
        logger.info(f"ℹ️ Storage Monitor error (optional): {e}")
        init_results['optional_modules']['storage_monitor'] = False
    
    # === PHASE 5: Optional Services ===
    logger.info("🔌 Phase 5: Optional Services")
    
    # WebSocket Sender (Optional)
    try:
        websocket_sender = get_service('websocket_sender')
        if websocket_sender:
            success = websocket_sender.initialize()
            if success:
                logger.info("✅ WebSocket Sender initialized successfully")
                init_results['optional_modules']['websocket_sender'] = True
                if AUTO_START_WEBSOCKET_SENDER:
                    logger.info("📤 WebSocket Sender auto-start enabled")
                    import time
                    time.sleep(WEBSOCKET_SENDER_STARTUP_DELAY)
                    if websocket_sender.start():
                        logger.info("✅ WebSocket Sender started successfully")
                    else:
                        logger.warning("⚠️ WebSocket Sender failed to start")
            else:
                logger.warning("⚠️ WebSocket Sender initialization failed")
                init_results['optional_modules']['websocket_sender'] = False
        else:
            logger.info("ℹ️ WebSocket Sender not available (optional)")
            init_results['optional_modules']['websocket_sender'] = False
    except Exception as e:
        logger.info(f"ℹ️ WebSocket Sender error (optional): {e}")
        init_results['optional_modules']['websocket_sender'] = False
    
    # Storage Service (Optional)
    try:
        storage_service = get_service('storage_service')
        if storage_service:
            success = storage_service.initialize()
            if success:
                logger.info("✅ Storage Service initialized successfully")
                init_results['optional_modules']['storage_service'] = True
                if AUTO_START_STORAGE_MONITOR:
                    logger.info("💾 Storage Monitor auto-start enabled")
                    import time
                    time.sleep(STORAGE_MONITOR_STARTUP_DELAY)
                    if storage_service.start_storage_monitoring(interval=STORAGE_MONITOR_INTERVAL):
                        logger.info("✅ Storage monitoring started successfully")
                    else:
                        logger.warning("⚠️ Storage monitoring failed to start")
            else:
                logger.warning("⚠️ Storage Service initialization failed")
                init_results['optional_modules']['storage_service'] = False
        else:
            logger.info("ℹ️ Storage Service not available (optional)")
            init_results['optional_modules']['storage_service'] = False
    except Exception as e:
        logger.info(f"ℹ️ Storage Service error (optional): {e}")
        init_results['optional_modules']['storage_service'] = False
    
    # === SUMMARY ===
    logger.info("📊 Initialization Summary:")
    
    # Core modules status
    core_success = sum(init_results['core_modules'].values())
    core_total = len(init_results['core_modules'])
    logger.info(f"   Core Modules: {core_success}/{core_total} successful")
    
    for module, status in init_results['core_modules'].items():
        status_icon = "✅" if status else "❌"
        logger.info(f"     {status_icon} {module}")
    
    # Optional modules status
    optional_success = sum(init_results['optional_modules'].values())
    optional_total = len(init_results['optional_modules'])
    logger.info(f"   Optional Modules: {optional_success}/{optional_total} successful")
    
    for module, status in init_results['optional_modules'].items():
        status_icon = "✅" if status else "ℹ️"
        logger.info(f"     {status_icon} {module}")
    
    # Error summary
    if init_results['errors']:
        logger.warning(f"   Errors: {len(init_results['errors'])} errors occurred")
        for error in init_results['errors']:
            logger.warning(f"     ❌ {error}")
    
    # Determine if system is functional
    critical_modules = ['camera_handler', 'camera_manager', 'database_manager', 'health_monitor', 'health_service']
    critical_success = all(init_results['core_modules'].get(module, False) for module in critical_modules)
    
    if critical_success:
        logger.info("🎉 System initialization completed successfully!")
        logger.info("   Core functionality is available")
        if optional_success > 0:
            logger.info(f"   {optional_success} optional modules are also available")
        return True
    else:
        logger.error("❌ System initialization failed!")
        logger.error("   Critical modules are missing or failed")
        return False


def create_app():
    """Create and configure Flask application using absolute imports."""
    # Setup logging
    logger = setup_logging(level="INFO")
    logger.info("Creating Flask application...")
    
    # Validate imports
    import_errors = validate_imports()
    if import_errors:
        logger.warning("Some imports failed:")
        for error in import_errors:
            logger.warning(f"  {error}")
    
    # Set template and static folders
    current_dir = Path(__file__).parent
    template_dir = current_dir / 'web' / 'templates'
    static_dir = current_dir / 'web' / 'static'

    # Create Flask app
    app = Flask(__name__, 
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    
    # Load configuration using absolute import
    app.config.from_object('v1_3.src.core.config')
    
    # Initialize dependency container
    container = get_container()
    logger.info("Dependency container initialized")
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register blueprints using existing structure
    register_blueprints(app, socketio)
    
    # Initialize services with auto-startup sequence
    try:
        _initialize_services(logger)
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
    
    @app.route('/api/health')
    def api_health():
        """API Health check endpoint."""
        try:
            camera_manager = get_service('camera_manager')
            detection_manager = get_service('detection_manager')
            
            camera_health = camera_manager.health_check() if camera_manager else {}
            detection_health = detection_manager.get_status() if detection_manager else {}
            
            return jsonify({
                'success': True,
                'status': 'healthy',
                'camera': camera_health,
                'detection': detection_health,
                'errors': [],
                'database_errors': [],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'error': str(e),
                'errors': [str(e)],
                'database_errors': [],
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    logger.info("Flask application created successfully")
    return app, socketio


def main():
    """Main application entry point."""
    app, socketio = create_app()
    
    # Run the application
    host = app.config.get('FLASK_HOST', '0.0.0.0')
    port = app.config.get('FLASK_PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    logger = get_logger(__name__)
    logger.info(f"Starting AI Camera application on {host}:{port}")
    
    try:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        # Cleanup
        try:
            camera_manager = get_service('camera_manager')
            if camera_manager:
                camera_manager.cleanup()
                logger.info("Camera manager cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


if __name__ == '__main__':
    main()