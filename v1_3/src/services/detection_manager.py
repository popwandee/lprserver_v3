#!/usr/bin/env python3
"""
Detection Manager Service for AI Camera v1.3

This service manages the complete detection workflow:
- Coordinates with camera service to receive image frames
- Orchestrates the detection pipeline using DetectionProcessor
- Manages detection timing and intervals
- Handles database storage of detection results
- Provides detection status and management APIs

Author: AI Camera Team
Version: 1.3  
Date: December 2024
"""

import threading
import time
import queue
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.core.config import DETECTION_INTERVAL

logger = get_logger(__name__)


class DetectionManager:
    """
    Detection Manager Service for orchestrating AI detection workflow.
    
    This service provides:
    - Detection pipeline management
    - Integration with camera service
    - Detection timing and scheduling
    - Database integration for results
    - Status monitoring and reporting
    
    Workflow:
    1. Receive images from camera service
    2. Image frame validation and enhancing for vehicle detection model
    3. Vehicle detection - if not found, skip and continue next loop
    4. If found vehicle object, perform license plate detection
    5. Crop license plate then perform OCR
    6. Save original image with license plate detection result bounding box drawing
    7. Insert information from OCR and MODEL detection results into SQLite
    """
    
    def __init__(self, detection_processor=None, database_manager=None, logger=None):
        """
        Initialize Detection Manager.
        
        Args:
            detection_processor: DetectionProcessor component instance
            database_manager: DatabaseManager component instance
            logger: Logger instance
        """
        self.detection_processor = detection_processor
        self.database_manager = database_manager
        self.logger = logger or get_logger(__name__)
        
        # Detection state
        self.is_running = False
        self.detection_thread = None
        self.detection_queue = queue.Queue(maxsize=10)
        
        # Statistics tracking
        self.detection_stats = {
            'started_at': None,
            'total_frames_processed': 0,
            'total_vehicles_detected': 0,
            'total_plates_detected': 0,
            'successful_ocr': 0,
            'failed_detections': 0,
            'last_detection': None,
            'processing_time_avg': 0.0
        }
        
        # Configuration
        self.detection_interval = DETECTION_INTERVAL
        self.auto_start = False  # Can be enabled for continuous detection
        
        self.logger.info("DetectionManager initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the detection manager and load models.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing Detection Manager...")
            
            # Initialize detection processor models
            if self.detection_processor:
                success = self.detection_processor.load_models()
                if success:
                    self.logger.info("Detection models loaded successfully")
                    
                    # Initialize database if available
                    if self.database_manager:
                        db_success = self.database_manager.initialize()
                        if db_success:
                            self.logger.info("Database initialized successfully")
                        else:
                            self.logger.warning("Database initialization failed")
                    
                    return True
                else:
                    self.logger.error("Failed to load detection models")
                    return False
            else:
                self.logger.error("Detection processor not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing detection manager: {e}")
            return False
    
    def start_detection(self) -> bool:
        """
        Start the detection service.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.is_running:
            self.logger.warning("Detection service already running")
            return True
        
        try:
            self.logger.info("Starting detection service...")
            
            # Check if detection processor is ready
            if not self.detection_processor or not self.detection_processor.models_loaded:
                self.logger.error("Detection processor not ready - models not loaded")
                return False
            
            # Start detection thread
            self.is_running = True
            self.detection_thread = threading.Thread(
                target=self._detection_loop,
                name="DetectionThread",
                daemon=True
            )
            self.detection_thread.start()
            
            # Update statistics
            self.detection_stats['started_at'] = datetime.now().isoformat()
            
            self.logger.info("Detection service started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting detection service: {e}")
            self.is_running = False
            return False
    
    def stop_detection(self) -> bool:
        """
        Stop the detection service.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self.is_running:
            self.logger.warning("Detection service not running")
            return True
        
        try:
            self.logger.info("Stopping detection service...")
            
            # Signal thread to stop
            self.is_running = False
            
            # Wait for thread to finish
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=5.0)
                
                if self.detection_thread.is_alive():
                    self.logger.warning("Detection thread did not stop gracefully")
                else:
                    self.logger.info("Detection thread stopped successfully")
            
            self.detection_thread = None
            
            self.logger.info("Detection service stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping detection service: {e}")
            return False
    
    def process_frame_from_camera(self, camera_manager) -> Optional[Dict[str, Any]]:
        """
        Process a single frame from the camera manager.
        
        Args:
            camera_manager: CameraManager service instance
            
        Returns:
            Optional[Dict[str, Any]]: Detection results or None if processing failed
        """
        try:
            if not camera_manager:
                self.logger.warning("Camera manager not available")
                return None
            
            # Capture frame from camera
            frame = camera_manager.capture_frame()
            if frame is None:
                self.logger.debug("No frame available from camera")
                return None
            
            return self.process_frame(frame)
            
        except Exception as e:
            self.logger.error(f"Error processing frame from camera: {e}")
            self.detection_stats['failed_detections'] += 1
            return None
    
    def process_frame(self, frame) -> Optional[Dict[str, Any]]:
        """
        Process a single frame through the complete detection pipeline.
        
        Args:
            frame: Image frame as numpy array
            
        Returns:
            Optional[Dict[str, Any]]: Detection results or None if processing failed
        """
        start_time = time.time()
        
        try:
            self.detection_stats['total_frames_processed'] += 1
            
            # Step 1: Validate and enhance frame
            enhanced_frame = self.detection_processor.validate_and_enhance_frame(frame)
            if enhanced_frame is None:
                self.logger.debug("Frame validation failed")
                return None
            
            # Step 2: Vehicle detection
            vehicle_boxes = self.detection_processor.detect_vehicles(enhanced_frame)
            if not vehicle_boxes:
                self.logger.debug("No vehicles detected - skipping to next frame")
                return None
            
            self.detection_stats['total_vehicles_detected'] += len(vehicle_boxes)
            
            # Step 3: License plate detection (only if vehicles found)
            plate_boxes = self.detection_processor.detect_license_plates(frame, vehicle_boxes)
            if not plate_boxes:
                self.logger.debug("No license plates detected")
                # Still save vehicle detection results
            else:
                self.detection_stats['total_plates_detected'] += len(plate_boxes)
            
            # Step 4: OCR on detected plates
            ocr_results = []
            if plate_boxes:
                ocr_results = self.detection_processor.perform_ocr(frame, plate_boxes)
                if ocr_results:
                    self.detection_stats['successful_ocr'] += len(ocr_results)
            
            # Step 5: Save detection results (images with bounding boxes)
            annotated_path, cropped_paths = self.detection_processor.save_detection_results(
                frame, vehicle_boxes, plate_boxes, ocr_results
            )
            
            # Step 6: Store results in database
            detection_record = {
                'timestamp': datetime.now().isoformat(),
                'vehicles_count': len(vehicle_boxes),
                'plates_count': len(plate_boxes),
                'ocr_results': ocr_results,
                'annotated_image_path': annotated_path,
                'cropped_plates_paths': cropped_paths,
                'vehicle_detections': vehicle_boxes,
                'plate_detections': plate_boxes
            }
            
            if self.database_manager:
                self.database_manager.insert_detection_result(detection_record)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time)
            self.detection_stats['last_detection'] = datetime.now().isoformat()
            
            self.logger.info(
                f"Detection completed: {len(vehicle_boxes)} vehicles, "
                f"{len(plate_boxes)} plates, {len(ocr_results)} OCR results in {processing_time:.3f}s"
            )
            
            return detection_record
            
        except Exception as e:
            self.logger.error(f"Error in detection pipeline: {e}")
            self.detection_stats['failed_detections'] += 1
            return None
    
    def _detection_loop(self):
        """
        Main detection loop running in separate thread.
        
        This loop continuously processes frames from the camera when detection is active.
        """
        self.logger.info("Detection loop started")
        
        # Get camera manager from dependency container
        from v1_3.src.core.dependency_container import get_service
        
        while self.is_running:
            try:
                # Get camera manager
                camera_manager = get_service('camera_manager')
                
                if camera_manager and camera_manager.is_active():
                    # Process frame from camera
                    result = self.process_frame_from_camera(camera_manager)
                    
                    if result:
                        self.logger.debug("Frame processed successfully")
                    else:
                        self.logger.debug("Frame processing returned no results")
                else:
                    self.logger.debug("Camera not active, waiting...")
                
                # Wait for next detection interval
                time.sleep(self.detection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                time.sleep(1.0)  # Wait before retry
        
        self.logger.info("Detection loop stopped")
    
    def _update_processing_stats(self, processing_time: float):
        """Update processing time statistics."""
        if self.detection_stats['processing_time_avg'] == 0.0:
            self.detection_stats['processing_time_avg'] = processing_time
        else:
            # Simple moving average
            alpha = 0.1
            self.detection_stats['processing_time_avg'] = (
                alpha * processing_time + 
                (1 - alpha) * self.detection_stats['processing_time_avg']
            )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the detection manager.
        
        Returns:
            Dict[str, Any]: Status information including statistics
        """
        processor_status = {}
        if self.detection_processor:
            processor_status = self.detection_processor.get_status()
        
        return {
            'service_running': self.is_running,
            'detection_processor_status': processor_status,
            'detection_interval': self.detection_interval,
            'auto_start': self.auto_start,
            'statistics': self.detection_stats.copy(),
            'queue_size': self.detection_queue.qsize() if self.detection_queue else 0,
            'thread_alive': self.detection_thread.is_alive() if self.detection_thread else False,
            'last_update': datetime.now().isoformat()
        }
    
    def cleanup(self):
        """Clean up resources and stop detection service."""
        try:
            self.logger.info("Cleaning up DetectionManager...")
            
            # Stop detection service
            self.stop_detection()
            
            # Clean up detection processor
            if self.detection_processor:
                self.detection_processor.cleanup()
            
            self.logger.info("DetectionManager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during DetectionManager cleanup: {e}")


def create_detection_manager(detection_processor=None, database_manager=None, logger=None) -> DetectionManager:
    """
    Factory function to create DetectionManager with dependencies.
    
    Args:
        detection_processor: DetectionProcessor component instance
        database_manager: DatabaseManager component instance  
        logger: Logger instance
        
    Returns:
        DetectionManager: Configured DetectionManager instance
    """
    manager = DetectionManager(
        detection_processor=detection_processor,
        database_manager=database_manager,
        logger=logger
    )
    
    # Initialize the manager
    if manager.initialize():
        logger.info("DetectionManager created and initialized successfully") if logger else None
        return manager
    else:
        logger.error("Failed to initialize DetectionManager") if logger else None
        return manager  # Return anyway, but not initialized
