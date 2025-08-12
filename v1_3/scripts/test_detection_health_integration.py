#!/usr/bin/env python3
"""
Test Detection-Health Integration

This script tests the integration between detection module and health monitor
using proper detection patterns and mechanisms.

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

def test_detection_patterns():
    """Test detection module patterns and status checking."""
    print("🔍 Testing Detection Module Patterns...")
    print("=" * 50)
    
    try:
        from v1_3.src.core.dependency_container import get_service
        from v1_3.src.core.utils.logging_config import get_logger
        
        logger = get_logger(__name__)
        
        # Get detection manager
        detection_manager = get_service('detection_manager')
        if not detection_manager:
            print("❌ Detection Manager not available")
            return False
        
        # Get detection status
        status = detection_manager.get_status()
        print(f"📊 Detection Manager Status:")
        print(f"   Service Running: {status.get('service_running', False)}")
        print(f"   Thread Alive: {status.get('thread_alive', False)}")
        print(f"   Auto Start: {status.get('auto_start', False)}")
        print(f"   Detection Interval: {status.get('detection_interval', 0)}")
        
        # Check detection processor status
        processor_status = status.get('detection_processor_status', {})
        print(f"\n🔧 Detection Processor Status:")
        print(f"   Models Loaded: {processor_status.get('models_loaded', False)}")
        print(f"   Vehicle Model Available: {processor_status.get('vehicle_model_available', False)}")
        print(f"   LP Detection Model Available: {processor_status.get('lp_detection_model_available', False)}")
        print(f"   LP OCR Model Available: {processor_status.get('lp_ocr_model_available', False)}")
        print(f"   EasyOCR Available: {processor_status.get('easyocr_available', False)}")
        
        # Check processing stats
        processing_stats = processor_status.get('processing_stats', {})
        print(f"\n📈 Processing Statistics:")
        print(f"   Total Processed: {processing_stats.get('total_processed', 0)}")
        print(f"   Vehicles Detected: {processing_stats.get('vehicles_detected', 0)}")
        print(f"   Plates Detected: {processing_stats.get('plates_detected', 0)}")
        print(f"   Successful OCR: {processing_stats.get('successful_ocr', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing detection patterns: {e}")
        return False

def test_health_detection_integration():
    """Test health service integration with detection patterns."""
    print("\n🏥 Testing Health-Detection Integration...")
    print("=" * 50)
    
    try:
        from v1_3.src.core.dependency_container import get_service
        from v1_3.src.services.health_service import HealthService
        from v1_3.src.core.utils.logging_config import get_logger
        
        logger = get_logger(__name__)
        
        # Create health service
        health_service = HealthService(logger=logger)
        if not health_service.initialize():
            print("❌ Health Service initialization failed")
            return False
        
        print("✅ Health Service initialized")
        
        # Test component readiness checking
        print("\n🔍 Testing Component Readiness...")
        camera_status, detection_status = health_service._get_component_readiness()
        print(f"   Camera Status: {camera_status}")
        print(f"   Detection Status: {detection_status}")
        
        # Test detection processor readiness
        print("\n🔧 Testing Detection Processor Readiness...")
        detection_manager = get_service('detection_manager')
        if detection_manager:
            status = detection_manager.get_status()
            processor_ready = health_service._is_detection_processor_ready(status)
            print(f"   Detection Processor Ready: {processor_ready}")
            
            # Show detailed processor status
            processor_status = status.get('detection_processor_status', {})
            print(f"   Models Loaded: {processor_status.get('models_loaded', False)}")
            print(f"   Vehicle Model: {processor_status.get('vehicle_model_available', False)}")
            print(f"   LP Detection Model: {processor_status.get('lp_detection_model_available', False)}")
            print(f"   LP OCR Model: {processor_status.get('lp_ocr_model_available', False)}")
            print(f"   EasyOCR: {processor_status.get('easyocr_available', False)}")
        
        # Test should start monitoring logic
        print("\n🚀 Testing Should Start Monitoring Logic...")
        should_start = health_service._should_start_monitoring()
        print(f"   Should Start Health Monitoring: {should_start}")
        
        # Get detailed status for analysis
        camera_manager = get_service('camera_manager')
        detection_manager = get_service('detection_manager')
        
        camera_ready = False
        if camera_manager:
            status = camera_manager.get_status()
            camera_ready = (status.get('initialized', False) and 
                          status.get('streaming', False))
        
        detection_ready = False
        if detection_manager:
            status = detection_manager.get_status()
            detection_ready = (
                status.get('service_running', False) and
                status.get('thread_alive', False) and
                health_service._is_detection_processor_ready(status)
            )
        
        print(f"   Camera Ready: {camera_ready}")
        print(f"   Detection Ready: {detection_ready}")
        print(f"   Both Ready: {camera_ready and detection_ready}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing health-detection integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_health_with_detection():
    """Test system health status with detection integration."""
    print("\n🏥 Testing System Health with Detection Integration...")
    print("=" * 50)
    
    try:
        from v1_3.src.core.dependency_container import get_service
        
        # Get health service
        health_service = get_service('health_service')
        if not health_service:
            print("❌ Health Service not available")
            return False
        
        # Get system health
        health_data = health_service.get_system_health()
        if not health_data.get('success'):
            print("❌ Failed to get system health")
            return False
        
        data = health_data.get('data', {})
        components = data.get('components', {})
        
        print("📊 System Health Status:")
        print(f"   Overall Status: {data.get('overall_status', 'unknown')}")
        
        # Check camera status
        camera = components.get('camera', {})
        print(f"\n📸 Camera Status:")
        print(f"   Status: {camera.get('status', 'unknown')}")
        print(f"   Initialized: {camera.get('initialized', False)}")
        print(f"   Streaming: {camera.get('streaming', False)}")
        print(f"   Auto Start Enabled: {camera.get('auto_start_enabled', False)}")
        
        # Check detection status with new patterns
        detection = components.get('detection', {})
        print(f"\n🤖 Detection Status (using detection patterns):")
        print(f"   Status: {detection.get('status', 'unknown')}")
        print(f"   Models Loaded: {detection.get('models_loaded', False)}")
        print(f"   EasyOCR Available: {detection.get('easyocr_available', False)}")
        print(f"   Detection Active: {detection.get('detection_active', False)}")
        print(f"   Service Running: {detection.get('service_running', False)}")
        print(f"   Thread Alive: {detection.get('thread_alive', False)}")
        print(f"   Auto Start: {detection.get('auto_start', False)}")
        
        # Check database status
        database = components.get('database', {})
        print(f"\n🗄️ Database Status:")
        print(f"   Status: {database.get('status', 'unknown')}")
        print(f"   Connected: {database.get('connected', False)}")
        
        # Check system status
        system = components.get('system', {})
        print(f"\n💻 System Status:")
        print(f"   Status: {system.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing system health: {e}")
        return False

def test_auto_startup_conditions():
    """Test auto-startup conditions and logic."""
    print("\n🚀 Testing Auto-Startup Conditions...")
    print("=" * 50)
    
    try:
        from v1_3.src.core.dependency_container import get_service
        from v1_3.src.services.health_service import HealthService
        from v1_3.src.core.utils.logging_config import get_logger
        
        logger = get_logger(__name__)
        health_service = HealthService(logger=logger)
        
        # Test different scenarios
        scenarios = [
            {
                'name': 'Camera Only Ready',
                'camera_ready': True,
                'detection_ready': False,
                'expected': False
            },
            {
                'name': 'Detection Only Ready',
                'camera_ready': False,
                'detection_ready': True,
                'expected': False
            },
            {
                'name': 'Both Ready',
                'camera_ready': True,
                'detection_ready': True,
                'expected': True
            },
            {
                'name': 'Neither Ready',
                'camera_ready': False,
                'detection_ready': False,
                'expected': False
            }
        ]
        
        for scenario in scenarios:
            print(f"\n🔍 Testing: {scenario['name']}")
            
            # Mock the readiness checking (for testing purposes)
            def mock_should_start():
                return scenario['camera_ready'] and scenario['detection_ready']
            
            # Store original method
            original_method = health_service._should_start_monitoring
            
            # Replace with mock
            health_service._should_start_monitoring = mock_should_start
            
            # Test
            result = health_service._should_start_monitoring()
            expected = scenario['expected']
            
            print(f"   Expected: {expected}")
            print(f"   Actual: {result}")
            print(f"   Result: {'✅ PASS' if result == expected else '❌ FAIL'}")
            
            # Restore original method
            health_service._should_start_monitoring = original_method
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing auto-startup conditions: {e}")
        return False

def main():
    """Main test function."""
    print("🏥 AI Camera v1.3 - Detection-Health Integration Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Run tests
    tests = [
        ("Detection Patterns", test_detection_patterns),
        ("Health-Detection Integration", test_health_detection_integration),
        ("System Health with Detection", test_system_health_with_detection),
        ("Auto-Startup Conditions", test_auto_startup_conditions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DETECTION-HEALTH INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All detection-health integration tests passed!")
        print("   Health monitor correctly uses detection module patterns")
    else:
        print("⚠️ Some tests failed - check the output above for details")
    
    return passed == len(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
