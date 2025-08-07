#!/usr/bin/env python3
"""
Test script for Camera Settings API
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_get_settings():
    """Test getting camera settings"""
    print("Testing get camera settings...")
    try:
        response = requests.get(f"{BASE_URL}/api/get_camera_settings")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Current settings: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"✗ Failed to get settings: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error getting settings: {e}")
        return None

def test_update_settings(settings):
    """Test updating camera settings"""
    print(f"\nTesting update camera settings: {settings}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/update_camera_settings",
            headers={'Content-Type': 'application/json'},
            json=settings
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Update response: {json.dumps(data, indent=2)}")
            return data['status'] == 'success'
        else:
            print(f"✗ Failed to update settings: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error updating settings: {e}")
        return False

def test_invalid_settings():
    """Test invalid settings validation"""
    print("\nTesting invalid settings validation...")
    
    # Test brightness out of range
    invalid_brightness = {"brightness": 2.0}  # Should be -1.0 to 1.0
    response = requests.post(
        f"{BASE_URL}/api/update_camera_settings",
        headers={'Content-Type': 'application/json'},
        json=invalid_brightness
    )
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'error':
            print(f"✓ Brightness validation works: {data['message']}")
        else:
            print(f"✗ Brightness validation failed")
    
    # Test contrast out of range
    invalid_contrast = {"contrast": -1.0}  # Should be 0.0 to 2.0
    response = requests.post(
        f"{BASE_URL}/api/update_camera_settings",
        headers={'Content-Type': 'application/json'},
        json=invalid_contrast
    )
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'error':
            print(f"✓ Contrast validation works: {data['message']}")
        else:
            print(f"✗ Contrast validation failed")

def main():
    """Run all camera settings tests"""
    print("=== Camera Settings Test Suite ===")
    print(f"Testing against: {BASE_URL}")
    
    # Test 1: Get current settings
    current_settings = test_get_settings()
    if current_settings is None:
        print("✗ Cannot get current settings")
        return
    
    # Test 2: Update brightness
    if test_update_settings({"brightness": 0.3}):
        print("✓ Brightness update successful")
        time.sleep(1)
        
        # Verify the change
        new_settings = test_get_settings()
        if new_settings and new_settings.get('settings', {}).get('brightness') == 0.3:
            print("✓ Brightness change verified")
        else:
            print("✗ Brightness change not verified")
    
    # Test 3: Update contrast
    if test_update_settings({"contrast": 1.5}):
        print("✓ Contrast update successful")
        time.sleep(1)
        
        # Verify the change
        new_settings = test_get_settings()
        if new_settings and new_settings.get('settings', {}).get('contrast') == 1.5:
            print("✓ Contrast change verified")
        else:
            print("✗ Contrast change not verified")
    
    # Test 4: Update multiple settings
    if test_update_settings({
        "saturation": 1.3,
        "sharpness": 2.0,
        "awb_mode": 5  # Daylight
    }):
        print("✓ Multiple settings update successful")
        time.sleep(1)
        
        # Verify the changes
        new_settings = test_get_settings()
        if new_settings:
            settings = new_settings.get('settings', {})
            if (settings.get('saturation') == 1.3 and 
                settings.get('sharpness') == 2.0 and 
                settings.get('awb_mode') == 5):
                print("✓ Multiple settings changes verified")
            else:
                print("✗ Multiple settings changes not verified")
    
    # Test 5: Test focus (if supported)
    if test_update_settings({"focus": 0.5}):
        print("✓ Focus update successful")
        time.sleep(1)
        
        # Verify the change
        new_settings = test_get_settings()
        if new_settings and new_settings.get('settings', {}).get('focus') == 0.5:
            print("✓ Focus change verified")
        else:
            print("✗ Focus change not verified")
    
    # Test 6: Test invalid settings
    test_invalid_settings()
    
    # Test 7: Reset to default
    if test_update_settings({
        "brightness": 0.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "sharpness": 1.0,
        "awb_mode": 0,
        "focus": 0.0
    }):
        print("✓ Reset to default successful")
    
    print("\n=== Camera Settings Test Complete ===")

if __name__ == "__main__":
    main() 