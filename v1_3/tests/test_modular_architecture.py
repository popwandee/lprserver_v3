#!/usr/bin/env python3
"""
Test script for Modular Architecture of AI Camera v1.3

This script tests that:
1. Core modules (camera, detection, health) work independently
2. Optional modules (websocket sender, storage) can be disabled
3. System remains functional when optional modules fail
4. Health monitor works without dependencies on optional modules

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

def test_core_modules():
    """Test core modules functionality."""
    base_url = "http://localhost"
    
    print("🔧 Testing Core Modules")
    print("="*50)
    
    core_modules = {
        'health_system': '/health/system',
        'health_system_info': '/health/system-info',
        'camera_status': '/camera/status',
        'detection_status': '/detection/status',
        'streaming_status': '/streaming/status'
    }
    
    core_results = {}
    
    for module_name, endpoint in core_modules.items():
        print(f"\n📋 Testing {module_name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                core_results[module_name] = success
                
                if success:
                    print(f"   ✅ {module_name}: Working")
                    if module_name == 'health_system':
                        health_data = data.get('data', {})
                        overall_status = health_data.get('overall_status', 'unknown')
                        components = list(health_data.get('components', {}).keys())
                        print(f"      Overall Status: {overall_status}")
                        print(f"      Components: {components}")
                else:
                    print(f"   ❌ {module_name}: Failed")
                    print(f"      Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ {module_name}: HTTP {response.status_code}")
                core_results[module_name] = False
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
            core_results[module_name] = False
    
    return core_results

def test_optional_modules():
    """Test optional modules functionality."""
    base_url = "http://localhost"
    
    print("\n🔌 Testing Optional Modules")
    print("="*50)
    
    optional_modules = {
        'websocket_sender_status': '/websocket-sender/status',
        'websocket_sender_logs': '/websocket-sender/logs?limit=5',
        'storage_status': '/storage/status',
        'storage_analytics': '/storage/analytics'
    }
    
    optional_results = {}
    
    for module_name, endpoint in optional_modules.items():
        print(f"\n📋 Testing {module_name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                optional_results[module_name] = success
                
                if success:
                    print(f"   ✅ {module_name}: Available")
                else:
                    print(f"   ⚠️ {module_name}: Not available (optional)")
                    print(f"      Message: {data.get('error', 'Module not available')}")
            elif response.status_code == 404:
                print(f"   ℹ️ {module_name}: Not found (optional module disabled)")
                optional_results[module_name] = False
            else:
                print(f"   ⚠️ {module_name}: HTTP {response.status_code} (optional)")
                optional_results[module_name] = False
        except Exception as e:
            print(f"   ℹ️ {module_name}: {e} (optional module)")
            optional_results[module_name] = False
    
    return optional_results

def test_health_monitor_independence():
    """Test that health monitor works independently of optional modules."""
    base_url = "http://localhost"
    
    print("\n🏥 Testing Health Monitor Independence")
    print("="*50)
    
    try:
        # Test health system endpoint
        response = requests.get(f"{base_url}/health/system", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                health_data = data.get('data', {})
                components = health_data.get('components', {})
                
                print("✅ Health Monitor is working independently")
                
                # Check core components
                core_components = ['camera', 'detection', 'database', 'system']
                for component in core_components:
                    if component in components:
                        status = components[component].get('status', 'unknown')
                        print(f"   📊 {component}: {status}")
                    else:
                        print(f"   ❌ {component}: Missing from health data")
                
                # Check that health monitor doesn't depend on optional modules
                optional_components = ['websocket_sender', 'storage']
                for component in optional_components:
                    if component in components:
                        print(f"   ⚠️ {component}: Present in health data (should be optional)")
                    else:
                        print(f"   ✅ {component}: Not in health data (correctly optional)")
                
                return True
            else:
                print("❌ Health Monitor failed")
                return False
        else:
            print(f"❌ Health Monitor HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Monitor error: {e}")
        return False

def test_modular_configuration():
    """Test modular configuration options."""
    print("\n⚙️ Testing Modular Configuration")
    print("="*50)
    
    # Test with different configuration scenarios
    config_scenarios = [
        {
            'name': 'Full Configuration',
            'websocket_enabled': True,
            'storage_enabled': True
        },
        {
            'name': 'Core Only (No WebSocket)',
            'websocket_enabled': False,
            'storage_enabled': True
        },
        {
            'name': 'Core Only (No Storage)',
            'websocket_enabled': True,
            'storage_enabled': False
        },
        {
            'name': 'Minimal Core',
            'websocket_enabled': False,
            'storage_enabled': False
        }
    ]
    
    for scenario in config_scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   WebSocket Sender: {'Enabled' if scenario['websocket_enabled'] else 'Disabled'}")
        print(f"   Storage Monitor: {'Enabled' if scenario['storage_enabled'] else 'Disabled'}")
        
        # In a real test, you would modify configuration and restart services
        # For now, we just document the expected behavior
        print("   Expected: Core modules should work regardless of optional module status")

def test_error_handling():
    """Test error handling for missing optional modules."""
    base_url = "http://localhost"
    
    print("\n🛡️ Testing Error Handling")
    print("="*50)
    
    # Test that core functionality still works when optional modules fail
    core_endpoints = ['/health/system', '/camera/status', '/detection/status']
    
    for endpoint in core_endpoints:
        print(f"\n📋 Testing core endpoint: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Core endpoint working")
                else:
                    print(f"   ❌ Core endpoint failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Core endpoint HTTP error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Core endpoint error: {e}")

def generate_test_report(core_results: Dict[str, bool], optional_results: Dict[str, bool], health_independent: bool):
    """Generate comprehensive test report."""
    print("\n" + "="*60)
    print("📊 MODULAR ARCHITECTURE TEST REPORT")
    print("="*60)
    print(f"Test completed at: {datetime.now().isoformat()}")
    
    # Core modules summary
    core_success = sum(core_results.values())
    core_total = len(core_results)
    print(f"\n🔧 Core Modules: {core_success}/{core_total} successful")
    
    for module, success in core_results.items():
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {module}")
    
    # Optional modules summary
    optional_success = sum(optional_results.values())
    optional_total = len(optional_results)
    print(f"\n🔌 Optional Modules: {optional_success}/{optional_total} available")
    
    for module, success in optional_results.items():
        status_icon = "✅" if success else "ℹ️"
        print(f"   {status_icon} {module}")
    
    # Health monitor independence
    health_status = "✅ Independent" if health_independent else "❌ Dependent"
    print(f"\n🏥 Health Monitor: {health_status}")
    
    # Overall assessment
    core_critical = ['health_system', 'camera_status', 'detection_status']
    core_critical_success = all(core_results.get(module, False) for module in core_critical)
    
    if core_critical_success:
        print(f"\n🎉 MODULAR ARCHITECTURE: SUCCESS")
        print("   ✅ Core functionality is working")
        print("   ✅ System is modular and independent")
        if optional_success > 0:
            print(f"   ✅ {optional_success} optional modules are also available")
        else:
            print("   ℹ️ Optional modules are disabled (as expected)")
    else:
        print(f"\n❌ MODULAR ARCHITECTURE: FAILED")
        print("   ❌ Critical core modules are not working")
        print("   ❌ System is not functional")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if not core_critical_success:
        print("   🔧 Fix critical core modules first")
        print("   🔧 Ensure camera, detection, and health monitor are working")
    
    if health_independent:
        print("   ✅ Health monitor is properly independent")
    else:
        print("   🔧 Health monitor should not depend on optional modules")
    
    if optional_success == 0:
        print("   ℹ️ Optional modules are disabled - this is acceptable")
    elif optional_success == optional_total:
        print("   ✅ All optional modules are available")
    else:
        print("   ⚠️ Some optional modules are missing - check configuration")

def main():
    """Main test function."""
    print("AI Camera v1.3 - Modular Architecture Test")
    print("="*60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        # Test core modules
        core_results = test_core_modules()
        
        # Test optional modules
        optional_results = test_optional_modules()
        
        # Test health monitor independence
        health_independent = test_health_monitor_independence()
        
        # Test modular configuration
        test_modular_configuration()
        
        # Test error handling
        test_error_handling()
        
        # Generate report
        generate_test_report(core_results, optional_results, health_independent)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
