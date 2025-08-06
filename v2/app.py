#!/usr/bin/env python3
"""
AI Camera Application v2
A comprehensive version with camera management, detection, and health monitoring
"""

import os
import threading
import queue
import time
import signal
import sys
import socket
from datetime import datetime
from flask import Flask, render_template, Response, request, jsonify, send_file
import logging
import cv2
import numpy as np
from picamera2 import Picamera2
from libcamera import controls

# Import our custom modules
from config import (
    FLASK_HOST, FLASK_PORT, BASE_DIR, SECRET_KEY
)
from camera_config import (
    get_camera_config, get_default_settings, get_detection_resolution, get_video_feed_resolution,
    DEFAULT_BRIGHTNESS, DEFAULT_CONTRAST, DEFAULT_SATURATION, DEFAULT_SHARPNESS, DEFAULT_AWB_MODE
)
from database_manager import DatabaseManager
from logging_config import setup_logging
from health_monitor import get_health_monitor
from detection_thread import DetectionThread
from websocket_manager import websocket_manager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Global variables
camera = None
camera_lock = threading.Lock()
frames_queue = queue.Queue(maxsize=10)
metadata_queue = queue.Queue(maxsize=10)
db_manager = DatabaseManager(threading.Lock())
streaming_active = False
stream_thread = None
camera_manager = None
shutdown_requested = False

