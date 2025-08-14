#!/usr/bin/env python3
"""
Test script for Detection Processor Component

This script tests the DetectionProcessor component with various Hailo models
to ensure proper functionality and performance.

Usage:
    python test_detection_processor.py [--model MODEL_NAME] [--frames NUM_FRAMES]

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from components.detection_processor import (
    DetectionProcessor,
    DetectionResult,
    create_detection_processor
)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        level (str): Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('detection_test.log')
        ]
    )
    return logging.getLogger(__name__)


def test_model_loading(processor: DetectionProcessor, logger: logging.Logger):
    """
    Test model loading functionality.
    
    Args:
        processor (DetectionProcessor): Detection processor instance
        logger (logging.Logger): Logger instance
    """
    logger.info("=== Testing Model Loading ===")
    
    # Get available models
    available_models = processor.model_manager.get_available_models()
    logger.info(f"Available models: {available_models}")
    
    # Test loading each model
    for model_name in available_models:
        logger.info(f"Testing model: {model_name}")
        
        try:
            success = processor.model_manager.load_model(model_name)
            if success:
                logger.info(f"✓ Model {model_name} loaded successfully")
                
                # Check if model is in loaded models
                loaded_models = processor.model_manager.get_loaded_models()
                if model_name in loaded_models:
                    logger.info(f"✓ Model {model_name} confirmed in loaded models")
                else:
                    logger.error(f"✗ Model {model_name} not found in loaded models")
            else:
                logger.error(f"✗ Failed to load model {model_name}")
                
        except Exception as e:
            logger.error(f"✗ Error loading model {model_name}: {e}")


def test_camera_initialization(processor: DetectionProcessor, logger: logging.Logger):
    """
    Test camera initialization.
    
    Args:
        processor (DetectionProcessor): Detection processor instance
        logger (logging.Logger): Logger instance
        
    Returns:
        bool: True if camera initialized successfully
    """
    logger.info("=== Testing Camera Initialization ===")
    
    try:
        success = processor.initialize_camera(resolution=(1280, 960), framerate=30)
        if success:
            logger.info("✓ Camera initialized successfully")
            return True
        else:
            logger.error("✗ Failed to initialize camera")
            return False
    except Exception as e:
        logger.error(f"✗ Error initializing camera: {e}")
        return False


def test_detection_with_camera(processor: DetectionProcessor, 
                              model_name: str, 
                              num_frames: int,
                              logger: logging.Logger):
    """
    Test detection using camera input.
    
    Args:
        processor (DetectionProcessor): Detection processor instance
        model_name (str): Name of the model to test
        num_frames (int): Number of frames to process
        logger (logging.Logger): Logger instance
    """
    logger.info(f"=== Testing Detection with Camera (Model: {model_name}) ===")
    
    if not processor.camera:
        logger.error("✗ Camera not initialized")
        return
    
    if model_name not in processor.model_manager.get_loaded_models():
        logger.error(f"✗ Model {model_name} not loaded")
        return
    
    frame_count = 0
    total_detections = 0
    start_time = time.time()
    
    try:
        while frame_count < num_frames:
            logger.info(f"Processing frame {frame_count + 1}/{num_frames}")
            
            # Run detection
            detections = processor.detect_objects(model_name)
            
            # Log results
            if detections:
                logger.info(f"  Found {len(detections)} objects:")
                for detection in detections:
                    logger.info(f"    - {detection.class_name}: {detection.confidence:.2f}")
                total_detections += len(detections)
            else:
                logger.info("  No objects detected")
            
            frame_count += 1
            
            # Small delay between frames
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("Detection interrupted by user")
    except Exception as e:
        logger.error(f"Error during detection: {e}")
    
    # Calculate statistics
    end_time = time.time()
    total_time = end_time - start_time
    fps = frame_count / total_time if total_time > 0 else 0
    
    logger.info(f"Detection completed:")
    logger.info(f"  Frames processed: {frame_count}")
    logger.info(f"  Total detections: {total_detections}")
    logger.info(f"  Total time: {total_time:.2f} seconds")
    logger.info(f"  Average FPS: {fps:.2f}")
    
    # Get processor statistics
    stats = processor.get_processing_stats()
    logger.info(f"Processor stats: {stats}")


def test_static_image_detection(processor: DetectionProcessor,
                               model_name: str,
                               logger: logging.Logger):
    """
    Test detection with a static test image.
    
    Args:
        processor (DetectionProcessor): Detection processor instance
        model_name (str): Name of the model to test
        logger (logging.Logger): Logger instance
    """
    logger.info(f"=== Testing Static Image Detection (Model: {model_name}) ===")
    
    # Create a simple test image (you can replace this with a real image file)
    import numpy as np
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    try:
        detections = processor.detect_objects(model_name, image=test_image)
        
        if detections:
            logger.info(f"Found {len(detections)} objects in test image:")
            for detection in detections:
                logger.info(f"  - {detection.class_name}: {detection.confidence:.2f}")
        else:
            logger.info("No objects detected in test image")
            
    except Exception as e:
        logger.error(f"Error in static image detection: {e}")


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test Detection Processor Component")
    parser.add_argument("--model", default="coco", 
                       help="Model to test (coco, car, lp, lp_ocr)")
    parser.add_argument("--frames", type=int, default=5,
                       help="Number of frames to process")
    parser.add_argument("--log-level", default="INFO",
                       help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    parser.add_argument("--no-camera", action="store_true",
                       help="Skip camera tests")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting Detection Processor Test")
    
    # Create detection processor
    processor = create_detection_processor(logger)
    
    try:
        # Test 1: Model loading
        test_model_loading(processor, logger)
        
        # Test 2: Camera initialization (if not skipped)
        camera_available = False
        if not args.no_camera:
            camera_available = test_camera_initialization(processor, logger)
        
        # Test 3: Static image detection
        test_static_image_detection(processor, args.model, logger)
        
        # Test 4: Camera-based detection (if camera is available)
        if camera_available:
            test_detection_with_camera(processor, args.model, args.frames, logger)
        else:
            logger.info("Skipping camera-based detection tests")
        
        logger.info("=== Test Summary ===")
        logger.info("✓ All tests completed")
        
        # Final statistics
        stats = processor.get_processing_stats()
        logger.info(f"Final processor stats: {stats}")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return 1
    finally:
        # Cleanup
        processor.cleanup()
        logger.info("Detection processor cleaned up")
    
    return 0


if __name__ == "__main__":
    exit(main())
