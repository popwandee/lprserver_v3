#!/usr/bin/env python3
"""
WebSocket Blueprint for AI Camera v1.3

This blueprint handles general WebSocket communication functionality using absolute imports
and dependency injection pattern.

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

from flask import Blueprint, render_template, jsonify, request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime

# Use absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# Create blueprint
websocket_bp = Blueprint('websocket', __name__, url_prefix='/websocket')
logger = get_logger(__name__)


@websocket_bp.route('/')
def websocket_dashboard():
    """Render WebSocket dashboard."""
    return render_template('websocket/dashboard.html')


@websocket_bp.route('/status')
def get_websocket_status():
    """Get WebSocket connection status."""
    try:
        # Get status from various services
        camera_manager = get_service('camera_manager')
        detection_manager = get_service('detection_manager')
        health_service = get_service('health_service')
        websocket_sender = get_service('websocket_sender')
        
        status = {
            'camera': camera_manager.get_status() if camera_manager else None,
            'detection': detection_manager.get_status() if detection_manager else None,
            'health': health_service.get_system_health() if health_service else None,
            'websocket_sender': websocket_sender.get_status() if websocket_sender else None
        }
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def register_websocket_events(socketio):
    """Register WebSocket events for general WebSocket functionality."""
    
    @socketio.on('websocket_status_request')
    def handle_websocket_status_request():
        """Handle WebSocket status request from client."""
        try:
            # Get status from various services
            camera_manager = get_service('camera_manager')
            detection_manager = get_service('detection_manager')
            health_service = get_service('health_service')
            websocket_sender = get_service('websocket_sender')
            
            status = {
                'camera': camera_manager.get_status() if camera_manager else None,
                'detection': detection_manager.get_status() if detection_manager else None,
                'health': health_service.get_system_health() if health_service else None,
                'websocket_sender': websocket_sender.get_status() if websocket_sender else None
            }
            
            emit('websocket_status_update', status)
        except Exception as e:
            logger.error(f"Error handling WebSocket status request: {e}")
            emit('websocket_status_update', {
                'error': str(e)
            })
    
    @socketio.on('system_status_request')
    def handle_system_status_request():
        """Handle system-wide status request."""
        try:
            # Get comprehensive system status
            camera_manager = get_service('camera_manager')
            detection_manager = get_service('detection_manager')
            health_service = get_service('health_service')
            websocket_sender = get_service('websocket_sender')
            
            system_status = {
                'camera': {
                    'status': camera_manager.get_status() if camera_manager else None,
                    'component': 'Camera Manager'
                },
                'detection': {
                    'status': detection_manager.get_status() if detection_manager else None,
                    'component': 'Detection Manager'
                },
                'health': {
                    'status': health_service.get_system_health() if health_service else None,
                    'component': 'Health Service'
                },
                'websocket_sender': {
                    'status': websocket_sender.get_status() if websocket_sender else None,
                    'component': 'WebSocket Sender'
                }
            }
            
            emit('system_status_update', system_status)
        except Exception as e:
            logger.error(f"Error handling system status request: {e}")
            emit('system_status_update', {
                'error': str(e)
            })
    
    @socketio.on('join_system_room')
    def handle_join_system_room():
        """Join system room for real-time updates."""
        join_room('system')
        emit('system_room_joined', {
            'success': True,
            'message': 'Joined system room'
        })
    
    @socketio.on('leave_system_room')
    def handle_leave_system_room():
        """Leave system room."""
        leave_room('system')
        emit('system_room_left', {
            'success': True,
            'message': 'Left system room'
        })
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('connection_response', {
            'success': True,
            'message': 'Connected to AI Camera v1.3 WebSocket',
            'timestamp': datetime.now().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping request."""
        emit('pong', {
            'timestamp': datetime.now().isoformat()
        })