# Custom Jinja2 filter for datetime formatting
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object to a string."""
    if isinstance(value, str):
        # Assuming value is in ISO format from database
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value # Return as is if not a valid ISO format string
    return value.strftime(format)

# Initialize our handlers (they use the Singleton pattern, so this gets the single instance)
camera_handler = CameraHandler(frames_queue, metadata_queue)
db_manager = DatabaseManager(db_lock) 
detection_processor = DetectionProcessor(frames_queue)
websocket_client = WebSocketClient()
health_monitor = HealthMonitor(frames_queue, camera_handler)

# Thread objects
detection_thread = None
sender_thread = None
monitor_thread = None
metadata_thread = None
stop_event = threading.Event() # Event to signal threads to stop

# --- Thread Management Functions ---

def run_detection_processor():
    """Function to run the detection processor in a separate thread."""
    detection_processor.run()

def run_websocket_client_async_loop(loop):
    """Function to run the asyncio loop for the WebSocket client in a thread."""
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_client.run())

def run_health_monitor(): 
    """Function to run the health monitor in a separate thread."""
    health_monitor.run()

def run_metadata_sender():
    """Function to read from the metadata queue and emit to all connected clients."""
    while True:
        try:
            # ดึง metadata จากคิวด้วย timeout
            metadata = metadata_queue.get(timeout=1)
            # ส่งข้อมูลไปยัง client ผ่าน WebSocket
            socketio.emit('camera_metadata', metadata, broadcast=True)
            metadata_queue.task_done()
        except queue.Empty:
            # คิวว่างก็ให้ทำต่อไปเรื่อยๆ
            continue
        except Exception as e:
            logging.error(f"Error in metadata sender thread: {e}")
            time.sleep(1)

def start_threads():
    """Starts the background detection and sender threads."""
    global detection_thread, sender_thread, monitor_thread,metadata_thread

   
    # Start Metadata Sender Thread
    if metadata_thread and metadata_thread.is_alive():
        logger.info("Metadata sender thread already running.")
    else:
        logger.info("Starting metadata sender thread...")
        metadata_thread = threading.Thread(target=run_metadata_sender, daemon=True)
        metadata_thread.start()
        logger.info("Metadata sender thread started.")

    # Start Detection Thread
    if detection_thread and detection_thread.is_alive():
        logger.info("Detection thread already running.")
    else:
        logger.info("Starting detection thread...")
        last_props = camera_handler.get_latest_camera_properties()
        detection_thread = threading.Thread(target=run_detection_processor, daemon=True)
        detection_thread.start()
        logger.info("Detection thread started.")

    # Start WebSocket sender Thread
    if sender_thread and sender_thread.is_alive():
        logger.info("Sender thread already running.")
    else:
        logger.info("Starting WebSocket sender thread...")
        # Create a new event loop for the async client in this thread
        new_loop = asyncio.new_event_loop()
        sender_thread = threading.Thread(target=run_websocket_client_async_loop, args=(new_loop,), daemon=True)
        sender_thread.start()
        logger.info("WebSocket sender thread started.")

    # Start Health Monitor Thread
    if monitor_thread and monitor_thread.is_alive():
        logger.info("Health monitor thread already running.")
    else:
        logger.info("Starting health monitor thread...")
        monitor_thread = threading.Thread(target=run_health_monitor, daemon=True)
        monitor_thread.start()
        logger.info("Health monitor thread started.")

def stop_threads():
    """Signals background threads to stop and waits for them."""
    logger.info("Signaling background threads to stop...")
    detection_processor.stop()
    health_monitor.stop()
    asyncio.run(websocket_client.stop()) # Await the async stop method
    
    def __init__(self):
        self.camera = None
        self.is_initialized = False
        self.streaming = False
        self.lock = threading.Lock()
        
    def initialize_camera(self, **settings):
        """Initialize camera with basic settings"""
        with self.lock:
            try:
                logger.info("Initializing camera...")
                
                # Create camera instance
                logger.info("Creating Picamera2 instance...")
                self.camera = Picamera2()
                logger.info("Picamera2 instance created successfully")
                
                # Optimized configuration: Detection uses main stream, Video feed uses lores stream
                camera_config = get_camera_config()
                detection_res = get_detection_resolution()
                video_feed_res = get_video_feed_resolution()
                
                logger.info(f"Creating optimized video configuration:")
                logger.info(f"  Main stream: {detection_res} (for detection - high quality)")
                logger.info(f"  Lores stream: {video_feed_res} (for video feed - display only)")
                
                config = self.camera.create_video_configuration(
                    main=camera_config["main"],
                    lores=camera_config["lores"],
                    encode=camera_config["encode"],
                    buffer_count=camera_config["buffer_count"]
                )
                logger.info("Optimized video configuration created successfully")
                
                logger.info("Configuring camera...")
                self.camera.configure(config)
                logger.info("Camera configured successfully")
                
                # Log the actual configuration that was applied
                try:
                    sensor_config = self.camera.camera_configuration()
                    logger.info(f"Actual sensor configuration: {sensor_config}")
                    if 'main' in sensor_config:
                        logger.info(f"Actual main stream size: {sensor_config['main']['size']}")
                    if 'lores' in sensor_config:
                        logger.info(f"Actual lores stream size: {sensor_config['lores']['size']}")
                except Exception as e:
                    logger.warning(f"Could not get actual camera configuration: {e}")
                
                # Apply basic controls (with error handling)
                try:
                    controls_dict = {}
                    if settings.get('brightness') is not None:
                        controls_dict["Brightness"] = settings.get('brightness', DEFAULT_BRIGHTNESS)
                    if settings.get('contrast') is not None:
                        controls_dict["Contrast"] = settings.get('contrast', DEFAULT_CONTRAST)
                    if settings.get('saturation') is not None:
                        controls_dict["Saturation"] = settings.get('saturation', DEFAULT_SATURATION)
                    if settings.get('sharpness') is not None:
                        controls_dict["Sharpness"] = settings.get('sharpness', DEFAULT_SHARPNESS)
                    if settings.get('awb_mode') is not None:
                        controls_dict["AwbMode"] = settings.get('awb_mode', DEFAULT_AWB_MODE)
                    
                    # Set auto focus mode (remove AfTrigger as it's not supported)
                    controls_dict["AfMode"] = 2  # Auto focus mode
                    
                    if controls_dict:
                        self.camera.set_controls(controls_dict)
                        logger.info(f"Applied camera controls: {controls_dict}")
                        logger.info("Auto focus enabled")
                except Exception as e:
                    logger.warning(f"Could not apply some camera controls: {e}")
                    # Continue without controls - camera will still work
                
                # Start camera
                logger.info("Starting camera...")
                self.camera.start()
                logger.info("Camera start() called successfully")
                self.is_initialized = True
                
                # Initialize current settings
                self._current_brightness = settings.get('brightness', 0.0)
                self._current_contrast = settings.get('contrast', 1.0)
                self._current_saturation = settings.get('saturation', 1.0)
                self._current_sharpness = settings.get('sharpness', 1.0)
                self._current_awb_mode = settings.get('awb_mode', 0)
                self._current_focus = settings.get('focus', 0.0)
                
                logger.info("Camera initialized successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to initialize camera: {e}")
                self.camera = None
                self.is_initialized = False
                return False
    
    def start_streaming(self):
        """Start camera streaming"""
        if not self.is_initialized:
            logger.error("Camera not initialized")
            return False
            
        with self.lock:
            self.streaming = True
            logger.info("Camera streaming started")
            return True
    
    def stop_streaming(self):
        """Stop camera streaming"""
        with self.lock:
            self.streaming = False
            logger.info("Camera streaming stopped")
    
    def get_frame(self):
        """Get a frame from camera (main stream for detection)"""
        if not self.is_initialized or not self.camera:
            return None
            
        try:
            request = self.camera.capture_request()
            frame = request.make_array("main")
            request.release()
            
            # Log frame info for debugging
            if frame is not None:
                logger.debug(f"Main frame shape: {frame.shape}, dtype: {frame.dtype}")
            
            return frame
        except Exception as e:
            logger.error(f"Error capturing main frame: {e}")
            return None
    
    def get_lores_frame(self):
        """Get a lores frame from camera (for video feed display)"""
        if not self.is_initialized or not self.camera:
            return None
            
        try:
            request = self.camera.capture_request()
            frame = request.make_array("lores")
            request.release()
            
            # Log frame info for debugging
            if frame is not None:
                logger.debug(f"Lores frame shape: {frame.shape}, dtype: {frame.dtype}")
            
            return frame
        except Exception as e:
            logger.error(f"Error capturing lores frame: {e}")
            return None
    
    def close(self):
        """Close camera"""
        with self.lock:
            if self.camera:
                try:
                    if hasattr(self.camera, 'started') and self.camera.started:
                        self.camera.stop()
                    self.camera.close()
                except Exception as e:
                    logger.error(f"Error closing camera: {e}")
                finally:
                    self.camera = None
                    self.is_initialized = False
                    self.streaming = False
    
    def update_settings(self, **settings):
        """Update camera settings"""
        if not self.is_initialized or not self.camera:
            logger.error("Cannot update settings - camera not initialized")
            return False
        
        try:
            with self.lock:
                # Convert settings to camera controls
                controls = {}
                
                if 'brightness' in settings:
                    controls['Brightness'] = settings['brightness']
                
                if 'contrast' in settings:
                    controls['Contrast'] = settings['contrast']
                
                if 'saturation' in settings:
                    controls['Saturation'] = settings['saturation']
                
                if 'sharpness' in settings:
                    controls['Sharpness'] = settings['sharpness']
                
                if 'awb_mode' in settings:
                    controls['AwbMode'] = settings['awb_mode']
                
                if 'focus' in settings:
                    controls['LensPosition'] = settings['focus']
                
                # Apply controls
                if controls:
                    self.camera.set_controls(controls)
                    logger.info(f"Updated camera settings: {controls}")
                    
                    # Store current values in memory
                    if 'brightness' in settings:
                        self._current_brightness = settings['brightness']
                    if 'contrast' in settings:
                        self._current_contrast = settings['contrast']
                    if 'saturation' in settings:
                        self._current_saturation = settings['saturation']
                    if 'sharpness' in settings:
                        self._current_sharpness = settings['sharpness']
                    if 'awb_mode' in settings:
                        self._current_awb_mode = settings['awb_mode']
                    if 'focus' in settings:
                        self._current_focus = settings['focus']
                
                return True
                
        except Exception as e:
            logger.error(f"Error updating camera settings: {e}")
            return False
    
    def get_current_settings(self):
        """Get current camera settings"""
        if not self.is_initialized or not self.camera:
            return {}
        
        try:
            with self.lock:
                # Store current settings in memory since we can't read them back from camera
                # This is a limitation of Picamera2 - we can't read back the current values
                # So we'll return the default values or stored values
                settings = {
                    'brightness': getattr(self, '_current_brightness', 0.0),
                    'contrast': getattr(self, '_current_contrast', 1.0),
                    'saturation': getattr(self, '_current_saturation', 1.0),
                    'sharpness': getattr(self, '_current_sharpness', 1.0),
                    'awb_mode': getattr(self, '_current_awb_mode', 0),
                    'focus': getattr(self, '_current_focus', 0.0)
                }
                
                return settings
                
        except Exception as e:
            logger.error(f"Error getting camera settings: {e}")
            return {}

# Global camera manager
camera_manager = CameraManager()

# Global health monitor
health_monitor = get_health_monitor(camera_manager)

# Global detection thread
detection_thread = None

# Global shutdown flag
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True
    shutdown()
    sys.exit(0)

def stream_worker():
    """Worker thread for streaming frames"""
    global streaming_active
    
    logger.info("Stream worker started")
    
    while streaming_active:
        try:
            if camera_manager.is_initialized and camera_manager.streaming:
                frame = camera_manager.get_frame()
                if frame is not None:
                    # Put frame in queue (non-blocking)
                    try:
                        frames_queue.put_nowait(frame)
                        logger.debug(f"Frame added to queue, size: {frames_queue.qsize()}")
                    except queue.Full:
                        # Remove old frame and add new one
                        try:
                            frames_queue.get_nowait()
                            frames_queue.put_nowait(frame)
                            logger.debug("Replaced old frame in queue")
                        except queue.Empty:
                            pass
                else:
                    logger.warning("Received None frame from camera")
            else:
                logger.debug("Camera not ready for streaming")
            time.sleep(0.033)  # ~30 FPS
        except Exception as e:
            logger.error(f"Error in stream worker: {e}")
            time.sleep(1)
    
    logger.info("Stream worker stopped")

def start_camera_streaming():
    """Start camera streaming in background thread"""
    global streaming_active, stream_thread
    
    if not camera_manager.is_initialized:
        logger.error("Cannot start streaming - camera not initialized")
        return False
    
    if streaming_active:
        logger.info("Streaming already active")
        return True
    
    # Start camera streaming
    if not camera_manager.start_streaming():
        logger.error("Failed to start camera streaming")
        return False
    
    # Start background streaming thread
    streaming_active = True
    stream_thread = threading.Thread(target=stream_worker, daemon=True)
    stream_thread.start()
    
    logger.info("Camera streaming started in background")
    return True

def stop_camera_streaming():
    """Stop camera streaming"""
    global streaming_active
    
    streaming_active = False
    if stream_thread and stream_thread.is_alive():
        stream_thread.join(timeout=5)
    
    camera_manager.stop_streaming()
    logger.info("Camera streaming stopped")

# Flask Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/test')
def test_page():
    """Test page for debugging health status"""
    return render_template('test_health_js.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming endpoint"""
    def generate_frames():
        """Generate video frames using lores stream (display only)"""
        video_feed_res = get_video_feed_resolution()
        while True:
            try:
                # Get lores frame for video feed (display only)
                frame = camera_manager.get_lores_frame() if camera_manager else None
                if frame is not None:
                    # Log frame info for debugging
                    logger.debug(f"Video feed frame shape: {frame.shape}, dtype: {frame.dtype}")
                    
                    # Ensure frame is in RGB format for normal viewing
                    if len(frame.shape) == 3:
                        if frame.shape[2] == 4:  # BGRA
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                        elif frame.shape[2] == 3:  # BGR
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for normal viewing
                        # If already RGB, use as is
                    elif len(frame.shape) == 2:  # Grayscale
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)  # Convert to RGB
                    
                    # Encode frame as JPEG with quality 80
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    else:
                        logger.warning("Failed to encode frame")
                else:
                    # Send a blank frame if no frame available
                    blank_frame = np.zeros((video_feed_res[1], video_feed_res[0], 3), dtype=np.uint8)
                    ret, buffer = cv2.imencode('.jpg', blank_frame)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    
            except Exception as e:
                logger.error(f"Error in video feed: {e}")
                # Send blank frame instead of sleeping
                blank_frame = np.zeros((640, 640, 3), dtype=np.uint8)
                ret, buffer = cv2.imencode('.jpg', blank_frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera_status')
def api_camera_status():
    """API endpoint for camera status"""
    # Check if camera is actually initialized in this process
    try:
        initialized = camera_manager.is_initialized and camera_manager.camera is not None
        streaming = camera_manager.streaming and initialized
        
        # Try to get a frame to verify camera is working
        if initialized:
            try:
                test_frame = camera_manager.get_lores_frame()
                camera_working = test_frame is not None
            except:
                camera_working = False
        else:
            camera_working = False
            
        return jsonify({
            'initialized': initialized,
            'streaming': streaming,
            'camera_working': camera_working,
            'queue_size': frames_queue.qsize()
        })
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return jsonify({
            'initialized': False,
            'streaming': False,
            'camera_working': False,
            'queue_size': 0,
            'error': str(e)
        })

@app.route('/api/start_camera', methods=['POST'])
def api_start_camera():
    """API endpoint to start camera"""
    try:
        if not camera_manager.is_initialized:
            # Initialize camera with default settings
            settings = get_default_settings()
            
            if not camera_manager.initialize_camera(**settings):
                return jsonify({'status': 'error', 'message': 'Failed to initialize camera'})
        
        # Start streaming automatically after initialization
        if start_camera_streaming():
            return jsonify({'status': 'success', 'message': 'Camera started and streaming successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to start camera streaming'})
            
    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_camera', methods=['POST'])
def api_stop_camera():
    """API endpoint to stop camera"""
    try:
        stop_camera_streaming()
        return jsonify({'status': 'success', 'message': 'Camera stopped successfully'})
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/close_camera', methods=['POST'])
def api_close_camera():
    """API endpoint to close camera completely"""
    try:
        stop_camera_streaming()
        camera_manager.close()
        return jsonify({'status': 'success', 'message': 'Camera closed successfully'})
    except Exception as e:
        logger.error(f"Error closing camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/update_camera_settings', methods=['POST'])
def api_update_camera_settings():
    """API endpoint to update camera settings"""
    try:
        if not camera_manager.is_initialized:
            return jsonify({'status': 'error', 'message': 'Camera not initialized'})
        
        # Get settings from request
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No settings provided'})
        
        # Validate and apply settings
        settings = {}
        
        # Brightness control (-1.0 to 1.0)
        if 'brightness' in data:
            brightness = float(data['brightness'])
            if -1.0 <= brightness <= 1.0:
                settings['brightness'] = brightness
            else:
                return jsonify({'status': 'error', 'message': 'Brightness must be between -1.0 and 1.0'})
        
        # Contrast control (0.0 to 2.0)
        if 'contrast' in data:
            contrast = float(data['contrast'])
            if 0.0 <= contrast <= 2.0:
                settings['contrast'] = contrast
            else:
                return jsonify({'status': 'error', 'message': 'Contrast must be between 0.0 and 2.0'})
        
        # Saturation control (0.0 to 2.0)
        if 'saturation' in data:
            saturation = float(data['saturation'])
            if 0.0 <= saturation <= 2.0:
                settings['saturation'] = saturation
            else:
                return jsonify({'status': 'error', 'message': 'Saturation must be between 0.0 and 2.0'})
        
        # Sharpness control (0.0 to 4.0)
        if 'sharpness' in data:
            sharpness = float(data['sharpness'])
            if 0.0 <= sharpness <= 4.0:
                settings['sharpness'] = sharpness
            else:
                return jsonify({'status': 'error', 'message': 'Sharpness must be between 0.0 and 4.0'})
        
        # AWB Mode control (0-8)
        if 'awb_mode' in data:
            awb_mode = int(data['awb_mode'])
            if 0 <= awb_mode <= 8:
                settings['awb_mode'] = awb_mode
            else:
                return jsonify({'status': 'error', 'message': 'AWB Mode must be between 0 and 8'})
        
        # Focus control (0.0 to 1.0)
        if 'focus' in data:
            focus = float(data['focus'])
            if 0.0 <= focus <= 1.0:
                settings['focus'] = focus
            else:
                return jsonify({'status': 'error', 'message': 'Focus must be between 0.0 and 1.0'})
        
        # Apply settings to camera
        if settings:
            success = camera_manager.update_settings(**settings)
            if success:
                return jsonify({
                    'status': 'success', 
                    'message': 'Camera settings updated successfully',
                    'settings': settings
                })
            else:
                return jsonify({'status': 'error', 'message': 'Failed to apply camera settings'})
        else:
            return jsonify({'status': 'error', 'message': 'No valid settings provided'})
            
    except Exception as e:
        logger.error(f"Error updating camera settings: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/get_camera_settings', methods=['GET'])
def api_get_camera_settings():
    """API endpoint to get current camera settings"""
    try:
        if not camera_manager.is_initialized:
            return jsonify({'status': 'error', 'message': 'Camera not initialized'})
        
        settings = camera_manager.get_current_settings()
        return jsonify({
            'status': 'success',
            'settings': settings
        })
    except Exception as e:
        logger.error(f"Error getting camera settings: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/health_check', methods=['POST'])
def api_run_health_check():
    """API endpoint to run health check manually"""
    try:
        results = health_monitor.run_all_checks()
        return jsonify({
            'status': 'success',
            'message': 'Health check completed',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error running health check: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/health_status', methods=['GET'])
def api_get_health_status():
    """API endpoint to get latest health check results"""
    try:
        latest_checks = health_monitor.get_latest_health_checks(10)
        return jsonify({
            'status': 'success',
            'health_checks': latest_checks
        })
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/health_data')
def api_get_health_data():
    """API endpoint to get health data with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        component = request.args.get('component', '')
        status_filter = request.args.get('status', '')
        
        # Get health data from database
        data = db_manager.get_health_data_paginated(
            page=page,
            per_page=per_page,
            component=component,
            status_filter=status_filter
        )
        
        return jsonify({
            'status': 'success',
            'data': data['results'],
            'total': data['total'],
            'page': page,
            'per_page': per_page,
            'total_pages': data['total_pages']
        })
    except Exception as e:
        logger.error(f"Error getting health data: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/start_health_monitoring', methods=['POST'])
def api_start_health_monitoring():
    """API endpoint to start health monitoring"""
    try:
        health_monitor.start_monitoring()
        return jsonify({
            'status': 'success',
            'message': 'Health monitoring started'
        })
    except Exception as e:
        logger.error(f"Error starting health monitoring: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_health_monitoring', methods=['POST'])
def api_stop_health_monitoring():
    """API endpoint to stop health monitoring"""
    try:
        health_monitor.stop_monitoring()
        return jsonify({
            'status': 'success',
            'message': 'Health monitoring stopped'
        })
    except Exception as e:
        logger.error(f"Error stopping health monitoring: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/health_monitor_status', methods=['GET'])
def api_get_health_monitor_status():
    """API endpoint to get health monitor status"""
    try:
        is_running = health_monitor.is_monitoring()
        return jsonify({
            'status': 'success',
            'monitoring_active': is_running,
            'message': 'Health monitoring is running' if is_running else 'Health monitoring is stopped'
        })
    except Exception as e:
        logger.error(f"Error getting health monitor status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/start_detection', methods=['POST'])
def api_start_detection():
    """API endpoint to start detection thread"""
    global detection_thread
    try:
        if detection_thread and detection_thread.is_alive():
            return jsonify({
                'status': 'warning',
                'message': 'Detection thread is already running'
            })
        
        # Check if camera is working by trying to get a frame
        try:
            test_frame = camera_manager.get_frame()
            if test_frame is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Camera is not working properly - cannot get frames'
                })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Camera is not working properly: {str(e)}'
            })
        
        # Create and start detection thread
        detection_thread = DetectionThread(camera_manager, frames_queue, db_manager)
        detection_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Detection thread started successfully'
        })
    except Exception as e:
        logger.error(f"Error starting detection thread: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_detection', methods=['POST'])
def api_stop_detection():
    """API endpoint to stop detection thread"""
    global detection_thread
    try:
        if detection_thread and detection_thread.is_alive():
            detection_thread.stop()
            detection_thread.join(timeout=5)
            detection_thread = None
            return jsonify({
                'status': 'success',
                'message': 'Detection thread stopped successfully'
            })
        else:
            return jsonify({
                'status': 'warning',
                'message': 'Detection thread is not running'
            })
    except Exception as e:
        logger.error(f"Error stopping detection thread: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/detection_status', methods=['GET'])
def api_get_detection_status():
    """API endpoint to get detection thread status"""
    global detection_thread
    try:
        is_running = detection_thread is not None and detection_thread.is_alive()
        processing_count = detection_thread.detection_count if detection_thread else 0
        
        # Get actual detection results count from database
        try:
            stats = db_manager.get_detection_statistics()
            detection_results_count = stats.get('total_detections', 0)
        except Exception as e:
            logger.warning(f"Could not get detection statistics: {e}")
            detection_results_count = 0
        
        return jsonify({
            'status': 'success',
            'detection_active': is_running,
            'processing_count': processing_count,
            'detection_results_count': detection_results_count,
            'message': 'Detection is running' if is_running else 'Detection is stopped'
        })
    except Exception as e:
        logger.error(f"Error getting detection status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/detection')
def detection_page():
    """Detection results page with table view"""
    return render_template('detection.html')

@app.route('/health')
def health_page():
    """Health monitoring page with table view"""
    return render_template('health.html')

@app.route('/websocket')
def websocket_page():
    """WebSocket sender management page"""
    return render_template('websocket.html')

@app.route('/api/detection_data')
def api_get_detection_data():
    """API endpoint to get detection data with pagination, sorting, and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        search = request.args.get('search', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Get data from database
        data = db_manager.get_detection_data_paginated(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            date_from=date_from,
            date_to=date_to
        )
        
        return jsonify({
            'status': 'success',
            'data': data['results'],
            'total': data['total'],
            'page': page,
            'per_page': per_page,
            'total_pages': data['total_pages']
        })
    except Exception as e:
        logger.error(f"Error getting detection data: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/detection_stats')
def api_get_detection_stats():
    """API endpoint to get detection statistics"""
    try:
        stats = db_manager.get_detection_statistics()
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting detection stats: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/detection/<int:detection_id>')
def detection_detail(detection_id):
    """Display detection detail page"""
    try:
        detection = db_manager.get_detection_by_id(detection_id)
        return render_template('detection_detail.html', detection=detection)
    except Exception as e:
        logger.error(f"Error getting detection detail: {e}")
        return render_template('detection_detail.html', detection=None)

@app.route('/download/<filename>')
def download_image(filename):
    """Download image file"""
    try:
        # Security: ensure filename is safe
        if '..' in filename or '/' in filename:
            return "Invalid filename", 400
        
        # Import IMAGE_SAVE_DIR from config
        from config import IMAGE_SAVE_DIR
        
        # Try different possible paths
        possible_paths = [
            os.path.join(IMAGE_SAVE_DIR, filename),
            os.path.join('captured_images', filename),
            os.path.join('static/images', filename),
            filename  # If it's already a full path
        ]
        
        for image_path in possible_paths:
            if os.path.exists(image_path):
                return send_file(image_path, as_attachment=True)
        
        logger.warning(f"Image file not found: {filename}")
        logger.warning(f"Searched paths: {possible_paths}")
        return "File not found", 404
        
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return "Error downloading file", 500

@app.route('/api/export_detection_data')
def api_export_detection_data():
    """API endpoint to export detection data as CSV"""
    try:
        from flask import send_file
        import csv
        import io
        from datetime import datetime
        
        # Get query parameters
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        search = request.args.get('search', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Get all data (no pagination for export)
        data = db_manager.get_detection_data_paginated(
            page=1,
            per_page=10000,  # Large number to get all data
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            date_from=date_from,
            date_to=date_to
        )
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'License Plate', 'Confidence (%)', 'Timestamp', 
            'Exposure Time', 'Analog Gain', 'Brightness (Lux)', 
            'Image Filename', 'Processed Image Filename'
        ])
        
        # Write data
        for item in data['results']:
            writer.writerow([
                item['id'],
                item['license_plate_text'] or 'N/A',
                item['lp_confidence'] or 0,
                item['timestamp'] or 'N/A',
                item['exposure_time'] or 'N/A',
                item['analog_gain'] or 'N/A',
                item['lux'] or 'N/A',
                item['lp_image_filename'] or 'N/A',
                item['processed_image_filename'] or 'N/A'
            ])
        
        # Prepare response
        output.seek(0)
        csv_data = output.getvalue()
        
        # Create response
        response = app.response_class(
            response=csv_data,
            status=200,
            mimetype='text/csv'
        )
        response.headers['Content-Disposition'] = f'attachment; filename=detection_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting detection data: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

# WebSocket Sender API Endpoints

@app.route('/api/websocket_status', methods=['GET'])
def api_get_websocket_status():
    """API endpoint to get WebSocket sender status"""
    try:
        status = websocket_manager.get_status()
        is_running = websocket_manager.is_running()
        
        return jsonify({
            'status': 'success',
            'websocket_running': is_running,
            'details': status,
            'message': 'WebSocket sender is running' if is_running else 'WebSocket sender is stopped'
        })
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/start_websocket_sender', methods=['POST'])
def api_start_websocket_sender():
    """API endpoint to start WebSocket sender"""
    try:
        if websocket_manager.is_running():
            return jsonify({
                'status': 'warning',
                'message': 'WebSocket sender is already running'
            })
        
        success = websocket_manager.start_sender()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'WebSocket sender started successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to start WebSocket sender'
            })
    except Exception as e:
        logger.error(f"Error starting WebSocket sender: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_websocket_sender', methods=['POST'])
def api_stop_websocket_sender():
    """API endpoint to stop WebSocket sender"""
    try:
        if not websocket_manager.is_running():
            return jsonify({
                'status': 'warning',
                'message': 'WebSocket sender is not running'
            })
        
        success = websocket_manager.stop_sender()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'WebSocket sender stopped successfully'
            })
        else:
            return jsonify({
                'status': 'error',  
                'message': 'Failed to stop WebSocket sender'
            })
    except Exception as e:
        logger.error(f"Error stopping WebSocket sender: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/restart_websocket_sender', methods=['POST'])
def api_restart_websocket_sender():
    """API endpoint to restart WebSocket sender"""
    try:
        success = websocket_manager.restart_sender()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'WebSocket sender restarted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to restart WebSocket sender'
            })
    except Exception as e:
        logger.error(f"Error restarting WebSocket sender: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/websocket_unsent_data', methods=['GET'])
def api_get_websocket_unsent_data():
    """API endpoint to get count of unsent data"""
    try:
        import sqlite3
        from config import DATABASE_PATH
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Count unsent detection records
        cursor.execute("SELECT COUNT(*) FROM detection_results WHERE sent_to_server = 0")
        unsent_detections = cursor.fetchone()[0]
        
        # Count unsent health records
        cursor.execute("SELECT COUNT(*) FROM health_checks WHERE sent_to_server = 0")
        unsent_health = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'unsent_detections': unsent_detections,
            'unsent_health': unsent_health,
            'total_unsent': unsent_detections + unsent_health
        })
    except Exception as e:
        logger.error(f"Error getting unsent data count: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def startup():
    """Startup function with automatic camera and detection initialization"""
    logger.info("Starting AI camera application with automatic camera and detection...")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize database first
    try:
        # Database is automatically initialized when DatabaseManager is created
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    
    # Start health monitoring (without camera dependency)
    try:
        logger.info("Starting health monitoring...")
        health_monitor.start_monitoring()
        logger.info("✅ Health monitoring started")
        
        # Verify health monitor is running (with retry)
        max_retries = 3
        for attempt in range(max_retries):
            if health_monitor.is_monitoring():
                logger.info("✅ Health monitor verification successful")
                break
            else:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Health monitor verification attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                else:
                    logger.warning("⚠️ Health monitor may not be running properly, but continuing...")
            
    except Exception as e:
        logger.error(f"Health monitoring startup failed: {e}")
        # Don't fail startup if health monitoring fails
    
    # Run basic health check (without camera dependency)
    try:
        logger.info("Running basic health check...")
        health_results = health_monitor.run_all_checks()
        passed_checks = sum(1 for result in health_results.values() if result)
        total_checks = len(health_results)
        logger.info(f"Health check results: {passed_checks}/{total_checks} components passed")
        
        # Check non-camera critical components
        critical_components = ['database', 'detection_models']
        critical_failed = [comp for comp in critical_components if not health_results.get(comp, False)]
        
        if critical_failed:
            logger.error(f"❌ Critical components failed: {critical_failed}")
            return False
        else:
            logger.info("✅ All critical components are healthy")
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
    
    # Start WebSocket sender
    try:
        logger.info("Starting WebSocket sender...")
        success = websocket_manager.start_sender()
        if success:
            logger.info("✅ WebSocket sender started successfully")
        else:
            logger.error("❌ Failed to start WebSocket sender")
            # Don't fail startup if WebSocket sender fails
    except Exception as e:
        logger.error(f"WebSocket sender startup failed: {e}")
        # Don't fail startup if WebSocket sender fails
    
    # Automatically start camera and detection after a longer delay to avoid memory issues
    try:
        logger.info("Starting automatic camera and detection initialization...")
        # Use a separate thread to avoid blocking startup
        import threading
        def auto_start_camera_detection():
            time.sleep(10)  # Wait longer for Flask to be fully ready and memory to stabilize
            try:
                logger.info("=== AUTO-START: Initializing camera ===")
                default_settings = get_default_settings()
                
                if camera_manager.initialize_camera(**default_settings):
                    logger.info("✅ Camera initialized automatically")
                    
                    # Start camera streaming
                    if start_camera_streaming():
                        logger.info("✅ Camera streaming started automatically")
                        
                        # Start detection after camera is ready
                        time.sleep(3)
                        logger.info("=== AUTO-START: Starting detection ===")
                        global detection_thread
                        
                        if not (detection_thread and detection_thread.is_alive()):
                            detection_thread = DetectionThread(camera_manager, frames_queue, db_manager)
                            detection_thread.start()
                            logger.info("✅ Detection started automatically")
                        else:
                            logger.info("✅ Detection already running")
                    else:
                        logger.error("❌ Failed to start camera streaming automatically")
                else:
                    logger.error("❌ Failed to initialize camera automatically")
            except Exception as e:
                logger.error(f"❌ Auto-start camera/detection failed: {e}")
        
        # Start auto-initialization in background
        auto_thread = threading.Thread(target=auto_start_camera_detection, daemon=True)
        auto_thread.start()
        logger.info("🔄 Auto-start thread launched - camera and detection will start in 10 seconds")
        
    except Exception as e:
        logger.error(f"Failed to launch auto-start thread: {e}")
    
    logger.info("🎉 Application startup complete - Auto-start enabled:")
    logger.info("   1. ✅ Database initialized")
    logger.info("   2. ✅ Camera initialization and streaming")
    logger.info("   3. ✅ Detection active")   
    logger.info("   4. ✅ Health monitoring active")
    logger.info("   5. ✅ WebSocket sender active")

    return True

def shutdown():
    """Cleanup on shutdown with proper resource release"""
    logger.info("🛑 Starting application shutdown sequence...") 
    
    # STEP 1: Stop detection thread first (most resource intensive)
    global detection_thread
    if detection_thread and detection_thread.is_alive():
        try:
            logger.info("=== STEP 1: Stopping detection thread ===")
            detection_thread.stop()
            detection_thread.join(timeout=10)
            logger.info("✅ Detection thread stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping detection thread: {e}")
    
    # STEP 2: Stop camera streaming and release camera resources
    try:
        logger.info("=== STEP 2: Stopping camera streaming and releasing resources ===")
        stop_camera_streaming()
        if camera_manager:
            camera_manager.close()
        logger.info("✅ Camera stopped and resources released")
    except Exception as e:
        logger.error(f"❌ Error stopping camera: {e}")
    
    # STEP 3: Stop health monitoring
    try:
        logger.info("=== STEP 3: Stopping health monitoring ===")
        health_monitor.stop_monitoring()
        logger.info("✅ Health monitoring stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping health monitoring: {e}")
    
    # STEP 4: Stop WebSocket sender
    try:
        logger.info("=== STEP 4: Stopping WebSocket sender ===")
        websocket_manager.stop_sender()
        logger.info("✅ WebSocket sender stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping WebSocket sender: {e}")
    
    # STEP 5: Clear queues and release memory
    try:
        logger.info("=== STEP 5: Clearing queues and releasing memory ===")
        # Clear frames queue
        while not frames_queue.empty():
            try:
                frames_queue.get_nowait()
            except:
                break
        
        # Clear metadata queue
        while not metadata_queue.empty():
            try:
                metadata_queue.get_nowait()
            except:
                break
        
        logger.info("✅ Queues cleared and memory released")
    except Exception as e:
        logger.error(f"❌ Error clearing queues: {e}")
    
    # STEP 6: Force garbage collection
    try:
        logger.info("=== STEP 6: Force garbage collection ===")
        import gc
        gc.collect()
        logger.info("✅ Garbage collection completed")
    except Exception as e:
        logger.error(f"❌ Error during garbage collection: {e}")
    
    logger.info("🎉 Application shutdown complete - All resources released")

def check_port_availability(host, port):
    """Check if port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def find_available_port(host, start_port):
    """Find an available port starting from start_port"""
    port = start_port
    while port < start_port + 100:  # Try up to 100 ports
        if check_port_availability(host, port):
            return port
        port += 1
    return None

if __name__ == '__main__':
    if startup():
        try:
            # Check if default port is available
            if not check_port_availability(FLASK_HOST, FLASK_PORT):
                logger.warning(f"Port {FLASK_PORT} is already in use")
                available_port = find_available_port(FLASK_HOST, FLASK_PORT + 1)
                if available_port:
                    logger.info(f"Using alternative port: {available_port}")
                    actual_port = available_port
                else:
                    logger.error("No available ports found")
                    shutdown()
                    sys.exit(1)
            else:
                actual_port = FLASK_PORT
            
            logger.info(f"Starting Flask server on {FLASK_HOST}:{actual_port}")
            app.run(host=FLASK_HOST, port=actual_port, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Flask server failed to start: {e}")
            # Keep health monitor running even if Flask fails
            logger.info("Keeping health monitor running despite Flask server failure")
            try:
                # Keep the main thread alive to allow health monitor to continue
                while not shutdown_requested:
                    time.sleep(10)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
        finally:
            shutdown()
    else:
        logger.error("Failed to start application") 