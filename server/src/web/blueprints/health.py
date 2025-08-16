"""
Health Monitoring Blueprint

This blueprint provides endpoints for system health monitoring and status checks.
"""

from flask import Blueprint, jsonify, request
from flask_socketio import emit, join_room, leave_room
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.dependency_container import get_service
from constants import HEALTH_STATUS_PASS, HEALTH_STATUS_FAIL, HEALTH_STATUS_WARNING

health_bp = Blueprint('health', __name__)

@health_bp.route('/status', methods=['GET'])
def health_status():
    """
    Get current system health status.
    
    Returns:
        JSON response with health status
    """
    try:
        health_service = get_service('health_service')
        status = health_service.get_current_status()
        
        if not status:
            # Perform health check if no current status
            status = health_service.perform_health_check()
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'status': HEALTH_STATUS_FAIL,
            'message': f'Health check failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/check', methods=['POST'])
def perform_health_check():
    """
    Perform a new health check.
    
    Returns:
        JSON response with health check results
    """
    try:
        health_service = get_service('health_service')
        results = health_service.perform_health_check()
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/history', methods=['GET'])
def health_history():
    """
    Get health check history.
    
    Query Parameters:
        hours: Number of hours to look back (default: 24)
        
    Returns:
        JSON response with health history
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        health_service = get_service('health_service')
        history = health_service.get_health_history(hours)
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/database/stats', methods=['GET'])
def database_stats():
    """
    Get database statistics.
    
    Returns:
        JSON response with database statistics
    """
    try:
        database_service = get_service('database_service')
        stats = database_service.get_database_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/database/cleanup', methods=['POST'])
def cleanup_database():
    """
    Clean up old database records.
    
    JSON Body:
        days: Number of days to keep data (default: 30)
        
    Returns:
        JSON response with cleanup results
    """
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        
        database_service = get_service('database_service')
        results = database_service.cleanup_old_data(days)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@health_bp.route('/database/optimize', methods=['POST'])
def optimize_database():
    """
    Optimize database performance.
    
    Returns:
        JSON response with optimization results
    """
    try:
        database_service = get_service('database_service')
        success = database_service.optimize_database()
        
        return jsonify({
            'success': success,
            'message': 'Database optimization completed' if success else 'Database optimization failed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket events for real-time health monitoring
# Note: These events should be registered in the main WebSocket service
# to avoid circular imports and ensure proper SocketIO initialization
