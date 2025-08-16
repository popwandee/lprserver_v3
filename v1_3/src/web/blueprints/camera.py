#!/usr/bin/env python3
"""
Camera Blueprint for AI Camera v1.3

This blueprint provides camera control and video streaming functionality:
- Video streaming endpoints
- Camera configuration management
- Camera status monitoring
- WebSocket events for real-time updates
- Auto-start status display

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import cv2
import numpy as np
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
camera_bp = Blueprint('camera', __name__, url_prefix='/camera')

logger = get_logger(__name__)


@camera_bp.route('/')
def camera_dashboard():
    """
    Camera dashboard page with auto-start status.
    
    Returns:
        str: Rendered HTML template
    """
    try:
        camera_manager = get_service('camera_manager')
        camera_status = camera_manager.get_status() if camera_manager else {}
        camera_settings = camera_manager.get_available_settings() if camera_manager else {}
        
        # Add auto-start information to template context
        auto_start_info = {
            'enabled': camera_status.get('auto_start_enabled', False),
            'uptime': camera_status.get('uptime', 0)
        }
        
        return render_template('camera/dashboard.html',
                             camera_status=camera_status,
                             camera_settings=camera_settings,
                             auto_start_info=auto_start_info,
                             title="Camera Dashboard")
    except Exception as e:
        logger.error(f"Error in camera dashboard: {e}")
        return render_template('camera/dashboard.html',
                             camera_status={},
                             camera_settings={},
                             auto_start_info={'enabled': False, 'uptime': 0},
                             title="Camera Dashboard")


@camera_bp.route('/status')
def get_camera_status():
    """
    Get current camera status including auto-start information.
    
    Returns:
        dict: JSON response with camera status
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        status = camera_manager.get_status()
        
        # Ensure all status data is JSON serializable
        serializable_status = make_json_serializable(status)
        
        return jsonify({
            'success': True,
            'status': serializable_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/start', methods=['POST'])
def start_camera():
    """
    Start camera streaming (manual start).
    
    Returns:
        dict: JSON response with start result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        success = camera_manager.start()
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera started successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start camera',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/stop', methods=['POST'])
def stop_camera():
    """
    Stop camera streaming.
    
    Returns:
        dict: JSON response with stop result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        success = camera_manager.stop()
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera stopped successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to stop camera',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/restart', methods=['POST'])
def restart_camera():
    """
    Restart camera.
    
    Returns:
        dict: JSON response with restart result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        success = camera_manager.restart()
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera restarted successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to restart camera',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error restarting camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/config', methods=['GET', 'POST'])
def camera_config():
    """
    Camera configuration management.
    
    Returns:
        dict: JSON response with configuration data
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        if request.method == 'GET':
            # Get current configuration
            config = camera_manager.get_available_settings()
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Update configuration
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            result = camera_manager.update_configuration(data)
            
            return jsonify({
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'error': result.get('error', ''),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error in camera config: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/capture', methods=['POST'])
def capture_image():
    """
    Capture a single image.
    
    Returns:
        dict: JSON response with capture result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        image_data = camera_manager.capture_image()
        if image_data:
            return jsonify({
                'success': True,
                'message': 'Image captured successfully',
                'image_path': image_data.get('saved_path'),
                'size': image_data.get('size'),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to capture image',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/health')
def camera_health():
    """
    Camera health check endpoint.
    
    Returns:
        dict: JSON response with health status
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        health = camera_manager.health_check()
        
        return jsonify({
            'success': True,
            'health': health,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in camera health check: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def generate_frames():
    """
    Generate video frames for streaming.
    
    Yields:
        bytes: Frame data in multipart format
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager or not camera_manager.camera_handler:
            logger.error("Camera manager or handler not available for streaming")
            return
        
        camera_handler = camera_manager.camera_handler
        
        # Check if camera is initialized and streaming
        camera_status = camera_handler.get_status()
        if not camera_status.get('initialized', False):
            logger.warning("Camera not initialized, waiting...")
            time.sleep(1)
            return
        
        while True:
            try:
                # Call capture_frame directly without timeout parameter
                frame_data = camera_handler.capture_frame()
                
                if frame_data and 'frame' in frame_data:
                    # Convert frame to JPEG
                    frame = frame_data['frame']
                    if frame is not None and frame.size > 0:
                        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        if ret:
                            frame_bytes = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        else:
                            logger.warning("Failed to encode frame")
                    else:
                        logger.warning("Empty frame received")
                else:
                    # Send a placeholder frame or wait
                    logger.debug("No frame data available, waiting...")
                    time.sleep(0.1)
                    continue
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error generating frame: {e}")
                time.sleep(0.1)  # Reduced wait time
                
    except Exception as e:
        logger.error(f"Error in generate_frames: {e}")


@camera_bp.route('/video_feed')
def video_feed():
    """
    Video streaming endpoint.
    
    Returns:
        Response: Multipart video stream
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_lores_frames():
    """
    Generate low resolution video frames for streaming.
    
    Yields:
        bytes: Frame data in multipart format
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager or not camera_manager.camera_handler:
            logger.error("Camera manager or handler not available for lores streaming")
            return
        
        camera_handler = camera_manager.camera_handler
        
        # Check if camera is initialized and streaming
        camera_status = camera_handler.get_status()
        if not camera_status.get('initialized', False):
            logger.warning("Camera not initialized for lores streaming, waiting...")
            time.sleep(1)
            return
        
        while True:
            try:
                # Call capture_lores_frame directly without timeout parameter
                frame_data = camera_handler.capture_lores_frame()
                
                if frame_data and 'frame' in frame_data:
                    frame = frame_data['frame']
                    if frame is not None and frame.size > 0:
                        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                        if ret:
                            frame_bytes = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        else:
                            logger.warning("Failed to encode lores frame")
                    else:
                        logger.warning("Empty lores frame received")
                else:
                    # Send a placeholder frame or wait
                    logger.debug("No lores frame data available, waiting...")
                    time.sleep(0.1)
                    continue
                
                time.sleep(0.1)  # ~10 FPS for lores
                
            except Exception as e:
                logger.error(f"Error generating lores frame: {e}")
                time.sleep(0.1)  # Reduced wait time
                
    except Exception as e:
        logger.error(f"Error in generate_lores_frames: {e}")


@camera_bp.route('/video_feed_lores')
def video_feed_lores():
    """
    Low resolution video streaming endpoint.
    
    Returns:
        Response: Multipart video stream
    """
    return Response(generate_lores_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@camera_bp.route('/ml_frame')
def get_ml_frame():
    """
    Get ML-optimized frame for AI processing.
    
    Returns:
        dict: JSON response with frame data
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager or not camera_manager.camera_handler:
            return jsonify({'error': 'Camera manager or handler not available'}), 500
        
        camera_handler = camera_manager.camera_handler
        frame_data = camera_handler.capture_ml_frame()
        
        if frame_data and 'main_frame' in frame_data:
            main_frame = frame_data['main_frame']
            if main_frame is not None:
                # Convert to base64 for JSON response
                ret, buffer = cv2.imencode('.jpg', main_frame)
                if ret:
                    import base64
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    return jsonify({
                        'success': True,
                        'frame': frame_base64,
                        'metadata': frame_data.get('metadata', {}),
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to encode frame',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'Empty frame received',
                    'timestamp': datetime.now().isoformat()
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'No frame data available',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error getting ML frame: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def register_camera_events(socketio):
    """
    Register WebSocket events for camera functionality.
    
    Args:
        socketio: Flask-SocketIO instance
    """
    
    @socketio.on('connect', namespace='/camera')
    def handle_camera_connect():
        logger.info("Client connected to camera namespace")
        emit('camera_connected', {'status': 'Connected to camera service'})
    
    @socketio.on('disconnect', namespace='/camera')
    def handle_camera_disconnect():
        logger.info("Client disconnected from camera namespace")
    
    @socketio.on('join_camera_room', namespace='/camera')
    def handle_join_camera_room(data):
        room = data.get('room', 'camera_room')
        join_room(room)
        emit('joined_room', {'room': room})
    
    @socketio.on('camera_status_request', namespace='/camera')
    def handle_camera_status_request():
        try:
            camera_manager = get_service('camera_manager')
            if camera_manager:
                status = camera_manager.get_status()
                # Add auto-start information to status
                status['auto_start'] = {
                    'enabled': status.get('auto_start_enabled', False),
                    'uptime': status.get('uptime', 0)
                }
                emit('camera_status_update', status)
            else:
                emit('camera_status_update', {'error': 'Camera manager not available'})
        except Exception as e:
            logger.error(f"Error in camera status request: {e}")
            emit('camera_status_update', {'error': str(e)})
    
    @socketio.on('camera_control', namespace='/camera')
    def handle_camera_control(data):
        try:
            command = data.get('command')
            camera_manager = get_service('camera_manager')
            
            if not camera_manager:
                emit('camera_control_response', {
                    'command': command,
                    'success': False,
                    'error': 'Camera manager not available'
                })
                return
            
            if command == 'start':
                success = camera_manager.start()
                message = 'Camera started successfully' if success else 'Failed to start camera'
            elif command == 'stop':
                success = camera_manager.stop()
                message = 'Camera stopped successfully' if success else 'Failed to stop camera'
            elif command == 'restart':
                success = camera_manager.restart()
                message = 'Camera restarted successfully' if success else 'Failed to restart camera'
            else:
                success = False
                message = f"Unknown command: {command}"
            
            emit('camera_control_response', {
                'command': command,
                'success': success,
                'message': message,
                'error': None if success else message
            })
        except Exception as e:
            logger.error(f"Error in camera control: {e}")
            emit('camera_control_response', {
                'command': data.get('command'),
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('camera_config_update', namespace='/camera')
    def handle_camera_config_update(data):
        try:
            camera_manager = get_service('camera_manager')
            if camera_manager:
                config = data.get('config', {})
                success = camera_manager.update_configuration(config)
                
                # Get updated configuration that's JSON serializable
                updated_config = camera_manager.get_configuration()
                
                emit('camera_config_response', {
                    'success': success,
                    'message': 'Configuration updated successfully' if success else 'Configuration update failed',
                    'config': updated_config
                })
            else:
                emit('camera_config_response', {
                    'success': False,
                    'error': 'Camera manager not available'
                })
        except Exception as e:
            logger.error(f"Error in camera config update: {e}")
            emit('camera_config_response', {
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('camera_health_request', namespace='/camera')
    def handle_camera_health_request():
        try:
            camera_manager = get_service('camera_manager')
            if camera_manager:
                health = camera_manager.health_check()
                emit('camera_health_update', health)
            else:
                emit('camera_health_update', {'error': 'Camera manager not available'})
        except Exception as e:
            logger.error(f"Error in camera health request: {e}")
            emit('camera_health_update', {'error': str(e)})


@camera_bp.route('/debug')
def camera_debug():
    """
    Debug endpoint to check camera status and frame capture.
    
    Returns:
        dict: JSON response with debug information
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        camera_handler = camera_manager.camera_handler
        if not camera_handler:
            return jsonify({'error': 'Camera handler not available'}), 500
        
        # Get camera status
        camera_status = camera_handler.get_status()
        
        # Try to capture a test frame
        test_frame = None
        frame_error = None
        try:
            test_frame = camera_handler.capture_frame()
            if test_frame and 'image' in test_frame:
                frame_shape = test_frame['image'].shape if test_frame['image'] is not None else None
            else:
                frame_shape = None
        except Exception as e:
            frame_error = str(e)
            frame_shape = None
        
        debug_info = {
            'camera_status': camera_status,
            'frame_capture_success': test_frame is not None,
            'frame_shape': frame_shape,
            'frame_error': frame_error,
            'camera_initialized': camera_status.get('initialized', False),
            'camera_streaming': camera_status.get('streaming', False),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'debug': debug_info
        })
        
    except Exception as e:
        logger.error(f"Error in camera debug: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/debug_metadata')
def debug_camera_metadata():
    """
    Debug endpoint to test metadata capture step by step.
    
    Returns:
        dict: JSON response with debug information
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        camera_handler = camera_manager.camera_handler
        if not camera_handler:
            return jsonify({
                'success': False,
                'error': 'Camera handler not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get debug information from camera handler
        debug_info = camera_handler.debug_metadata_capture()
        
        return jsonify({
            'success': True,
            'debug_info': debug_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in debug metadata: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/metadata')
def camera_metadata_viewer():
    """
    Camera metadata viewer page.
    
    Returns:
        str: Rendered HTML template with metadata information
    """
    try:
        logger.info("Starting camera metadata viewer...")
        
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            logger.error("Camera manager not available")
            return render_template('camera/metadata_viewer.html',
                                 camera_status={'error': 'Camera manager not available'},
                                 title="Camera Metadata Viewer")
        
        logger.info("Camera manager found, getting status...")
        
        # Get comprehensive camera status and metadata
        try:
            camera_status = camera_manager.get_status()
            logger.info("Camera status retrieved successfully")
        except Exception as e:
            logger.error(f"Error getting camera status: {e}")
            return render_template('camera/metadata_viewer.html',
                                 camera_status={'error': f'Failed to get camera status: {e}'},
                                 title="Camera Metadata Viewer")
        
        # Get camera handler for detailed metadata
        camera_handler = None
        try:
            if hasattr(camera_manager, 'camera_handler'):
                camera_handler = camera_manager.camera_handler
                logger.info("Camera handler found")
            else:
                logger.warning("Camera handler not available")
        except Exception as e:
            logger.error(f"Error accessing camera handler: {e}")
        
        # Debug metadata capture
        debug_info = None
        if camera_handler:
            try:
                logger.info("Starting debug metadata capture...")
                debug_info = camera_handler.debug_metadata_capture()
                logger.info("Debug metadata capture completed")
            except Exception as e:
                logger.error(f"Error in debug metadata capture: {e}")
                debug_info = {'error': str(e)}
        else:
            debug_info = {'error': 'Camera handler not available'}
        
        # Prepare metadata for template with safe defaults
        try:
            metadata_data = {
                'camera_status': camera_status or {},
                'camera_properties': camera_status.get('camera_handler', {}).get('camera_properties', {}) if camera_status else {},
                'current_config': camera_status.get('camera_handler', {}).get('current_config', {}) if camera_status else {},
                'camera_controls': camera_status.get('camera_handler', {}).get('configuration', {}).get('controls', {}) if camera_status else {},
                'frame_metadata': camera_status.get('metadata', {}) if camera_status else {},
                'frame_statistics': {
                    'frame_count': camera_status.get('frame_count', 0) if camera_status else 0,
                    'average_fps': camera_status.get('average_fps', 0.0) if camera_status else 0.0,
                    'last_frame_time': camera_status.get('timestamp', 'N/A') if camera_status else 'N/A'
                },
                'available_modes': camera_status.get('camera_handler', {}).get('sensor_modes', []) if camera_status else [],
                'sensor_modes_count': camera_status.get('camera_handler', {}).get('sensor_modes_count', 0) if camera_status else 0,
                'debug_info': debug_info
            }
            logger.info("Metadata data prepared successfully")
        except Exception as e:
            logger.error(f"Error preparing metadata data: {e}")
            metadata_data = {
                'camera_status': {'error': f'Failed to prepare metadata: {e}'},
                'debug_info': {'error': str(e)}
            }
        
        logger.info("Rendering metadata viewer template...")
        return render_template('camera/metadata_viewer.html',
                             **metadata_data,
                             title="Camera Metadata Viewer")
                             
    except Exception as e:
        logger.error(f"Unexpected error in camera metadata viewer: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return render_template('camera/metadata_viewer.html',
                             camera_status={'error': f'Unexpected error: {e}'},
                             title="Camera Metadata Viewer")


@camera_bp.route('/api/metadata')
def get_camera_metadata_api():
    """
    API endpoint to get camera metadata in JSON format.
    
    Returns:
        dict: JSON response with camera metadata
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get comprehensive camera status and metadata
        camera_status = camera_manager.get_status()
        
        # Prepare metadata for API response
        metadata_response = {
            'success': True,
            'camera_status': camera_status,
            'camera_properties': camera_status.get('camera_handler', {}).get('camera_properties', {}),
            'current_config': camera_status.get('camera_handler', {}).get('current_config', {}),
            'camera_controls': camera_status.get('camera_handler', {}).get('configuration', {}).get('controls', {}),
            'frame_metadata': camera_status.get('metadata', {}),
            'frame_statistics': {
                'frame_count': camera_status.get('frame_count', 0),
                'average_fps': camera_status.get('average_fps', 0.0),
                'last_frame_time': camera_status.get('timestamp', 'N/A')
            },
            'available_modes': camera_status.get('camera_handler', {}).get('sensor_modes', []),
            'sensor_modes_count': camera_status.get('camera_handler', {}).get('sensor_modes_count', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(metadata_response)
        
    except Exception as e:
        logger.error(f"Error getting camera metadata API: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500