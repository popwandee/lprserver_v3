#!/usr/bin/env python3
"""
Test Script for Storage Management Service

This script tests the storage management functionality including
disk space monitoring, file cleanup, and storage analytics.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup import paths
from v1_3.src.core.utils.import_helper import setup_import_paths
setup_import_paths()

from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_storage_monitor():
    """Test Storage Monitor Component."""
    print("\n=== Testing Storage Monitor Component ===")
    
    try:
        storage_monitor = get_service('storage_monitor')
        if not storage_monitor:
            print("❌ Storage Monitor not available")
            return False
        
        print("✅ Storage Monitor service found")
        
        # Test initialization
        if storage_monitor.initialize():
            print("✅ Storage Monitor initialized successfully")
        else:
            print("❌ Storage Monitor initialization failed")
            return False
        
        # Test disk usage
        disk_usage = storage_monitor.get_disk_usage()
        print(f"✅ Disk Usage: {disk_usage}")
        
        # Test folder size
        folder_stats = storage_monitor.get_folder_size()
        print(f"✅ Folder Stats: {folder_stats}")
        
        # Test storage status
        status = storage_monitor.get_storage_status()
        print(f"✅ Storage Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage Monitor test failed: {e}")
        return False

def test_storage_service():
    """Test Storage Service."""
    print("\n=== Testing Storage Service ===")
    
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        print("✅ Storage Service found")
        
        # Test initialization
        if storage_service.initialize():
            print("✅ Storage Service initialized successfully")
        else:
            print("❌ Storage Service initialization failed")
            return False
        
        # Test storage status
        status_data = storage_service.get_storage_status()
        if status_data.get('success'):
            print("✅ Storage status retrieved successfully")
            print(f"   Disk Usage: {status_data['data'].get('disk_usage', {})}")
            print(f"   File Counts: {status_data['data'].get('file_counts', {})}")
        else:
            print(f"❌ Storage status failed: {status_data.get('error')}")
            return False
        
        # Test analytics
        analytics_data = storage_service.get_storage_analytics(days=7)
        if analytics_data.get('success'):
            print("✅ Storage analytics retrieved successfully")
        else:
            print(f"❌ Storage analytics failed: {analytics_data.get('error')}")
        
        # Test alerts
        alerts_data = storage_service.get_storage_alerts()
        if alerts_data.get('success'):
            print("✅ Storage alerts retrieved successfully")
            print(f"   Total Alerts: {alerts_data['data'].get('total_alerts', 0)}")
        else:
            print(f"❌ Storage alerts failed: {alerts_data.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage Service test failed: {e}")
        return False

def test_manual_cleanup():
    """Test manual cleanup functionality."""
    print("\n=== Testing Manual Cleanup ===")
    
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        # Test manual cleanup
        cleanup_result = storage_service.perform_manual_cleanup()
        if cleanup_result.get('success'):
            print("✅ Manual cleanup completed successfully")
            print(f"   Files Deleted: {cleanup_result['data'].get('cleanup_stats', {}).get('total_deleted', 0)}")
            print(f"   Space Freed: {cleanup_result['data'].get('space_freed_mb', 0):.2f} MB")
        else:
            print(f"❌ Manual cleanup failed: {cleanup_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual cleanup test failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\n=== Testing Configuration Management ===")
    
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        # Test configuration update
        test_config = {
            'min_free_space_gb': 8.0,
            'retention_days': 5,
            'batch_size': 50,
            'monitor_interval': 180
        }
        
        config_result = storage_service.update_storage_configuration(test_config)
        if config_result.get('success'):
            print("✅ Configuration updated successfully")
        else:
            print(f"❌ Configuration update failed: {config_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_monitoring():
    """Test monitoring functionality."""
    print("\n=== Testing Monitoring Functionality ===")
    
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        # Test start monitoring
        start_result = storage_service.start_storage_monitoring(interval=60)
        if start_result.get('success'):
            print("✅ Storage monitoring started successfully")
        else:
            print(f"❌ Storage monitoring start failed: {start_result.get('error')}")
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # Test stop monitoring
        stop_result = storage_service.stop_storage_monitoring()
        if stop_result.get('success'):
            print("✅ Storage monitoring stopped successfully")
        else:
            print(f"❌ Storage monitoring stop failed: {stop_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting Storage Management Service Tests")
    print("=" * 50)
    
    # Test results
    test_results = []
    
    # Run tests
    test_results.append(("Storage Monitor", test_storage_monitor()))
    test_results.append(("Storage Service", test_storage_service()))
    test_results.append(("Manual Cleanup", test_manual_cleanup()))
    test_results.append(("Configuration", test_configuration()))
    test_results.append(("Monitoring", test_monitoring()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Storage management service is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
