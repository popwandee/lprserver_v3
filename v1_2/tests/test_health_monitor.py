#!/usr/bin/env python3
"""
Test script for Health Monitor API
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test running health check"""
    print("Testing health check...")
    try:
        response = requests.post(f"{BASE_URL}/api/health_check")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check response: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"✗ Failed to run health check: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error running health check: {e}")
        return None

def test_health_status():
    """Test getting health status"""
    print("\nTesting health status...")
    try:
        response = requests.get(f"{BASE_URL}/api/health_status")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health status response: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"✗ Failed to get health status: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error getting health status: {e}")
        return None

def test_start_health_monitoring():
    """Test starting health monitoring"""
    print("\nTesting start health monitoring...")
    try:
        response = requests.post(f"{BASE_URL}/api/start_health_monitoring")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Start monitoring response: {json.dumps(data, indent=2)}")
            return data['status'] == 'success'
        else:
            print(f"✗ Failed to start monitoring: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error starting monitoring: {e}")
        return False

def test_stop_health_monitoring():
    """Test stopping health monitoring"""
    print("\nTesting stop health monitoring...")
    try:
        response = requests.post(f"{BASE_URL}/api/stop_health_monitoring")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Stop monitoring response: {json.dumps(data, indent=2)}")
            return data['status'] == 'success'
        else:
            print(f"✗ Failed to stop monitoring: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error stopping monitoring: {e}")
        return False

def analyze_health_results(health_data):
    """Analyze health check results"""
    if not health_data or 'health_checks' not in health_data:
        print("No health data to analyze")
        return
    
    checks = health_data['health_checks']
    if not checks:
        print("No health checks found")
        return
    
    print(f"\n=== Health Analysis ===")
    print(f"Total checks: {len(checks)}")
    
    # Group by component
    components = {}
    for check in checks:
        component = check['component']
        if component not in components:
            components[component] = []
        components[component].append(check)
    
    # Analyze each component
    for component, component_checks in components.items():
        latest = component_checks[0]  # Most recent
        print(f"\n{component}:")
        print(f"  Latest Status: {latest['status']}")
        print(f"  Latest Message: {latest['message']}")
        print(f"  Latest Time: {latest['timestamp']}")
        
        # Count statuses
        status_counts = {}
        for check in component_checks:
            status = check['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"  Status History: {status_counts}")

def main():
    """Run all health monitor tests"""
    print("=== Health Monitor Test Suite ===")
    print(f"Testing against: {BASE_URL}")
    
    # Test 1: Run health check
    health_check_result = test_health_check()
    if health_check_result is None:
        print("✗ Cannot run health check")
        return
    
    # Test 2: Get health status
    health_status = test_health_status()
    if health_status is None:
        print("✗ Cannot get health status")
        return
    
    # Test 3: Analyze results
    analyze_health_results(health_status)
    
    # Test 4: Test monitoring control (optional)
    print(f"\n=== Monitoring Control Tests ===")
    
    # Start monitoring
    if test_start_health_monitoring():
        print("✓ Health monitoring started")
        time.sleep(2)
        
        # Stop monitoring
        if test_stop_health_monitoring():
            print("✓ Health monitoring stopped")
        else:
            print("✗ Failed to stop health monitoring")
    else:
        print("✗ Failed to start health monitoring")
    
    print("\n=== Health Monitor Test Complete ===")

if __name__ == "__main__":
    main() 