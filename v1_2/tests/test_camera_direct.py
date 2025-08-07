#!/usr/bin/env python3
"""
Direct camera test script
"""

import logging
from picamera2 import Picamera2
from config import DEFAULT_RESOLUTION, DEFAULT_FRAMERATE, DEFAULT_BRIGHTNESS, DEFAULT_CONTRAST, DEFAULT_SATURATION, DEFAULT_SHARPNESS, DEFAULT_AWB_MODE

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def test_camera_initialization():
    """Test camera initialization step by step"""
    
    print("=== Camera Initialization Test ===")
    
    try:
        # Step 1: Create camera instance
        print("1. Creating Picamera2 instance...")
        camera = Picamera2()
        print("✓ Picamera2 instance created")
        
        # Step 2: Create configuration
        print("2. Creating video configuration...")
        config = camera.create_video_configuration(
            main={"size": DEFAULT_RESOLUTION},
            lores={"size": (640, 480)},
            encode="lores"
        )
        print("✓ Video configuration created")
        print(f"  Config: {config}")
        
        # Step 3: Configure camera
        print("3. Configuring camera...")
        camera.configure(config)
        print("✓ Camera configured")
        
        # Step 4: Apply controls
        print("4. Applying camera controls...")
        try:
            controls_dict = {
                "Brightness": DEFAULT_BRIGHTNESS,
                "Contrast": DEFAULT_CONTRAST,
                "Saturation": DEFAULT_SATURATION,
                "Sharpness": DEFAULT_SHARPNESS,
                "AwbMode": DEFAULT_AWB_MODE
            }
            camera.set_controls(controls_dict)
            print("✓ Camera controls applied")
        except Exception as e:
            print(f"⚠ Warning: Could not apply camera controls: {e}")
        
        # Step 5: Start camera
        print("5. Starting camera...")
        camera.start()
        print("✓ Camera started")
        
        # Step 6: Test frame capture
        print("6. Testing frame capture...")
        request = camera.capture_request()
        frame = request.make_array("main")
        request.release()
        print(f"✓ Frame captured successfully - shape: {frame.shape}")
        
        # Step 7: Stop camera
        print("7. Stopping camera...")
        camera.stop()
        print("✓ Camera stopped")
        
        # Step 8: Close camera
        print("8. Closing camera...")
        camera.close()
        print("✓ Camera closed")
        
        print("\n=== All tests passed! ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_camera_with_settings():
    """Test camera with specific settings"""
    
    print("\n=== Camera Settings Test ===")
    
    try:
        camera = Picamera2()
        
        # Test with minimal configuration
        print("Testing minimal configuration...")
        config = camera.create_video_configuration(
            main={"size": (640, 480)}
        )
        camera.configure(config)
        camera.start()
        
        # Capture a frame
        request = camera.capture_request()
        frame = request.make_array("main")
        request.release()
        print(f"✓ Minimal config works - frame shape: {frame.shape}")
        
        camera.stop()
        camera.close()
        
        print("✓ Minimal configuration test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Minimal configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting camera tests...")
    
    # Test 1: Full initialization
    success1 = test_camera_initialization()
    
    # Test 2: Minimal configuration
    success2 = test_camera_with_settings()
    
    if success1 and success2:
        print("\n🎉 All camera tests passed!")
    else:
        print("\n❌ Some camera tests failed!") 