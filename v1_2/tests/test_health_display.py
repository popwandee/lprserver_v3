#!/usr/bin/env python3
"""
Test script to verify health status API and data processing
"""

import requests
import json
from datetime import datetime

def test_health_status_api():
    """Test the health status API endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health_status')
        if response.status_code == 200:
            data = response.json()
            print("✅ Health status API is working")
            print(f"Status: {data['status']}")
            print(f"Number of health checks: {len(data['health_checks'])}")
            
            # Show the latest check for each component
            components = {}
            for check in data['health_checks']:
                components[check['component']] = {
                    'status': check['status'],
                    'message': check['message'],
                    'timestamp': check['timestamp']
                }
            
            print("\n📊 Latest Health Status by Component:")
            for component, info in components.items():
                status_emoji = "✅" if info['status'] == 'PASS' else "❌" if info['status'] == 'FAIL' else "⚠️"
                print(f"{status_emoji} {component}: {info['status']}")
                print(f"   Message: {info['message']}")
                print(f"   Time: {info['timestamp']}")
                print()
            
            return True
        else:
            print(f"❌ Health status API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing health status API: {e}")
        return False

def test_health_check_api():
    """Test the manual health check API endpoint"""
    try:
        response = requests.post('http://localhost:5000/api/health_check')
        if response.status_code == 200:
            data = response.json()
            print("✅ Manual health check API is working")
            print(f"Status: {data['status']}")
            if 'results' in data:
                print("Results:", data['results'])
            return True
        else:
            print(f"❌ Manual health check API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual health check API: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Health Status System")
    print("=" * 50)
    
    # Test health status API
    print("\n1. Testing Health Status API...")
    health_status_ok = test_health_status_api()
    
    # Test manual health check API
    print("\n2. Testing Manual Health Check API...")
    health_check_ok = test_health_check_api()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"Health Status API: {'✅ Working' if health_status_ok else '❌ Failed'}")
    print(f"Manual Health Check API: {'✅ Working' if health_check_ok else '❌ Failed'}")
    
    if health_status_ok and health_check_ok:
        print("\n🎉 All health monitoring APIs are working correctly!")
        print("The web interface should now display health status information.")
    else:
        print("\n⚠️ Some health monitoring APIs are not working.")
        print("Check the server logs for more details.") 