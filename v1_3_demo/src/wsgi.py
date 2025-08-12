#!/usr/bin/env python3
"""
WSGI Entry Point for AI Camera v1.3

This is the WSGI entry point for the v1.3 application.
It can be used with Gunicorn or other WSGI servers.
"""

import os
import sys

# Add project root to path first
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import import helper first to setup paths
from v1_3.src.core.utils.import_helper import setup_import_paths, validate_imports
setup_import_paths()

from v1_3.src.core.utils.logging_config import setup_logging, get_logger

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging first
logger = setup_logging(level="INFO")

# Import the application
from v1_3.src.app import create_app
app, socketio = create_app()

# Validate imports
import_errors = validate_imports()
if import_errors:
    logger.warning("Some imports failed:")
    for error in import_errors:
        logger.warning(f"  {error}")

def application(environ, start_response):
    """
    WSGI application entry point
    
    This function is called by the WSGI server (e.g., Gunicorn)
    """
    return app(environ, start_response)

if __name__ == '__main__':
    # For direct execution
    logger.info("Starting AI Camera v1.3 WSGI")
    
    try:
        # Run with Flask development server
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
