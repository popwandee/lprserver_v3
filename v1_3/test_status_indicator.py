#!/usr/bin/env python3
"""
Test script for Status Indicator improvements
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_status_indicator_css():
    """Test if status indicator CSS is properly updated"""
    print("🔍 Testing Status Indicator CSS...")
    
    try:
        # Check CSS file directly
        response = requests.get('http://localhost/static/css/health.css', timeout=10)
        css_content = response.text
        
        # Check for new CSS properties
        has_inline_flex = 'display: inline-flex' in css_content
        has_fit_content = 'width: fit-content' in css_content
        has_height_32px = 'height: 32px' in css_content
        has_padding_8px = 'padding: 8px 16px' in css_content
        has_border_radius_20px = 'border-radius: 20px' in css_content
        
        print(f"  ✅ inline-flex: {has_inline_flex}")
        print(f"  ✅ fit-content: {has_fit_content}")
        print(f"  ✅ height 32px: {has_height_32px}")
        print(f"  ✅ padding 8px 16px: {has_padding_8px}")
        print(f"  ✅ border-radius 20px: {has_border_radius_20px}")
        
        if has_inline_flex and has_fit_content and has_height_32px:
            print("  🎉 Status Indicator CSS: PASSED")
            return True
        else:
            print("  ❌ Status Indicator CSS: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Status Indicator CSS test failed: {e}")
        return False

def test_status_indicator_usage():
    """Test if status indicators are properly used in cards"""
    print("\n🔍 Testing Status Indicator Usage...")
    
    try:
        response = requests.get('http://localhost/health/', timeout=10)
        html_content = response.text
        
        # Check for status indicator usage
        status_indicator_count = html_content.count('status-indicator')
        create_status_indicator_count = html_content.count('createStatusIndicator')
        
        print(f"  ✅ status-indicator class count: {status_indicator_count}")
        print(f"  ✅ createStatusIndicator function count: {create_status_indicator_count}")
        
        # Check for different status types
        has_healthy = 'status-healthy' in html_content
        has_unhealthy = 'status-unhealthy' in html_content
        has_critical = 'status-critical' in html_content
        has_unknown = 'status-unknown' in html_content
        
        print(f"  ✅ status-healthy: {has_healthy}")
        print(f"  ✅ status-unhealthy: {has_unhealthy}")
        print(f"  ✅ status-critical: {has_critical}")
        print(f"  ✅ status-unknown: {has_unknown}")
        
        if status_indicator_count >= 2 and create_status_indicator_count >= 4:
            print("  🎉 Status Indicator Usage: PASSED")
            return True
        else:
            print("  ❌ Status Indicator Usage: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Status Indicator Usage test failed: {e}")
        return False

def test_responsive_status_indicator():
    """Test responsive design for status indicators"""
    print("\n🔍 Testing Responsive Status Indicator...")
    
    try:
        # Check CSS file directly
        response = requests.get('http://localhost/static/css/health.css', timeout=10)
        css_content = response.text
        
        # Check for responsive CSS
        has_tablet_media = '@media (max-width: 768px)' in css_content
        has_mobile_media = '@media (max-width: 480px)' in css_content
        
        # Check for responsive status indicator rules
        has_tablet_status = 'height: 28px' in css_content
        has_mobile_status = 'height: 24px' in css_content
        
        print(f"  ✅ Tablet media query: {has_tablet_media}")
        print(f"  ✅ Mobile media query: {has_mobile_media}")
        print(f"  ✅ Tablet height 28px: {has_tablet_status}")
        print(f"  ✅ Mobile height 24px: {has_mobile_status}")
        
        if has_tablet_media and has_mobile_media and has_tablet_status and has_mobile_status:
            print("  🎉 Responsive Status Indicator: PASSED")
            return True
        else:
            print("  ❌ Responsive Status Indicator: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Responsive Status Indicator test failed: {e}")
        return False

def test_status_indicator_sizes():
    """Test status indicator size variations"""
    print("\n🔍 Testing Status Indicator Sizes...")
    
    try:
        # Check CSS file directly
        response = requests.get('http://localhost/static/css/health.css', timeout=10)
        css_content = response.text
        
        # Check for size variations
        has_min_width_auto = 'min-width: auto' in css_content
        has_width_fit_content = 'width: fit-content' in css_content
        has_white_space_nowrap = 'white-space: nowrap' in css_content
        
        print(f"  ✅ min-width: auto: {has_min_width_auto}")
        print(f"  ✅ width: fit-content: {has_width_fit_content}")
        print(f"  ✅ white-space: nowrap: {has_white_space_nowrap}")
        
        if has_min_width_auto and has_width_fit_content and has_white_space_nowrap:
            print("  🎉 Status Indicator Sizes: PASSED")
            return True
        else:
            print("  ❌ Status Indicator Sizes: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Status Indicator Sizes test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Status Indicator Improvements")
    print("=" * 50)
    
    tests = [
        test_status_indicator_css,
        test_status_indicator_usage,
        test_responsive_status_indicator,
        test_status_indicator_sizes
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
        print("🎉 All tests passed! Status Indicator improvements are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
