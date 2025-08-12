"""
WebSocket Service for LPR Data Communication

This service handles WebSocket connections and data communication with edge AI cameras,
including LPR data processing, camera registration, and health monitoring.
"""

import json
import base64
import os
import logging
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
        logger.info("WebSocket service initialized")
    
    def _register_events(self):
        """Register WebSocket event handlers."""
        if not self.socketio:
            logger.error("SocketIO instance not available")
            return
        
        # Register event handlers
        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)
        self.socketio.on_event(WS_EVENT_CAMERA_REGISTER, self.handle_camera_register)
        self.socketio.on_event(WS_EVENT_LPR_DATA, self.handle_lpr_data)
        self.socketio.on_event('join_dashboard', self.handle_join_dashboard)
        
        # Health monitoring events
        self.socketio.on_event('join_health_room', self.handle_join_health_room)
        self.socketio.on_event('leave_health_room', self.handle_leave_health_room)
        self.socketio.on_event('request_health_check', self.handle_request_health_check)
        
        logger.info("WebSocket events registered")
    
    def handle_connect(self, sid=None, environ=None):
        """Handle client connection."""
        logger.info(f"Client connected: {sid}")
        emit(WS_EVENT_STATUS, {'message': 'Connected to LPR Server'})
    
    def handle_disconnect(self, sid=None):
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {sid}")
        if sid and sid in self.connected_cameras:
            camera_id = self.connected_cameras[sid]
            del self.connected_cameras[sid]
            logger.info(f"Camera {camera_id} disconnected")
    
    def handle_camera_register(self, sid, data):
        """Handle camera registration."""
        try:
            camera_id = data.get('camera_id')
            if camera_id:
                self.connected_cameras[sid] = camera_id
                join_room(camera_id)
                
                # Update camera status in database
                self._update_camera_status(camera_id, 'active')
                
                logger.info(f"Camera {camera_id} registered with SID {sid}")
                emit(WS_EVENT_STATUS, {'message': f'Camera {camera_id} registered successfully'})
            else:
                emit(WS_EVENT_ERROR, {'message': 'Camera ID is required'})
        except Exception as e:
            logger.error(f"Camera registration error: {str(e)}")
            emit(WS_EVENT_ERROR, {'message': f'Registration failed: {str(e)}'})
    
    def handle_lpr_data(self, sid, data):
        """Handle LPR data from camera."""
        try:
            camera_id = data.get('camera_id')
            plate_number = data.get('plate_number')
            confidence = data.get('confidence', 0.0)
            image_data = data.get('image_data')
            location = data.get('location', '')
            
            if not camera_id or not plate_number:
                emit(WS_EVENT_ERROR, {'message': 'Camera ID and plate number are required'})
                return
            
            # Save image if provided
            image_path = None
            if image_data:
                image_path = self._save_image(image_data, camera_id, plate_number)
            
            # Create database record
            record = LPRRecord(
                camera_id=camera_id,
                plate_number=plate_number,
                confidence=confidence,
                image_path=image_path,
                location=location,
                location_lat=data.get('location_lat'),
                location_lon=data.get('location_lon')
            )
            
            self.db_session.add(record)
            self.db_session.commit()
            
            # Check for blacklist
            blacklist_service = get_service('blacklist_service')
            blacklist_service.process_lpr_detection(record)
            
            # Emit success response
            emit('lpr_response', {
                'status': 'success',
                'record_id': record.id,
                'message': 'LPR data saved successfully'
            })
            
            # Broadcast to all connected clients
            self.socketio.emit('new_lpr_record', record.to_dict(), room='dashboard')
            
            logger.info(f"LPR data saved: {plate_number} from {camera_id}")
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error saving LPR data: {str(e)}")
            emit(WS_EVENT_ERROR, {'message': f'Error saving data: {str(e)}'})
    
    def handle_join_dashboard(self):
        """Handle dashboard room join request."""
        join_room('dashboard')
        emit(WS_EVENT_STATUS, {'message': 'Joined dashboard room'})
    
    def handle_join_health_room(self, data):
        """Handle health monitoring room join request."""
        room = 'health_monitoring'
        join_room(room)
        emit(WS_EVENT_STATUS, {'message': 'Joined health monitoring room'}, room=room)
    
    def handle_leave_health_room(self, data):
        """Handle health monitoring room leave request."""
        room = 'health_monitoring'
        leave_room(room)
        emit(WS_EVENT_STATUS, {'message': 'Left health monitoring room'}, room=room)
    
    def handle_request_health_check(self, data):
        """Handle immediate health check request via WebSocket."""
        try:
            health_service = get_service('health_service')
            results = health_service.perform_health_check()
            emit('health_check_result', results)
        except Exception as e:
            logger.error(f"Health check request failed: {str(e)}")
            emit('health_check_error', {'error': str(e)})
    
    def _save_image(self, image_data, camera_id, plate_number):
        """
        Save image data to storage.
        
        Args:
            image_data: Base64 encoded image data
            camera_id: Camera identifier
            plate_number: License plate number
            
        Returns:
            Path to saved image file
        """
        try:
            # Create image directory if not exists
            image_dir = os.path.join(Config.IMAGE_STORAGE_PATH, camera_id)
            os.makedirs(image_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{plate_number}_{timestamp}.jpg"
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
    
    def _update_camera_status(self, camera_id, status):
        """
        Update camera status in database.
        
        Args:
            camera_id: Camera identifier
            status: Camera status
        """
        try:
            camera = self.db_session.query(Camera).filter_by(camera_id=camera_id).first()
            if camera:
                camera.status = status
                camera.last_activity = datetime.utcnow()
            else:
                # Create new camera record
                camera = Camera(
                    camera_id=camera_id,
                    name=f"Camera {camera_id}",
                    status=status,
                    last_activity=datetime.utcnow()
                )
                self.db_session.add(camera)
            
            self.db_session.commit()
            logger.debug(f"Camera {camera_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating camera status: {str(e)}")
            self.db_session.rollback()

# Global WebSocket service instance
websocket_service = WebSocketService()
