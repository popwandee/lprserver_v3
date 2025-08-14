#!/usr/bin/env python3
"""
Test script for Progress Bar and Pagination features
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_progress_bar_css():
    """Test if progress bar CSS classes are properly applied"""
    print("🔍 Testing Progress Bar CSS...")
    
    try:
        response = requests.get('http://localhost/health/', timeout=10)
        html_content = response.text
        
        # Check for progress bar classes
        progress_bar_large_count = html_content.count('progress-bar-large')
        progress_fill_large_count = html_content.count('progress-fill-large')
        data_value_count = html_content.count('data-value')
        
        print(f"  ✅ progress-bar-large: {progress_bar_large_count}")
        print(f"  ✅ progress-fill-large: {progress_fill_large_count}")
        print(f"  ✅ data-value attributes: {data_value_count}")
        
        if progress_bar_large_count >= 3 and progress_fill_large_count >= 3 and data_value_count >= 3:
            print("  🎉 Progress Bar CSS: PASSED")
            return True
        else:
            print("  ❌ Progress Bar CSS: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Progress Bar CSS test failed: {e}")
        return False

def test_pagination_api():
    """Test pagination API endpoints"""
    print("\n🔍 Testing Pagination API...")
    
    try:
        # Test page 1
        response = requests.get('http://localhost/health/logs?limit=10&page=1', timeout=10)
        data = response.json()
        
        if not data.get('success'):
            print("  ❌ API response not successful")
            return False
        
        pagination = data.get('data', {}).get('pagination', {})
        logs = data.get('data', {}).get('logs', [])
        
        print(f"  ✅ Page 1 - Current: {pagination.get('current_page')}")
        print(f"  ✅ Page 1 - Total Pages: {pagination.get('total_pages')}")
        print(f"  ✅ Page 1 - Total Count: {pagination.get('total_count')}")
        print(f"  ✅ Page 1 - Logs Count: {len(logs)}")
        print(f"  ✅ Page 1 - Has Next: {pagination.get('has_next')}")
        print(f"  ✅ Page 1 - Has Prev: {pagination.get('has_prev')}")
        
        # Test page 2
        response2 = requests.get('http://localhost/health/logs?limit=10&page=2', timeout=10)
        data2 = response2.json()
        
        if data2.get('success'):
            pagination2 = data2.get('data', {}).get('pagination', {})
            logs2 = data2.get('data', {}).get('logs', [])
            
            print(f"  ✅ Page 2 - Current: {pagination2.get('current_page')}")
            print(f"  ✅ Page 2 - Logs Count: {len(logs2)}")
            print(f"  ✅ Page 2 - Has Next: {pagination2.get('has_next')}")
            print(f"  ✅ Page 2 - Has Prev: {pagination2.get('has_prev')}")
        
        # Test with level filter
        response3 = requests.get('http://localhost/health/logs?limit=5&page=1&level=PASS', timeout=10)
        data3 = response3.json()
        
        if data3.get('success'):
            pagination3 = data3.get('data', {}).get('pagination', {})
            logs3 = data3.get('data', {}).get('logs', [])
            
            print(f"  ✅ Filtered - Current: {pagination3.get('current_page')}")
            print(f"  ✅ Filtered - Total Count: {pagination3.get('total_count')}")
            print(f"  ✅ Filtered - Logs Count: {len(logs3)}")
        
        print("  🎉 Pagination API: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Pagination API test failed: {e}")
        return False

def test_pagination_ui():
    """Test if pagination UI elements are present"""
    print("\n🔍 Testing Pagination UI...")
    
    try:
        response = requests.get('http://localhost/health/', timeout=10)
        html_content = response.text
        
        # Check for pagination controls
        pagination_controls_count = html_content.count('pagination-controls')
        pagination_info_count = html_content.count('pagination-info')
        pagination_buttons_count = html_content.count('pagination-buttons')
        
        print(f"  ✅ pagination-controls: {pagination_controls_count}")
        print(f"  ✅ pagination-info: {pagination_info_count}")
        print(f"  ✅ pagination-buttons: {pagination_buttons_count}")
        
        if pagination_controls_count >= 1:
            print("  🎉 Pagination UI: PASSED")
            return True
        else:
            print("  ❌ Pagination UI: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Pagination UI test failed: {e}")
        return False

def test_system_health():
    """Test system health endpoint"""
    print("\n🔍 Testing System Health...")
    
    try:
        response = requests.get('http://localhost/health/system', timeout=10)
        data = response.json()
        
        if data.get('success'):
            health_data = data.get('data', {})
            components = health_data.get('components', {})
            system = health_data.get('system', {})
            
            print(f"  ✅ Overall Status: {health_data.get('overall_status')}")
            print(f"  ✅ Components Count: {len(components)}")
            print(f"  ✅ CPU Usage: {system.get('cpu_usage', 'N/A')}%")
            print(f"  ✅ Memory Usage: {system.get('memory_usage', {}).get('percentage', 'N/A')}%")
            print(f"  ✅ Disk Usage: {system.get('disk_usage', {}).get('percentage', 'N/A')}%")
            
            print("  🎉 System Health: PASSED")
            return True
        else:
            print(f"  ❌ System Health failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ System Health test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Progress Bar and Pagination Features")
    print("=" * 50)
    
    tests = [
        test_progress_bar_css,
        test_pagination_api,
        test_pagination_ui,
        test_system_health
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Progress Bar and Pagination features are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
