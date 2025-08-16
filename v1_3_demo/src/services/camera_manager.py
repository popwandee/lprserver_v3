#!/usr/bin/env python3
"""
Camera Manager Service for AI Camera v1.3

This service manages camera operations using CameraHandler component
and provides high-level camera management functionality.

Features:
- Camera initialization and lifecycle management
- Video streaming for web interface
- Frame capture for inference pipeline
- Camera status monitoring and health checks
- Configuration management
- Error handling and recovery
- Auto-start capability

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import logging
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime

from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.components.camera_handler import make_json_serializable
from v1_3.src.core.config import AUTO_START_CAMERA, AUTO_START_STREAMING, STARTUP_DELAY

logger = get_logger(__name__)


class CameraManager:
    """
    Camera Manager Service for high-level camera operations.
    
    This service provides:
    - Camera initialization and startup
    - Video streaming management
    - Configuration management
    - Status monitoring
    - Auto-start functionality (NEW)
    
    Thread-safe: Uses CameraHandler's singleton pattern for safe camera access
    """
    
    def __init__(self, camera_handler, logger=None):
        self.camera_handler = camera_handler
        self.logger = logger or get_logger(__name__)
        self.auto_start_enabled = AUTO_START_CAMERA  # Auto-start from config
        self.auto_streaming_enabled = AUTO_START_STREAMING  # Auto-streaming from config
        self.startup_time = None
        
        # Metadata tracking (NEW) - Event-based only
        self.last_metadata = {}
        self.last_metadata_update = None
        
    def initialize(self):
        """
        Initialize camera manager with auto-start capability.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing Camera Manager...")
            
            # Initialize camera handler
            if self.camera_handler:
                success = self.camera_handler.initialize_camera()
                if success:
                    self.logger.info("Camera handler initialized successfully")
                    
                    # Auto-start camera if enabled
                    if self.auto_start_enabled:
                        self.logger.info("Auto-start enabled - starting camera automatically")
                        return self._auto_start_camera()
                    else:
                        self.logger.info("Auto-start disabled - camera ready for manual start")
                        return True
                else:
                    self.logger.error("Failed to initialize camera handler")
                    return False
            else:
                self.logger.error("Camera handler not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing camera manager: {e}")
            return False
    
    def _auto_start_camera(self):
        """
        Auto-start camera functionality with streaming.
        
        Returns:
            bool: True if auto-start successful, False otherwise
        """
        try:
            self.logger.info("🚀 Starting auto-start sequence...")
            
            # Start camera using existing start method
            if self.start():
                self.logger.info("✅ Camera auto-started successfully")
                self.startup_time = datetime.now()
                
                # Auto-start streaming if enabled
                if self.auto_streaming_enabled:
                    self.logger.info("🎥 Auto-streaming enabled - camera should be streaming now")
                    
                    # Verify streaming status
                    if self.camera_handler and self.camera_handler.streaming:
                        self.logger.info("✅ Camera streaming confirmed active")
                    else:
                        self.logger.warning("⚠️  Camera not streaming after auto-start")
                
                return True
            else:
                self.logger.error("❌ Failed to auto-start camera")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in auto-start: {e}")
            return False
    
    def start(self):
        """
        Start camera streaming.
        
        Returns:
            bool: True if camera started successfully, False otherwise
        """
        try:
            if not self.camera_handler:
                self.logger.error("Camera handler not available")
                return False
            
            success = self.camera_handler.start_camera()
            if success:
                self.logger.info("Camera started successfully")
                if not self.startup_time:
                    self.startup_time = datetime.now()
                
                # Capture initial metadata after camera starts (NEW)
                self._update_metadata()
                
                return True
            else:
                self.logger.error("Failed to start camera")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting camera: {e}")
            return False
    
    def stop(self):
        """
        Stop camera streaming.
        
        Returns:
            bool: True if camera stopped successfully, False otherwise
        """
        try:
            if self.camera_handler:

                
                success = self.camera_handler.stop_camera()
                if success:
                    self.logger.info("Camera stopped successfully")
                else:
                    self.logger.error("Failed to stop camera")
                return success
            else:
                self.logger.error("Camera handler not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping camera: {e}")
            return False
    
    def restart(self):
        """
        Restart camera.
        
        Returns:
            bool: True if camera restarted successfully, False otherwise
        """
        try:
            self.logger.info("Restarting camera...")
            self.stop()
            time.sleep(1)  # Brief pause
            return self.start()
        except Exception as e:
            self.logger.error(f"Error restarting camera: {e}")
            return False
    
    def _update_metadata(self):
        """
        Update camera metadata from camera handler.
        Called after camera starts or configuration changes.
        """
        try:
            if self.camera_handler and self.camera_handler.streaming:
                metadata = self.camera_handler.get_metadata()
                if metadata:
                    self.last_metadata = metadata
                    self.last_metadata_update = datetime.now()
                    self.logger.info("Camera metadata updated successfully")
                else:
                    self.logger.warning("No metadata available from camera")
            else:
                self.logger.debug("Camera not streaming, skipping metadata update")
        except Exception as e:
            self.logger.warning(f"Error updating metadata: {e}")
    

    
    def get_status(self):
        """
        Get comprehensive camera status.
        
        Returns:
            dict: Camera status information including auto-start details
        """
        try:
            if not self.camera_handler:
                return {
                    'initialized': False,
                    'streaming': False,
                    'error': 'Camera handler not available'
                }
            
            # Get camera handler status
            camera_status = self.camera_handler.get_status()
            
            # Add manager-specific status
            status = {
                'initialized': camera_status.get('initialized', False),
                'streaming': camera_status.get('streaming', False),
                'auto_start_enabled': self.auto_start_enabled,  # NEW
                'uptime': None,
                'frame_count': camera_status.get('frame_count', 0),
                'average_fps': camera_status.get('average_fps', 0),
                'config': camera_status.get('configuration', {}),
                'metadata': self.last_metadata,  # Add metadata to status
                'camera_handler': camera_status
            }
            
            # Calculate uptime
            if self.startup_time:
                uptime = (datetime.now() - self.startup_time).total_seconds()
                status['uptime'] = uptime
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting camera status: {e}")
            return {
                'initialized': False,
                'streaming': False,
                'error': str(e)
            }
    
    def health_check(self):
        """
        Perform health check on camera system.
        
        Returns:
            dict: Health status information
        """
        try:
            status = self.get_status()
            
            health = {
                'status': 'healthy' if status.get('initialized', False) else 'unhealthy',
                'camera_initialized': status.get('initialized', False),
                'streaming_active': status.get('streaming', False),
                'auto_start_enabled': status.get('auto_start_enabled', False),  # NEW
                'uptime': status.get('uptime', 0),
                'frame_count': status.get('frame_count', 0),
                'average_fps': status.get('average_fps', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            if not status.get('initialized', False):
                health['status'] = 'unhealthy'
                health['error'] = status.get('error', 'Camera not initialized')
            
            return health
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_available_settings(self):
        """
        Get available camera settings.
        
        Returns:
            dict: Available camera settings
        """
        try:
            if self.camera_handler:
                return self.camera_handler.get_configuration()
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error getting available settings: {e}")
            return {}
    
    def capture_frame(self):
        """
        Capture a single frame from the camera for detection processing.
        
        Returns:
            numpy.ndarray or None: Camera frame as numpy array, None if capture failed
        """
        try:
            if not self.camera_handler or not self.camera_handler.initialized:
                self.logger.warning("Cannot capture frame - camera not initialized")
                return None
           
            # Capture frame from camera handler (returns dict with 'frame' key)
            frame_data = self.camera_handler.capture_frame()
            if frame_data is not None and isinstance(frame_data, dict) and 'frame' in frame_data:
                frame = frame_data['frame']
                if frame is not None:
                    self.logger.debug("Frame captured successfully for detection")
                    return frame  # Return the actual numpy array
                else:
                    self.logger.debug("Frame is None in frame_data")
                    return None
            else:
                self.logger.debug("No frame available from camera or invalid frame_data format")
                return None
                
        except Exception as e:
            self.logger.error(f"Error capturing frame: {e}")
            return None
    
    def get_configuration(self):
        """
        Get current camera configuration.
        
        Returns:
            dict: Current camera configuration
        """
        try:
            if self.camera_handler:
                config = self.camera_handler.get_configuration()
                # Ensure all values are JSON serializable
                return make_json_serializable(config)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error getting configuration: {e}")
            return {}
    
    def update_configuration(self, config: Dict[str, Any]):
        """
        Update camera configuration.
        
        Args:
            config (dict): New configuration settings
            
        Returns:
            dict: Updated configuration
        """
        try:
            if self.camera_handler:
                self.logger.info("Updating camera configuration...")
                success = self.camera_handler.update_configuration(config)
                if success:
                    self.logger.info("Camera configuration updated and restarted successfully")
                    return self.get_configuration()
                else:
                    self.logger.error("Failed to update camera configuration")
                    return self.get_configuration()
            else:
                self.logger.error("Camera handler not available")
                return {}
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return self.get_configuration()
    
    def capture_image(self):
        """
        Capture a single image.
        
        Returns:
            dict: Image capture result with path and metadata
        """
        try:
            if not self.camera_handler:
                self.logger.error("Camera handler not available")
                return None
            
            frame_data = self.camera_handler.capture_frame()
            if frame_data and 'frame' in frame_data:
                # Save image logic here if needed
                return {
                    'success': True,
                    'size': frame_data['frame'].shape if frame_data['frame'] is not None else None,
                    'saved_path': None  # Add path if saving is implemented
                }
            else:
                self.logger.error("Failed to capture image")
                return None
        except Exception as e:
            self.logger.error(f"Error capturing image: {e}")
            return None
    
    def get_frame(self, timeout=0.1):
        """
        Get a single frame with timeout.
        
        Args:
            timeout (float): Timeout in seconds
            
        Returns:
            dict: Frame data or None if timeout
        """
        try:
            if not self.camera_handler:
                return None
            
            frame_data = self.camera_handler.capture_frame()
            return frame_data
        except Exception as e:
            self.logger.error(f"Error getting frame: {e}")
            return None
    
    def cleanup(self):
        """
        Cleanup camera resources.
        """
        try:
            self.logger.info("Cleaning up camera manager...")
            
            if self.camera_handler:
                self.camera_handler.cleanup()
            
            self.logger.info("Camera manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def create_camera_manager(camera_handler=None, logger=None):
    """
    Factory function to create camera manager instance.
    
    Args:
        camera_handler: Camera handler instance
        logger: Logger instance
        
    Returns:
        CameraManager: Camera manager instance
    """
    if camera_handler is None:
        # Try to get camera handler from dependency container
        try:
            from v1_3.src.core.dependency_container import get_service
            camera_handler = get_service('camera_handler')
        except Exception as e:
            logger = logger or get_logger(__name__)
            logger.warning(f"Could not get camera handler from DI container: {e}")
    
    return CameraManager(camera_handler, logger)
