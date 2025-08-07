#!/usr/bin/env python3
"""
Video Service Template for v1.3 Application

This is a simplified template version for testing the systemd service.
It provides basic video streaming functionality without complex processing.
"""

import threading
import time
import logging
from datetime import datetime
import queue
import json
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)

class VideoServiceTemplate:
    """
    Template Video Service for testing purposes
    
    Features:
    - Simulated video streaming
    - Frame generation and processing
    - Thread-safe operations
    - Basic video encoding
    """
    
    def __init__(self, camera_manager=None, detection_processor=None):
        self.camera_manager = camera_manager
        self.detection_processor = detection_processor
        
        # Video state
        self.streaming = False
        self.streaming_thread = None
        self.stop_event = threading.Event()
        
        # Video settings
        self.width = 1280
        self.height = 720
        self.fps = 30
        self.quality = 80
        
        # Statistics
        self.frames_generated = 0
        self.start_time = None
        self.last_frame_time = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Video Service Template initialized")
    
    def start_streaming(self):
        """Start video streaming"""
        with self.lock:
            if self.streaming:
                logger.info("Video streaming already active")
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
                logger.info("Video streaming started (template)")
                return True
            except Exception as e:
                logger.error(f"Failed to start video streaming: {e}")
                return False
    
    def stop_streaming(self):
        """Stop video streaming"""
        with self.lock:
            if not self.streaming:
                logger.info("Video streaming not active")
                return True
            
            try:
                self.stop_event.set()
                if self.streaming_thread and self.streaming_thread.is_alive():
                    self.streaming_thread.join(timeout=5)
                self.streaming = False
                logger.info("Video streaming stopped")
                return True
            except Exception as e:
                logger.error(f"Failed to stop video streaming: {e}")
                return False
    
    def _streaming_worker(self):
        """Video streaming worker"""
        logger.info("Video streaming worker started")
        
        while not self.stop_event.is_set():
            try:
                # Generate simulated frame
                frame_data = self._generate_frame()
                
                # Process frame if detection processor is available
                if self.detection_processor:
                    self._process_frame_with_detection(frame_data)
                
                self.frames_generated += 1
                self.last_frame_time = datetime.now()
                
                # Simulate frame rate
                time.sleep(1/self.fps)
                
            except Exception as e:
                logger.error(f"Error in video streaming worker: {e}")
                time.sleep(1)
        
        logger.info("Video streaming worker stopped")
    
    def _generate_frame(self):
        """Generate a simulated video frame"""
        # Create a simple test pattern
        img = Image.new('RGB', (self.width, self.height), color='black')
        draw = ImageDraw.Draw(img)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((10, 10), f"AI Camera v1.3 - {timestamp}", fill='white')
        
        # Add frame counter
        draw.text((10, 40), f"Frame: {self.frames_generated}", fill='white')
        
        # Add test pattern
        for i in range(0, self.width, 50):
            draw.line([(i, 0), (i, self.height)], fill='gray', width=1)
        for i in range(0, self.height, 50):
            draw.line([(0, i), (self.width, i)], fill='gray', width=1)
        
        # Add moving object
        x = (self.frames_generated * 5) % self.width
        y = self.height // 2
        draw.ellipse([x-20, y-20, x+20, y+20], fill='red')
        
        # Convert to JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=self.quality)
        jpeg_data = buffer.getvalue()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'frame_id': self.frames_generated,
            'width': self.width,
            'height': self.height,
            'jpeg_data': base64.b64encode(jpeg_data).decode('utf-8'),
            'size_bytes': len(jpeg_data)
        }
    
    def _process_frame_with_detection(self, frame_data):
        """Process frame with detection results"""
        if not self.detection_processor:
            return
        
        try:
            # Get latest detection result
            detection_result = self.detection_processor.get_result(timeout=0.1)
            if detection_result and detection_result.get('detection_found'):
                # Add detection overlay to frame
                frame_data['detection'] = detection_result
                logger.debug(f"Detection found in frame {frame_data['frame_id']}")
        except Exception as e:
            logger.error(f"Error processing frame with detection: {e}")
    
    def get_frame(self, timeout=1.0):
        """Get current frame data"""
        if not self.streaming:
            return None
        
        # Return simulated frame data
        return self._generate_frame()
    
    def get_stream_url(self):
        """Get streaming URL"""
        return "/video_feed"
    
    def health_check(self):
        """Check video service health"""
        health_status = {
            'streaming': self.streaming,
            'frames_generated': self.frames_generated,
            'last_frame_time': self.last_frame_time.isoformat() if self.last_frame_time else None,
            'fps': self.fps,
            'resolution': f"{self.width}x{self.height}",
            'status': 'healthy' if self.streaming else 'unhealthy'
        }
        return health_status
    
    def get_statistics(self):
        """Get video service statistics"""
        if not self.start_time:
            return {}
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        actual_fps = self.frames_generated / elapsed if elapsed > 0 else 0
        
        return {
            'total_frames': self.frames_generated,
            'elapsed_time': elapsed,
            'actual_fps': round(actual_fps, 2),
            'target_fps': self.fps,
            'uptime': elapsed
        }
    
    def update_settings(self, **settings):
        """Update video settings"""
        with self.lock:
            if 'width' in settings:
                self.width = settings['width']
            if 'height' in settings:
                self.height = settings['height']
            if 'fps' in settings:
                self.fps = settings['fps']
            if 'quality' in settings:
                self.quality = settings['quality']
            
            logger.info(f"Video settings updated: {settings}")
    
    def run(self):
        """Start streaming and keep running"""
        self.start_streaming()
        
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Video service interrupted")
        finally:
            self.stop_streaming()
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_streaming()
        logger.info("Video service cleaned up")
