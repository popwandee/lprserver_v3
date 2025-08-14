#!/usr/bin/env python3
"""
Test Script for Storage Service Connection

This script tests the connection and data flow between storage components.
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

from v1_3.src.core.dependency_container import get_service, get_container
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_dependency_injection():
    """Test dependency injection setup."""
    print("\n=== Testing Dependency Injection ===")
    
    try:
        # Get container
        container = get_container()
        print("✅ Dependency container created")
        
        # Check if services are registered
        services = container.services
        print(f"✅ Registered services: {list(services.keys())}")
        
        # Check storage services
        if 'storage_monitor' in services:
            print("✅ Storage Monitor service registered")
        else:
            print("❌ Storage Monitor service not registered")
            return False
        
        if 'storage_service' in services:
            print("✅ Storage Service registered")
        else:
            print("❌ Storage Service not registered")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency injection test failed: {e}")
        return False

def test_service_creation():
    """Test service creation."""
    print("\n=== Testing Service Creation ===")
    
    try:
        # Test storage monitor
        storage_monitor = get_service('storage_monitor')
        if storage_monitor:
            print("✅ Storage Monitor service created")
            print(f"   Type: {type(storage_monitor).__name__}")
            print(f"   Folder path: {storage_monitor.folder_path}")
        else:
            print("❌ Storage Monitor service creation failed")
            return False
        
        # Test storage service
        storage_service = get_service('storage_service')
        if storage_service:
            print("✅ Storage Service created")
            print(f"   Type: {type(storage_service).__name__}")
        else:
            print("❌ Storage Service creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Service creation test failed: {e}")
        return False

def test_storage_monitor_methods():
    """Test storage monitor methods."""
    print("\n=== Testing Storage Monitor Methods ===")
    
    try:
        storage_monitor = get_service('storage_monitor')
        if not storage_monitor:
            print("❌ Storage Monitor not available")
            return False
        
        # Test initialization
        print("Testing initialization...")
        if storage_monitor.initialize():
            print("✅ Storage Monitor initialized")
        else:
            print("❌ Storage Monitor initialization failed")
            return False
        
        # Test disk usage
        print("Testing disk usage...")
        disk_usage = storage_monitor.get_disk_usage()
        print(f"✅ Disk usage: {disk_usage}")
        
        # Test folder size
        print("Testing folder size...")
        folder_stats = storage_monitor.get_folder_size()
        print(f"✅ Folder stats: {folder_stats}")
        
        # Test files by status
        print("Testing files by status...")
        sent_files, unsent_files = storage_monitor.get_files_by_status()
        print(f"✅ Files by status - Sent: {len(sent_files)}, Unsent: {len(unsent_files)}")
        
        # Test storage status
        print("Testing storage status...")
        status = storage_monitor.get_storage_status()
        print(f"✅ Storage status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage monitor methods test failed: {e}")
        return False

def test_storage_service_methods():
    """Test storage service methods."""
    print("\n=== Testing Storage Service Methods ===")
    
    try:
        storage_service = get_service('storage_service')
        if not storage_service:
            print("❌ Storage Service not available")
            return False
        
        # Test initialization
        print("Testing initialization...")
        if storage_service.initialize():
            print("✅ Storage Service initialized")
        else:
            print("❌ Storage Service initialization failed")
            return False
        
        # Test storage status
        print("Testing storage status...")
        status_data = storage_service.get_storage_status()
        if status_data.get('success'):
            print("✅ Storage status retrieved")
            data = status_data.get('data', {})
            print(f"   Disk usage: {data.get('disk_usage', {})}")
            print(f"   File counts: {data.get('file_counts', {})}")
            print(f"   Folder stats: {data.get('folder_stats', {})}")
        else:
            print(f"❌ Storage status failed: {status_data.get('error')}")
            return False
        
        # Test analytics
        print("Testing analytics...")
        analytics_data = storage_service.get_storage_analytics(days=7)
        if analytics_data.get('success'):
            print("✅ Analytics retrieved")
        else:
            print(f"❌ Analytics failed: {analytics_data.get('error')}")
        
        # Test alerts
        print("Testing alerts...")
        alerts_data = storage_service.get_storage_alerts()
        if alerts_data.get('success'):
            print("✅ Alerts retrieved")
            print(f"   Total alerts: {alerts_data['data'].get('total_alerts', 0)}")
        else:
            print(f"❌ Alerts failed: {alerts_data.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage service methods test failed: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    print("\n=== Testing Database Connection ===")
    
    try:
        db_manager = get_service('database_manager')
        if not db_manager:
            print("❌ Database manager not available")
            return False
        
        print("✅ Database manager found")
        
        # Test connection
        if db_manager.connection:
            print("✅ Database connection active")
            
            # Test query
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ Database tables: {[table[0] for table in tables]}")
            
            # Test detection_results table
            if any('detection_results' in table for table in tables):
                print("✅ detection_results table exists")
                
                # Test query detection_results
                cursor.execute("SELECT COUNT(*) FROM detection_results")
                count = cursor.fetchone()[0]
                print(f"✅ detection_results count: {count}")
                
                # Test query with image_path
                cursor.execute("SELECT COUNT(*) FROM detection_results WHERE image_path IS NOT NULL")
                image_count = cursor.fetchone()[0]
                print(f"✅ detection_results with image_path: {image_count}")
                
            else:
                print("❌ detection_results table not found")
                return False
        else:
            print("❌ Database connection not active")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_folder_creation():
    """Test folder creation."""
    print("\n=== Testing Folder Creation ===")
    
    try:
        import os
        from pathlib import Path
        
        # Test current working directory
        cwd = os.getcwd()
        print(f"✅ Current working directory: {cwd}")
        
        # Test aicamera folder
        aicamera_path = os.path.join(cwd, "aicamera")
        if os.path.exists(aicamera_path):
            print(f"✅ aicamera folder exists: {aicamera_path}")
        else:
            print(f"⚠️  aicamera folder does not exist: {aicamera_path}")
            os.makedirs(aicamera_path, exist_ok=True)
            print(f"✅ Created aicamera folder: {aicamera_path}")
        
        # Test captured_images folder
        captured_images_path = os.path.join(aicamera_path, "captured_images")
        if os.path.exists(captured_images_path):
            print(f"✅ captured_images folder exists: {captured_images_path}")
        else:
            print(f"⚠️  captured_images folder does not exist: {captured_images_path}")
            os.makedirs(captured_images_path, exist_ok=True)
            print(f"✅ Created captured_images folder: {captured_images_path}")
        
        # Test folder permissions
        if os.access(captured_images_path, os.W_OK):
            print("✅ captured_images folder is writable")
        else:
            print("❌ captured_images folder is not writable")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Folder creation test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 Starting Storage Connection Tests")
    print("=" * 50)
    
    # Test results
    test_results = []
    
    # Run tests
    test_results.append(("Dependency Injection", test_dependency_injection()))
    test_results.append(("Service Creation", test_service_creation()))
    test_results.append(("Folder Creation", test_folder_creation()))
    test_results.append(("Database Connection", test_database_connection()))
    test_results.append(("Storage Monitor Methods", test_storage_monitor_methods()))
    test_results.append(("Storage Service Methods", test_storage_service_methods()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Connection Test Results Summary")
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
        print("🎉 All connection tests passed! Storage service should work correctly.")
        return 0
    else:
        print("⚠️  Some connection tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
