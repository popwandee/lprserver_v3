#!/usr/bin/env python3
"""
Health Blueprint for AI Camera v1.3

This blueprint provides health monitoring endpoints and WebSocket events
for system health status and monitoring.

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

from flask import Blueprint, render_template, jsonify, request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from typing import Dict, Any

from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.core.dependency_container import get_service

health_bp = Blueprint('health', __name__, url_prefix='/health')
logger = get_logger(__name__)


@health_bp.route('/')
def health_dashboard():
    """Render health monitoring dashboard."""
    try:
        return render_template('health/dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering health dashboard: {e}")
        return "Health dashboard not available", 500


@health_bp.route('')
def health_redirect():
    """Redirect /health to /health/ for dashboard."""
    from flask import redirect, url_for
    return redirect(url_for('health.health_dashboard'))


@health_bp.route('/system')
def get_system_health():
    """
    Get comprehensive system health status.
    
    Returns:
        JSON response with system health information
    """
    try:
        health_service = get_service('health_service')
        if not health_service:
            return jsonify({
                'success': False,
                'error': 'Health service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get system health status
        health_data = health_service.get_system_health()
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@health_bp.route('/logs')
def get_health_logs():
    """
    Get health check logs with pagination.
    
    Query Parameters:
        level (optional): Log level filter (PASS, FAIL, WARNING)
        page (optional): Page number (default: 1)
        limit (optional): Number of log entries per page (default: 50, max: 100)
    
    Returns:
        JSON response with health logs and pagination info
    """
    try:
        health_service = get_service('health_service')
        if not health_service:
            return jsonify({
                'success': False,
                'error': 'Health service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get query parameters
        level = request.args.get('level')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # Validate parameters
        if limit > 100:
            limit = 100
        elif limit < 1:
            limit = 50
        
        if page < 1:
            page = 1
        
        # Get health logs with pagination
        logs_data = health_service.get_health_logs(level=level, limit=limit, page=page)
        
        return jsonify(logs_data)
        
    except Exception as e:
        logger.error(f"Error getting health logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@health_bp.route('/status')
def get_health_status():
    """
    Get health service status.
    
    Returns:
        JSON response with health service status
    """
    try:
        health_service = get_service('health_service')
        if not health_service:
            return jsonify({
                'success': False,
                'error': 'Health service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        status = health_service.get_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@health_bp.route('/monitor/start', methods=['POST'])
def start_monitoring():
    """
    Start continuous health monitoring.
    
    Returns:
        JSON response with operation result
    """
    try:
        health_service = get_service('health_service')
        if not health_service:
            return jsonify({
                'success': False,
                'error': 'Health service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get interval from request
        data = request.get_json() or {}
        interval = data.get('interval')
        
        # Start monitoring
        success = health_service.start_monitoring(interval=interval)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Health monitoring started successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start health monitoring',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"Error starting health monitoring: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@health_bp.route('/monitor/stop', methods=['POST'])
def stop_monitoring():
    """
    Stop continuous health monitoring.
    
    Returns:
        JSON response with operation result
    """
    try:
        health_service = get_service('health_service')
        if not health_service:
            return jsonify({
                'success': False,
                'error': 'Health service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Stop monitoring
        health_service.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Health monitoring stopped successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error stopping health monitoring: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@health_bp.route('/check/run', methods=['POST'])
def run_health_check():
    """
    Run a single health check.
    
    Returns:
        JSON response with health check results
    """
    try:
        health_service = get_service('health_service')
        if not health_service:
            return jsonify({
                'success': False,
                'error': 'Health service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Run health check
        health_data = health_service.get_system_health()
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error(f"Error running health check: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def register_health_events(socketio):
    """Register WebSocket events for health functionality."""
    
    @socketio.on('health_status_request')
    def handle_health_status_request():
        """Handle health status request from client."""
        try:
            health_service = get_service('health_service')
            if not health_service:
                emit('health_status_update', {
                    'success': False,
                    'error': 'Health service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Get system health
            health_data = health_service.get_system_health()
            emit('health_status_update', health_data)
            
        except Exception as e:
            logger.error(f"Error handling health status request: {e}")
            emit('health_status_update', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('health_logs_request')
    def handle_health_logs_request(data):
        """Handle health logs request from client."""
        try:
            health_service = get_service('health_service')
            if not health_service:
                emit('health_logs_update', {
                    'success': False,
                    'error': 'Health service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Get parameters from data
            level = data.get('level')
            page = data.get('page', 1)
            limit = data.get('limit', 50)
            
            # Get health logs with pagination
            logs_data = health_service.get_health_logs(level=level, limit=limit, page=page)
            emit('health_logs_update', logs_data)
            
        except Exception as e:
            logger.error(f"Error handling health logs request: {e}")
            emit('health_logs_update', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('health_monitor_start')
    def handle_health_monitor_start(data):
        """Handle health monitoring start request."""
        try:
            health_service = get_service('health_service')
            if not health_service:
                emit('health_monitor_response', {
                    'success': False,
                    'error': 'Health service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Get interval from data
            interval = data.get('interval')
            
            # Start monitoring
            success = health_service.start_monitoring(interval=interval)
            
            emit('health_monitor_response', {
                'success': success,
                'message': 'Health monitoring started successfully' if success else 'Failed to start monitoring',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error starting health monitoring: {e}")
            emit('health_monitor_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('health_monitor_stop')
    def handle_health_monitor_stop():
        """Handle health monitoring stop request."""
        try:
            health_service = get_service('health_service')
            if not health_service:
                emit('health_monitor_response', {
                    'success': False,
                    'error': 'Health service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Stop monitoring
            health_service.stop_monitoring()
            
            emit('health_monitor_response', {
                'success': True,
                'message': 'Health monitoring stopped successfully',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error stopping health monitoring: {e}")
            emit('health_monitor_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('health_check_run')
    def handle_health_check_run():
        """Handle manual health check request."""
        try:
            health_service = get_service('health_service')
            if not health_service:
                emit('health_check_response', {
                    'success': False,
                    'error': 'Health service not available',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Run health check
            health_data = health_service.get_system_health()
            emit('health_check_response', health_data)
            
        except Exception as e:
            logger.error(f"Error running health check: {e}")
            emit('health_check_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('join_health_room')
    def handle_join_health_room():
        """Handle client joining health monitoring room."""
        try:
            join_room('health_monitoring')
            emit('health_room_joined', {
                'success': True,
                'message': 'Joined health monitoring room',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error joining health room: {e}")
            emit('health_room_joined', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('leave_health_room')
    def handle_leave_health_room():
        """Handle client leaving health monitoring room."""
        try:
            leave_room('health_monitoring')
            emit('health_room_left', {
                'success': True,
                'message': 'Left health monitoring room',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error leaving health room: {e}")
            emit('health_room_left', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
