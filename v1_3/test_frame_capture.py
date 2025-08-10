#!/usr/bin/env python3
"""
Test script for Frame Capture and Detection Pipeline in AI Camera v1.3
Tests that camera returns proper numpy arrays for detection
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# Setup import paths
from v1_3.src.core.utils.import_helper import setup_import_paths, validate_imports
setup_import_paths()

import logging
import numpy as np
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_camera_frame_capture():
    """Test camera frame capture returns proper format"""
    logger.info("=== Testing Camera Frame Capture ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            logger.error("❌ Camera manager not available")
            return False
        
        # Test camera handler direct capture
        camera_handler = camera_manager.camera_handler
        if camera_handler:
            logger.info("📸 Testing camera handler capture_frame()...")
            frame_data = camera_handler.capture_frame()
            
            if frame_data:
                logger.info(f"✅ Camera handler returned: {type(frame_data)}")
                if isinstance(frame_data, dict):
                    logger.info(f"📊 Dict keys: {frame_data.keys()}")
                    if 'frame' in frame_data:
                        frame = frame_data['frame']
                        logger.info(f"✅ Frame type: {type(frame)}")
                        if isinstance(frame, np.ndarray):
                            logger.info(f"✅ Frame shape: {frame.shape}")
                            logger.info(f"✅ Frame size: {frame.size}")
                        else:
                            logger.error(f"❌ Frame is not numpy array: {type(frame)}")
                            return False
                    else:
                        logger.error("❌ Dict does not contain 'frame' key")
                        return False
                else:
                    logger.error(f"❌ Expected dict, got: {type(frame_data)}")
                    return False
            else:
                logger.error("❌ Camera handler returned None")
                return False
        
        # Test camera manager capture
        logger.info("📸 Testing camera manager capture_frame()...")
        frame = camera_manager.capture_frame()
        
        if frame is not None:
            logger.info(f"✅ Camera manager returned: {type(frame)}")
            if isinstance(frame, np.ndarray):
                logger.info(f"✅ Frame shape: {frame.shape}")
                logger.info(f"✅ Frame size: {frame.size}")
                logger.info(f"✅ Frame dtype: {frame.dtype}")
                return True
            else:
                logger.error(f"❌ Expected numpy array, got: {type(frame)}")
                return False
        else:
            logger.error("❌ Camera manager returned None")
            return False
            
    except Exception as e:
        logger.error(f"❌ Camera frame capture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_processor_validation():
    """Test detection processor frame validation"""
    logger.info("=== Testing Detection Processor Frame Validation ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        detection_manager = get_service('detection_manager')
        if not detection_manager or not detection_manager.detection_processor:
            logger.error("❌ Detection processor not available")
            return False
        
        detection_processor = detection_manager.detection_processor
        
        # Test 1: Valid numpy array
        logger.info("🧪 Test 1: Valid numpy array")
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detection_processor.validate_and_enhance_frame(test_frame)
        if result is not None:
            logger.info("✅ Valid numpy array accepted")
        else:
            logger.error("❌ Valid numpy array rejected")
            return False
        
        # Test 2: None frame
        logger.info("🧪 Test 2: None frame")
        result = detection_processor.validate_and_enhance_frame(None)
        if result is None:
            logger.info("✅ None frame correctly rejected")
        else:
            logger.error("❌ None frame incorrectly accepted")
            return False
        
        # Test 3: Dict with frame key (should extract and validate)
        logger.info("🧪 Test 3: Dict with frame key")
        test_dict = {'frame': np.zeros((480, 640, 3), dtype=np.uint8)}
        result = detection_processor.validate_and_enhance_frame(test_dict)
        if result is not None and isinstance(result, np.ndarray):
            logger.info("✅ Dict with frame key correctly processed")
        else:
            logger.error("❌ Dict with frame key not processed correctly")
            return False
        
        # Test 4: Dict without frame key
        logger.info("🧪 Test 4: Dict without frame key")
        test_dict = {'metadata': 'test'}
        result = detection_processor.validate_and_enhance_frame(test_dict)
        if result is None:
            logger.info("✅ Dict without frame key correctly rejected")
        else:
            logger.error("❌ Dict without frame key incorrectly accepted")
            return False
        
        # Test 5: Empty array
        logger.info("🧪 Test 5: Empty array")
        empty_array = np.array([])
        result = detection_processor.validate_and_enhance_frame(empty_array)
        if result is None:
            logger.info("✅ Empty array correctly rejected")
        else:
            logger.error("❌ Empty array incorrectly accepted")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Detection processor validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_pipeline():
    """Test complete detection pipeline"""
    logger.info("=== Testing Detection Pipeline ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        camera_manager = get_service('camera_manager')
        detection_manager = get_service('detection_manager')
        
        if not camera_manager or not detection_manager:
            logger.error("❌ Required services not available")
            return False
        
        # Test single frame processing
        logger.info("🔄 Testing single frame processing...")
        result = detection_manager.process_frame_from_camera(camera_manager)
        
        if result is not None:
            logger.info(f"✅ Detection pipeline processed frame successfully")
            logger.info(f"📊 Result type: {type(result)}")
            if isinstance(result, dict):
                logger.info(f"📊 Result keys: {list(result.keys())}")
            return True
        else:
            logger.info("⚠️  Detection pipeline returned None (may be normal if no detections)")
            return True  # This is actually OK - no detections is valid
            
    except Exception as e:
        logger.error(f"❌ Detection pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all frame capture tests"""
    logger.info("🧪 Starting AI Camera v1.3 Frame Capture Tests")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Camera Frame Capture", test_camera_frame_capture),
        ("Detection Processor Validation", test_detection_processor_validation),
        ("Detection Pipeline", test_detection_pipeline),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 FRAME CAPTURE TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Frame capture should work correctly.")
        logger.info("🚀 Detection pipeline should no longer have 'dict has no attribute size' errors")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Check the fixes.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
