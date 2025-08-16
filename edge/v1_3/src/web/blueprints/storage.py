#!/usr/bin/env python3
"""
Storage Blueprint for AI Camera v1.3

This blueprint provides web interface for storage management including
disk space monitoring, file cleanup, and storage analytics.
"""

from flask import Blueprint, render_template, jsonify, request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime

from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# Create blueprint
storage_bp = Blueprint('storage', __name__, url_prefix='/storage')

logger = get_logger(__name__)

@storage_bp.route('/')
def storage_dashboard():
    """Render storage management dashboard."""
    return render_template('storage/dashboard.html', 
                         active_page='storage',
                         title='Storage Management')

@storage_bp.route('/status')
def get_storage_status():
    """Get comprehensive storage status."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        status_data = storage_service.get_storage_status()
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Error getting storage status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_bp.route('/analytics')
def get_storage_analytics():
    """Get storage analytics."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        days = request.args.get('days', 7, type=int)
        analytics_data = storage_service.get_storage_analytics(days)
        return jsonify(analytics_data)
        
    except Exception as e:
        logger.error(f"Error getting storage analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_bp.route('/alerts')
def get_storage_alerts():
    """Get storage alerts."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        alerts_data = storage_service.get_storage_alerts()
        return jsonify(alerts_data)
        
    except Exception as e:
        logger.error(f"Error getting storage alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_bp.route('/cleanup', methods=['POST'])
def perform_cleanup():
    """Perform manual cleanup of old files."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        cleanup_result = storage_service.perform_manual_cleanup()
        return jsonify(cleanup_result)
        
    except Exception as e:
        logger.error(f"Error performing cleanup: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_bp.route('/config', methods=['GET', 'POST'])
def manage_configuration():
    """Get or update storage configuration."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        if request.method == 'GET':
            # Get current configuration
            status_data = storage_service.get_storage_status()
            if status_data.get('success'):
                config = status_data['data'].get('configuration', {})
                return jsonify({
                    'success': True,
                    'data': config,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify(status_data), 500
        
        elif request.method == 'POST':
            # Update configuration
            config_data = request.get_json()
            if not config_data:
                return jsonify({
                    'success': False,
                    'error': 'No configuration data provided',
                    'timestamp': datetime.now().isoformat()
                }), 400
            
            update_result = storage_service.update_storage_configuration(config_data)
            return jsonify(update_result)
        
    except Exception as e:
        logger.error(f"Error managing configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_bp.route('/monitor/start', methods=['POST'])
def start_monitoring():
    """Start continuous storage monitoring."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        data = request.get_json() or {}
        interval = data.get('interval')
        
        start_result = storage_service.start_storage_monitoring(interval)
        return jsonify(start_result)
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_bp.route('/monitor/stop', methods=['POST'])
def stop_monitoring():
    """Stop continuous storage monitoring."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        stop_result = storage_service.stop_storage_monitoring()
        return jsonify(stop_result)
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_bp.route('/alerts/clear', methods=['POST'])
def clear_alerts():
    """Clear all storage alerts."""
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            return jsonify({
                'success': False,
                'error': 'Storage service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        clear_result = storage_service.clear_storage_alerts()
        return jsonify(clear_result)
        
    except Exception as e:
        logger.error(f"Error clearing alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def register_storage_events(socketio):
    """Register WebSocket events for storage management."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info("Client connected to storage events")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info("Client disconnected from storage events")
    
    @socketio.on('storage_status_request')
    def handle_storage_status_request():
        """Handle storage status request via WebSocket."""
        logger.info("Received storage_status_request via WebSocket")
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                logger.error("Storage service not available for WebSocket request")
                emit('storage_status_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            logger.info("Getting storage status for WebSocket request")
            status_data = storage_service.get_storage_status()
            logger.info(f"Emitting storage_status_response: {status_data.get('success', False)}")
            emit('storage_status_response', status_data)
            
        except Exception as e:
            logger.error(f"Error handling storage status request: {e}")
            emit('storage_status_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('storage_analytics_request')
    def handle_storage_analytics_request(data):
        """Handle storage analytics request via WebSocket."""
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                emit('storage_analytics_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            days = data.get('days', 7)
            analytics_data = storage_service.get_storage_analytics(days)
            emit('storage_analytics_response', analytics_data)
            
        except Exception as e:
            logger.error(f"Error handling storage analytics request: {e}")
            emit('storage_analytics_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('storage_cleanup_request')
    def handle_storage_cleanup_request():
        """Handle storage cleanup request via WebSocket."""
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                emit('storage_cleanup_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            cleanup_result = storage_service.perform_manual_cleanup()
            emit('storage_cleanup_response', cleanup_result)
            
        except Exception as e:
            logger.error(f"Error handling storage cleanup request: {e}")
            emit('storage_cleanup_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('storage_config_update')
    def handle_storage_config_update(data):
        """Handle storage configuration update via WebSocket."""
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                emit('storage_config_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            config_data = data.get('config', {})
            if not config_data:
                emit('storage_config_response', {
                    'success': False,
                    'error': 'No configuration data provided',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            update_result = storage_service.update_storage_configuration(config_data)
            emit('storage_config_response', update_result)
            
        except Exception as e:
            logger.error(f"Error handling storage config update: {e}")
            emit('storage_config_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('storage_monitor_start')
    def handle_storage_monitor_start(data):
        """Handle storage monitoring start via WebSocket."""
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                emit('storage_monitor_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            interval = data.get('interval')
            start_result = storage_service.start_storage_monitoring(interval)
            emit('storage_monitor_response', start_result)
            
        except Exception as e:
            logger.error(f"Error handling storage monitor start: {e}")
            emit('storage_monitor_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('storage_monitor_stop')
    def handle_storage_monitor_stop():
        """Handle storage monitoring stop via WebSocket."""
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                emit('storage_monitor_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            stop_result = storage_service.stop_storage_monitoring()
            emit('storage_monitor_response', stop_result)
            
        except Exception as e:
            logger.error(f"Error handling storage monitor stop: {e}")
            emit('storage_monitor_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('storage_alerts_request')
    def handle_storage_alerts_request():
        """Handle storage alerts request via WebSocket."""
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                emit('storage_alerts_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            alerts_data = storage_service.get_storage_alerts()
            emit('storage_alerts_response', alerts_data)
            
        except Exception as e:
            logger.error(f"Error handling storage alerts request: {e}")
            emit('storage_alerts_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('storage_alerts_clear')
    def handle_storage_alerts_clear():
        """Handle storage alerts clear via WebSocket."""
        try:
            storage_service = get_service('storage_service')
            if not storage_service:
                emit('storage_alerts_response', {
                    'success': False,
                    'error': 'Storage service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            clear_result = storage_service.clear_storage_alerts()
            emit('storage_alerts_response', clear_result)
            
        except Exception as e:
            logger.error(f"Error handling storage alerts clear: {e}")
            emit('storage_alerts_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('join_storage_room')
    def handle_join_storage_room():
        """Join storage monitoring room."""
        join_room('storage_monitoring')
        emit('storage_room_joined', {
            'success': True,
            'message': 'Joined storage monitoring room',
            'timestamp': datetime.now().isoformat()
        })
    
    @socketio.on('leave_storage_room')
    def handle_leave_storage_room():
        """Leave storage monitoring room."""
        leave_room('storage_monitoring')
        emit('storage_room_left', {
            'success': True,
            'message': 'Left storage monitoring room',
            'timestamp': datetime.now().isoformat()
        })
