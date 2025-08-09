#!/usr/bin/env python3
"""
Main Blueprint for AI Camera v1.3

This blueprint handles the main dashboard and system overview.
"""

from flask import Blueprint, render_template, current_app
from flask_socketio import emit
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

main_bp = Blueprint('main', __name__)
logger = get_logger(__name__)


@main_bp.route('/')
def index():
    """Main dashboard page."""
    try:
        camera_manager = get_service('camera_manager')
        camera_status = camera_manager.get_status() if camera_manager else {}
        
        return render_template('index.html', 
                             camera_status=camera_status,
                             title="AI Camera Dashboard")
    except KeyError as e:
        logger.error(f"Service not Registered: {e}")
        return render_template('index.html', 
                             camera_status={'error': f'Camera service not available: {e}'},
                             title="AI Camera Dashboard")
    except Exception as e:
        logger.error(f"Error in main index: {e}")
        return render_template('index.html', 
                             camera_status={'error': str(e)},
                             title="AI Camera Dashboard")


def register_main_events(socketio):
    """Register WebSocket events for main functionality."""
    
    @socketio.on('main_status_request')
    def handle_main_status_request():
        """Handle main status request from client."""
        try:
            camera_manager = get_service('camera_manager')
            status = camera_manager.get_status() if camera_manager else {}
            
            emit('main_status_update', {
                'status': 'ok',
                'camera': status,
                'message': 'System status retrieved successfully'
            })
        except KeyError as e:
            logger.error(f"Service not registered: {e}")
            emit('main_status_update', {
                'status': 'error',
                'error': 'Camera service not available',
                'message': 'Failed to get system status'
            })
        except Exception as e:
            logger.error(f"Error handling main status request: {e}")
            emit('main_status_update', {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to get system status'
            })
