#!/usr/bin/env python3
"""
Streaming Blueprint for AI Camera v1.3

This blueprint handles video streaming functionality using absolute imports
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
streaming_bp = Blueprint('streaming', __name__, url_prefix='/streaming')
logger = get_logger(__name__)


@streaming_bp.route('/')
def streaming_dashboard():
    """Render streaming dashboard."""
    return render_template('streaming/dashboard.html')


@streaming_bp.route('/status')
def get_streaming_status():
    """Get streaming service status."""
    try:
        video_streaming = get_service('video_streaming')
        if not video_streaming:
            return jsonify({'error': 'Video streaming service not available'}), 500
        
        status = video_streaming.get_status()
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting streaming status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@streaming_bp.route('/start', methods=['POST'])
def start_streaming():
    """Start video streaming."""
    try:
        video_streaming = get_service('video_streaming')
        if not video_streaming:
            return jsonify({'error': 'Video streaming service not available'}), 500
        
        success = video_streaming.start_streaming()
        return jsonify({
            'success': success,
            'message': 'Streaming started successfully' if success else 'Failed to start streaming',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error starting streaming: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@streaming_bp.route('/stop', methods=['POST'])
def stop_streaming():
    """Stop video streaming."""
    try:
        video_streaming = get_service('video_streaming')
        if not video_streaming:
            return jsonify({'error': 'Video streaming service not available'}), 500
        
        success = video_streaming.stop_streaming()
        return jsonify({
            'success': success,
            'message': 'Streaming stopped successfully' if success else 'Failed to stop streaming',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error stopping streaming: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def register_streaming_events(socketio):
    """Register WebSocket events for streaming functionality."""
    
    @socketio.on('streaming_status_request')
    def handle_streaming_status_request():
        """Handle streaming status request from client."""
        try:
            video_streaming = get_service('video_streaming')
            if video_streaming:
                status = video_streaming.get_status()
                emit('streaming_status_update', status)
            else:
                emit('streaming_status_update', {
                    'error': 'Video streaming service not available'
                })
        except Exception as e:
            logger.error(f"Error handling streaming status request: {e}")
            emit('streaming_status_update', {
                'error': str(e)
            })
    
    @socketio.on('streaming_control')
    def handle_streaming_control(data):
        """Handle streaming control commands."""
        try:
            command = data.get('command')
            video_streaming = get_service('video_streaming')
            
            if not video_streaming:
                emit('streaming_control_response', {
                    'success': False,
                    'error': 'Video streaming service not available'
                })
                return
            
            if command == 'start':
                success = video_streaming.start_streaming()
                message = 'Streaming started successfully' if success else 'Failed to start streaming'
            elif command == 'stop':
                success = video_streaming.stop_streaming()
                message = 'Streaming stopped successfully' if success else 'Failed to stop streaming'
            else:
                emit('streaming_control_response', {
                    'success': False,
                    'error': f'Unknown command: {command}'
                })
                return
            
            emit('streaming_control_response', {
                'success': success,
                'message': message
            })
        except Exception as e:
            logger.error(f"Error handling streaming control: {e}")
            emit('streaming_control_response', {
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('join_streaming_room')
    def handle_join_streaming_room():
        """Join streaming room for real-time updates."""
        join_room('streaming')
        emit('streaming_room_joined', {
            'success': True,
            'message': 'Joined streaming room'
        })
    
    @socketio.on('leave_streaming_room')
    def handle_leave_streaming_room():
        """Leave streaming room."""
        leave_room('streaming')
        emit('streaming_room_left', {
            'success': True,
            'message': 'Left streaming room'
        })
