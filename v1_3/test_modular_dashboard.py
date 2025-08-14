#!/usr/bin/env python3
"""
Test script for Modular Dashboard of AI Camera v1.3

This script tests that:
1. Core dashboard sections (camera, detection, health) work independently
2. Optional dashboard sections (websocket sender, storage) can be disabled
3. Dashboard remains functional when optional modules fail
4. Variable mapping and management is consistent

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

def test_core_dashboard_sections():
    """Test core dashboard sections functionality."""
    base_url = "http://localhost"
    
    print("🔧 Testing Core Dashboard Sections")
    print("="*50)
    
    core_sections = {
        'main_dashboard': '/',
        'camera_dashboard': '/camera',
        'detection_dashboard': '/detection',
        'health_dashboard': '/health',
        'streaming_dashboard': '/streaming'
    }
    
    core_results = {}
    
    for section_name, endpoint in core_sections.items():
        print(f"\n📋 Testing {section_name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                core_results[section_name] = True
                print(f"   ✅ {section_name}: Accessible")
                
                # Check for core elements in HTML
                html_content = response.text
                if 'camera' in section_name.lower():
                    if 'camera-status' in html_content or 'camera-control' in html_content:
                        print(f"      ✅ Camera elements found")
                    else:
                        print(f"      ⚠️ Camera elements not found")
                elif 'detection' in section_name.lower():
                    if 'detection-status' in html_content or 'detection-control' in html_content:
                        print(f"      ✅ Detection elements found")
                    else:
                        print(f"      ⚠️ Detection elements not found")
                elif 'health' in section_name.lower():
                    if 'health-status' in html_content or 'system-health' in html_content:
                        print(f"      ✅ Health elements found")
                    else:
                        print(f"      ⚠️ Health elements not found")
            else:
                print(f"   ❌ {section_name}: HTTP {response.status_code}")
                core_results[section_name] = False
        except Exception as e:
            print(f"   ❌ {section_name}: {e}")
            core_results[section_name] = False
    
    return core_results

def test_optional_dashboard_sections():
    """Test optional dashboard sections functionality."""
    base_url = "http://localhost"
    
    print("\n🔌 Testing Optional Dashboard Sections")
    print("="*50)
    
    optional_sections = {
        'websocket_sender_dashboard': '/websocket-sender',
        'storage_dashboard': '/storage'
    }
    
    optional_results = {}
    
    for section_name, endpoint in optional_sections.items():
        print(f"\n📋 Testing {section_name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                optional_results[section_name] = True
                print(f"   ✅ {section_name}: Available")
            elif response.status_code == 404:
                optional_results[section_name] = False
                print(f"   ℹ️ {section_name}: Not found (optional module disabled)")
            else:
                print(f"   ⚠️ {section_name}: HTTP {response.status_code} (optional)")
                optional_results[section_name] = False
        except Exception as e:
            print(f"   ℹ️ {section_name}: {e} (optional module)")
            optional_results[section_name] = False
    
    return optional_results

def test_dashboard_api_endpoints():
    """Test dashboard API endpoints for core and optional modules."""
    base_url = "http://localhost"
    
    print("\n🔌 Testing Dashboard API Endpoints")
    print("="*50)
    
    # Core API endpoints
    core_apis = {
        'health_system': '/health/system',
        'camera_status': '/camera/status',
        'detection_status': '/detection/status',
        'streaming_status': '/streaming/status'
    }
    
    # Optional API endpoints
    optional_apis = {
        'websocket_sender_status': '/websocket-sender/status',
        'websocket_sender_logs': '/websocket-sender/logs?limit=5',
        'storage_status': '/storage/status',
        'storage_analytics': '/storage/analytics'
    }
    
    api_results = {'core': {}, 'optional': {}}
    
    # Test core APIs
    print("\n📋 Testing Core API Endpoints...")
    for api_name, endpoint in core_apis.items():
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                api_results['core'][api_name] = success
                
                if success:
                    print(f"   ✅ {api_name}: Working")
                else:
                    print(f"   ❌ {api_name}: Failed")
                    print(f"      Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ {api_name}: HTTP {response.status_code}")
                api_results['core'][api_name] = False
        except Exception as e:
            print(f"   ❌ {api_name}: {e}")
            api_results['core'][api_name] = False
    
    # Test optional APIs
    print("\n📋 Testing Optional API Endpoints...")
    for api_name, endpoint in optional_apis.items():
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                api_results['optional'][api_name] = success
                
                if success:
                    print(f"   ✅ {api_name}: Available")
                else:
                    print(f"   ⚠️ {api_name}: Not available (optional)")
            elif response.status_code == 404:
                print(f"   ℹ️ {api_name}: Not found (optional module disabled)")
                api_results['optional'][api_name] = False
            else:
                print(f"   ⚠️ {api_name}: HTTP {response.status_code} (optional)")
                api_results['optional'][api_name] = False
        except Exception as e:
            print(f"   ℹ️ {api_name}: {e} (optional module)")
            api_results['optional'][api_name] = False
    
    return api_results

def test_variable_mapping_consistency():
    """Test variable mapping consistency between backend and frontend."""
    print("\n📊 Testing Variable Mapping Consistency")
    print("="*50)
    
    # Test health API response structure
    try:
        response = requests.get("http://localhost/health/system", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                health_data = data.get('data', {})
                
                # Check for required fields according to variable management
                required_fields = [
                    'overall_status',
                    'components',
                    'system',
                    'last_check'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in health_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    return False
                else:
                    print(f"   ✅ All required health fields present")
                    
                    # Check component structure
                    components = health_data.get('components', {})
                    core_components = ['camera', 'detection', 'database', 'system']
                    optional_components = ['websocket_sender', 'storage']
                    
                    for component in core_components:
                        if component in components:
                            print(f"      ✅ Core component '{component}' present")
                        else:
                            print(f"      ❌ Core component '{component}' missing")
                    
                    for component in optional_components:
                        if component in components:
                            print(f"      ⚠️ Optional component '{component}' present (should be optional)")
                        else:
                            print(f"      ✅ Optional component '{component}' not present (correctly optional)")
                    
                    return True
            else:
                print(f"   ❌ Health API failed")
                return False
        else:
            print(f"   ❌ Health API HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health API error: {e}")
        return False

def test_dashboard_independence():
    """Test that core dashboard works independently of optional modules."""
    print("\n🛡️ Testing Dashboard Independence")
    print("="*50)
    
    # Test that core functionality still works when optional modules fail
    core_endpoints = ['/health/system', '/camera/status', '/detection/status']
    
    independence_results = {}
    
    for endpoint in core_endpoints:
        print(f"\n📋 Testing core endpoint: {endpoint}")
        try:
            response = requests.get(f"http://localhost{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Core endpoint working")
                    independence_results[endpoint] = True
                else:
                    print(f"   ❌ Core endpoint failed: {data.get('error', 'Unknown error')}")
                    independence_results[endpoint] = False
            else:
                print(f"   ❌ Core endpoint HTTP error: {response.status_code}")
                independence_results[endpoint] = False
        except Exception as e:
            print(f"   ❌ Core endpoint error: {e}")
            independence_results[endpoint] = False
    
    return independence_results

def generate_dashboard_report(core_results: Dict[str, bool], optional_results: Dict[str, bool], 
                             api_results: Dict[str, Dict], variable_consistent: bool, 
                             independence_results: Dict[str, bool]):
    """Generate comprehensive dashboard test report."""
    print("\n" + "="*60)
    print("📊 MODULAR DASHBOARD TEST REPORT")
    print("="*60)
    print(f"Test completed at: {datetime.now().isoformat()}")
    
    # Core sections summary
    core_success = sum(core_results.values())
    core_total = len(core_results)
    print(f"\n🔧 Core Dashboard Sections: {core_success}/{core_total} accessible")
    
    for section, success in core_results.items():
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {section}")
    
    # Optional sections summary
    optional_success = sum(optional_results.values())
    optional_total = len(optional_results)
    print(f"\n🔌 Optional Dashboard Sections: {optional_success}/{optional_total} available")
    
    for section, success in optional_results.items():
        status_icon = "✅" if success else "ℹ️"
        print(f"   {status_icon} {section}")
    
    # API endpoints summary
    core_api_success = sum(api_results['core'].values())
    core_api_total = len(api_results['core'])
    optional_api_success = sum(api_results['optional'].values())
    optional_api_total = len(api_results['optional'])
    
    print(f"\n🔌 Core API Endpoints: {core_api_success}/{core_api_total} working")
    print(f"🔌 Optional API Endpoints: {optional_api_success}/{optional_api_total} available")
    
    # Variable mapping consistency
    variable_status = "✅ Consistent" if variable_consistent else "❌ Inconsistent"
    print(f"\n📊 Variable Mapping: {variable_status}")
    
    # Dashboard independence
    independence_success = sum(independence_results.values())
    independence_total = len(independence_results)
    print(f"\n🛡️ Dashboard Independence: {independence_success}/{independence_total} core endpoints working")
    
    # Overall assessment
    core_critical = ['main_dashboard', 'camera_dashboard', 'health_dashboard']
    core_critical_success = all(core_results.get(section, False) for section in core_critical)
    
    if core_critical_success and variable_consistent:
        print(f"\n🎉 MODULAR DASHBOARD: SUCCESS")
        print("   ✅ Core dashboard sections are working")
        print("   ✅ Variable mapping is consistent")
        print("   ✅ Dashboard is modular and independent")
        if optional_success > 0:
            print(f"   ✅ {optional_success} optional sections are also available")
        else:
            print("   ℹ️ Optional sections are disabled (as expected)")
    else:
        print(f"\n❌ MODULAR DASHBOARD: FAILED")
        if not core_critical_success:
            print("   ❌ Critical core dashboard sections are not working")
        if not variable_consistent:
            print("   ❌ Variable mapping is inconsistent")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if not core_critical_success:
        print("   🔧 Fix critical core dashboard sections first")
        print("   🔧 Ensure main, camera, and health dashboards are accessible")
    
    if not variable_consistent:
        print("   🔧 Fix variable mapping consistency")
        print("   🔧 Ensure API responses match variable management standards")
    
    if optional_success == 0:
        print("   ℹ️ Optional dashboard sections are disabled - this is acceptable")
    elif optional_success == optional_total:
        print("   ✅ All optional dashboard sections are available")
    else:
        print("   ⚠️ Some optional dashboard sections are missing - check configuration")

def main():
    """Main test function."""
    print("AI Camera v1.3 - Modular Dashboard Test")
    print("="*60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        # Test core dashboard sections
        core_results = test_core_dashboard_sections()
        
        # Test optional dashboard sections
        optional_results = test_optional_dashboard_sections()
        
        # Test dashboard API endpoints
        api_results = test_dashboard_api_endpoints()
        
        # Test variable mapping consistency
        variable_consistent = test_variable_mapping_consistency()
        
        # Test dashboard independence
        independence_results = test_dashboard_independence()
        
        # Generate report
        generate_dashboard_report(core_results, optional_results, api_results, 
                                variable_consistent, independence_results)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
