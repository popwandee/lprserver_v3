#!/usr/bin/env python3
"""
Camera Blueprint for AI Camera v1.3

This blueprint provides camera control and video streaming functionality:
- Video streaming endpoints
- Camera configuration management
- Camera status monitoring
- WebSocket events for real-time updates

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
from core.dependency_container import get_service
from core.utils.logging_config import get_logger

# Create blueprint
camera_bp = Blueprint('camera', __name__, url_prefix='/camera')

logger = get_logger(__name__)


@camera_bp.route('/')
def camera_dashboard():
    """Camera dashboard page."""
    try:
        camera_manager = get_service('camera_manager')
        camera_status = camera_manager.get_status() if camera_manager else {}
        camera_settings = camera_manager.get_available_settings() if camera_manager else {}
        
        return render_template('camera/dashboard.html',
                             camera_status=camera_status,
                             camera_settings=camera_settings,
                             title="Camera Dashboard")
    except Exception as e:
        logger.error(f"Error in camera dashboard: {e}")
        return render_template('camera/dashboard.html',
                             camera_status={},
                             camera_settings={},
                             title="Camera Dashboard")


@camera_bp.route('/status')
def get_camera_status():
    """Get current camera status."""
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        status = camera_manager.get_status()
        return jsonify({
            'success': True,
            'status': status,
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
    """Start camera streaming."""
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
    """Stop camera streaming."""
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
    """Restart camera streaming."""
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
    """Get or update camera configuration."""
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        if request.method == 'GET':
            # Get current configuration
            config = camera_manager.get_configuration()
            settings = camera_manager.get_available_settings()
            
            return jsonify({
                'success': True,
                'config': config,
                'settings': settings,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Update configuration
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            updated_config = camera_manager.update_configuration(data)
            
            return jsonify({
                'success': True,
                'config': updated_config,
                'message': 'Configuration updated successfully',
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
    """Capture a single image."""
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
    """Get camera health status."""
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
        logger.error(f"Error getting camera health: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def generate_frames():
    """Generate video frames optimized for ML detection streaming."""
    camera_manager = get_service('camera_manager')
    
    while True:
        try:
            if not camera_manager or not camera_manager.streaming:
                # Send a placeholder frame or wait
                time.sleep(0.1)
                continue
            
            # Get ML-optimized frame from camera handler
            if camera_manager.camera_handler:
                frame_data = camera_manager.camera_handler.capture_ml_frame()
                if frame_data:
                    # Use main frame for high-quality display
                    frame = frame_data['main_frame']
                    
                    # Encode frame to JPEG with optimized quality
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        
                        # Yield frame in multipart format
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        
                        # Optimized frame rate for ML processing
                        time.sleep(0.033)  # ~30 FPS
                        continue
            
            # Fallback to regular frame capture
            frame_data = camera_manager.get_frame(timeout=0.1)
            if frame_data:
                frame = frame_data['frame']
                
                # Encode frame to JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
        except Exception as e:
            logger.error(f"Error generating frame: {e}")
            time.sleep(0.1)


@camera_bp.route('/video_feed')
def video_feed():
    """Video streaming endpoint."""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@camera_bp.route('/video_feed_lores')
def video_feed_lores():
    """Low-resolution video streaming endpoint optimized for ML detection."""
    camera_manager = get_service('camera_manager')
    
    def generate_lores_frames():
        while True:
            try:
                if not camera_manager or not camera_manager.streaming:
                    time.sleep(0.1)
                    continue
                
                # Get ML-optimized frame from camera handler
                if camera_manager.camera_handler:
                    frame_data = camera_manager.camera_handler.capture_ml_frame()
                    if frame_data:
                        # Use lores frame for ML processing display
                        frame = frame_data['lores_frame']
                        
                        # Encode frame to JPEG with optimized quality for ML
                        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                        if ret:
                            frame_bytes = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        
                        # Optimized frame rate for ML processing
                        time.sleep(0.033)  # ~30 FPS
                        continue
                
                # Fallback to regular lores frame capture
                frame_data = camera_manager.camera_handler.capture_lores_frame()
                if frame_data:
                    frame = frame_data['frame']
                    
                    # Encode frame to JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error generating low-res frame: {e}")
                time.sleep(0.1)
    
    return Response(generate_lores_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@camera_bp.route('/ml_frame')
def get_ml_frame():
    """Get ML-optimized frame data for detection processing."""
    camera_manager = get_service('camera_manager')
    
    try:
        if not camera_manager or not camera_manager.streaming:
            return jsonify({
                'success': False,
                'error': 'Camera not streaming'
            }), 400
        
        if not camera_manager.camera_handler:
            return jsonify({
                'success': False,
                'error': 'Camera handler not available'
            }), 400
        
        # Get ML-optimized frame
        frame_data = camera_manager.camera_handler.capture_ml_frame()
        if not frame_data:
            return jsonify({
                'success': False,
                'error': 'Failed to capture ML frame'
            }), 500
        
        # Convert frames to base64 for JSON response
        import base64
        
        # Encode main frame
        ret_main, buffer_main = cv2.imencode('.jpg', frame_data['main_frame'], [cv2.IMWRITE_JPEG_QUALITY, 85])
        main_frame_b64 = base64.b64encode(buffer_main).decode('utf-8') if ret_main else None
        
        # Encode lores frame
        ret_lores, buffer_lores = cv2.imencode('.jpg', frame_data['lores_frame'], [cv2.IMWRITE_JPEG_QUALITY, 75])
        lores_frame_b64 = base64.b64encode(buffer_lores).decode('utf-8') if ret_lores else None
        
        return jsonify({
            'success': True,
            'timestamp': frame_data['timestamp'],
            'main_frame': main_frame_b64,
            'lores_frame': lores_frame_b64,
            'metadata': frame_data['metadata'],
            'main_size': frame_data['main_size'],
            'lores_size': frame_data['lores_size']
        })
        
    except Exception as e:
        logger.error(f"Error getting ML frame: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# WebSocket event handlers
def register_camera_events(socketio):
    """Register WebSocket events for camera control."""
    
    @socketio.on('connect', namespace='/camera')
    def handle_camera_connect():
        """Handle client connection."""
        logger.info("Client connected to camera namespace")
        emit('camera_connected', {'message': 'Connected to camera service'})
    
    @socketio.on('disconnect', namespace='/camera')
    def handle_camera_disconnect():
        """Handle client disconnection."""
        logger.info("Client disconnected from camera namespace")
    
    @socketio.on('join_camera_room', namespace='/camera')
    def handle_join_camera_room(data):
        """Join camera control room."""
        room = data.get('room', 'camera_control')
        join_room(room)
        emit('camera_room_joined', {'room': room})
    
    @socketio.on('camera_status_request', namespace='/camera')
    def handle_camera_status_request():
        """Handle camera status request."""
        try:
            camera_manager = get_service('camera_manager')
            if camera_manager:
                status = camera_manager.get_status()
                emit('camera_status_update', status)
            else:
                emit('camera_status_update', {'error': 'Camera manager not available'})
        except Exception as e:
            logger.error(f"Error handling camera status request: {e}")
            emit('camera_status_update', {'error': str(e)})
    
    @socketio.on('camera_control', namespace='/camera')
    def handle_camera_control(data):
        """Handle camera control commands."""
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
            
            success = False
            message = ""
            
            if command == 'start':
                success = camera_manager.start()
                message = "Camera started" if success else "Failed to start camera"
            elif command == 'stop':
                success = camera_manager.stop()
                message = "Camera stopped" if success else "Failed to stop camera"
            elif command == 'restart':
                success = camera_manager.restart()
                message = "Camera restarted" if success else "Failed to restart camera"
            elif command == 'capture':
                image_data = camera_manager.capture_image()
                success = image_data is not None
                message = "Image captured" if success else "Failed to capture image"
            else:
                message = f"Unknown command: {command}"
            
            emit('camera_control_response', {
                'command': command,
                'success': success,
                'message': message
            })
            
            # Broadcast status update to all clients
            if success:
                status = camera_manager.get_status()
                socketio.emit('camera_status_update', status, namespace='/camera')
                
        except Exception as e:
            logger.error(f"Error handling camera control: {e}")
            emit('camera_control_response', {
                'command': data.get('command'),
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('camera_config_update', namespace='/camera')
    def handle_camera_config_update(data):
        """Handle camera configuration updates."""
        try:
            config = data.get('config', {})
            camera_manager = get_service('camera_manager')
            
            if not camera_manager:
                emit('camera_config_response', {
                    'success': False,
                    'error': 'Camera manager not available'
                })
                return
            
            updated_config = camera_manager.update_configuration(config)
            
            emit('camera_config_response', {
                'success': True,
                'config': updated_config,
                'message': 'Configuration updated successfully'
            })
            
            # Broadcast status update
            status = camera_manager.get_status()
            socketio.emit('camera_status_update', status, namespace='/camera')
            
        except Exception as e:
            logger.error(f"Error updating camera config: {e}")
            emit('camera_config_response', {
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('camera_health_request', namespace='/camera')
    def handle_camera_health_request():
        """Handle camera health request."""
        try:
            camera_manager = get_service('camera_manager')
            if camera_manager:
                health = camera_manager.health_check()
                emit('camera_health_update', health)
            else:
                emit('camera_health_update', {'error': 'Camera manager not available'})
        except Exception as e:
            logger.error(f"Error handling camera health request: {e}")
            emit('camera_health_update', {'error': str(e)})
    
    logger.info("Camera WebSocket events registered")
