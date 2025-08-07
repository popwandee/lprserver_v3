#!/usr/bin/env python3
"""
Test script for Simple AI Camera Application
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_camera_status():
    """Test camera status endpoint"""
    print("Testing camera status...")
    try:
        response = requests.get(f"{BASE_URL}/api/camera_status")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Camera status: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"✗ Failed to get camera status: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error testing camera status: {e}")
        return None

def test_start_camera():
    """Test starting camera"""
    print("\nTesting camera start...")
    try:
        response = requests.post(f"{BASE_URL}/api/start_camera")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Start camera response: {json.dumps(data, indent=2)}")
            return data['status'] == 'success'
        else:
            print(f"✗ Failed to start camera: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error starting camera: {e}")
        return False

def test_stop_camera():
    """Test stopping camera"""
    print("\nTesting camera stop...")
    try:
        response = requests.post(f"{BASE_URL}/api/stop_camera")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Stop camera response: {json.dumps(data, indent=2)}")
            return data['status'] == 'success'
        else:
            print(f"✗ Failed to stop camera: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error stopping camera: {e}")
        return False

def test_close_camera():
    """Test closing camera"""
    print("\nTesting camera close...")
    try:
        response = requests.post(f"{BASE_URL}/api/close_camera")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Close camera response: {json.dumps(data, indent=2)}")
            return data['status'] == 'success'
        else:
            print(f"✗ Failed to close camera: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error closing camera: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Simple AI Camera Test Suite ===")
    print(f"Testing against: {BASE_URL}")
    
    # Test initial status
    initial_status = test_camera_status()
    if initial_status is None:
        print("✗ Cannot connect to application")
        return
    
    # Test start camera
    if test_start_camera():
        print("✓ Camera started successfully")
        
        # Wait a moment for camera to initialize
        time.sleep(2)
        
        # Check status after start
        status_after_start = test_camera_status()
        if status_after_start and status_after_start.get('initialized'):
            print("✓ Camera is initialized")
        else:
            print("✗ Camera is not initialized")
        
        # Test stop camera
        if test_stop_camera():
            print("✓ Camera stopped successfully")
            
            # Check status after stop
            time.sleep(1)
            status_after_stop = test_camera_status()
            if status_after_stop and not status_after_stop.get('streaming'):
                print("✓ Camera streaming stopped")
            else:
                print("✗ Camera streaming did not stop")
        
        # Test close camera
        if test_close_camera():
            print("✓ Camera closed successfully")
            
            # Check status after close
            time.sleep(1)
            status_after_close = test_camera_status()
            if status_after_close and not status_after_close.get('initialized'):
                print("✓ Camera is properly closed")
            else:
                print("✗ Camera is not properly closed")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 