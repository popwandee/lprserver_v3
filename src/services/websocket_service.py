"""
WebSocket Service for LPR Data Communication

This service handles WebSocket connections and data communication with edge AI cameras,
including LPR data processing, camera registration, and health monitoring.
Supports both SocketIO and REST API communication with fallback mechanism.
"""

import json
import base64
import os
import logging
import uuid
from datetime import datetime
from flask import request
from flask_socketio import emit, join_room, leave_room
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from src.app import socketio, db
from core.models.lpr_record import LPRRecord
from core.models.camera import Camera
from core.dependency_container import get_service
from config import Config
from constants import WS_EVENT_CAMERA_REGISTER, WS_EVENT_LPR_DATA, WS_EVENT_STATUS, WS_EVENT_ERROR

logger = logging.getLogger(__name__)

class WebSocketService:
    """
    WebSocket service for handling LPR data from edge cameras.
    
    This service manages:
    - Camera registration and connection tracking
    - LPR data processing and storage
    - Real-time health monitoring
    - Dashboard updates
    - Support for both SocketIO and REST API communication
    """
    
    def __init__(self):
        self.connected_cameras = {}
        self.socketio = None
        self.db_session = None
    
    def initialize(self, socketio_instance, db_session):
        """
        Initialize the WebSocket service with dependencies.
        
        Args:
            socketio_instance: SocketIO instance
            db_session: Database session
        """
        self.socketio = socketio_instance
        self.db_session = db_session
        self._register_events()
        logger.info("WebSocket service initialized with new communication specification")
    
    def _register_events(self):
        """Register WebSocket event handlers."""
        if not self.socketio:
            logger.error("SocketIO instance not available")
            return
        
        # Register event handlers for new specification
        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)
        self.socketio.on_event('camera_register', self.handle_camera_register)
        self.socketio.on_event('lpr_data', self.handle_lpr_data)
        self.socketio.on_event('health_status', self.handle_health_status)
        self.socketio.on_event('ping', self.handle_ping)
        
        # Dashboard and monitoring events
        self.socketio.on_event('join_dashboard', self.handle_join_dashboard)
        self.socketio.on_event('join_health_room', self.handle_join_health_room)
        self.socketio.on_event('leave_health_room', self.handle_leave_health_room)
        self.socketio.on_event('request_health_check', self.handle_request_health_check)
        
        logger.info("WebSocket events registered for new communication specification")
    
    def handle_connect(self, sid=None, environ=None):
        """Handle client connection."""
        logger.info(f"Client connected: {sid}")
        emit('connect', {
            'success': True,
            'message': 'Connected to LPR Server',
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_disconnect(self, sid=None):
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {sid}")
        if sid and sid in self.connected_cameras:
            camera_key = self.connected_cameras[sid]
            del self.connected_cameras[sid]
            logger.info(f"Camera {camera_key} disconnected")
    
    def handle_camera_register(self, sid, data):
        """Handle camera registration with new specification."""
        try:
            camera_id = data.get('camera_id')
            checkpoint_id = data.get('checkpoint_id')
            timestamp = data.get('timestamp')
            
            if not camera_id or not checkpoint_id:
                emit('error', {'message': 'camera_id and checkpoint_id are required'})
                return
            
            camera_key = f"{camera_id}_{checkpoint_id}"
            self.connected_cameras[sid] = camera_key
            join_room(camera_key)
            
            # Update camera status in database
            self._update_camera_status(camera_id, checkpoint_id, 'active', timestamp)
            
            logger.info(f"Camera {camera_id} at checkpoint {checkpoint_id} registered with SID {sid}")
            emit('camera_register', {
                'success': True,
                'message': f'Camera {camera_id} registered successfully',
                'camera_id': camera_id,
                'checkpoint_id': checkpoint_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Broadcast to dashboard
            self.socketio.emit('camera_status', {
                'camera_id': camera_id,
                'checkpoint_id': checkpoint_id,
                'status': 'online',
                'timestamp': datetime.now().isoformat()
            }, room='dashboard')
            
        except Exception as e:
            logger.error(f"Camera registration error: {str(e)}")
            emit('error', {'message': f'Registration failed: {str(e)}'})
    
    def handle_lpr_data(self, sid, data):
        """Handle LPR data from camera with new specification."""
        try:
            # Validate required fields
            required_fields = ['type', 'camera_id', 'checkpoint_id', 'timestamp']
            for field in required_fields:
                if field not in data:
                    emit('error', {'message': f'Missing required field: {field}'})
                    return
            
            camera_id = data.get('camera_id')
            checkpoint_id = data.get('checkpoint_id')
            vehicles_count = data.get('vehicles_count', 0)
            plates_count = data.get('plates_count', 0)
            ocr_results = data.get('ocr_results', [])
            vehicle_detections = data.get('vehicle_detections', [])
            plate_detections = data.get('plate_detections', [])
            processing_time_ms = data.get('processing_time_ms', 0)
            annotated_image = data.get('annotated_image', '')
            cropped_plates = data.get('cropped_plates', [])
            
            # Generate detection ID
            detection_id = str(uuid.uuid4())
            
            # Save annotated image if provided
            image_path = None
            if annotated_image:
                image_path = self._save_image(annotated_image, camera_id, checkpoint_id, f"detection_{detection_id}")
            
            # Save cropped plates if provided
            plate_images = []
            for i, plate_image in enumerate(cropped_plates):
                if plate_image:
                    plate_path = self._save_image(plate_image, camera_id, checkpoint_id, f"plate_{detection_id}_{i}")
                    plate_images.append(plate_path)
            
            # Create database record
            record = LPRRecord(
                detection_id=detection_id,
                camera_id=camera_id,
                checkpoint_id=checkpoint_id,
                vehicles_count=vehicles_count,
                plates_count=plates_count,
                ocr_results=ocr_results,
                vehicle_detections=vehicle_detections,
                plate_detections=plate_detections,
                processing_time_ms=processing_time_ms,
                image_path=image_path,
                plate_images=plate_images,
                timestamp=datetime.fromisoformat(data.get('timestamp'))
            )
            
            self.db_session.add(record)
            self.db_session.commit()
            
            # Check for blacklist
            blacklist_service = get_service('blacklist_service')
            blacklist_service.process_lpr_detection(record)
            
            # Emit success response
            emit('lpr_response', {
                'success': True,
                'message': 'LPR data received successfully',
                'detection_id': detection_id,
                'camera_id': camera_id,
                'checkpoint_id': checkpoint_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Broadcast to all connected clients
            self.socketio.emit('new_detection', {
                'detection_id': detection_id,
                'camera_id': camera_id,
                'checkpoint_id': checkpoint_id,
                'vehicles_count': vehicles_count,
                'plates_count': plates_count,
                'ocr_results': ocr_results,
                'timestamp': datetime.now().isoformat()
            }, room='dashboard')
            
            logger.info(f"LPR data saved: {detection_id} from {camera_id} at {checkpoint_id}")
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error saving LPR data: {str(e)}")
            emit('error', {'message': f'Error saving data: {str(e)}'})
    
    def handle_health_status(self, sid, data):
        """Handle health status from camera with new specification."""
        try:
            # Validate required fields
            required_fields = ['type', 'camera_id', 'checkpoint_id', 'timestamp', 'component', 'status']
            for field in required_fields:
                if field not in data:
                    emit('error', {'message': f'Missing required field: {field}'})
                    return
            
            camera_id = data.get('camera_id')
            checkpoint_id = data.get('checkpoint_id')
            component = data.get('component')
            status = data.get('status')
            message = data.get('message', '')
            details = data.get('details', {})
            
            # Generate health ID
            health_id = str(uuid.uuid4())
            
            # Update camera health status in database
            self._update_camera_health(camera_id, checkpoint_id, status, details)
            
            # Emit success response
            emit('health_response', {
                'success': True,
                'message': 'Health status received successfully',
                'health_id': health_id,
                'camera_id': camera_id,
                'checkpoint_id': checkpoint_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Broadcast to health monitoring room
            self.socketio.emit('health_update', {
                'health_id': health_id,
                'camera_id': camera_id,
                'checkpoint_id': checkpoint_id,
                'component': component,
                'status': status,
                'message': message,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }, room='health_monitoring')
            
            logger.info(f"Health status received: {health_id} from {camera_id} at {checkpoint_id}")
            
        except Exception as e:
            logger.error(f"Error processing health status: {str(e)}")
            emit('error', {'message': f'Error processing health data: {str(e)}'})
    
    def handle_ping(self, sid, data):
        """Handle ping for connection testing."""
        try:
            message = data.get('message', 'Hello from AI Camera')
            timestamp = data.get('timestamp', datetime.now().isoformat())
            
            logger.debug(f"Ping received: {message}")
            
            emit('pong', {
                'success': True,
                'message': 'pong',
                'original_message': message,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling ping: {str(e)}")
            emit('error', {'message': str(e)})
    
    def handle_join_dashboard(self):
        """Handle dashboard room join request."""
        join_room('dashboard')
        emit('status', {
            'success': True,
            'message': 'Joined dashboard room',
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_join_health_room(self, data):
        """Handle health monitoring room join request."""
        room = 'health_monitoring'
        join_room(room)
        emit('status', {
            'success': True,
            'message': 'Joined health monitoring room',
            'timestamp': datetime.now().isoformat()
        }, room=room)
    
    def handle_leave_health_room(self, data):
        """Handle health monitoring room leave request."""
        room = 'health_monitoring'
        leave_room(room)
        emit('status', {
            'success': True,
            'message': 'Left health monitoring room',
            'timestamp': datetime.now().isoformat()
        }, room=room)
    
    def handle_request_health_check(self, data):
        """Handle immediate health check request via WebSocket."""
        try:
            health_service = get_service('health_service')
            results = health_service.perform_health_check()
            emit('health_check_result', {
                'success': True,
                'data': results,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check request failed: {str(e)}")
            emit('health_check_error', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def _save_image(self, image_data, camera_id, checkpoint_id, filename_prefix):
        """
        Save image data to storage.
        
        Args:
            image_data: Base64 encoded image data
            camera_id: Camera identifier
            checkpoint_id: Checkpoint identifier
            filename_prefix: Prefix for filename
            
        Returns:
            Path to saved image file
        """
        try:
            # Create image directory if not exists
            image_dir = os.path.join(Config.IMAGE_STORAGE_PATH, camera_id, checkpoint_id)
            os.makedirs(image_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{timestamp}.jpg"
            file_path = os.path.join(image_dir, filename)
            
            # Decode and save image
            image_bytes = base64.b64decode(image_data)
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            logger.debug(f"Image saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return None
    
    def _update_camera_status(self, camera_id, checkpoint_id, status, timestamp=None):
        """
        Update camera status in database.
        
        Args:
            camera_id: Camera identifier
            checkpoint_id: Checkpoint identifier
            status: Camera status
            timestamp: Registration timestamp
        """
        try:
            camera = self.db_session.query(Camera).filter_by(
                camera_id=camera_id,
                checkpoint_id=checkpoint_id
            ).first()
            
            if camera:
                camera.status = status
                camera.last_activity = datetime.utcnow()
            else:
                # Create new camera record
                camera = Camera(
                    camera_id=camera_id,
                    checkpoint_id=checkpoint_id,
                    name=f"Camera {camera_id} at Checkpoint {checkpoint_id}",
                    status=status,
                    registered_at=datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow(),
                    last_activity=datetime.utcnow()
                )
                self.db_session.add(camera)
            
            self.db_session.commit()
            logger.debug(f"Camera {camera_id} at {checkpoint_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating camera status: {str(e)}")
            self.db_session.rollback()
    
    def _update_camera_health(self, camera_id, checkpoint_id, status, details):
        """
        Update camera health status in database.
        
        Args:
            camera_id: Camera identifier
            checkpoint_id: Checkpoint identifier
            status: Health status
            details: Health details
        """
        try:
            camera = self.db_session.query(Camera).filter_by(
                camera_id=camera_id,
                checkpoint_id=checkpoint_id
            ).first()
            
            if camera:
                camera.health_status = status
                camera.health_details = details
                camera.last_activity = datetime.utcnow()
                self.db_session.commit()
                logger.debug(f"Camera {camera_id} at {checkpoint_id} health updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating camera health: {str(e)}")
            self.db_session.rollback()

# Global WebSocket service instance
websocket_service = WebSocketService()
