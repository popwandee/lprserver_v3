#!/usr/bin/env python3
"""
Test script for Auto Startup functionality in AI Camera v1.3
Tests the complete startup sequence: System → Camera → Detection
"""

import sys
import os
import time
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

def test_config_auto_startup():
    """Test auto startup configuration"""
    logger.info("=== Testing Auto Startup Configuration ===")
    try:
        from v1_3.src.core.config import (
            AUTO_START_CAMERA, AUTO_START_STREAMING, AUTO_START_DETECTION, STARTUP_DELAY
        )
        
        logger.info(f"✅ AUTO_START_CAMERA: {AUTO_START_CAMERA}")
        logger.info(f"✅ AUTO_START_STREAMING: {AUTO_START_STREAMING}")
        logger.info(f"✅ AUTO_START_DETECTION: {AUTO_START_DETECTION}")
        logger.info(f"✅ STARTUP_DELAY: {STARTUP_DELAY} seconds")
        
        return True
    except Exception as e:
        logger.error(f"❌ Config test failed: {e}")
        return False

def test_dependency_container():
    """Test dependency container initialization"""
    logger.info("=== Testing Dependency Container ===")
    try:
        from v1_3.src.core.dependency_container import get_container, get_service
        
        container = get_container()
        logger.info("✅ Dependency container initialized")
        
        # Check services availability
        camera_manager = get_service('camera_manager')
        detection_manager = get_service('detection_manager')
        
        logger.info(f"✅ Camera Manager available: {camera_manager is not None}")
        logger.info(f"✅ Detection Manager available: {detection_manager is not None}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Dependency container test failed: {e}")
        return False

def test_camera_auto_startup():
    """Test camera manager auto startup"""
    logger.info("=== Testing Camera Auto Startup ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            logger.error("❌ Camera manager not available")
            return False
        
        logger.info("🚀 Initializing camera manager...")
        success = camera_manager.initialize()
        
        if success:
            logger.info("✅ Camera manager initialized successfully")
            
            # Check status
            status = camera_manager.get_status()
            logger.info(f"📊 Camera Status: {status}")
            
            # Check if camera is running and streaming
            is_initialized = status.get('initialized', False)
            is_streaming = status.get('streaming', False)
            
            logger.info(f"✅ Camera initialized: {is_initialized}")
            logger.info(f"✅ Camera streaming: {is_streaming}")
            
            return is_initialized and is_streaming
        else:
            logger.error("❌ Camera manager initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Camera auto startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_auto_startup():
    """Test detection manager auto startup"""
    logger.info("=== Testing Detection Auto Startup ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            logger.error("❌ Detection manager not available")
            return False
        
        logger.info("🤖 Initializing detection manager...")
        success = detection_manager.initialize()
        
        if success:
            logger.info("✅ Detection manager initialized successfully")
            
            # Check status
            status = detection_manager.get_status()
            logger.info(f"📊 Detection Status: {status}")
            
            # Check if detection is running
            is_running = status.get('is_running', False)
            models_loaded = status.get('models_loaded', False)
            
            logger.info(f"✅ Models loaded: {models_loaded}")
            logger.info(f"✅ Detection running: {is_running}")
            
            return models_loaded  # Detection may auto-start or not based on config
        else:
            logger.error("❌ Detection manager initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Detection auto startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_status():
    """Test complete system status after auto startup"""
    logger.info("=== Testing Complete System Status ===")
    try:
        from v1_3.src.core.dependency_container import get_service
        
        camera_manager = get_service('camera_manager')
        detection_manager = get_service('detection_manager')
        
        if camera_manager and detection_manager:
            camera_status = camera_manager.get_status()
            detection_status = detection_manager.get_status()
            
            logger.info("📊 Complete System Status:")
            logger.info(f"📸 Camera: {camera_status}")
            logger.info(f"🤖 Detection: {detection_status}")
            
            # Check if everything is ready for operation
            camera_ready = camera_status.get('initialized', False) and camera_status.get('streaming', False)
            detection_ready = detection_status.get('models_loaded', False)
            
            logger.info(f"✅ System ready for operation: Camera={camera_ready}, Detection={detection_ready}")
            
            return camera_ready and detection_ready
        else:
            logger.error("❌ Services not available")
            return False
            
    except Exception as e:
        logger.error(f"❌ Complete status test failed: {e}")
        return False

def main():
    """Run all auto startup tests"""
    logger.info("🚀 Starting AI Camera v1.3 Auto Startup Tests")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Auto Startup Configuration", test_config_auto_startup),
        ("Dependency Container", test_dependency_container),
        ("Camera Auto Startup", test_camera_auto_startup),
        ("Detection Auto Startup", test_detection_auto_startup),
        ("Complete System Status", test_complete_status),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        try:
            results[test_name] = test_func()
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 AUTO STARTUP TEST SUMMARY")
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
        logger.info("🎉 All tests passed! Auto startup is working correctly.")
        logger.info("🚀 System should automatically start: Camera → Streaming → Detection")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Check configuration and logs.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
