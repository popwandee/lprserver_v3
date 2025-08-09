#!/usr/bin/env python3
"""
Test script to verify attribute fixes in AI Camera v1.3
Tests that CameraManager and DetectionManager have correct attributes
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
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_camera_manager_attributes():
    """Test CameraManager attributes"""
    logger.info("=== Testing CameraManager Attributes ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            logger.error("❌ Camera manager not available")
            return False
        
        # Test required attributes
        required_attrs = [
            'auto_start_enabled',
            'auto_streaming_enabled',
            'camera_handler',
            'logger'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(camera_manager, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            logger.error(f"❌ Missing attributes: {missing_attrs}")
            return False
        else:
            logger.info("✅ All required attributes present")
        
        # Test that is_active method is NOT needed (we use get_status instead)
        if hasattr(camera_manager, 'is_active'):
            logger.info("⚠️  is_active method exists (not needed)")
        else:
            logger.info("✅ is_active method correctly not present")
        
        # Test get_status method works
        try:
            status = camera_manager.get_status()
            logger.info(f"✅ get_status() works: {type(status)}")
            
            # Check if status has required keys
            required_keys = ['initialized', 'streaming']
            missing_keys = [key for key in required_keys if key not in status]
            
            if missing_keys:
                logger.warning(f"⚠️  Status missing keys: {missing_keys}")
            else:
                logger.info("✅ Status has all required keys")
                
        except Exception as e:
            logger.error(f"❌ get_status() failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CameraManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_manager_attributes():
    """Test DetectionManager attributes"""
    logger.info("=== Testing DetectionManager Attributes ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            logger.error("❌ Detection manager not available")
            return False
        
        # Test required attributes
        required_attrs = [
            'auto_start_enabled',  # Should be this, not 'auto_start'
            'detection_processor',
            'database_manager',
            'logger',
            'is_running',
            'detection_interval'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(detection_manager, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            logger.error(f"❌ Missing attributes: {missing_attrs}")
            return False
        else:
            logger.info("✅ All required attributes present")
        
        # Test that old 'auto_start' attribute is NOT present
        if hasattr(detection_manager, 'auto_start'):
            logger.warning("⚠️  Old 'auto_start' attribute still exists")
        else:
            logger.info("✅ Old 'auto_start' attribute correctly removed")
        
        # Test get_status method works
        try:
            status = detection_manager.get_status()
            logger.info(f"✅ get_status() works: {type(status)}")
            
            # Check if status has auto_start key (from auto_start_enabled)
            if 'auto_start' in status:
                logger.info(f"✅ Status contains auto_start: {status['auto_start']}")
            else:
                logger.warning("⚠️  Status missing auto_start key")
                
        except Exception as e:
            logger.error(f"❌ get_status() failed: {e}")
            return False
        
        # Test _is_camera_ready method
        try:
            camera_manager = get_service('camera_manager')
            if camera_manager:
                result = detection_manager._is_camera_ready(camera_manager)
                logger.info(f"✅ _is_camera_ready() works: {result}")
            else:
                logger.warning("⚠️  Cannot test _is_camera_ready() - no camera manager")
        except Exception as e:
            logger.error(f"❌ _is_camera_ready() failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DetectionManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_loop_simulation():
    """Test detection loop logic without actually running it"""
    logger.info("=== Testing Detection Loop Logic ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        detection_manager = get_service('detection_manager')
        camera_manager = get_service('camera_manager')
        
        if not detection_manager or not camera_manager:
            logger.error("❌ Required services not available")
            return False
        
        # Simulate the problematic line from detection loop
        try:
            # This was the problematic line: camera_manager.is_active()
            # Now it should be: detection_manager._is_camera_ready(camera_manager)
            is_ready = detection_manager._is_camera_ready(camera_manager)
            logger.info(f"✅ Camera ready check works: {is_ready}")
            
            # Test that the old method would fail
            try:
                # This should fail if we fixed it correctly
                is_active = camera_manager.is_active()
                logger.warning("⚠️  Old is_active() method still exists!")
                return False
            except AttributeError:
                logger.info("✅ Old is_active() method correctly removed")
            
        except Exception as e:
            logger.error(f"❌ Detection loop simulation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Detection loop test failed: {e}")
        return False

def main():
    """Run all attribute fix tests"""
    logger.info("🔧 Starting AI Camera v1.3 Attribute Fix Tests")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("CameraManager Attributes", test_camera_manager_attributes),
        ("DetectionManager Attributes", test_detection_manager_attributes),
        ("Detection Loop Logic", test_detection_loop_simulation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📊 ATTRIBUTE FIX TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Attribute fixes are working correctly.")
        logger.info("🚀 Detection loop should no longer have attribute errors")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Check the fixes.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
