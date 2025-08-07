#!/usr/bin/env python3
"""
Test script for model loading and detection functionality
"""

import os
import sys
import logging
import numpy as np
import cv2
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_config_loading():
    """Test if config.py loads environment variables correctly"""
    logger.info("=== Testing Config Loading ===")
    try:
        from config import HEF_MODEL_PATH, MODEL_ZOO_URL, VEHICLE_DETECTION_MODEL, LICENSE_PLATE_DETECTION_MODEL, LICENSE_PLATE_OCR_MODEL
        
        logger.info(f"HEF_MODEL_PATH: {HEF_MODEL_PATH}")
        logger.info(f"MODEL_ZOO_URL: {MODEL_ZOO_URL}")
        logger.info(f"VEHICLE_DETECTION_MODEL: {VEHICLE_DETECTION_MODEL}")
        logger.info(f"LICENSE_PLATE_DETECTION_MODEL: {LICENSE_PLATE_DETECTION_MODEL}")
        logger.info(f"LICENSE_PLATE_OCR_MODEL: {LICENSE_PLATE_OCR_MODEL}")
        
        return True
    except Exception as e:
        logger.error(f"Config loading failed: {e}")
        return False

def test_degirum_import():
    """Test if degirum can be imported"""
    logger.info("=== Testing DeGirum Import ===")
    try:
        import degirum as dg
        logger.info(f"DeGirum version: {dg.__version__}")
        logger.info(f"DeGirum path: {dg.__file__}")
        logger.info(f"DeGirum CLOUD: {dg.CLOUD}")
        logger.info(f"DeGirum LOCAL: {dg.LOCAL}")
        return True
    except Exception as e:
        logger.error(f"DeGirum import failed: {e}")
        return False

def test_model_loading():
    """Test loading individual models"""
    logger.info("=== Testing Model Loading ===")
    
    try:
        import degirum as dg
        from config import HEF_MODEL_PATH, MODEL_ZOO_URL, VEHICLE_DETECTION_MODEL, LICENSE_PLATE_DETECTION_MODEL, LICENSE_PLATE_OCR_MODEL
        
        models = {}
        
        # Test vehicle detection model
        if VEHICLE_DETECTION_MODEL:
            logger.info(f"Loading vehicle detection model: {VEHICLE_DETECTION_MODEL}")
            models['vehicle'] = dg.load_model(
                model_name=VEHICLE_DETECTION_MODEL,
                inference_host_address=HEF_MODEL_PATH,
                zoo_url=MODEL_ZOO_URL
            )
            logger.info("✅ Vehicle detection model loaded successfully")
        
        # Test license plate detection model
        if LICENSE_PLATE_DETECTION_MODEL:
            logger.info(f"Loading license plate detection model: {LICENSE_PLATE_DETECTION_MODEL}")
            models['lp_detection'] = dg.load_model(
                model_name=LICENSE_PLATE_DETECTION_MODEL,
                inference_host_address=HEF_MODEL_PATH,
                zoo_url=MODEL_ZOO_URL,
                overlay_color=[(255, 255, 0), (0, 255, 0)]
            )
            logger.info("✅ License plate detection model loaded successfully")
        
        # Test license plate OCR model
        if LICENSE_PLATE_OCR_MODEL:
            logger.info(f"Loading license plate OCR model: {LICENSE_PLATE_OCR_MODEL}")
            models['lp_ocr'] = dg.load_model(
                model_name=LICENSE_PLATE_OCR_MODEL,
                inference_host_address=HEF_MODEL_PATH,
                zoo_url=MODEL_ZOO_URL,
                output_use_regular_nms=False,
                output_confidence_threshold=0.1
            )
            logger.info("✅ License plate OCR model loaded successfully")
        
        logger.info(f"Total models loaded: {len(models)}")
        return models
        
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        return {}

def test_easyocr():
    """Test EasyOCR functionality"""
    logger.info("=== Testing EasyOCR ===")
    try:
        import easyocr
        from config import EASYOCR_LANGUAGES
        
        logger.info(f"Loading EasyOCR with languages: {EASYOCR_LANGUAGES}")
        reader = easyocr.Reader(EASYOCR_LANGUAGES)
        logger.info("✅ EasyOCR loaded successfully")
        return reader
    except Exception as e:
        logger.error(f"EasyOCR loading failed: {e}")
        return None

