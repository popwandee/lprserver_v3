#!/usr/bin/env python3
"""
Camera Handler Component for AI Camera v1.3

This component provides low-level camera operations using Picamera2
for Camera Module 3 on Raspberry Pi 5.

Features:
- Picamera2 integration
- Camera configuration and control
- Frame capture and metadata handling
- Camera status monitoring
- Error handling and recovery

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import threading
import time
import logging
import multiprocessing
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
import queue

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, MJPEGEncoder
from picamera2.outputs import FileOutput
from picamera2.controls import Controls
from libcamera import controls
import cv2
import numpy as np
import logging
logger = logging.getLogger(__name__)


def make_json_serializable(obj: Any) -> Any:
    """
    Convert any object to JSON-serializable format.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable object
    """
    if obj is None:
        return None
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        # Handle objects with attributes
        if hasattr(obj, 'name'):
            return str(obj.name)
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return str(type(obj).__name__)
    else:
        return str(obj) 


class CameraHandler:
    """
    Camera Handler Component using Picamera2 with Singleton pattern and access control.
    
    This class provides low-level camera operations including:
    - Camera initialization and configuration
    - Frame capture and metadata handling
    - Camera controls (exposure, gain, focus, etc.)
    - Video recording and streaming
    - Error handling and recovery
    
    Singleton pattern ensures only one camera instance exists across all workers.
    Thread-safe and multiprocessing-safe camera access using locks and queues.
    
    Attributes:
        picam2: Picamera2 instance
        logger: Logger instance
        initialized: Whether camera is initialized
        streaming: Whether camera is currently streaming
        current_config: Current camera configuration
        camera_properties: Camera sensor properties
        sensor_modes: Available sensor modes
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    # Global camera access control - Thread-safe only
    _camera_lock = threading.Lock()
    _camera_queue = queue.Queue(maxsize=1)  # Single slot queue for camera access
    _camera_queue.put(None)  # เติม slot แรกให้ queue พร้อมใช้งาน
    
    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CameraHandler, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, logger=None):
        """
        Initialize CameraHandler (only once due to Singleton).
        
        Args:
            logger: Logger instance (optional)
        """
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            self.logger = logger or logging.getLogger(__name__)
            
            # Camera state
            self.picam2 = None
            self.initialized = False
            self.streaming = False
            self.camera_properties = {}
            self.sensor_modes = []
            self.current_config = {}
            
            self._initialized = True
            self.logger.info("CameraHandler Singleton initialized")
        self.streaming = False
        
        # Configuration
        self.current_config = {}
        self.camera_properties = {}
        self.sensor_modes = []
        
        # Recording state
        self.recording = False
        self.recording_encoder = None
        self.recording_file = None
        
        # Threading
        self._lock = threading.RLock()
        
        self.logger.info("CameraHandler initialized")
    
    def initialize_camera(self) -> bool:
        """
        Initialize the camera with default configuration.
        Based on v1_2 successful implementation with Singleton protection and safe access.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        def _initialize_camera_internal():
            with self._lock:
                if self.initialized:
                    self.logger.warning("Camera already initialized (Singleton protection)")
                    return True
                
                # Clean up any existing camera instances first
                self._cleanup_existing_picamera2()
                
                # If camera exists, deactivate and re-initialize
                if self.picam2:
                    self.logger.info("Deactivating existing camera instance for re-initialization...")
                    try:
                        if self.picam2.started:
                            self.picam2.stop()
                        self.picam2.close()
                    except:
                        pass
                    self.picam2 = None
                    self.initialized = False
                    time.sleep(1.0)  # Give more time to release resources
                
                self.logger.info("Initializing camera...")
                
                # Create Picamera2 instance
                self.picam2 = Picamera2()
                
                # Get camera properties (available before configuration)
                self.camera_properties = self.picam2.camera_properties
                self.sensor_modes = self.picam2.sensor_modes
                
                self.logger.info(f"Camera properties: {self.camera_properties}")
                self.logger.info(f"Available sensor modes: {len(self.sensor_modes)}")
                
                # Create video configuration optimized for ML detection
                # According to Picamera2 manual, use proper stream configuration
                main_config = {"size": (1280, 720), "format": "RGB888"}
                lores_config = {"size": (640, 480), "format": "XBGR8888"}
                
                # Create configuration with proper stream setup
                config = self.picam2.create_video_configuration(
                    main=main_config, 
                    lores=lores_config, 
                    encode="lores"
                )
                
                # Configure camera (this sets up the camera but doesn't start it)
                self.picam2.configure(config)
                
                # Get initial configuration after configure()
                self.current_config = self.picam2.camera_configuration()
                
                # Camera is now configured but not started
                self.initialized = True
                self.logger.info("Camera configured successfully (not started yet)")
                
                return True
                
        return self.safe_camera_operation(_initialize_camera_internal)
    
    def start_camera(self) -> bool:
        """
        Start the camera streaming with Singleton protection and safe access.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        def _start_camera_internal():
            with self._lock:
                if not self.initialized:
                    self.logger.error("Camera not initialized")
                    return False
                
                if self.streaming:
                    self.logger.warning("Camera already streaming (Singleton protection)")
                    return True
                
                # Check if camera is being used by another process
                self.logger.info("Checking camera availability...")
                if self._is_camera_in_use():
                    self.logger.warning("Camera is in use by another process, attempting to release...")
                    import subprocess
                    subprocess.run(['sudo', 'fuser', '-k', '/dev/media*'], capture_output=True)
                    subprocess.run(['sudo', 'fuser', '-k', '/dev/video*'], capture_output=True)
                    if not self._release_camera_resources():
                        self.logger.warning("Failed to release camera resources, attempting hardware reset...")
                        if not self._reset_camera_hardware():
                            self.logger.error("Failed to reset camera hardware")
                            return False
                        else:
                            self.logger.info("Camera hardware reset successful")
                
                # Cleanup previous camera instance if already started
                if self.picam2 and getattr(self.picam2, 'started', False):
                    self.logger.info("Camera already started, stopping before restart")
                    try:
                        self.picam2.stop()
                        self.logger.info("Camera stopped successfully before restart")
                    except Exception as e:
                        self.logger.warning(f"Error stopping camera before restart: {e}")
                    try:
                        self.picam2.close()
                        self.logger.info("Camera closed successfully before restart")
                    except Exception as e:
                        self.logger.warning(f"Error closing camera before restart: {e}")
                    self.picam2 = None
                    self.initialized = False
                    time.sleep(1.0)  # Give more time to release resources
                
                self.logger.info("Starting camera...")
                try:
                    # According to Picamera2 manual, start() should be called after configure()
                    self.logger.info(f"Picam2 object: {self.picam2}")
                    self.logger.info(f"Picam2 started: {getattr(self.picam2, 'started', 'N/A')}")
                    self.logger.info(f"Picam2 is_open: {getattr(self.picam2, 'is_open', 'N/A')}")
                    
                    # Check if camera is properly configured before starting
                    if not self.picam2.camera_configuration():
                        self.logger.error("Camera not properly configured")
                        return False
                    
                    self.logger.info(f"About to call picam2.start() - picam2 object: {self.picam2}")
                    self.logger.info(f"Picam2 state before start: started={getattr(self.picam2, 'started', 'N/A')}, is_open={getattr(self.picam2, 'is_open', 'N/A')}")
                    
                    # Start the camera according to Picamera2 manual
                    self.picam2.start()
                    self.logger.info("Picamera2 start() completed successfully")
                    
                    # Verify camera is started
                    if not self.picam2.started:
                        self.logger.error("Camera start() called but not actually started")
                        return False
                    
                    self.streaming = True
                    self.logger.info("Streaming flag set to True")
                    
                    # Wait for camera to stabilize (based on v1_2)
                    time.sleep(0.5)
                    
                    # Apply basic camera controls (based on v1_2 approach)
                    try:
                        self.picam2.set_controls({
                            "Brightness": 0.0,
                            "Contrast": 1.0,
                            "Saturation": 1.0,
                            "Sharpness": 1.0
                        })
                        self.logger.info("Basic camera controls applied")
                    except Exception as e:
                        self.logger.warning(f"Failed to apply basic controls: {e}")
                    
                    self.logger.info("Camera started successfully")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Failed to start picam2: {e}")
                    self.streaming = False
                    return False
        
        return self.safe_camera_operation(_start_camera_internal)
    
    def stop_camera(self) -> bool:
        """
        Stop the camera streaming.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.warning("Camera not streaming")
                    return True
                
                self.logger.info("Stopping camera...")
                
                # Stop recording if active
                if self.recording:
                    self.stop_recording()
                
                self.picam2.stop()
                self.streaming = False
                
                self.logger.info("Camera stopped successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop camera: {e}")
            return False
    
    def close_camera(self) -> bool:
        """
        Close the camera and cleanup resources.
        
        Returns:
            bool: True if closed successfully, False otherwise
        """
        try:
            with self._lock:
                self.logger.info("Closing camera...")
                
                # Stop camera if streaming
                if self.streaming:
                    self.stop_camera()
                
                # Close Picamera2
                if self.picam2:
                    self.picam2.close()
                    self.picam2 = None
                
                self.initialized = False
                self.logger.info("Camera closed successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to close camera: {e}")
            return False
    
    def capture_frame(self) -> Optional[Dict[str, Any]]:
        """
        Capture a single frame with metadata.
        Based on Picamera2 manual - proper capture_request() usage.
        
        Returns:
            Optional[Dict[str, Any]]: Frame data with metadata, None if failed
        """
        if not self.streaming or not self.picam2:
            self.logger.error("Camera not streaming or not initialized")
            return None
            
        if not self.picam2.started:
            self.logger.error("Camera not started - cannot capture")
            return None
            
        request = None
        try:
            # According to Picamera2 manual, capture_request() should be used when camera is started
            request = self.picam2.capture_request()
            frame = request.make_array("main")  # Get frame as numpy array
            metadata = request.get_metadata()   # Get metadata
            request.release()
            request = None
            
            return {
                'frame': frame,
                'metadata': make_json_serializable(metadata),
                'timestamp': time.time(),
                'format': 'RGB888',
                'size': frame.shape[:2]
            }
                
        except Exception as e:
            self.logger.error(f"Failed to capture frame: {e}")
            return None
        finally:
            if request:
                request.release()
    
    def capture_lores_frame(self) -> Optional[Dict[str, Any]]:
        """
        Capture a low-resolution frame optimized for ML detection.
        Based on Picamera2 ML integration approach.
        
        Returns:
            Optional[Dict[str, Any]]: Low-res frame data, None if failed
        """
        if not self.streaming or not self.picam2:
            self.logger.error("Camera not streaming or not initialized")
            return None
            
        request = None
        try:
            # Use capture_request() approach optimized for ML
            request = self.picam2.capture_request()
            frame = request.make_array("lores")  # Get low-res frame as numpy array
            metadata = request.get_metadata()    # Get metadata
            request.release()
            request = None
            
            return {
                'frame': frame,
                'metadata': make_json_serializable(metadata),
                'timestamp': time.time(),
                'format': 'XBGR8888',
                'size': frame.shape[:2]
            }
                
        except Exception as e:
            self.logger.error(f"Failed to capture low-res frame: {e}")
            return None
        finally:
            if request:
                request.release()
    
    def capture_ml_frame(self) -> Optional[Dict[str, Any]]:
        """
        Capture frame optimized for machine learning detection.
        Based on Picamera2 ML integration best practices.
        
        Returns:
            Optional[Dict[str, Any]]: ML-optimized frame data, None if failed
        """
        if not self.streaming or not self.picam2:
            self.logger.error("Camera not streaming or not initialized")
            return None
            
        request = None
        try:
            # Capture both main and lores streams for ML processing
            request = self.picam2.capture_request()
            
            # Get main frame for high-quality detection
            main_frame = request.make_array("main")
            # Get lores frame for fast processing
            lores_frame = request.make_array("lores")
            metadata = request.get_metadata()
            request.release()
            request = None
            
            return {
                'main_frame': main_frame,
                'lores_frame': lores_frame,
                'metadata': make_json_serializable(metadata),
                'timestamp': time.time(),
                'main_format': 'RGB888',
                'lores_format': 'XBGR8888',
                'main_size': main_frame.shape[:2],
                'lores_size': lores_frame.shape[:2]
            }
                
        except Exception as e:
            self.logger.error(f"Failed to capture ML frame: {e}")
            return None
        finally:
            if request:
                request.release()
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get current camera metadata using capture_request().
        Based on v1_2 successful implementation.
        
        Returns:
            Optional[Dict[str, Any]]: Camera metadata, None if failed
        """
        if not self.streaming or not self.picam2:
            self.logger.error("Camera not streaming or not initialized")
            return None
            
        request = None
        try:
            # Use capture_request() approach from v1_2
            request = self.picam2.capture_request()
            metadata = request.get_metadata()
            request.release()
            request = None
            
            # Convert to JSON-serializable format
            return make_json_serializable(metadata)
                
        except Exception as e:
            self.logger.error(f"Failed to get metadata: {e}")
            return None
        finally:
            if request:
                request.release()
    
    def set_controls(self, controls: Dict[str, Any]) -> bool:
        """
        Set camera controls.
        
        Args:
            controls: Dictionary of control values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                self.picam2.set_controls(controls)
                self.logger.info(f"Set camera controls: {controls}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set controls: {e}")
            return False
    
    def get_controls(self) -> Dict[str, Any]:
        """
        Get available camera controls.
        
        Returns:
            Dict[str, Any]: Available controls
        """
        try:
            with self._lock:
                if not self.initialized:
                    return {}
                
                return self.picam2.camera_controls
                
        except Exception as e:
            self.logger.error(f"Failed to get controls: {e}")
            return {}
    
    def start_recording(self, filename: str, bitrate: int = 10000000) -> bool:
        """
        Start video recording.
        
        Args:
            filename: Output filename
            bitrate: Video bitrate
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                if self.recording:
                    self.logger.warning("Already recording")
                    return True
                
                self.logger.info(f"Starting recording: {filename}")
                
                # Create encoder and start recording
                self.recording_encoder = H264Encoder(bitrate)
                self.recording_file = filename
                
                self.picam2.start_recording(self.recording_encoder, filename)
                self.recording = True
                
                self.logger.info("Recording started successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """
        Stop video recording.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            with self._lock:
                if not self.recording:
                    self.logger.warning("Not recording")
                    return True
                
                self.logger.info("Stopping recording...")
                
                self.picam2.stop_recording()
                self.recording = False
                self.recording_encoder = None
                self.recording_file = None
                
                self.logger.info("Recording stopped successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get camera handler status.
        
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            with self._lock:
                status = {
                    'initialized': self.initialized,
                    'streaming': self.streaming,
                    'recording': self.recording,
                    'camera_properties': make_json_serializable(self.camera_properties),
                    'sensor_modes_count': len(self.sensor_modes),
                    'current_config': make_json_serializable(self.current_config)
                }
                
                if self.recording:
                    status['recording_file'] = self.recording_file
                
                if self.streaming:
                    try:
                        metadata = self.get_metadata()
                        if metadata:
                            status['metadata'] = metadata
                    except:
                        pass
                
                return status
                
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {
                'initialized': False,
                'streaming': False,
                'error': str(e)
            }
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current camera configuration.
        
        Returns:
            Dict[str, Any]: Current configuration
        """
        try:
            with self._lock:
                if not self.initialized:
                    return {}
                
                return self.picam2.camera_configuration()
                
        except Exception as e:
            self.logger.error(f"Failed to get configuration: {e}")
            return {}
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update camera configuration.
        
        Args:
            config: New configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.initialized:
                    self.logger.error("Camera not initialized")
                    return False
                
                # Stop camera if streaming
                was_streaming = self.streaming
                if was_streaming:
                    self.stop_camera()
                
                # Apply new configuration
                self.picam2.configure(config)
                self.current_config = self.picam2.camera_configuration()
                
                # Restart if was streaming
                if was_streaming:
                    self.start_camera()
                
                self.logger.info("Configuration updated successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False
    
    def autofocus_cycle(self) -> bool:
        """
        Perform autofocus cycle.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                self.logger.info("Starting autofocus cycle...")
                success = self.picam2.autofocus_cycle()
                
                if success:
                    self.logger.info("Autofocus cycle completed successfully")
                else:
                    self.logger.warning("Autofocus cycle failed")
                
                return success
                
        except Exception as e:
            self.logger.error(f"Failed to perform autofocus cycle: {e}")
            return False
    
    def set_autofocus_mode(self, mode: str) -> bool:
        """
        Set autofocus mode.
        
        Args:
            mode: Autofocus mode ('Manual', 'Auto', 'Continuous')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                mode_map = {
                    'Manual': controls.AfModeEnum.Manual,
                    'Auto': controls.AfModeEnum.Auto,
                    'Continuous': controls.AfModeEnum.Continuous
                }
                
                if mode not in mode_map:
                    self.logger.error(f"Invalid autofocus mode: {mode}")
                    return False
                
                self.picam2.set_controls({"AfMode": mode_map[mode]})
                self.logger.info(f"Set autofocus mode: {mode}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set autofocus mode: {e}")
            return False
    
    def _cleanup_existing_picamera2(self):
        """
        Clean up any existing Picamera2 instances that might be holding resources.
        """
        try:
            self.logger.info("Attempting to cleanup existing Picamera2 instances...")
            
            # Check for Python processes that might be holding camera
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'python' in line.lower() and ('picamera' in line.lower() or 'aicamera' in line.lower()):
                        self.logger.info(f"Found potential camera process: {line.strip()}")
            
            # Try to kill any processes using camera devices
            if self._is_camera_in_use():
                self.logger.warning("Camera devices in use, attempting to kill processes...")
                subprocess.run(['sudo', 'fuser', '-k', '/dev/media*'], 
                             capture_output=True, timeout=10)
                subprocess.run(['sudo', 'fuser', '-k', '/dev/video*'], 
                             capture_output=True, timeout=10)
                time.sleep(2)  # Wait for processes to be killed
                
        except Exception as e:
            self.logger.error(f"Error during Picamera2 cleanup: {e}")
    
    def _is_camera_in_use(self) -> bool:
        """
        Check if camera is being used by another process.
        
        Returns:
            bool: True if camera is in use, False otherwise
        """
        try:
            import subprocess
            import os
            
            # Check if media devices are being used
            result = subprocess.run(['sudo', 'fuser', '/dev/media*'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse PIDs that are using media devices
                pids = set()
                for line in result.stdout.split():
                    if line.isdigit():
                        pids.add(int(line))
                
                # Remove our own process from the list
                current_pid = os.getpid()
                pids.discard(current_pid)
                
                if pids:
                    self.logger.info(f"Camera in use by PIDs: {pids}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking camera usage: {e}")
            return False
    
    def _release_camera_resources(self) -> bool:
        """
        Release camera resources by stopping other processes.
        
        Returns:
            bool: True if resources released successfully, False otherwise
        """
        try:
            import subprocess
            import time
            
            self.logger.info("Attempting to release camera resources...")
            
            # First, try to gracefully stop other camera processes
            result = subprocess.run(['sudo', 'fuser', '-k', '/dev/media*'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info("Sent SIGKILL to processes using camera")
                time.sleep(2)  # Wait for processes to terminate
                
                # Check if camera is still in use
                if not self._is_camera_in_use():
                    self.logger.info("Camera resources released successfully")
                    return True
                else:
                    self.logger.warning("Camera still in use after SIGKILL")
            
            # If graceful termination failed, try force kill
            self.logger.info("Attempting force kill of camera processes...")
            result = subprocess.run(['sudo', 'fuser', '-9', '/dev/media*'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                time.sleep(3)  # Wait longer for force kill
                
                if not self._is_camera_in_use():
                    self.logger.info("Camera resources released with force kill")
                    return True
            
            self.logger.error("Failed to release camera resources")
            return False
            
        except Exception as e:
            self.logger.error(f"Error releasing camera resources: {e}")
            return False
    
    def _reset_camera_hardware(self) -> bool:
        """
        Reset camera hardware by unloading and reloading modules.
        
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            import subprocess
            import time
            
            self.logger.info("Attempting to reset camera hardware...")
            
            # Unload camera modules
            modules_to_unload = ['bcm2835-v4l2', 'imx708']
            for module in modules_to_unload:
                try:
                    subprocess.run(['sudo', 'modprobe', '-r', module], 
                                 capture_output=True, timeout=5)
                    self.logger.info(f"Unloaded module: {module}")
                except:
                    pass  # Module might not be loaded
            
            time.sleep(2)
            
            # Reload camera modules
            for module in reversed(modules_to_unload):
                try:
                    subprocess.run(['sudo', 'modprobe', module], 
                                 capture_output=True, timeout=5)
                    self.logger.info(f"Reloaded module: {module}")
                except:
                    pass
            
            time.sleep(3)  # Wait for modules to initialize
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting camera hardware: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            with self._lock:
                self.logger.info("Cleaning up camera handler...")
                self.close_camera()
                self.logger.info("Camera handler cleanup completed")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    @classmethod
    def reset_instance(cls):
        """Reset the Singleton instance (for testing/debugging)."""
        with cls._lock:
            if cls._instance:
                cls._instance.cleanup()
                cls._instance = None
                cls._initialized = False
                logger.info("CameraHandler Singleton instance reset")
    
    @classmethod
    def get_instance(cls, **kwargs):
        """Get the Singleton instance."""
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance
    
    @classmethod
    def acquire_camera_access(cls, timeout=5.0):
        """
        Acquire camera access lock (thread-safe only).
        
        Args:
            timeout (float): Timeout in seconds
            
        Returns:
            bool: True if access acquired, False if timeout
        """
        try:
            # Try to acquire thread lock
            thread_acquired = cls._camera_lock.acquire(timeout=timeout)
            if not thread_acquired:
                return False
                
            # Try to get queue slot
            try:
                cls._camera_queue.get(timeout=timeout)
                return True
            except queue.Empty:
                cls._camera_lock.release()
                return False
                
        except Exception as e:
            logger.error(f"Error acquiring camera access: {e}")
            return False
    
    @classmethod
    def release_camera_access(cls):
        """Release camera access lock."""
        try:
            # Return queue slot
            cls._camera_queue.put(None, timeout=1.0)
            # Release thread lock
            cls._camera_lock.release()
        except Exception as e:
            logger.error(f"Error releasing camera access: {e}")
    
    def safe_camera_operation(self, operation_func, *args, **kwargs):
        """
        Execute camera operation with safe access control.
        
        Args:
            operation_func: Function to execute
            *args: Arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of operation or None if failed
        """
        if not self.acquire_camera_access(timeout=10.0):
            self.logger.error("Failed to acquire camera access")
            return None
            
        try:
            result = operation_func(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Camera operation failed: {e}")
            return None
        finally:
            self.release_camera_access()