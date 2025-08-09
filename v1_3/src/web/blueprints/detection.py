#!/usr/bin/env python3
"""
Detection Blueprint for AI Camera v1.3

This blueprint provides detection control and monitoring functionality:
- Detection service control endpoints
- Detection status monitoring
- Detection results viewing
- WebSocket events for real-time detection updates
- Detection statistics and reporting

Author: AI Camera Team
Version: 1.3
Date: December 2024
"""

import json
import time
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, Response, current_app
from flask_socketio import emit, join_room, leave_room

# Use absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.components.camera_handler import make_json_serializable

# Create blueprint
detection_bp = Blueprint('detection', __name__, url_prefix='/detection')

logger = get_logger(__name__)


@detection_bp.route('/')
def detection_dashboard():
    """
    Detection dashboard page with service status and statistics.
    
    Returns:
        str: Rendered HTML template
    """
    try:
        detection_manager = get_service('detection_manager')
        detection_status = detection_manager.get_status() if detection_manager else {}
        
        return render_template('detection/dashboard.html',
                             detection_status=detection_status,
                             title="Detection Dashboard")
    except Exception as e:
        logger.error(f"Error in detection dashboard: {e}")
        return render_template('detection/dashboard.html',
                             detection_status={},
                             title="Detection Dashboard")


