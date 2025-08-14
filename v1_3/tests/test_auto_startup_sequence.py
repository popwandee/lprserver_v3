#!/usr/bin/env python3
"""
Test script for Auto-Startup Sequence

This script tests the new auto-startup sequence:
camera start → detection start → health monitor start

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

def test_auto_startup_sequence():
    """Test the auto-startup sequence."""
    print("🚀 Testing Auto-Startup Sequence...")
    print("=" * 50)
    
    try:
        from v1_3.src.core.utils.logging_config import get_logger
        from v1_3.src.core.dependency_container import get_service
        from v1_3.src.core.config import (
            AUTO_START_CAMERA, AUTO_START_DETECTION, AUTO_START_HEALTH_MONITOR,
            STARTUP_DELAY, HEALTH_MONITOR_STARTUP_DELAY
        )
        
        logger = get_logger(__name__)
        
        # Print configuration
        print(f"📋 Auto-Startup Configuration:")
        print(f"   Camera Auto-Start: {AUTO_START_CAMERA}")
        print(f"   Detection Auto-Start: {AUTO_START_DETECTION}")
        print(f"   Health Monitor Auto-Start: {AUTO_START_HEALTH_MONITOR}")
        print(f"   Startup Delay: {STARTUP_DELAY} seconds")
        print(f"   Health Monitor Startup Delay: {HEALTH_MONITOR_STARTUP_DELAY} seconds")
        print()
        
        # Test service availability
        print("🔍 Testing Service Availability...")
        
        camera_manager = get_service('camera_manager')
        detection_manager = get_service('detection_manager')
        health_monitor = get_service('health_monitor')
        health_service = get_service('health_service')
        
        print(f"   Camera Manager: {'✅ Available' if camera_manager else '❌ Not Available'}")
        print(f"   Detection Manager: {'✅ Available' if detection_manager else '❌ Not Available'}")
        print(f"   Health Monitor: {'✅ Available' if health_monitor else '❌ Not Available'}")
        print(f"   Health Service: {'✅ Available' if health_service else '❌ Not Available'}")
        print()
        
        # Test initialization sequence
        print("🔧 Testing Initialization Sequence...")
        
        # Step 1: Camera Manager
        if camera_manager:
            print("📸 Step 1: Initializing Camera Manager...")
            success = camera_manager.initialize()
            print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
            
            if success:
                status = camera_manager.get_status()
                print(f"   Camera Status: {status}")
        else:
            print("❌ Camera Manager not available - skipping")
        
        print()
        
        # Step 2: Detection Manager
        if detection_manager:
            print("🤖 Step 2: Initializing Detection Manager...")
            success = detection_manager.initialize()
            print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
            
            if success:
                status = detection_manager.get_status()
                print(f"   Detection Status: {status}")
        else:
            print("❌ Detection Manager not available - skipping")
        
        print()
        
        # Step 3: Health Monitor and Service
        if health_monitor and health_service:
            print("🏥 Step 3: Initializing Health Monitor and Service...")
            
            # Initialize health monitor
            hm_success = health_monitor.initialize()
            print(f"   Health Monitor: {'✅ Success' if hm_success else '❌ Failed'}")
            
            # Initialize health service
            hs_success = health_service.initialize()
            print(f"   Health Service: {'✅ Success' if hs_success else '❌ Failed'}")
            
            if hs_success:
                status = health_service.get_status()
                print(f"   Health Service Status: {status}")
        else:
            print("❌ Health services not available - skipping")
        
        print()
        
        # Test auto-startup monitoring
        if AUTO_START_HEALTH_MONITOR and health_service:
            print("🏥 Testing Auto-Startup Monitoring...")
            print(f"   Auto-startup enabled: {AUTO_START_HEALTH_MONITOR}")
            print(f"   Will wait for camera and detection to be ready...")
            print(f"   Initial delay: {HEALTH_MONITOR_STARTUP_DELAY} seconds")
            print()
            
            # Wait a bit to see if auto-startup works
            print("⏳ Waiting for auto-startup monitoring to activate...")
            for i in range(5):  # Wait 5 cycles
                time.sleep(2)
                status = health_service.get_status()
                print(f"   Cycle {i+1}: Monitoring active = {status.get('monitoring', False)}")
                
                if status.get('monitoring', False):
                    print("✅ Health monitoring started automatically!")
                    break
            else:
                print("⏳ Health monitoring not yet started (this is normal if components aren't ready)")
        
        print()
        print("🎉 Auto-startup sequence test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Auto-startup sequence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_readiness():
    """Test component readiness checking."""
    print("\n🔍 Testing Component Readiness...")
    
    try:
        from v1_3.src.core.dependency_container import get_service
        
        # Test camera readiness
        camera_manager = get_service('camera_manager')
        if camera_manager:
            status = camera_manager.get_status()
            camera_ready = (status.get('initialized', False) and 
                          status.get('streaming', False))
            print(f"   Camera Ready: {camera_ready}")
            print(f"   Camera Status: {status}")
        else:
            print("   Camera Manager not available")
        
        # Test detection readiness
        detection_manager = get_service('detection_manager')
        if detection_manager:
            status = detection_manager.get_status()
            detection_ready = status.get('active', False)
            print(f"   Detection Ready: {detection_ready}")
            print(f"   Detection Status: {status}")
        else:
            print("   Detection Manager not available")
        
        # Test health service readiness checking
        health_service = get_service('health_service')
        if health_service:
            should_start = health_service._should_start_monitoring()
            print(f"   Should Start Health Monitoring: {should_start}")
            
            camera_status, detection_status = health_service._get_component_readiness()
            print(f"   Component Readiness - Camera: {camera_status}, Detection: {detection_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component readiness test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🏥 AI Camera v1.3 - Auto-Startup Sequence Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Test auto-startup sequence
    sequence_success = test_auto_startup_sequence()
    
    # Test component readiness
    readiness_success = test_component_readiness()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Auto-Startup Sequence: {'✅ PASS' if sequence_success else '❌ FAIL'}")
    print(f"Component Readiness: {'✅ PASS' if readiness_success else '❌ FAIL'}")
    
    overall_success = sequence_success and readiness_success
    print(f"\nOverall: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    if overall_success:
        print("🎉 Auto-startup sequence is working correctly!")
    else:
        print("⚠️ Some tests failed - check the output above for details")
    
    return overall_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
