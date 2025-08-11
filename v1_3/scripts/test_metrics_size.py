#!/usr/bin/env python3
"""
Test script for Metrics Size improvements
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_health_metrics_size():
    """Test if health metrics have been reduced in size"""
    print("🔍 Testing Health Metrics Size...")
    
    try:
        # Check CSS file directly
        response = requests.get('http://localhost/static/css/health.css', timeout=10)
        css_content = response.text
        
        # Check for reduced sizes
        has_minmax_140px = 'minmax(140px, 1fr)' in css_content
        has_gap_12px = 'gap: 12px' in css_content
        has_padding_12px = 'padding: 12px' in css_content
        has_min_width_120px = 'min-width: 120px' in css_content
        has_border_radius_10px = 'border-radius: 10px' in css_content
        
        print(f"  ✅ minmax(140px, 1fr): {has_minmax_140px}")
        print(f"  ✅ gap: 12px: {has_gap_12px}")
        print(f"  ✅ padding: 12px: {has_padding_12px}")
        print(f"  ✅ min-width: 120px: {has_min_width_120px}")
        print(f"  ✅ border-radius: 10px: {has_border_radius_10px}")
        
        if has_minmax_140px and has_gap_12px and has_padding_12px and has_min_width_120px:
            print("  🎉 Health Metrics Size: PASSED")
            return True
        else:
            print("  ❌ Health Metrics Size: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Health Metrics Size test failed: {e}")
        return False

def test_metric_item_size():
    """Test if metric items have been reduced in size"""
    print("\n🔍 Testing Metric Item Size...")
    
    try:
        # Check CSS file directly
        response = requests.get('http://localhost/static/css/health.css', timeout=10)
        css_content = response.text
        
        # Check for reduced sizes
        has_font_size_1_4rem = 'font-size: 1.4rem' in css_content
        has_margin_bottom_6px = 'margin-bottom: 6px' in css_content
        has_font_size_0_75rem = 'font-size: 0.75rem' in css_content
        has_letter_spacing_0_3px = 'letter-spacing: 0.3px' in css_content
        
        print(f"  ✅ font-size: 1.4rem: {has_font_size_1_4rem}")
        print(f"  ✅ margin-bottom: 6px: {has_margin_bottom_6px}")
        print(f"  ✅ font-size: 0.75rem: {has_font_size_0_75rem}")
        print(f"  ✅ letter-spacing: 0.3px: {has_letter_spacing_0_3px}")
        
        if has_font_size_1_4rem and has_margin_bottom_6px and has_font_size_0_75rem:
            print("  🎉 Metric Item Size: PASSED")
            return True
        else:
            print("  ❌ Metric Item Size: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Metric Item Size test failed: {e}")
        return False

def test_progress_bar_size():
    """Test if progress bars have been reduced in size"""
    print("\n🔍 Testing Progress Bar Size...")
    
    try:
        # Check CSS file directly
        response = requests.get('http://localhost/static/css/health.css', timeout=10)
        css_content = response.text
        
        # Check for reduced sizes
        has_height_10px = 'height: 10px' in css_content
        has_border_radius_6px = 'border-radius: 6px' in css_content
        has_margin_top_8px = 'margin-top: 8px' in css_content
        has_min_width_120px = 'min-width: 120px' in css_content
        
        print(f"  ✅ height: 10px: {has_height_10px}")
        print(f"  ✅ border-radius: 6px: {has_border_radius_6px}")
        print(f"  ✅ margin-top: 8px: {has_margin_top_8px}")
        print(f"  ✅ min-width: 120px: {has_min_width_120px}")
        
        if has_height_10px and has_border_radius_6px and has_margin_top_8px and has_min_width_120px:
            print("  🎉 Progress Bar Size: PASSED")
            return True
        else:
            print("  ❌ Progress Bar Size: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Progress Bar Size test failed: {e}")
        return False

def test_responsive_metrics():
    """Test responsive design for metrics"""
    print("\n🔍 Testing Responsive Metrics...")
    
    try:
        # Check CSS file directly
        response = requests.get('http://localhost/static/css/health.css', timeout=10)
        css_content = response.text
        
        # Check for responsive rules
        has_tablet_minmax_120px = 'minmax(120px, 1fr)' in css_content
        has_tablet_gap_10px = 'gap: 10px' in css_content
        has_mobile_1fr = 'grid-template-columns: 1fr' in css_content
        has_mobile_padding_8px = 'padding: 8px' in css_content
        has_mobile_font_1_2rem = 'font-size: 1.2rem' in css_content
        
        print(f"  ✅ Tablet minmax(120px, 1fr): {has_tablet_minmax_120px}")
        print(f"  ✅ Tablet gap: 10px: {has_tablet_gap_10px}")
        print(f"  ✅ Mobile 1fr: {has_mobile_1fr}")
        print(f"  ✅ Mobile padding: 8px: {has_mobile_padding_8px}")
        print(f"  ✅ Mobile font-size: 1.2rem: {has_mobile_font_1_2rem}")
        
        if has_tablet_minmax_120px and has_tablet_gap_10px and has_mobile_1fr and has_mobile_padding_8px:
            print("  🎉 Responsive Metrics: PASSED")
            return True
        else:
            print("  ❌ Responsive Metrics: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Responsive Metrics test failed: {e}")
        return False

def test_metrics_layout():
    """Test if metrics layout is properly structured"""
    print("\n🔍 Testing Metrics Layout...")
    
    try:
        response = requests.get('http://localhost/health/', timeout=10)
        html_content = response.text
        
        # Check for metrics structure
        health_metrics_count = html_content.count('health-metrics')
        metric_item_count = html_content.count('metric-item')
        metric_value_count = html_content.count('metric-value')
        metric_label_count = html_content.count('metric-label')
        
        print(f"  ✅ health-metrics count: {health_metrics_count}")
        print(f"  ✅ metric-item count: {metric_item_count}")
        print(f"  ✅ metric-value count: {metric_value_count}")
        print(f"  ✅ metric-label count: {metric_label_count}")
        
        if health_metrics_count >= 3 and metric_item_count >= 6 and metric_value_count >= 6 and metric_label_count >= 6:
            print("  🎉 Metrics Layout: PASSED")
            return True
        else:
            print("  ❌ Metrics Layout: FAILED")
            return False
            
    except Exception as e:
        print(f"  ❌ Metrics Layout test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Metrics Size Improvements")
    print("=" * 50)
    
    tests = [
        test_health_metrics_size,
        test_metric_item_size,
        test_progress_bar_size,
        test_responsive_metrics,
        test_metrics_layout
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
        print("🎉 All tests passed! Metrics size improvements are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