def test_camera():
    """Test camera functionality"""
    logger.info("=== Testing Camera ===")
    try:
        from picamera2 import Picamera2
        
        logger.info("Initializing Picamera2...")
        picam2 = Picamera2()
        
        # Create configuration
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        
        logger.info("Starting camera...")
        picam2.start()
        
        # Capture a test frame
        logger.info("Capturing test frame...")
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        logger.info(f"Frame captured: {frame_bgr.shape}")
        
        # Save test frame
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_image_path = f"test_frame_{timestamp}.jpg"
        cv2.imwrite(test_image_path, frame_bgr)
        logger.info(f"Test frame saved: {test_image_path}")
        
        # Stop camera
        picam2.stop()
        picam2.close()
        
        logger.info("✅ Camera test completed successfully")
        return frame_bgr
        
    except Exception as e:
        logger.error(f"Camera test failed: {e}")
        return None

def test_detection_pipeline(frame, models, ocr_reader):
    """Test the complete detection pipeline"""
    logger.info("=== Testing Detection Pipeline ===")
    
    if frame is None:
        logger.error("No frame available for testing")
        return
    
    try:
        # Test vehicle detection
        if 'vehicle' in models:
            logger.info("Testing vehicle detection...")
            vehicle_model = models['vehicle']
            
            # Resize frame for model input
            if hasattr(vehicle_model, 'input_shape'):
                target_size = (vehicle_model.input_shape[0][1], vehicle_model.input_shape[0][2])
            else:
                target_size = (640, 640)
            
            # Simple resize (you might want to use resize_with_letterbox)
            resized_frame = cv2.resize(frame, target_size)
            
            # Perform detection
            results = vehicle_model(resized_frame)
            vehicle_boxes = getattr(results, "results", [])
            
            logger.info(f"Vehicle detection results: {len(vehicle_boxes)} vehicles detected")
            
            # Draw bounding boxes
            frame_with_boxes = frame.copy()
            for box in vehicle_boxes:
                bbox = box.get("bbox")
                if bbox and len(bbox) == 4:
                    x_min, y_min, x_max, y_max = map(int, bbox)
                    cv2.rectangle(frame_with_boxes, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            
            # Save result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_path = f"test_detection_result_{timestamp}.jpg"
            cv2.imwrite(result_path, frame_with_boxes)
            logger.info(f"Detection result saved: {result_path}")
        
        # Test license plate detection
        if 'lp_detection' in models:
            logger.info("Testing license plate detection...")
            lp_model = models['lp_detection']
            
            # Use same resized frame
            results = lp_model(resized_frame)
            lp_boxes = getattr(results, "results", [])
            
            logger.info(f"License plate detection results: {len(lp_boxes)} plates detected")
        
        # Test OCR
        if ocr_reader and 'lp_ocr' in models:
            logger.info("Testing OCR...")
            ocr_model = models['lp_ocr']
            
            # Test with a sample text area (you might want to crop actual license plates)
            sample_region = frame[100:200, 200:400]  # Sample region
            
            # Test Hailo OCR
            try:
                ocr_results = ocr_model.predict(sample_region)
                logger.info(f"Hailo OCR results: {ocr_results}")
            except Exception as e:
                logger.warning(f"Hailo OCR failed: {e}")
            
            # Test EasyOCR
            try:
                rgb_region = cv2.cvtColor(sample_region, cv2.COLOR_BGR2RGB)
                easyocr_results = ocr_reader.readtext(rgb_region)
                logger.info(f"EasyOCR results: {easyocr_results}")
            except Exception as e:
                logger.warning(f"EasyOCR failed: {e}")
        
        logger.info("✅ Detection pipeline test completed")
        
    except Exception as e:
        logger.error(f"Detection pipeline test failed: {e}")

def main():
    """Main test function"""
    logger.info("🚀 Starting Model and Detection Tests")
    
    # Test 1: Config loading
    if not test_config_loading():
        logger.error("❌ Config loading failed, stopping tests")
        return
    
    # Test 2: DeGirum import
    if not test_degirum_import():
        logger.error("❌ DeGirum import failed, stopping tests")
        return
    
    # Test 3: Model loading
    models = test_model_loading()
    if not models:
        logger.warning("⚠️ No models loaded, some tests will be skipped")
    
    # Test 4: EasyOCR
    ocr_reader = test_easyocr()
    if not ocr_reader:
        logger.warning("⚠️ EasyOCR not available, OCR tests will be skipped")
    
    # Test 5: Camera
    frame = test_camera()
    if not frame:
        logger.warning("⚠️ Camera not available, detection tests will be skipped")
    
    # Test 6: Detection pipeline
    if frame and models:
        test_detection_pipeline(frame, models, ocr_reader)
    
    logger.info("🎉 All tests completed!")

if __name__ == "__main__":
    main() 