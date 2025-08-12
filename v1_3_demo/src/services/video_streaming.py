#!/usr/bin/env python3
"""
Video Streaming Service for AI Camera v1.3

This service manages video streaming functionality using absolute imports
and dependency injection pattern.

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

import threading
import time
import queue
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import cv2
import numpy as np
import base64
import io
from PIL import Image, ImageDraw, ImageFont

# Use absolute imports
from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.core.config import DEFAULT_RESOLUTION, DEFAULT_FRAMERATE

logger = get_logger(__name__)


class VideoStreamingService:
    """
    Video Streaming Service for managing video streaming functionality.
    
    Features:
    - Real-time video streaming
    - Frame processing and encoding
    - Thread-safe operations
    - Integration with camera manager
    - WebSocket broadcasting
    """
    
    def __init__(self, camera_manager=None, logger=None):
        """
        Initialize Video Streaming Service.
        
        Args:
            camera_manager: Camera manager instance
            logger: Logger instance
        """
        self.camera_manager = camera_manager
        self.logger = logger or get_logger(__name__)
        
        # Streaming state
        self.streaming = False
        self.streaming_thread = None
        self.stop_event = threading.Event()
        
        # Video settings
        self.width, self.height = DEFAULT_RESOLUTION
        self.fps = DEFAULT_FRAMERATE
        self.quality = 80
        
        # Frame queue for processing
        self.frame_queue = queue.Queue(maxsize=10)
        
        # Statistics
        self.frames_processed = 0
        self.start_time = None
        self.last_frame_time = None
        self.average_fps = 0.0
        
        # Thread safety
        self.lock = threading.Lock()
        
        self.logger.info("VideoStreamingService initialized")
    
    def start_streaming(self) -> bool:
        """
        Start video streaming.
        
        Returns:
            bool: True if streaming started successfully
        """
        with self.lock:
            if self.streaming:
                self.logger.info("Video streaming already active")
                return True
            
            try:
                self.stop_event.clear()
                self.streaming_thread = threading.Thread(
                    target=self._streaming_worker,
                    daemon=True
                )
                self.streaming_thread.start()
                self.streaming = True
                self.start_time = datetime.now()
                self.frames_processed = 0
                self.logger.info("Video streaming started successfully")
                return True
            except Exception as e:
                self.logger.error(f"Failed to start video streaming: {e}")
                return False
    
    def stop_streaming(self) -> bool:
        """
        Stop video streaming.
        
        Returns:
            bool: True if streaming stopped successfully
        """
        with self.lock:
            if not self.streaming:
                self.logger.info("Video streaming not active")
                return True
            
            try:
                self.stop_event.set()
                if self.streaming_thread and self.streaming_thread.is_alive():
                    self.streaming_thread.join(timeout=5)
                self.streaming = False
                self.logger.info("Video streaming stopped successfully")
                return True
            except Exception as e:
                self.logger.error(f"Failed to stop video streaming: {e}")
                return False
    
    def _streaming_worker(self):
        """Video streaming worker thread."""
        self.logger.info("Video streaming worker started")
        
        while not self.stop_event.is_set():
            try:
                # Get frame from camera manager
                if self.camera_manager:
                    frame = self.camera_manager.capture_frame()
                    if frame is not None:
                        # Process frame
                        processed_frame = self._process_frame(frame)
                        
                        # Add to queue (non-blocking)
                        try:
                            self.frame_queue.put_nowait(processed_frame)
                        except queue.Full:
                            # Remove oldest frame if queue is full
                            try:
                                self.frame_queue.get_nowait()
                                self.frame_queue.put_nowait(processed_frame)
                            except queue.Empty:
                                pass
                        
                        # Update statistics
                        self.frames_processed += 1
                        self.last_frame_time = datetime.now()
                        
                        # Calculate average FPS
                        if self.start_time:
                            elapsed = (self.last_frame_time - self.start_time).total_seconds()
                            if elapsed > 0:
                                self.average_fps = self.frames_processed / elapsed
                
                # Sleep to maintain target FPS
                time.sleep(1.0 / self.fps)
                
            except Exception as e:
                self.logger.error(f"Error in streaming worker: {e}")
                time.sleep(0.1)  # Brief pause on error
        
        self.logger.info("Video streaming worker stopped")
    
    def _process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process frame for streaming.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Dict containing processed frame data
        """
        try:
            # Resize frame if needed
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))
            
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
            jpeg_data = buffer.tobytes()
            
            # Convert to base64
            base64_frame = base64.b64encode(jpeg_data).decode('utf-8')
            
            return {
                'frame': base64_frame,
                'timestamp': datetime.now().isoformat(),
                'width': self.width,
                'height': self.height,
                'fps': self.fps
            }
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return None
    
    def get_frame(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Get the latest frame from the queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Frame data or None if no frame available
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get streaming service status.
        
        Returns:
            Dict containing status information
        """
        return {
            'streaming': self.streaming,
            'frames_processed': self.frames_processed,
            'average_fps': round(self.average_fps, 2),
            'queue_size': self.frame_queue.qsize(),
            'resolution': f"{self.width}x{self.height}",
            'target_fps': self.fps,
            'quality': self.quality,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_frame_time': self.last_frame_time.isoformat() if self.last_frame_time else None,
            'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def update_settings(self, **settings) -> bool:
        """
        Update streaming settings.
        
        Args:
            **settings: Settings to update
            
        Returns:
            bool: True if settings updated successfully
        """
        try:
            with self.lock:
                if 'width' in settings and 'height' in settings:
                    self.width = settings['width']
                    self.height = settings['height']
                
                if 'fps' in settings:
                    self.fps = settings['fps']
                
                if 'quality' in settings:
                    self.quality = max(1, min(100, settings['quality']))
                
                self.logger.info(f"Streaming settings updated: {settings}")
                return True
        except Exception as e:
            self.logger.error(f"Error updating streaming settings: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on streaming service.
        
        Returns:
            Dict containing health status
        """
        try:
            status = {
                'healthy': True,
                'streaming': self.streaming,
                'thread_alive': self.streaming_thread.is_alive() if self.streaming_thread else False,
                'queue_healthy': self.frame_queue.qsize() < 8,  # Not too full
                'fps_healthy': self.average_fps > 0.5 * self.fps,  # At least 50% of target FPS
                'last_frame_recent': True
            }
            
            # Check if last frame was recent
            if self.last_frame_time:
                time_since_last = (datetime.now() - self.last_frame_time).total_seconds()
                status['last_frame_recent'] = time_since_last < 5.0  # Within 5 seconds
            
            status['healthy'] = all([
                status['streaming'],
                status['thread_alive'],
                status['queue_healthy'],
                status['fps_healthy'],
                status['last_frame_recent']
            ])
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            self.stop_streaming()
            
            # Clear frame queue
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.logger.info("VideoStreamingService cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def create_video_streaming_service(camera_manager=None, logger=None) -> VideoStreamingService:
    """
    Factory function for VideoStreamingService.
    
    Args:
        camera_manager: Camera manager instance
        logger: Logger instance
        
    Returns:
        VideoStreamingService instance
    """
    return VideoStreamingService(camera_manager, logger)
