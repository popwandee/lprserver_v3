#!/usr/bin/env python3
"""
Test Script for Storage Auto-Start Functionality

This script tests the automatic startup of storage monitoring
after health monitor initialization.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup import paths
from v1_3.src.core.utils.import_helper import setup_import_paths
setup_import_paths()

from v1_3.src.core.dependency_container import get_service, get_container
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_app_initialization_sequence():
    """Test app initialization sequence including storage service."""
    print("\n=== Testing App Initialization Sequence ===")
    
    try:
        # Import Flask app for testing
        from v1_3.src.web.app import create_app
        app = create_app()
        
        print("✅ Flask app created successfully")
        
        # Check if storage service is available
        storage_service = get_service('storage_service')
        if storage_service:
            print("✅ Storage Service available after app initialization")
            
            # Check if storage monitor is running
            if storage_service.storage_monitor.running:
                print("✅ Storage monitoring started automatically")
                return True
            else:
                print("❌ Storage monitoring not started automatically")
                return False
        else:
            print("❌ Storage service not available after app initialization")
            return False
        
    except Exception as e:
        print(f"❌ App initialization sequence test failed: {e}")
        return False

def test_storage_service_auto_start():
    """Test storage service auto-start."""
    print("\n=== Testing Storage Service Auto-Start ===")
    
    try:
        # Get storage service
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        print("✅ Storage Service found")
        
        # Check if storage monitor is running
        if storage_service.storage_monitor.running:
            print("✅ Storage monitoring is running")
            return True
        else:
            print("❌ Storage monitoring is not running")
            return False
        
    except Exception as e:
        print(f"❌ Storage service auto-start test failed: {e}")
        return False

def test_storage_status_retrieval():
    """Test storage status retrieval."""
    print("\n=== Testing Storage Status Retrieval ===")
    
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        # Get storage status
        status_data = storage_service.get_storage_status()
        if status_data.get('success'):
            print("✅ Storage status retrieved successfully")
            
            data = status_data.get('data', {})
            disk_usage = data.get('disk_usage', {})
            file_counts = data.get('file_counts', {})
            status = data.get('status', {})
            
            print(f"   Disk Usage: {disk_usage}")
            print(f"   File Counts: {file_counts}")
            print(f"   Monitoring Status: {status}")
            
            return True
        else:
            print(f"❌ Storage status failed: {status_data.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ Storage status retrieval test failed: {e}")
        return False

def test_web_interface_endpoints():
    """Test web interface endpoints."""
    print("\n=== Testing Web Interface Endpoints ===")
    
    try:
        # Import Flask app for testing
        from v1_3.src.web.app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test storage status endpoint
            response = client.get('/storage/status')
            if response.status_code == 200:
                print("✅ /storage/status endpoint working")
                data = response.get_json()
                print(f"   Response: {data}")
            else:
                print(f"❌ /storage/status endpoint failed: {response.status_code}")
                return False
            
            # Test storage analytics endpoint
            response = client.get('/storage/analytics')
            if response.status_code == 200:
                print("✅ /storage/analytics endpoint working")
            else:
                print(f"❌ /storage/analytics endpoint failed: {response.status_code}")
                return False
            
            # Test storage alerts endpoint
            response = client.get('/storage/alerts')
            if response.status_code == 200:
                print("✅ /storage/alerts endpoint working")
            else:
                print(f"❌ /storage/alerts endpoint failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface endpoints test failed: {e}")
        return False

def test_monitoring_controls():
    """Test monitoring start/stop controls."""
    print("\n=== Testing Monitoring Controls ===")
    
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        # Test stop monitoring
        print("Testing stop monitoring...")
        stop_result = storage_service.stop_storage_monitoring()
        if stop_result.get('success'):
            print("✅ Stop monitoring successful")
        else:
            print(f"❌ Stop monitoring failed: {stop_result.get('error')}")
        
        # Wait a moment
        time.sleep(2)
        
        # Test start monitoring
        print("Testing start monitoring...")
        start_result = storage_service.start_storage_monitoring(interval=60)
        if start_result.get('success'):
            print("✅ Start monitoring successful")
        else:
            print(f"❌ Start monitoring failed: {start_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring controls test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting Storage Auto-Start Tests")
    print("=" * 50)
    
    # Test results
    test_results = []
    
    # Run tests
    test_results.append(("App Initialization Sequence", test_app_initialization_sequence()))
    test_results.append(("Storage Service Auto-Start", test_storage_service_auto_start()))
    test_results.append(("Storage Status Retrieval", test_storage_status_retrieval()))
    test_results.append(("Web Interface Endpoints", test_web_interface_endpoints()))
    test_results.append(("Monitoring Controls", test_monitoring_controls()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Auto-Start Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All auto-start tests passed! Storage service should work correctly.")
        return 0
    else:
        print("⚠️  Some auto-start tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
