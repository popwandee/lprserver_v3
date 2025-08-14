#!/usr/bin/env python3
"""
Test script for Health Monitor functionality

This script tests the health monitoring components and services
to ensure they work correctly.

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_health_monitor():
    """Test Health Monitor component."""
    print("🧪 Testing Health Monitor Component...")
    
    try:
        from v1_3.src.components.health_monitor import HealthMonitor
        from v1_3.src.core.utils.logging_config import get_logger
        
        logger = get_logger(__name__)
        
        # Create health monitor instance
        health_monitor = HealthMonitor(logger)
        print("✅ Health Monitor instance created")
        
        # Test initialization
        if health_monitor.initialize():
            print("✅ Health Monitor initialized successfully")
        else:
            print("❌ Health Monitor initialization failed")
            return False
        
        # Test individual health checks
        print("\n🔍 Testing individual health checks...")
        
        # Test disk space check
        disk_ok = health_monitor.check_disk_space()
        print(f"   Disk Space: {'✅ PASS' if disk_ok else '❌ FAIL'}")
        
        # Test CPU/RAM check
        cpu_ram_ok = health_monitor.check_cpu_ram()
        print(f"   CPU & RAM: {'✅ PASS' if cpu_ram_ok else '❌ FAIL'}")
        
        # Test model loading check
        models_ok = health_monitor.check_model_loading()
        print(f"   Detection Models: {'✅ PASS' if models_ok else '❌ FAIL'}")
        
        # Test EasyOCR check
        easyocr_ok = health_monitor.check_easyocr_init()
        print(f"   EasyOCR: {'✅ PASS' if easyocr_ok else '❌ FAIL'}")
        
        # Test database connection check
        db_ok = health_monitor.check_database_connection()
        print(f"   Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
        
        # Test network connectivity check
        network_ok = health_monitor.check_network_connectivity()
        print(f"   Network: {'✅ PASS' if network_ok else '❌ FAIL'}")
        
        # Test comprehensive health check
        print("\n🔍 Testing comprehensive health check...")
        health_result = health_monitor.run_all_checks()
        
        if health_result and 'overall_status' in health_result:
            print(f"   Overall Status: {health_result['overall_status']}")
            print(f"   Checks Passed: {health_result.get('checks_passed', 0)}")
            print(f"   Checks Failed: {health_result.get('checks_failed', 0)}")
            print(f"   Total Checks: {health_result.get('total_checks', 0)}")
        else:
            print("❌ Comprehensive health check failed")
            return False
        
        # Test getting latest health checks
        print("\n📋 Testing health check logs...")
        latest_checks = health_monitor.get_latest_health_checks(5)
        print(f"   Retrieved {len(latest_checks)} recent health checks")
        
        for check in latest_checks[:3]:  # Show first 3
            print(f"   - {check.get('component', 'Unknown')}: {check.get('status', 'Unknown')}")
        
        # Test status method
        status = health_monitor.get_status()
        print(f"\n📊 Health Monitor Status: {status}")
        
        print("\n✅ Health Monitor component tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Health Monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_service():
    """Test Health Service."""
    print("\n🧪 Testing Health Service...")
    
    try:
        from v1_3.src.services.health_service import HealthService
        from v1_3.src.core.utils.logging_config import get_logger
        
        logger = get_logger(__name__)
        
        # Create health service instance
        health_service = HealthService(logger=logger)
        print("✅ Health Service instance created")
        
        # Test initialization
        if health_service.initialize():
            print("✅ Health Service initialized successfully")
        else:
            print("❌ Health Service initialization failed")
            return False
        
        # Test getting system health
        print("\n🔍 Testing system health retrieval...")
        health_data = health_service.get_system_health()
        
        if health_data and health_data.get('success'):
            print("✅ System health data retrieved successfully")
            health = health_data.get('health', {})
            print(f"   Overall Status: {health.get('overall_status', 'Unknown')}")
            print(f"   Components: {len(health.get('components', {}))}")
        else:
            print("❌ Failed to retrieve system health data")
            return False
        
        # Test getting health logs
        print("\n📋 Testing health logs retrieval...")
        logs_data = health_service.get_health_logs(limit=10)
        
        if logs_data and logs_data.get('success'):
            logs = logs_data.get('data', {}).get('logs', [])
            print(f"✅ Retrieved {len(logs)} health log entries")
        else:
            print("❌ Failed to retrieve health logs")
            return False
        
        # Test service status
        status = health_service.get_status()
        print(f"\n📊 Health Service Status: {status}")
        
        print("\n✅ Health Service tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Health Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_api():
    """Test Health API endpoints."""
    print("\n🧪 Testing Health API endpoints...")
    
    try:
        from v1_3.src.web.blueprints.health import health_bp
        from v1_3.src.core.utils.logging_config import get_logger
        
        logger = get_logger(__name__)
        
        # Test blueprint creation
        if health_bp:
            print("✅ Health blueprint created successfully")
            print(f"   Blueprint name: {health_bp.name}")
            print(f"   URL prefix: {health_bp.url_prefix}")
        else:
            print("❌ Health blueprint creation failed")
            return False
        
        # Test blueprint attributes
        print(f"   Blueprint name: {health_bp.name}")
        print(f"   URL prefix: {health_bp.url_prefix}")
        print(f"   Import name: {health_bp.import_name}")
        
        # Note: url_map is only available after blueprint is registered with app
        print("   Note: Routes will be available after blueprint registration")
        
        print("\n✅ Health API tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Health API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration():
    """Test database integration for health checks."""
    print("\n🧪 Testing database integration...")
    
    try:
        from v1_3.src.components.database_manager import DatabaseManager
        from v1_3.src.core.utils.logging_config import get_logger
        
        logger = get_logger(__name__)
        
        # Create database manager
        db_manager = DatabaseManager(logger)
        print("✅ Database Manager instance created")
        
        # Initialize database
        if db_manager.initialize():
            print("✅ Database initialized successfully")
        else:
            print("❌ Database initialization failed")
            return False
        
        # Test health check result insertion
        print("\n📝 Testing health check result insertion...")
        timestamp = datetime.now().isoformat()
        result_id = db_manager.insert_health_check_result(
            timestamp=timestamp,
            component="Test Component",
            status="PASS",
            message="Test health check",
            details='{"test": "data"}'
        )
        
        if result_id:
            print(f"✅ Health check result inserted with ID: {result_id}")
        else:
            print("❌ Health check result insertion failed")
            return False
        
        # Test getting latest health checks
        latest_checks = db_manager.get_latest_health_checks(5)
        print(f"✅ Retrieved {len(latest_checks)} health checks from database")
        
        # Cleanup
        db_manager.cleanup()
        print("✅ Database cleanup completed")
        
        print("\n✅ Database integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all health monitor tests."""
    print("🏥 AI Camera v1.3 - Health Monitor Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Health Monitor Component", test_health_monitor),
        ("Health Service", test_health_service),
        ("Health API", test_health_api),
        ("Database Integration", test_database_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Health monitor is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
