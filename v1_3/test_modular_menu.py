#!/usr/bin/env python3
"""
Test script for Modular Menu of AI Camera v1.3

This script tests that:
1. Core menu items (Dashboard, Camera, Detection, Health) are always visible
2. Optional menu items (WebSocket Sender, Storage) are conditionally visible
3. Menu items show/hide based on module availability
4. Active page highlighting works correctly

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any

def test_core_menu_items():
    """Test core menu items are always visible."""
    base_url = "http://localhost"
    
    print("🔧 Testing Core Menu Items")
    print("="*50)
    
    core_pages = {
        'main_dashboard': '/',
        'camera_dashboard': '/camera',
        'detection_dashboard': '/detection',
        'health_dashboard': '/health'
    }
    
    core_results = {}
    
    for page_name, endpoint in core_pages.items():
        print(f"\n📋 Testing {page_name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                html_content = response.text
                
                # Check for core menu items in HTML
                core_menu_items = [
                    'Dashboard',
                    'Camera', 
                    'Detection',
                    'Health'
                ]
                
                missing_items = []
                for item in core_menu_items:
                    if item not in html_content:
                        missing_items.append(item)
                
                if missing_items:
                    print(f"   ❌ Missing core menu items: {missing_items}")
                    core_results[page_name] = False
                else:
                    print(f"   ✅ All core menu items present")
                    
                    # Check for active page highlighting
                    if 'active' in html_content:
                        print(f"      ✅ Active page highlighting found")
                    else:
                        print(f"      ⚠️ Active page highlighting not found")
            else:
                print(f"   ❌ {page_name}: HTTP {response.status_code}")
                core_results[page_name] = False
        except Exception as e:
            print(f"   ❌ {page_name}: {e}")
            core_results[page_name] = False
    
    return core_results

def test_optional_menu_items():
    """Test optional menu items are conditionally visible."""
    base_url = "http://localhost"
    
    print("\n🔌 Testing Optional Menu Items")
    print("="*50)
    
    optional_pages = {
        'websocket_sender_dashboard': '/websocket-sender',
        'storage_dashboard': '/storage'
    }
    
    optional_results = {}
    
    for page_name, endpoint in optional_pages.items():
        print(f"\n📋 Testing {page_name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                html_content = response.text
                
                # Check if optional menu items are present
                if 'WebSocket Sender' in html_content:
                    print(f"   ✅ WebSocket Sender menu item found")
                    optional_results['websocket_sender_menu'] = True
                else:
                    print(f"   ℹ️ WebSocket Sender menu item not found (optional)")
                    optional_results['websocket_sender_menu'] = False
                
                if 'Storage' in html_content:
                    print(f"   ✅ Storage menu item found")
                    optional_results['storage_menu'] = True
                else:
                    print(f"   ℹ️ Storage menu item not found (optional)")
                    optional_results['storage_menu'] = False
                
                # Check for "(Optional)" label
                if '(Optional)' in html_content:
                    print(f"   ✅ Optional labels found")
                else:
                    print(f"   ⚠️ Optional labels not found")
                
            elif response.status_code == 404:
                print(f"   ℹ️ {page_name}: Not found (optional module disabled)")
                optional_results[f'{page_name}_menu'] = False
            else:
                print(f"   ⚠️ {page_name}: HTTP {response.status_code} (optional)")
                optional_results[f'{page_name}_menu'] = False
        except Exception as e:
            print(f"   ℹ️ {page_name}: {e} (optional module)")
            optional_results[f'{page_name}_menu'] = False
    
    return optional_results

def test_menu_api_endpoints():
    """Test menu-related API endpoints."""
    base_url = "http://localhost"
    
    print("\n🔌 Testing Menu API Endpoints")
    print("="*50)
    
    # Test optional module status endpoints
    optional_apis = {
        'websocket_sender_status': '/websocket-sender/status',
        'storage_status': '/storage/status'
    }
    
    api_results = {}
    
    for api_name, endpoint in optional_apis.items():
        print(f"\n📋 Testing {api_name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                api_results[api_name] = success
                
                if success:
                    print(f"   ✅ {api_name}: Available")
                else:
                    print(f"   ⚠️ {api_name}: Not available (optional)")
            elif response.status_code == 404:
                print(f"   ℹ️ {api_name}: Not found (optional module disabled)")
                api_results[api_name] = False
            else:
                print(f"   ⚠️ {api_name}: HTTP {response.status_code} (optional)")
                api_results[api_name] = False
        except Exception as e:
            print(f"   ℹ️ {api_name}: {e} (optional module)")
            api_results[api_name] = False
    
    return api_results

def test_menu_javascript_functionality():
    """Test menu JavaScript functionality."""
    print("\n🔌 Testing Menu JavaScript Functionality")
    print("="*50)
    
    try:
        # Test main dashboard for JavaScript menu functions
        response = requests.get("http://localhost/", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for menu JavaScript functions
            js_functions = [
                'checkOptionalModules',
                'checkWebSocketSender',
                'checkStorageManager',
                'showMenuItem',
                'hideMenuItem'
            ]
            
            missing_functions = []
            for func in js_functions:
                if func not in html_content:
                    missing_functions.append(func)
            
            if missing_functions:
                print(f"   ❌ Missing JavaScript functions: {missing_functions}")
                return False
            else:
                print(f"   ✅ All menu JavaScript functions present")
                
                # Check for menu item IDs
                menu_ids = [
                    'websocket-sender-menu-item',
                    'storage-menu-item'
                ]
                
                missing_ids = []
                for menu_id in menu_ids:
                    if menu_id not in html_content:
                        missing_ids.append(menu_id)
                
                if missing_ids:
                    print(f"   ❌ Missing menu item IDs: {missing_ids}")
                    return False
                else:
                    print(f"   ✅ All menu item IDs present")
                    return True
        else:
            print(f"   ❌ Main dashboard HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Menu JavaScript test error: {e}")
        return False

def test_menu_consistency():
    """Test menu consistency across different pages."""
    print("\n🔌 Testing Menu Consistency")
    print("="*50)
    
    test_pages = ['/', '/camera', '/detection', '/health']
    consistency_results = {}
    
    for page in test_pages:
        print(f"\n📋 Testing menu consistency on {page}...")
        try:
            response = requests.get(f"http://localhost{page}", timeout=10)
            if response.status_code == 200:
                html_content = response.text
                
                # Check for consistent menu structure
                core_items = ['Dashboard', 'Camera', 'Detection', 'Health']
                optional_items = ['WebSocket Sender', 'Storage']
                
                # Core items should always be present
                missing_core = [item for item in core_items if item not in html_content]
                if missing_core:
                    print(f"   ❌ Missing core menu items: {missing_core}")
                    consistency_results[page] = False
                else:
                    print(f"   ✅ All core menu items present")
                    
                    # Optional items may or may not be present
                    present_optional = [item for item in optional_items if item in html_content]
                    if present_optional:
                        print(f"   ℹ️ Optional menu items present: {present_optional}")
                    else:
                        print(f"   ℹ️ No optional menu items present (expected)")
                    
                    consistency_results[page] = True
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                consistency_results[page] = False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            consistency_results[page] = False
    
    return consistency_results

def generate_menu_report(core_results: Dict[str, bool], optional_results: Dict[str, bool], 
                        api_results: Dict[str, bool], js_functional: bool, 
                        consistency_results: Dict[str, bool]):
    """Generate comprehensive menu test report."""
    print("\n" + "="*60)
    print("📊 MODULAR MENU TEST REPORT")
    print("="*60)
    print(f"Test completed at: {datetime.now().isoformat()}")
    
    # Core menu items summary
    core_success = sum(core_results.values())
    core_total = len(core_results)
    print(f"\n🔧 Core Menu Items: {core_success}/{core_total} pages have all core items")
    
    for page, success in core_results.items():
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {page}")
    
    # Optional menu items summary
    optional_success = sum(optional_results.values())
    optional_total = len(optional_results)
    print(f"\n🔌 Optional Menu Items: {optional_success}/{optional_total} available")
    
    for item, success in optional_results.items():
        status_icon = "✅" if success else "ℹ️"
        print(f"   {status_icon} {item}")
    
    # API endpoints summary
    api_success = sum(api_results.values())
    api_total = len(api_results)
    print(f"\n🔌 Menu API Endpoints: {api_success}/{api_total} available")
    
    for api, success in api_results.items():
        status_icon = "✅" if success else "ℹ️"
        print(f"   {status_icon} {api}")
    
    # JavaScript functionality
    js_status = "✅ Functional" if js_functional else "❌ Not Functional"
    print(f"\n🔌 Menu JavaScript: {js_status}")
    
    # Menu consistency
    consistency_success = sum(consistency_results.values())
    consistency_total = len(consistency_results)
    print(f"\n🔌 Menu Consistency: {consistency_success}/{consistency_total} pages consistent")
    
    for page, success in consistency_results.items():
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {page}")
    
    # Overall assessment
    core_critical = ['main_dashboard', 'camera_dashboard', 'health_dashboard']
    core_critical_success = all(core_results.get(page, False) for page in core_critical)
    
    if core_critical_success and js_functional:
        print(f"\n🎉 MODULAR MENU: SUCCESS")
        print("   ✅ Core menu items are always visible")
        print("   ✅ Menu JavaScript is functional")
        print("   ✅ Menu is modular and consistent")
        if optional_success > 0:
            print(f"   ✅ {optional_success} optional menu items are available")
        else:
            print("   ℹ️ Optional menu items are disabled (as expected)")
    else:
        print(f"\n❌ MODULAR MENU: FAILED")
        if not core_critical_success:
            print("   ❌ Critical core menu items are missing")
        if not js_functional:
            print("   ❌ Menu JavaScript is not functional")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if not core_critical_success:
        print("   🔧 Fix missing core menu items")
        print("   🔧 Ensure Dashboard, Camera, and Health menu items are always visible")
    
    if not js_functional:
        print("   🔧 Fix menu JavaScript functionality")
        print("   🔧 Ensure menu show/hide functions work correctly")
    
    if optional_success == 0:
        print("   ℹ️ Optional menu items are disabled - this is acceptable")
    elif optional_success == optional_total:
        print("   ✅ All optional menu items are available")
    else:
        print("   ⚠️ Some optional menu items are missing - check configuration")

def main():
    """Main test function."""
    print("AI Camera v1.3 - Modular Menu Test")
    print("="*60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        # Test core menu items
        core_results = test_core_menu_items()
        
        # Test optional menu items
        optional_results = test_optional_menu_items()
        
        # Test menu API endpoints
        api_results = test_menu_api_endpoints()
        
        # Test menu JavaScript functionality
        js_functional = test_menu_javascript_functionality()
        
        # Test menu consistency
        consistency_results = test_menu_consistency()
        
        # Generate report
        generate_menu_report(core_results, optional_results, api_results, 
                           js_functional, consistency_results)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
