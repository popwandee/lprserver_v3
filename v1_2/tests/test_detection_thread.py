#!/usr/bin/env python3
"""
Test script for SimpleDetectionThread class
"""

import os
import sys
import logging
import time
import queue
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_simple_detection_thread_import():
    """Test if SimpleDetectionThread can be imported"""
    logger.info("=== Testing SimpleDetectionThread Import ===")
    try:
        from simple_detection_thread import SimpleDetectionThread
        logger.info("✅ SimpleDetectionThread imported successfully")
        return True
    except Exception as e:
        logger.error(f"SimpleDetectionThread import failed: {e}")
        return False

def test_detection_thread_initialization():
    """Test SimpleDetectionThread initialization"""
    logger.info("=== Testing Detection Thread Initialization ===")
    try:
        from simple_detection_thread import SimpleDetectionThread
        from database_manager import DatabaseManager
        
        # Create mock objects
        class MockCameraManager:
            def get_frame(self):
                return None
        
        class MockDatabaseManager:
            def insert_detection_result(self, *args, **kwargs):
                logger.info("Mock database insert called")
        
        camera_manager = MockCameraManager()
        frames_queue = queue.Queue()
        db_manager = MockDatabaseManager()
        
        # Initialize detection thread
        detection_thread = SimpleDetectionThread(camera_manager, frames_queue, db_manager)
        logger.info("✅ Detection thread initialized successfully")
        
        return detection_thread
        
    except Exception as e:
        logger.error(f"Detection thread initialization failed: {e}")
        return None

def test_model_loading_in_thread():
    """Test model loading within the detection thread"""
    logger.info("=== Testing Model Loading in Thread ===")
    try:
        detection_thread = test_detection_thread_initialization()
        if not detection_thread:
            return False
        
        # Test model loading
        success = detection_thread.load_models()
        if success:
            logger.info("✅ Models loaded successfully in thread")
        else:
            logger.warning("⚠️ Model loading failed in thread")
        
        return success
        
    except Exception as e:
        logger.error(f"Model loading test failed: {e}")
        return False

def test_detection_thread_methods():
    """Test individual methods of SimpleDetectionThread"""
    logger.info("=== Testing Detection Thread Methods ===")
    try:
        detection_thread = test_detection_thread_initialization()
        if not detection_thread:
            return False
        
        # Test save_image_with_timestamp method
        import numpy as np
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :] = [255, 0, 0]  # Red image
        
        timestamp = datetime.now()
        filename = detection_thread.save_image_with_timestamp(test_image, "test")
        logger.info(f"✅ Test image saved: {filename}")
        
        # Test check_similarity method
        similarity = detection_thread.check_similarity("test_text", test_image)
        logger.info(f"✅ Similarity check result: {similarity}")
        
        # Test rearrange_detections method
        test_ocr_results = [{"label": "ABC", "bbox": [0, 0, 10, 10]}, {"label": "123", "bbox": [20, 0, 30, 10]}]
        rearranged = detection_thread.rearrange_detections(test_ocr_results)
        logger.info(f"✅ Rearranged OCR results: {rearranged}")
        
        return True
        
    except Exception as e:
        logger.error(f"Detection thread methods test failed: {e}")
        return False

def test_detection_thread_with_real_camera():
    """Test detection thread with real camera (if available)"""
    logger.info("=== Testing Detection Thread with Real Camera ===")
    try:
        from simple_detection_thread import SimpleDetectionThread
        from database_manager import DatabaseManager
        
        # Try to initialize real camera
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(main={"size": (640, 480)})
            picam2.configure(config)
            picam2.start()
            
            class RealCameraManager:
                def __init__(self, camera):
                    self.camera = camera
                
                def get_frame(self):
                    try:
                        frame = self.camera.capture_array()
                        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    except:
                        return None
            
            camera_manager = RealCameraManager(picam2)
            logger.info("✅ Real camera initialized")
            
        except Exception as e:
            logger.warning(f"Real camera not available: {e}")
            # Use mock camera
            class MockCameraManager:
                def get_frame(self):
                    return None
            camera_manager = MockCameraManager()
        
        # Initialize database
        db_manager = DatabaseManager()
        
        # Create frames queue
        frames_queue = queue.Queue()
        
        # Initialize detection thread
        detection_thread = SimpleDetectionThread(camera_manager, frames_queue, db_manager)
        
        # Load models
        models_loaded = detection_thread.load_models()
        logger.info(f"Models loaded: {models_loaded}")
        
        # Start detection thread
        detection_thread.start()
        logger.info("✅ Detection thread started")
        
        # Let it run for a few seconds
        time.sleep(5)
        
        # Stop detection thread
        detection_thread.stop()
        detection_thread.join(timeout=5)
        logger.info("✅ Detection thread stopped")
        
        # Clean up camera
        if 'picam2' in locals():
            picam2.stop()
            picam2.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Real camera test failed: {e}")
        return False

def test_config_integration():
    """Test if detection thread uses config correctly"""
    logger.info("=== Testing Config Integration ===")
    try:
        from config import HEF_MODEL_PATH, MODEL_ZOO_URL
        from simple_detection_thread import SimpleDetectionThread
        
        logger.info(f"Config values: HEF_MODEL_PATH={HEF_MODEL_PATH}, MODEL_ZOO_URL={MODEL_ZOO_URL}")
        
        # Test if detection thread can access these values
        detection_thread = test_detection_thread_initialization()
        if detection_thread:
            # The load_models method should use these config values
            success = detection_thread.load_models()
            logger.info(f"Model loading with config: {'✅ Success' if success else '❌ Failed'}")
            return success
        
        return False
        
    except Exception as e:
        logger.error(f"Config integration test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting SimpleDetectionThread Tests")
    
    # Test 1: Import
    if not test_simple_detection_thread_import():
        logger.error("❌ Import failed, stopping tests")
        return
    
    # Test 2: Initialization
    if not test_detection_thread_initialization():
        logger.error("❌ Initialization failed, stopping tests")
        return
    
    # Test 3: Model loading
    test_model_loading_in_thread()
    
    # Test 4: Methods
    test_detection_thread_methods()
    
    # Test 5: Config integration
    test_config_integration()
    
    # Test 6: Real camera (optional)
    test_detection_thread_with_real_camera()
    
    logger.info("🎉 All SimpleDetectionThread tests completed!")

if __name__ == "__main__":
    main() 