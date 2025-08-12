"""
AI Camera Manager Blueprint

This blueprint handles AI camera management including:
- Camera registration and configuration
- Camera status monitoring
- Camera settings management
- Camera health checks
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import logging

# Create blueprint
aicamera_bp = Blueprint('aicamera', __name__, url_prefix='/aicamera')

logger = logging.getLogger(__name__)

@aicamera_bp.route('/')
def index():
    """AI Camera Manager main page"""
    return render_template('aicamera/index.html')

@aicamera_bp.route('/cameras')
def cameras():
    """List all AI cameras"""
    try:
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        cameras = camera_service.get_all_cameras()
        return render_template('aicamera/cameras.html', cameras=cameras)
    except Exception as e:
        logger.error(f"Error loading cameras: {str(e)}")
        return render_template('aicamera/cameras.html', cameras=[], error=str(e))

@aicamera_bp.route('/cameras/<camera_id>')
def camera_detail(camera_id):
    """Camera detail page"""
    try:
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        camera = camera_service.get_camera_by_id(camera_id)
        if not camera:
            return render_template('error.html', message="Camera not found"), 404
        
        # Get camera statistics
        stats = camera_service.get_camera_statistics(camera_id)
        return render_template('aicamera/camera_detail.html', camera=camera, stats=stats)
    except Exception as e:
        logger.error(f"Error loading camera detail: {str(e)}")
        return render_template('error.html', message=str(e)), 500

@aicamera_bp.route('/cameras/<camera_id>/settings')
def camera_settings(camera_id):
    """Camera settings page"""
    try:
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        camera = camera_service.get_camera_by_id(camera_id)
        if not camera:
            return render_template('error.html', message="Camera not found"), 404
        
        return render_template('aicamera/camera_settings.html', camera=camera)
    except Exception as e:
        logger.error(f"Error loading camera settings: {str(e)}")
        return render_template('error.html', message=str(e)), 500

# API Endpoints
@aicamera_bp.route('/api/cameras', methods=['GET'])
def api_get_cameras():
    """Get all cameras API"""
    try:
        # Mock data for demonstration
        cameras = [
            {
                'camera_id': 'CAM001',
                'name': 'Main Entrance Camera',
                'location': 'Main Gate',
                'ip_address': '192.168.1.100',
                'port': 8765,
                'is_online': True,
                'last_detection': '2024-01-15 14:30:25',
                'total_detections': 1250,
                'settings': {
                    'resolution': '1920x1080',
                    'fps': 30,
                    'sensitivity': 0.8
                }
            },
            {
                'camera_id': 'CAM002',
                'name': 'Parking Lot Camera',
                'location': 'Parking Area A',
                'ip_address': '192.168.1.101',
                'port': 8765,
                'is_online': True,
                'last_detection': '2024-01-15 14:28:10',
                'total_detections': 890,
                'settings': {
                    'resolution': '1920x1080',
                    'fps': 25,
                    'sensitivity': 0.7
                }
            },
            {
                'camera_id': 'CAM003',
                'name': 'Exit Camera',
                'location': 'Exit Gate',
                'ip_address': '192.168.1.102',
                'port': 8765,
                'is_online': False,
                'last_detection': '2024-01-15 12:15:30',
                'total_detections': 567,
                'settings': {
                    'resolution': '1920x1080',
                    'fps': 30,
                    'sensitivity': 0.9
                }
            }
        ]
        
        return jsonify({
            'success': True,
            'cameras': cameras
        })
    except Exception as e:
        logger.error(f"API Error getting cameras: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/api/cameras', methods=['POST'])
def api_create_camera():
    """Create new camera API"""
    try:
        data = request.get_json()
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        
        camera = camera_service.create_camera(
            camera_id=data.get('camera_id'),
            name=data.get('name'),
            location=data.get('location'),
            ip_address=data.get('ip_address'),
            port=data.get('port', 8765),
            settings=data.get('settings', {})
        )
        
        return jsonify({
            'success': True,
            'camera': camera
        })
    except Exception as e:
        logger.error(f"API Error creating camera: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/api/cameras/<camera_id>', methods=['GET'])
def api_get_camera(camera_id):
    """Get camera by ID API"""
    try:
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        camera = camera_service.get_camera_by_id(camera_id)
        
        if not camera:
            return jsonify({
                'success': False,
                'error': 'Camera not found'
            }), 404
        
        return jsonify({
            'success': True,
            'camera': camera
        })
    except Exception as e:
        logger.error(f"API Error getting camera: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/api/cameras/<camera_id>', methods=['PUT'])
def api_update_camera(camera_id):
    """Update camera API"""
    try:
        data = request.get_json()
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        
        camera = camera_service.update_camera(camera_id, data)
        
        return jsonify({
            'success': True,
            'camera': camera
        })
    except Exception as e:
        logger.error(f"API Error updating camera: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/api/cameras/<camera_id>', methods=['DELETE'])
def api_delete_camera(camera_id):
    """Delete camera API"""
    try:
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        camera_service.delete_camera(camera_id)
        
        return jsonify({
            'success': True,
            'message': 'Camera deleted successfully'
        })
    except Exception as e:
        logger.error(f"API Error deleting camera: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/api/cameras/statistics', methods=['GET'])
def api_get_camera_statistics():
    """Get camera statistics API"""
    try:
        # Mock statistics data
        stats = {
            'total_cameras': 3,
            'online_cameras': 2,
            'offline_cameras': 1,
            'total_detections': 2707,
            'today_detections': 45,
            'avg_confidence': 0.87,
            'detection_rate': 0.92
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"API Error getting camera statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/api/cameras/status', methods=['GET'])
def api_get_camera_status():
    """Get camera status API"""
    try:
        # Mock status data
        cameras = [
            {
                'camera_id': 'CAM001',
                'is_online': True,
                'ip_address': '192.168.1.100',
                'last_detection': '2024-01-15 14:30:25',
                'status': 'online'
            },
            {
                'camera_id': 'CAM002',
                'is_online': True,
                'ip_address': '192.168.1.101',
                'last_detection': '2024-01-15 14:28:10',
                'status': 'online'
            },
            {
                'camera_id': 'CAM003',
                'is_online': False,
                'ip_address': '192.168.1.102',
                'last_detection': '2024-01-15 12:15:30',
                'status': 'offline'
            }
        ]
        
        return jsonify({
            'success': True,
            'cameras': cameras
        })
    except Exception as e:
        logger.error(f"API Error getting camera status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/api/cameras/<camera_id>/test-connection')
def api_test_camera_connection(camera_id):
    """Test camera connection API"""
    try:
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        result = camera_service.test_connection(camera_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"API Error testing camera connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@aicamera_bp.route('/socket/camera-register', methods=['POST'])
def socket_camera_register():
    """Handle camera registration via WebSocket"""
    try:
        data = request.get_json()
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        
        camera = camera_service.register_camera(
            camera_id=data.get('camera_id'),
            ip_address=request.remote_addr,
            port=data.get('port', 8765)
        )
        
        # Join camera room for real-time updates
        join_room(f"camera_{camera['camera_id']}")
        
        return jsonify({
            'success': True,
            'camera': camera
        })
    except Exception as e:
        logger.error(f"Socket Error registering camera: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@aicamera_bp.route('/socket/camera-heartbeat', methods=['POST'])
def socket_camera_heartbeat():
    """Handle camera heartbeat via WebSocket"""
    try:
        data = request.get_json()
        from src.services.camera_service import get_camera_service
        camera_service = get_camera_service()
        
        camera_service.update_heartbeat(
            camera_id=data.get('camera_id'),
            status=data.get('status', 'online')
        )
        
        # Emit status update to dashboard
        emit('camera_status_update', {
            'camera_id': data.get('camera_id'),
            'status': data.get('status', 'online'),
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
        
        return jsonify({
            'success': True,
            'message': 'Heartbeat received'
        })
    except Exception as e:
        logger.error(f"Socket Error processing heartbeat: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
