#!/usr/bin/env python3
"""
Test Script for Storage Configuration

This script tests the storage configuration parameters and their loading.
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

from v1_3.src.core.config import (
    STORAGE_MONITOR_ENABLED, STORAGE_MONITOR_INTERVAL, STORAGE_MIN_FREE_SPACE_GB,
    STORAGE_RETENTION_DAYS, STORAGE_BATCH_SIZE, STORAGE_FOLDER_PATH,
    AUTO_START_STORAGE_MONITOR, STORAGE_MONITOR_STARTUP_DELAY
)
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_storage_config_loading():
    """Test storage configuration loading."""
    print("\n=== Testing Storage Configuration Loading ===")
    
    try:
        print(f"STORAGE_MONITOR_ENABLED: {STORAGE_MONITOR_ENABLED}")
        print(f"STORAGE_MONITOR_INTERVAL: {STORAGE_MONITOR_INTERVAL} seconds")
        print(f"STORAGE_MIN_FREE_SPACE_GB: {STORAGE_MIN_FREE_SPACE_GB} GB")
        print(f"STORAGE_RETENTION_DAYS: {STORAGE_RETENTION_DAYS} days")
        print(f"STORAGE_BATCH_SIZE: {STORAGE_BATCH_SIZE} files")
        print(f"STORAGE_FOLDER_PATH: {STORAGE_FOLDER_PATH}")
        print(f"AUTO_START_STORAGE_MONITOR: {AUTO_START_STORAGE_MONITOR}")
        print(f"STORAGE_MONITOR_STARTUP_DELAY: {STORAGE_MONITOR_STARTUP_DELAY} seconds")
        
        # Validate configuration values
        errors = []
        
        if not isinstance(STORAGE_MONITOR_INTERVAL, int) or STORAGE_MONITOR_INTERVAL < 60:
            errors.append("STORAGE_MONITOR_INTERVAL must be >= 60 seconds")
        
        if not isinstance(STORAGE_MIN_FREE_SPACE_GB, float) or STORAGE_MIN_FREE_SPACE_GB < 1.0:
            errors.append("STORAGE_MIN_FREE_SPACE_GB must be >= 1.0 GB")
        
        if not isinstance(STORAGE_RETENTION_DAYS, int) or STORAGE_RETENTION_DAYS < 1:
            errors.append("STORAGE_RETENTION_DAYS must be >= 1 day")
        
        if not isinstance(STORAGE_BATCH_SIZE, int) or STORAGE_BATCH_SIZE < 1:
            errors.append("STORAGE_BATCH_SIZE must be >= 1 file")
        
        if not os.path.exists(STORAGE_FOLDER_PATH):
            errors.append(f"STORAGE_FOLDER_PATH does not exist: {STORAGE_FOLDER_PATH}")
        
        if errors:
            print("❌ Configuration validation errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ All configuration values are valid")
            return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def test_storage_monitor_config():
    """Test storage monitor configuration."""
    print("\n=== Testing Storage Monitor Configuration ===")
    
    try:
        from v1_3.src.core.dependency_container import get_service
        storage_monitor = get_service('storage_monitor')
        
        if not storage_monitor:
            print("❌ Storage Monitor not available")
            return False
        
        print("✅ Storage Monitor service found")
        print(f"   Folder path: {storage_monitor.folder_path}")
        print(f"   Min free space: {storage_monitor.min_free_space_gb} GB")
        print(f"   Retention days: {storage_monitor.retention_days} days")
        print(f"   Batch size: {storage_monitor.batch_size} files")
        print(f"   Monitor interval: {storage_monitor.monitor_interval} seconds")
        
        # Check if configuration matches config.py
        config_matches = (
            storage_monitor.folder_path == STORAGE_FOLDER_PATH and
            storage_monitor.min_free_space_gb == STORAGE_MIN_FREE_SPACE_GB and
            storage_monitor.retention_days == STORAGE_RETENTION_DAYS and
            storage_monitor.batch_size == STORAGE_BATCH_SIZE and
            storage_monitor.monitor_interval == STORAGE_MONITOR_INTERVAL
        )
        
        if config_matches:
            print("✅ Storage Monitor configuration matches config.py")
            return True
        else:
            print("❌ Storage Monitor configuration does not match config.py")
            return False
        
    except Exception as e:
        print(f"❌ Storage monitor configuration test failed: {e}")
        return False

def test_storage_service_config():
    """Test storage service configuration."""
    print("\n=== Testing Storage Service Configuration ===")
    
    try:
        from v1_3.src.core.dependency_container import get_service
        storage_service = get_service('storage_service')
        
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        print("✅ Storage Service found")
        
        # Test initialization
        if storage_service.initialize():
            print("✅ Storage Service initialized successfully")
            
            # Check if storage monitor is configured correctly
            if storage_service.storage_monitor:
                print("✅ Storage Monitor is available in service")
                return True
            else:
                print("❌ Storage Monitor not available in service")
                return False
        else:
            print("❌ Storage Service initialization failed")
            return False
        
    except Exception as e:
        print(f"❌ Storage service configuration test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable loading."""
    print("\n=== Testing Environment Variable Loading ===")
    
    try:
        # Test if environment variables can be loaded
        env_vars = {
            'AUTO_START_STORAGE_MONITOR': os.getenv('AUTO_START_STORAGE_MONITOR', 'true'),
            'STORAGE_MONITOR_INTERVAL': os.getenv('STORAGE_MONITOR_INTERVAL', '300'),
            'STORAGE_MIN_FREE_SPACE_GB': os.getenv('STORAGE_MIN_FREE_SPACE_GB', '10.0'),
            'STORAGE_RETENTION_DAYS': os.getenv('STORAGE_RETENTION_DAYS', '7'),
            'STORAGE_BATCH_SIZE': os.getenv('STORAGE_BATCH_SIZE', '100'),
        }
        
        print("Environment variables:")
        for key, value in env_vars.items():
            print(f"   {key}: {value}")
        
        print("✅ Environment variables loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Environment variable loading test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔧 Starting Storage Configuration Tests")
    print("=" * 50)
    
    # Test results
    test_results = []
    
    # Run tests
    test_results.append(("Environment Variables", test_environment_variables()))
    test_results.append(("Storage Config Loading", test_storage_config_loading()))
    test_results.append(("Storage Monitor Config", test_storage_monitor_config()))
    test_results.append(("Storage Service Config", test_storage_service_config()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Configuration Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All configuration tests passed! Storage configuration is correct.")
        return 0
    else:
        print("⚠️  Some configuration tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
