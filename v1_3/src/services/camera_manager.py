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

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import threading
import time
import logging
import queue
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Callable
from pathlib import Path
import json
import cv2
import numpy as np

# Default camera settings
DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_FRAMERATE = 30
DEFAULT_BRIGHTNESS = 0.0
DEFAULT_CONTRAST = 1.0
DEFAULT_SATURATION = 1.0
DEFAULT_SHARPNESS = 1.0
DEFAULT_AWB_MODE = 'auto'
IMAGE_SAVE_DIR = '/tmp/captured_images'

from core.utils.logging_config import get_logger
logger = get_logger(__name__)


class CameraManager:
    """
    Camera Manager Service using CameraHandler component.
    
    This class provides high-level camera management including:
    - Camera initialization and lifecycle management
    - Video streaming for web interface
    - Frame capture for inference pipeline
    - Status monitoring and health checks
    - Configuration management
    
    Attributes:
        camera_handler: CameraHandler instance for low-level operations
        logger: Logger instance
        streaming: Whether camera is currently streaming
        initialized: Whether camera is initialized
        config: Current camera configuration
        stop_event: Event to signal streaming to stop
        streaming_thread: Thread for camera streaming
        frames_queue: Queue for frame data
        metadata_queue: Queue for camera metadata
        frame_callbacks: List of frame processing callbacks
    """
    
    def __init__(self, camera_handler=None, logger=None):
        """
        Initialize CameraManager.
        
        Args:
            camera_handler: CameraHandler instance (optional)
            logger: Logger instance (optional)
        """
        self.camera_handler = camera_handler
        self.logger = logger or logging.getLogger(__name__)
        
        # Camera state
        self.streaming = False
        self.initialized = False
        self.stop_event = threading.Event()
        self.streaming_thread = None
        
        # Queues for frame and metadata
        self.frames_queue = queue.Queue(maxsize=10)
        self.metadata_queue = queue.Queue(maxsize=1)
        
        # Frame processing callbacks
        self.frame_callbacks = []
        
        # Configuration
        self.config = {
            'resolution': DEFAULT_RESOLUTION,
            'framerate': DEFAULT_FRAMERATE,
            'brightness': DEFAULT_BRIGHTNESS,
            'contrast': DEFAULT_CONTRAST,
            'saturation': DEFAULT_SATURATION,
            'sharpness': DEFAULT_SHARPNESS,
            'awb_mode': DEFAULT_AWB_MODE
        }
        
        # Statistics
        self.frame_count = 0
        self.start_time = None
        self.last_frame_time = None
        self.fps_stats = []
        
        self.logger.info("CameraManager initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the camera system.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if self.initialized:
                self.logger.warning("Camera already initialized")
                return True
            
            self.logger.info("Initializing camera system...")
            
            # Initialize camera handler if provided
            if self.camera_handler:
                success = self.camera_handler.initialize_camera()
                if not success:
                    self.logger.error("Failed to initialize camera handler")
                    return False
            else:
                self.logger.warning("No camera handler provided")
            
            self.initialized = True
            self.logger.info("Camera system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize camera system: {e}")
            self.initialized = False
            return False
    
    def start(self) -> bool:
        """
        Start camera streaming.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            if not self.initialized:
                self.logger.error("Camera not initialized")
                return False
            
            if self.streaming:
                self.logger.warning("Camera already streaming")
                return True
            
            self.logger.info("Starting camera streaming...")
            
            # Start camera handler if available
            if self.camera_handler:
                success = self.camera_handler.start_camera()
                if not success:
                    self.logger.error("Failed to start camera handler")
                    return False
            
            # Start streaming thread
            self.stop_event.clear()
            self.streaming_thread = threading.Thread(target=self._streaming_worker, daemon=True)
            self.streaming_thread.start()
            
            self.streaming = True
            self.start_time = time.time()
            self.frame_count = 0
            
            self.logger.info("Camera streaming started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start camera streaming: {e}")
            self.streaming = False
            return False
    
    def stop(self) -> bool:
        """
        Stop camera streaming.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            if not self.streaming:
                self.logger.warning("Camera not streaming")
                return True
            
            self.logger.info("Stopping camera streaming...")
            
            # Signal streaming thread to stop
            self.stop_event.set()
            
            # Wait for streaming thread to finish
            if self.streaming_thread and self.streaming_thread.is_alive():
                self.streaming_thread.join(timeout=5.0)
            
            # Stop camera handler if available
            if self.camera_handler:
                self.camera_handler.stop_camera()
            
            self.streaming = False
            self.streaming_thread = None
            
            self.logger.info("Camera streaming stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop camera streaming: {e}")
            return False
    
    def restart(self) -> bool:
        """
        Restart camera streaming.
        
        Returns:
            bool: True if restart successful, False otherwise
        """
        try:
            self.logger.info("Restarting camera streaming...")
            
            # Stop current streaming
            self.stop()
            
            # Wait a bit before restarting
            time.sleep(1)
            
            # Start streaming again
            return self.start()
            
        except Exception as e:
            self.logger.error(f"Failed to restart camera streaming: {e}")
            return False
    
    def _streaming_worker(self):
        """Worker thread for camera streaming."""
        try:
            self.logger.info("Camera streaming worker started")
            
            while not self.stop_event.is_set():
                try:
                    # Capture frame from camera handler
                    if self.camera_handler:
                        frame_data = self.camera_handler.capture_frame()
                        if frame_data:
                            # Update statistics
                            self.frame_count += 1
                            current_time = time.time()
                            self.last_frame_time = current_time
                            
                            # Calculate FPS
                            if self.start_time:
                                elapsed = current_time - self.start_time
                                if elapsed > 0:
                                    current_fps = self.frame_count / elapsed
                                    self.fps_stats.append(current_fps)
                                    if len(self.fps_stats) > 100:
                                        self.fps_stats.pop(0)
                            
                            # Put frame in queue (non-blocking)
                            try:
                                self.frames_queue.put_nowait(frame_data)
                            except queue.Full:
                                # Remove oldest frame if queue is full
                                try:
                                    self.frames_queue.get_nowait()
                                    self.frames_queue.put_nowait(frame_data)
                                except queue.Empty:
                                    pass
                            
                            # Process frame callbacks
                            for callback in self.frame_callbacks:
                                try:
                                    callback(frame_data)
                                except Exception as e:
                                    self.logger.error(f"Frame callback error: {e}")
                            
                            # Get metadata
                            metadata = self.camera_handler.get_metadata()
                            if metadata:
                                try:
                                    self.metadata_queue.put_nowait(metadata)
                                except queue.Full:
                                    # Replace metadata if queue is full
                                    try:
                                        self.metadata_queue.get_nowait()
                                        self.metadata_queue.put_nowait(metadata)
                                    except queue.Empty:
                                        pass
                        else:
                            # No frame available, sleep briefly
                            time.sleep(0.01)
                    else:
                        # No camera handler, sleep
                        time.sleep(0.1)
                        
                except Exception as e:
                    self.logger.error(f"Error in streaming worker: {e}")
                    time.sleep(0.1)
            
            self.logger.info("Camera streaming worker stopped")
            
        except Exception as e:
            self.logger.error(f"Fatal error in streaming worker: {e}")
    
    def get_frame(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Get a frame from the streaming queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Optional[Dict[str, Any]]: Frame data, None if timeout
        """
        try:
            return self.frames_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_metadata(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Get camera metadata from the queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Optional[Dict[str, Any]]: Camera metadata, None if timeout
        """
        try:
            return self.metadata_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def capture_image(self) -> Optional[Dict[str, Any]]:
        """
        Capture a single image for saving or processing.
        
        Returns:
            Optional[Dict[str, Any]]: Image data, None if failed
        """
        try:
            if not self.streaming:
                self.logger.error("Camera not streaming")
                return None
            
            # Get frame from queue
            frame_data = self.get_frame(timeout=2.0)
            if not frame_data:
                self.logger.error("Failed to capture frame")
                return None
            
            # Save image if directory exists
            if IMAGE_SAVE_DIR:
                save_dir = Path(IMAGE_SAVE_DIR)
                save_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
                filepath = save_dir / filename
                
                try:
                    cv2.imwrite(str(filepath), frame_data['frame'])
                    frame_data['saved_path'] = str(filepath)
                    self.logger.info(f"Image saved: {filepath}")
                except Exception as e:
                    self.logger.error(f"Failed to save image: {e}")
            
            return frame_data
            
        except Exception as e:
            self.logger.error(f"Failed to capture image: {e}")
            return None
    
    def add_frame_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Add a callback function to be called for each frame.
        
        Args:
            callback: Function to call with frame data
        """
        if callback not in self.frame_callbacks:
            self.frame_callbacks.append(callback)
            self.logger.info("Frame callback added")
    
    def remove_frame_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Remove a frame callback function.
        
        Args:
            callback: Function to remove
        """
        if callback in self.frame_callbacks:
            self.frame_callbacks.remove(callback)
            self.logger.info("Frame callback removed")
    
    def update_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update camera configuration.
        
        Args:
            config: New configuration parameters
            
        Returns:
            Dict[str, Any]: Updated configuration
        """
        try:
            self.logger.info(f"Updating camera configuration: {config}")
            
            # Update local config
            self.config.update(config)
            
            # Update camera handler configuration if available
            if self.camera_handler:
                # Create camera configuration
                camera_config = self.camera_handler.picam2.create_preview_configuration(
                    main={"size": self.config.get('resolution', DEFAULT_RESOLUTION), "format": "RGB888"},
                    lores={"size": (640, 480), "format": "XBGR8888"}
                )
                
                # Apply configuration
                success = self.camera_handler.update_configuration(camera_config)
                if not success:
                    self.logger.error("Failed to update camera handler configuration")
            
            self.logger.info("Camera configuration updated successfully")
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return self.config
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current camera configuration.
        
        Returns:
            Dict[str, Any]: Current configuration
        """
        return self.config.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get camera manager status.
        
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            status = {
                'initialized': self.initialized,
                'streaming': self.streaming,
                'frame_count': self.frame_count,
                'config': self.config,
                'queue_sizes': {
                    'frames': self.frames_queue.qsize(),
                    'metadata': self.metadata_queue.qsize()
                },
                'frame_callbacks_count': len(self.frame_callbacks)
            }
            
            # Add timing information
            if self.start_time:
                status['uptime'] = time.time() - self.start_time
                if self.frame_count > 0:
                    status['average_fps'] = sum(self.fps_stats) / len(self.fps_stats) if self.fps_stats else 0
            
            if self.last_frame_time:
                status['last_frame_time'] = self.last_frame_time
            
            # Add camera handler status if available
            if self.camera_handler:
                status['camera_handler'] = self.camera_handler.get_status()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {
                'initialized': False,
                'streaming': False,
                'error': str(e)
            }
    
    def get_available_settings(self) -> Dict[str, Any]:
        """
        Get available camera settings and controls.
        
        Returns:
            Dict[str, Any]: Available settings
        """
        try:
            settings = {
                'config': self.config,
                'available_controls': {}
            }
            
            # Get available controls from camera handler
            if self.camera_handler:
                settings['available_controls'] = self.camera_handler.get_controls()
                settings['camera_properties'] = self.camera_handler.camera_properties
                settings['sensor_modes'] = self.camera_handler.sensor_modes
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Failed to get available settings: {e}")
            return {'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform camera health check.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            health = {
                'status': 'healthy',
                'timestamp': time.time(),
                'checks': {}
            }
            
            # Check initialization
            health['checks']['initialized'] = {
                'status': 'ok' if self.initialized else 'error',
                'message': 'Camera initialized' if self.initialized else 'Camera not initialized'
            }
            
            # Check streaming
            health['checks']['streaming'] = {
                'status': 'ok' if self.streaming else 'warning',
                'message': 'Camera streaming' if self.streaming else 'Camera not streaming'
            }
            
            # Check frame rate
            if self.fps_stats:
                avg_fps = sum(self.fps_stats) / len(self.fps_stats)
                health['checks']['frame_rate'] = {
                    'status': 'ok' if avg_fps > 10 else 'warning',
                    'value': avg_fps,
                    'message': f'Average FPS: {avg_fps:.1f}'
                }
            
            # Check queue health
            frames_queue_size = self.frames_queue.qsize()
            health['checks']['frames_queue'] = {
                'status': 'ok' if frames_queue_size < 8 else 'warning',
                'value': frames_queue_size,
                'message': f'Frames queue size: {frames_queue_size}'
            }
            
            # Check camera handler health
            if self.camera_handler:
                handler_status = self.camera_handler.get_status()
                health['checks']['camera_handler'] = {
                    'status': 'ok' if handler_status.get('streaming', False) else 'error',
                    'message': 'Camera handler operational' if handler_status.get('streaming', False) else 'Camera handler not operational'
                }
            
            # Overall status
            error_count = sum(1 for check in health['checks'].values() if check['status'] == 'error')
            warning_count = sum(1 for check in health['checks'].values() if check['status'] == 'warning')
            
            if error_count > 0:
                health['status'] = 'error'
            elif warning_count > 0:
                health['status'] = 'warning'
            
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'timestamp': time.time(),
                'error': str(e)
            }
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            self.logger.info("Cleaning up camera manager...")
            
            # Stop streaming
            if self.streaming:
                self.stop()
            
            # Clear callbacks
            self.frame_callbacks.clear()
            
            # Clear queues
            while not self.frames_queue.empty():
                try:
                    self.frames_queue.get_nowait()
                except queue.Empty:
                    break
            
            while not self.metadata_queue.empty():
                try:
                    self.metadata_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Cleanup camera handler
            if self.camera_handler:
                self.camera_handler.cleanup()
            
            self.initialized = False
            self.logger.info("Camera manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def create_camera_manager(camera_handler=None, logger=None) -> CameraManager:
    """
    Factory function to create CameraManager instance.
    
    Args:
        camera_handler: CameraHandler instance (optional)
        logger: Logger instance (optional)
        
    Returns:
        CameraManager: New CameraManager instance
    """
    # Create camera handler if not provided
    if camera_handler is None:
        try:
            from components.camera_handler import CameraHandler
            camera_handler = CameraHandler(logger=logger)
        except ImportError as e:
            logger.warning(f"Could not import CameraHandler: {e}")
            camera_handler = None
    
    return CameraManager(camera_handler=camera_handler, logger=logger)
