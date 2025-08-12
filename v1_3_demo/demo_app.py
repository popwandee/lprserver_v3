#!/usr/bin/env python3
"""
AI Camera v1.3 Demo Application

This is a demo version of the AI Camera v1.3 system that uses video files
instead of real camera hardware for demonstration purposes.

Author: AI Camera Team
Version: 1.3 Demo
Date: August 8, 2025
"""

import os
import sys
from pathlib import Path
from typing import Tuple
from datetime import datetime
import cv2
import numpy as np
import threading
import time
import queue
import json
import base64
from io import BytesIO

# Load environment variables
def load_env_file():
    """Load environment variables from .env.production file."""
    env_file = Path(__file__).parent / '.env.production'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key.strip()] = value

# Load environment variables
load_env_file()

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO
import logging

# Import import helper first to setup paths
from src.core.utils.import_helper import setup_import_paths, validate_imports
setup_import_paths()

from src.core.utils.logging_config import setup_logging, get_logger
from src.core.dependency_container import get_container, get_service

# Demo configuration
DEMO_VIDEO_FILE = "example.mp4"
DEMO_MODE = True

def create_demo_camera_handler():
    """Create a demo camera handler that uses video file instead of real camera."""
    class DemoCameraHandler:
        def __init__(self):
            self.video_file = DEMO_VIDEO_FILE
            self.cap = None
            self.initialized = False
            self.streaming = False
            self.frame_count = 0
            self.start_time = None
            self.logger = get_logger(__name__)
            
        def initialize_camera(self):
            """Initialize video capture from file."""
            try:
                self.cap = cv2.VideoCapture(self.video_file)
                if not self.cap.isOpened():
                    self.logger.error(f"Could not open video file: {self.video_file}")
                    return False
                
                self.initialized = True
                self.frame_count = 0
                self.start_time = datetime.now()
                self.logger.info(f"Demo camera initialized with video: {self.video_file}")
                return True
            except Exception as e:
                self.logger.error(f"Error initializing demo camera: {e}")
                return False
        
        def capture_frame(self):
            """Capture frame from video file."""
            if not self.initialized or not self.cap:
                return None
            
            ret, frame = self.cap.read()
            if not ret:
                # Reset video to beginning
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    return None
            
            self.frame_count += 1
            return {
                'frame': frame,
                'metadata': {
                    'frame_number': self.frame_count,
                    'timestamp': datetime.now().isoformat()
                },
                'timestamp': time.time()
            }
        
        def get_status(self):
            """Get camera status."""
            return {
                'initialized': self.initialized,
                'streaming': self.streaming,
                'frame_count': self.frame_count,
                'video_file': self.video_file,
                'demo_mode': True
            }
        
        def close_camera(self):
            """Close video capture."""
            if self.cap:
                self.cap.release()
            self.initialized = False
            self.streaming = False
    
    return DemoCameraHandler()

def create_demo_detection_processor():
    """Create a demo detection processor that simulates AI detection."""
    class DemoDetectionProcessor:
        def __init__(self):
            self.logger = get_logger(__name__)
            self.demo_results = [
                {'type': 'vehicle', 'confidence': 0.95, 'bbox': [100, 100, 300, 200]},
                {'type': 'license_plate', 'confidence': 0.88, 'bbox': [150, 150, 250, 180], 'text': 'ABC123'},
                {'type': 'vehicle', 'confidence': 0.92, 'bbox': [400, 120, 600, 220]},
            ]
            self.result_index = 0
            
        def detect_objects(self, frame):
            """Simulate object detection."""
            # Simulate processing delay
            time.sleep(0.1)
            
            # Return demo results
            result = self.demo_results[self.result_index % len(self.demo_results)]
            self.result_index += 1
            
            return {
                'success': True,
                'detections': [result],
                'processing_time': 0.1
            }
    
    return DemoDetectionProcessor()

def create_demo_health_monitor():
    """Create a demo health monitor."""
    class DemoHealthMonitor:
        def __init__(self):
            self.logger = get_logger(__name__)
            
        def run_all_checks(self):
            """Run demo health checks."""
            return {
                'overall_status': 'healthy',
                'component_status': {
                    'camera': {'status': 'healthy', 'message': 'Demo camera working'},
                    'detection': {'status': 'healthy', 'message': 'Demo detection working'},
                    'system': {'status': 'healthy', 'message': 'Demo system healthy'}
                }
            }
    
    return DemoHealthMonitor()