@detection_bp.route('/status')
def get_detection_status():
    """
    Get current detection status and statistics.
    
    Returns:
        dict: JSON response with detection status
    """
    try:
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            return jsonify({'error': 'Detection manager not available'}), 500
        
        status = detection_manager.get_status()
        
        # Ensure all status data is JSON serializable
        serializable_status = make_json_serializable(status)
        
        return jsonify({
            'success': True,
            'status': serializable_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting detection status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_bp.route('/start', methods=['POST'])
def start_detection():
    """
    Start the detection service.
    
    Returns:
        dict: JSON response with operation result
    """
    try:
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            return jsonify({
                'success': False,
                'error': 'Detection manager not available'
            }), 500
        
        # Start detection service
        success = detection_manager.start_detection()
        
        if success:
            logger.info("Detection service started via API")
            return jsonify({
                'success': True,
                'message': 'Detection service started successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start detection service'
            }), 500
            
    except Exception as e:
        logger.error(f"Error starting detection service: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_bp.route('/stop', methods=['POST'])
def stop_detection():
    """
    Stop the detection service.
    
    Returns:
        dict: JSON response with operation result
    """
    try:
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            return jsonify({
                'success': False,
                'error': 'Detection manager not available'
            }), 500
        
        # Stop detection service
        success = detection_manager.stop_detection()
        
        if success:
            logger.info("Detection service stopped via API")
            return jsonify({
                'success': True,
                'message': 'Detection service stopped successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to stop detection service'
            }), 500
            
    except Exception as e:
        logger.error(f"Error stopping detection service: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_bp.route('/process_frame', methods=['POST'])
def process_single_frame():
    """
    Process a single frame for detection (for testing purposes).
    
    Returns:
        dict: JSON response with detection results
    """
    try:
        detection_manager = get_service('detection_manager')
        camera_manager = get_service('camera_manager')
        
        if not detection_manager:
            return jsonify({
                'success': False,
                'error': 'Detection manager not available'
            }), 500
        
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available'
            }), 500
        
        # Process current frame from camera
        result = detection_manager.process_frame_from_camera(camera_manager)
        
        if result:
            return jsonify({
                'success': True,
                'detection_result': make_json_serializable(result),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No detection results or processing failed',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error processing single frame: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_bp.route('/statistics')
def get_detection_statistics():
    """
    Get detailed detection statistics.
    
    Returns:
        dict: JSON response with detection statistics
    """
    try:
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            return jsonify({'error': 'Detection manager not available'}), 500
        
        status = detection_manager.get_status()
        statistics = status.get('statistics', {})
        
        # Calculate additional metrics
        total_frames = statistics.get('total_frames_processed', 0)
        successful_detections = statistics.get('total_vehicles_detected', 0)
        
        detection_rate = 0.0
        if total_frames > 0:
            detection_rate = (successful_detections / total_frames) * 100
        
        enhanced_stats = {
            **statistics,
            'detection_rate_percent': round(detection_rate, 2),
            'avg_processing_time_ms': round(statistics.get('processing_time_avg', 0) * 1000, 2)
        }
        
        return jsonify({
            'success': True,
            'statistics': enhanced_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting detection statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_bp.route('/results/recent')
def get_recent_results():
    """
    Get recent detection results from database.
    
    Returns:
        dict: JSON response with recent detection results
    """
    try:
        database_manager = get_service('database_manager')
        if not database_manager:
            return jsonify({
                'success': False,
                'error': 'Database manager not available'
            }), 500
        
        # Get recent detection results (limit to last 50)
        recent_results = database_manager.get_recent_detections(limit=50)
        
        return jsonify({
            'success': True,
            'results': make_json_serializable(recent_results),
            'count': len(recent_results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting recent results: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_bp.route('/models/status')
def get_models_status():
    """
    Get status of loaded detection models.
    
    Returns:
        dict: JSON response with model status
    """
    try:
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            return jsonify({'error': 'Detection manager not available'}), 500
        
        status = detection_manager.get_status()
        processor_status = status.get('detection_processor_status', {})
        
        model_info = {
            'models_loaded': processor_status.get('models_loaded', False),
            'vehicle_model_available': processor_status.get('vehicle_model_available', False),
            'lp_detection_model_available': processor_status.get('lp_detection_model_available', False),
            'lp_ocr_model_available': processor_status.get('lp_ocr_model_available', False),
            'easyocr_available': processor_status.get('easyocr_available', False),
            'detection_resolution': processor_status.get('detection_resolution', [0, 0]),
            'confidence_thresholds': {
                'vehicle': processor_status.get('confidence_threshold', 0.0),
                'plate': processor_status.get('plate_confidence_threshold', 0.0)
            }
        }
        
        return jsonify({
            'success': True,
            'models': model_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_bp.route('/config', methods=['GET', 'POST'])
def detection_config():
    """
    Get or update detection configuration.
    
    Returns:
        dict: JSON response with configuration
    """
    try:
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            return jsonify({'error': 'Detection manager not available'}), 500
        
        if request.method == 'GET':
            # Get current configuration
            status = detection_manager.get_status()
            config = {
                'detection_interval': status.get('detection_interval', 0.1),
                'auto_start': status.get('auto_start', False),
                'processor_config': status.get('detection_processor_status', {})
            }
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        
        elif request.method == 'POST':
            # Update configuration
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No configuration data provided'
                }), 400
            
            # Update detection interval
            if 'detection_interval' in data:
                interval = float(data['detection_interval'])
                if 0.01 <= interval <= 10.0:  # Reasonable bounds
                    detection_manager.detection_interval = interval
                    logger.info(f"Detection interval updated to {interval}s")
            
            # Update auto-start setting
            if 'auto_start' in data:
                detection_manager.auto_start = bool(data['auto_start'])
                logger.info(f"Auto-start set to {detection_manager.auto_start}")
            
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in detection config: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# WebSocket Events for real-time detection updates
def register_detection_events(socketio):
    """
    Register WebSocket events for real-time detection updates.
    
    Args:
        socketio: SocketIO instance
    """
    
    @socketio.on('detection_status_request')
    def handle_detection_status_request():
        """Handle request for detection status."""
        try:
            detection_manager = get_service('detection_manager')
            if detection_manager:
                status = detection_manager.get_status()
                serializable_status = make_json_serializable(status)
                emit('detection_status_update', serializable_status)
            else:
                emit('detection_status_error', {'error': 'Detection manager not available'})
        except Exception as e:
            logger.error(f"Error in detection status WebSocket: {e}")
            emit('detection_status_error', {'error': str(e)})
    
    @socketio.on('detection_control')
    def handle_detection_control(data):
        """Handle detection control commands."""
        try:
            command = data.get('command')
            detection_manager = get_service('detection_manager')
            
            if not detection_manager:
                emit('detection_control_response', {
                    'command': command,
                    'success': False,
                    'error': 'Detection manager not available'
                })
                return
            
            success = False
            message = ''
            
            if command == 'start':
                success = detection_manager.start_detection()
                message = 'Detection started' if success else 'Failed to start detection'
            elif command == 'stop':
                success = detection_manager.stop_detection()
                message = 'Detection stopped' if success else 'Failed to stop detection'
            elif command == 'process_frame':
                camera_manager = get_service('camera_manager')
                result = detection_manager.process_frame_from_camera(camera_manager)
                success = result is not None
                message = 'Frame processed' if success else 'Frame processing failed'
            else:
                emit('detection_control_response', {
                    'command': command,
                    'success': False,
                    'error': 'Unknown command'
                })
                return
            
            emit('detection_control_response', {
                'command': command,
                'success': success,
                'message': message
            })
            
            # Also send updated status
            status = detection_manager.get_status()
            serializable_status = make_json_serializable(status)
            emit('detection_status_update', serializable_status)
            
        except Exception as e:
            logger.error(f"Error in detection control WebSocket: {e}")
            emit('detection_control_response', {
                'command': data.get('command', 'unknown'),
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('detection_statistics_request')
    def handle_detection_statistics_request():
        """Handle request for detection statistics."""
        try:
            detection_manager = get_service('detection_manager')
            if detection_manager:
                status = detection_manager.get_status()
                statistics = status.get('statistics', {})
                
                # Calculate additional metrics
                total_frames = statistics.get('total_frames_processed', 0)
                successful_detections = statistics.get('total_vehicles_detected', 0)
                
                detection_rate = 0.0
                if total_frames > 0:
                    detection_rate = (successful_detections / total_frames) * 100
                
                enhanced_stats = {
                    **statistics,
                    'detection_rate_percent': round(detection_rate, 2),
                    'avg_processing_time_ms': round(statistics.get('processing_time_avg', 0) * 1000, 2)
                }
                
                emit('detection_statistics_update', enhanced_stats)
            else:
                emit('detection_statistics_error', {'error': 'Detection manager not available'})
        except Exception as e:
            logger.error(f"Error in detection statistics WebSocket: {e}")
            emit('detection_statistics_error', {'error': str(e)})
    
    @socketio.on('join_detection_room')
    def handle_join_detection_room():
        """Join detection updates room."""
        join_room('detection_updates')
        emit('joined_detection_room', {'message': 'Joined detection updates'})
    
    @socketio.on('leave_detection_room')
    def handle_leave_detection_room():
        """Leave detection updates room."""
        leave_room('detection_updates')
        emit('left_detection_room', {'message': 'Left detection updates'})
    
    logger.info("Detection WebSocket events registered")
