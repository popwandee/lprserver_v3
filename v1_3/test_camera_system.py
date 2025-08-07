#!/usr/bin/env python3
"""
Test script for Camera Handler and Camera Manager components.

This script tests the camera system components:
- CameraHandler: Low-level camera operations
- CameraManager: High-level camera management

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.utils.logging_config import setup_logging, get_logger
from src.components.camera_handler import CameraHandler
from src.services.camera_manager import CameraManager


def test_camera_handler():
    """Test CameraHandler component."""
    logger = get_logger(__name__)
    logger.info("=" * 50)
    logger.info("Testing CameraHandler Component")
    logger.info("=" * 50)
    
    # Create camera handler
    camera_handler = CameraHandler(logger=logger)
    
    try:
        # Test initialization
        logger.info("1. Testing camera initialization...")
        success = camera_handler.initialize_camera()
        if success:
            logger.info("✓ Camera initialization successful")
        else:
            logger.error("✗ Camera initialization failed")
            return False
        
        # Test getting status
        logger.info("2. Testing status retrieval...")
        status = camera_handler.get_status()
        logger.info(f"Camera status: {status}")
        
        # Test getting configuration
        logger.info("3. Testing configuration retrieval...")
        config = camera_handler.get_configuration()
        logger.info(f"Camera configuration: {config}")
        
        # Test getting controls
        logger.info("4. Testing controls retrieval...")
        controls = camera_handler.get_controls()
        logger.info(f"Available controls: {list(controls.keys())}")
        
        # Test starting camera
        logger.info("5. Testing camera start...")
        success = camera_handler.start_camera()
        if success:
            logger.info("✓ Camera start successful")
        else:
            logger.error("✗ Camera start failed")
            return False
        
        # Wait for camera to stabilize
        time.sleep(2)
        
        # Test frame capture
        logger.info("6. Testing frame capture...")
        frame_data = camera_handler.capture_frame()
        if frame_data:
            logger.info(f"✓ Frame captured: {frame_data['size']} - {frame_data['format']}")
        else:
            logger.error("✗ Frame capture failed")
            return False
        
        # Test metadata capture
        logger.info("7. Testing metadata capture...")
        metadata = camera_handler.get_metadata()
        if metadata:
            logger.info(f"✓ Metadata captured: {len(metadata)} fields")
        else:
            logger.error("✗ Metadata capture failed")
        
        # Test low-res frame capture
        logger.info("8. Testing low-res frame capture...")
        lores_data = camera_handler.capture_lores_frame()
        if lores_data:
            logger.info(f"✓ Low-res frame captured: {lores_data['size']} - {lores_data['format']}")
        else:
            logger.error("✗ Low-res frame capture failed")
        
        # Test autofocus (if available)
        logger.info("9. Testing autofocus...")
        try:
            success = camera_handler.autofocus_cycle()
            if success:
                logger.info("✓ Autofocus cycle successful")
            else:
                logger.warning("⚠ Autofocus cycle failed (may not be supported)")
        except Exception as e:
            logger.warning(f"⚠ Autofocus not available: {e}")
        
        # Test stopping camera
        logger.info("10. Testing camera stop...")
        success = camera_handler.stop_camera()
        if success:
            logger.info("✓ Camera stop successful")
        else:
            logger.error("✗ Camera stop failed")
        
        # Test cleanup
        logger.info("11. Testing cleanup...")
        camera_handler.cleanup()
        logger.info("✓ Cleanup completed")
        
        logger.info("=" * 50)
        logger.info("CameraHandler tests completed successfully!")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"CameraHandler test failed: {e}")
        return False


def test_camera_manager():
    """Test CameraManager service."""
    logger = get_logger(__name__)
    logger.info("=" * 50)
    logger.info("Testing CameraManager Service")
    logger.info("=" * 50)
    
    # Create camera handler and manager
    camera_handler = CameraHandler(logger=logger)
    camera_manager = CameraManager(camera_handler=camera_handler, logger=logger)
    
    try:
        # Test initialization
        logger.info("1. Testing camera manager initialization...")
        success = camera_manager.initialize()
        if success:
            logger.info("✓ Camera manager initialization successful")
        else:
            logger.error("✗ Camera manager initialization failed")
            return False
        
        # Test getting status
        logger.info("2. Testing status retrieval...")
        status = camera_manager.get_status()
        logger.info(f"Manager status: {status}")
        
        # Test getting configuration
        logger.info("3. Testing configuration retrieval...")
        config = camera_manager.get_configuration()
        logger.info(f"Manager configuration: {config}")
        
        # Test getting available settings
        logger.info("4. Testing available settings...")
        settings = camera_manager.get_available_settings()
        logger.info(f"Available settings: {list(settings.keys())}")
        
        # Test starting streaming
        logger.info("5. Testing streaming start...")
        success = camera_manager.start()
        if success:
            logger.info("✓ Streaming start successful")
        else:
            logger.error("✗ Streaming start failed")
            return False
        
        # Wait for streaming to start
        time.sleep(3)
        
        # Test frame retrieval
        logger.info("6. Testing frame retrieval...")
        frame_data = camera_manager.get_frame(timeout=5.0)
        if frame_data:
            logger.info(f"✓ Frame retrieved: {frame_data['size']} - {frame_data['format']}")
        else:
            logger.error("✗ Frame retrieval failed")
            return False
        
        # Test metadata retrieval
        logger.info("7. Testing metadata retrieval...")
        metadata = camera_manager.get_metadata(timeout=1.0)
        if metadata:
            logger.info(f"✓ Metadata retrieved: {len(metadata)} fields")
        else:
            logger.warning("⚠ Metadata retrieval failed")
        
        # Test image capture
        logger.info("8. Testing image capture...")
        image_data = camera_manager.capture_image()
        if image_data:
            logger.info(f"✓ Image captured: {image_data['size']}")
            if 'saved_path' in image_data:
                logger.info(f"  Saved to: {image_data['saved_path']}")
        else:
            logger.error("✗ Image capture failed")
        
        # Test frame callback
        logger.info("9. Testing frame callback...")
        callback_called = False
        
        def test_callback(frame_data):
            nonlocal callback_called
            callback_called = True
            logger.info(f"  Callback received frame: {frame_data['size']}")
        
        camera_manager.add_frame_callback(test_callback)
        time.sleep(2)  # Wait for callback to be called
        
        if callback_called:
            logger.info("✓ Frame callback working")
        else:
            logger.warning("⚠ Frame callback not called")
        
        # Test health check
        logger.info("10. Testing health check...")
        health = camera_manager.health_check()
        logger.info(f"Health status: {health['status']}")
        for check_name, check_result in health['checks'].items():
            logger.info(f"  {check_name}: {check_result['status']} - {check_result['message']}")
        
        # Test stopping streaming
        logger.info("11. Testing streaming stop...")
        success = camera_manager.stop()
        if success:
            logger.info("✓ Streaming stop successful")
        else:
            logger.error("✗ Streaming stop failed")
        
        # Test restart
        logger.info("12. Testing restart...")
        success = camera_manager.restart()
        if success:
            logger.info("✓ Restart successful")
            camera_manager.stop()  # Stop again
        else:
            logger.error("✗ Restart failed")
        
        # Test cleanup
        logger.info("13. Testing cleanup...")
        camera_manager.cleanup()
        logger.info("✓ Cleanup completed")
        
        logger.info("=" * 50)
        logger.info("CameraManager tests completed successfully!")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"CameraManager test failed: {e}")
        return False


def test_integration():
    """Test integration between CameraHandler and CameraManager."""
    logger = get_logger(__name__)
    logger.info("=" * 50)
    logger.info("Testing Integration")
    logger.info("=" * 50)
    
    try:
        # Create components
        camera_handler = CameraHandler(logger=logger)
        camera_manager = CameraManager(camera_handler=camera_handler, logger=logger)
        
        # Initialize and start
        logger.info("1. Initializing and starting camera system...")
        if not camera_manager.initialize():
            logger.error("✗ Initialization failed")
            return False
        
        if not camera_manager.start():
            logger.error("✗ Start failed")
            return False
        
        # Test continuous operation
        logger.info("2. Testing continuous operation for 10 seconds...")
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 10:
            frame_data = camera_manager.get_frame(timeout=1.0)
            if frame_data:
                frame_count += 1
                if frame_count % 30 == 0:  # Log every 30 frames
                    logger.info(f"  Processed {frame_count} frames...")
            time.sleep(0.1)
        
        logger.info(f"✓ Processed {frame_count} frames in 10 seconds")
        
        # Test status during operation
        logger.info("3. Testing status during operation...")
        status = camera_manager.get_status()
        logger.info(f"  Streaming: {status['streaming']}")
        logger.info(f"  Frame count: {status['frame_count']}")
        logger.info(f"  Average FPS: {status.get('average_fps', 0):.1f}")
        
        # Stop and cleanup
        logger.info("4. Stopping and cleaning up...")
        camera_manager.stop()
        camera_manager.cleanup()
        
        logger.info("=" * 50)
        logger.info("Integration tests completed successfully!")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return False


def main():
    """Main test function."""
    # Setup logging
    logger = setup_logging(level="INFO")
    
    logger.info("Starting Camera System Tests")
    logger.info("=" * 60)
    
    # Test results
    results = {}
    
    # Test CameraHandler
    logger.info("\nTesting CameraHandler Component...")
    results['camera_handler'] = test_camera_handler()
    
    # Test CameraManager
    logger.info("\nTesting CameraManager Service...")
    results['camera_manager'] = test_camera_manager()
    
    # Test Integration
    logger.info("\nTesting Integration...")
    results['integration'] = test_integration()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.info("\n❌ Some tests failed!")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