def create_demo_services():
    """Create demo services for the demo application."""
    # Override service creation with demo versions
    demo_camera_handler = create_demo_camera_handler()
    demo_detection_processor = create_demo_detection_processor()
    demo_health_monitor = create_demo_health_monitor()
    
    return {
        'camera_handler': demo_camera_handler,
        'detection_processor': demo_detection_processor,
        'health_monitor': demo_health_monitor
    }

def create_demo_app():
    """Create and configure Flask demo application."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Validate imports
    import_errors = validate_imports()
    if import_errors:
        logger.warning("Some imports failed:")
        for error in import_errors:
            logger.warning(f"  {error}")
    
    # Create Flask app
    current_dir = Path(__file__).parent
    template_dir = current_dir / 'src' / 'web' / 'templates'
    static_dir = current_dir / 'src' / 'web' / 'static'
    
    app = Flask(__name__, 
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    
    # Load configuration
    app.config.from_object('src.core.config')
    
    # Initialize dependency container
    container = get_container()
    
    # Create demo services
    demo_services = create_demo_services()
    
    # Override services in container with demo versions
    for service_name, service_instance in demo_services.items():
        container.instances[service_name] = service_instance
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register blueprints
    from src.web.blueprints import register_blueprints
    register_blueprints(app, socketio)
    
    # Demo-specific routes
    @app.route('/')
    def demo_dashboard():
        """Demo dashboard."""
        return render_template('index.html', demo_mode=True)
    
    @app.route('/demo/status')
    def demo_status():
        """Get demo system status."""
        try:
            camera_handler = get_service('camera_handler')
            detection_processor = get_service('detection_processor')
            health_monitor = get_service('health_monitor')
            
            status = {
                'demo_mode': True,
                'camera': camera_handler.get_status() if camera_handler else None,
                'detection': {'status': 'demo', 'processor': 'demo'} if detection_processor else None,
                'health': health_monitor.run_all_checks() if health_monitor else None,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': status
            })
        except Exception as e:
            logger.error(f"Error getting demo status: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/demo/video')
    def demo_video():
        """Stream demo video."""
        def generate():
            camera_handler = get_service('camera_handler')
            if not camera_handler:
                return
            
            if not camera_handler.initialized:
                camera_handler.initialize_camera()
            
            while True:
                frame_data = camera_handler.capture_frame()
                if frame_data and 'frame' in frame_data:
                    frame = frame_data['frame']
                    
                    # Encode frame to JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    jpeg_data = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg_data + b'\r\n')
                
                time.sleep(1.0 / 30)  # 30 FPS
        
        return Response(generate(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/demo/detection')
    def demo_detection():
        """Simulate detection results."""
        try:
            detection_processor = get_service('detection_processor')
            if not detection_processor:
                return jsonify({'error': 'Detection processor not available'}), 500
            
            # Create a dummy frame for detection
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = detection_processor.detect_objects(dummy_frame)
            
            return jsonify({
                'success': True,
                'data': result
            })
        except Exception as e:
            logger.error(f"Error in demo detection: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # WebSocket events for demo
    @socketio.on('demo_status_request')
    def handle_demo_status_request():
        """Handle demo status request."""
        try:
            camera_handler = get_service('camera_handler')
            detection_processor = get_service('detection_processor')
            health_monitor = get_service('health_monitor')
            
            status = {
                'demo_mode': True,
                'camera': camera_handler.get_status() if camera_handler else None,
                'detection': {'status': 'demo', 'processor': 'demo'} if detection_processor else None,
                'health': health_monitor.run_all_checks() if health_monitor else None,
                'timestamp': datetime.now().isoformat()
            }
            
            emit('demo_status_update', status)
        except Exception as e:
            logger.error(f"Error handling demo status request: {e}")
            emit('demo_status_update', {'error': str(e)})
    
    @socketio.on('demo_detection_request')
    def handle_demo_detection_request():
        """Handle demo detection request."""
        try:
            detection_processor = get_service('detection_processor')
            if not detection_processor:
                emit('demo_detection_response', {'error': 'Detection processor not available'})
                return
            
            # Create a dummy frame for detection
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result = detection_processor.detect_objects(dummy_frame)
            
            emit('demo_detection_response', result)
        except Exception as e:
            logger.error(f"Error handling demo detection request: {e}")
            emit('demo_detection_response', {'error': str(e)})
    
    return app, socketio

def main():
    """Main function for demo application."""
    app, socketio = create_demo_app()
    
    logger = get_logger(__name__)
    logger.info("🚀 Starting AI Camera v1.3 Demo Application")
    logger.info("📹 Demo mode: Using video file instead of real camera")
    logger.info("🌐 Web interface: http://localhost:5000")
    logger.info("📺 Video stream: http://localhost:5000/demo/video")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
