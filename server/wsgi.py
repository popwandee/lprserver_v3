#!/usr/bin/env python3
"""
WSGI entry point for production deployment

This module serves as the WSGI entry point for the LPR Server application.
It sets up the Flask application with proper configuration and imports.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup absolute imports
try:
    from src.core.import_helper import setup_absolute_imports, validate_imports
    setup_absolute_imports()
    
    # Validate imports before creating app
    failed_imports = validate_imports()
    if failed_imports:
        logging.error(f"Failed to import required modules: {failed_imports}")
        sys.exit(1)
except ImportError:
    # Fallback if core module is not available
    logging.warning("Core import helper not available, using basic imports")

from src.app import create_app

# Create Flask app for WSGI
app = create_app()

# Import WebSocket service to register handlers
from src.services.websocket_service import websocket_service

# Setup periodic health checks
def setup_health_monitoring():
    """Setup periodic health monitoring."""
    try:
        from src.core.dependency_container import get_service
        from apscheduler.schedulers.background import BackgroundScheduler
        
        health_service = get_service('health_service')
        scheduler = BackgroundScheduler()
        
        # Schedule health check every 5 minutes
        scheduler.add_job(
            func=health_service.perform_health_check,
            trigger="interval",
            minutes=5,
            id="health_check_job"
        )
        
        scheduler.start()
        app.logger.info("Health monitoring scheduler started")
        
    except Exception as e:
        app.logger.error(f"Failed to setup health monitoring: {str(e)}")

# Setup health monitoring if not in debug mode
if not app.debug:
    setup_health_monitoring()

if __name__ == '__main__':
    app.run()
