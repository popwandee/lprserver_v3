#!/usr/bin/env python3
"""
Test script for API endpoints
"""

import requests
import json
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://localhost:5000"

def test_api_health():
    """Test if the API server is running"""
    logger.info("=== Testing API Health ===")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            logger.info("✅ API server is running")
            return True
        else:
            logger.error(f"❌ API server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API server not reachable: {e}")
        return False

def test_health_status_api():
    """Test health status API"""
    logger.info("=== Testing Health Status API ===")
    try:
        response = requests.get(f"{BASE_URL}/api/health_status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Health status API working")
            logger.info(f"Status: {data.get('status')}")
            logger.info(f"Number of health checks: {len(data.get('health_checks', []))}")
            
            # Show latest health checks
            for check in data.get('health_checks', [])[:3]:
                logger.info(f"  {check.get('component')}: {check.get('status')}")
            
            return True
        else:
            logger.error(f"❌ Health status API failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Health status API error: {e}")
        return False

def test_detection_status_api():
    """Test detection status API"""
    logger.info("=== Testing Detection Status API ===")
    try:
        response = requests.get(f"{BASE_URL}/api/detection_status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Detection status API working")
            logger.info(f"Detection active: {data.get('detection_active')}")
            logger.info(f"Detection count: {data.get('detection_count')}")
            logger.info(f"Message: {data.get('message')}")
            return True
        else:
            logger.error(f"❌ Detection status API failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Detection status API error: {e}")
        return False

def test_camera_control_apis():
    """Test camera control APIs"""
    logger.info("=== Testing Camera Control APIs ===")
    
    # Test camera status
    try:
        response = requests.get(f"{BASE_URL}/api/camera_status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Camera status API working")
            logger.info(f"Camera status: {data.get('status')}")
        else:
            logger.warning(f"⚠️ Camera status API failed: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Camera status API error: {e}")
    
    # Test start camera
    try:
        response = requests.post(f"{BASE_URL}/api/start_camera", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Start camera API working")
            logger.info(f"Message: {data.get('message')}")
        else:
            logger.warning(f"⚠️ Start camera API failed: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Start camera API error: {e}")

def test_detection_control_apis():
    """Test detection control APIs"""
    logger.info("=== Testing Detection Control APIs ===")
    
    # Test start detection
    try:
        response = requests.post(f"{BASE_URL}/api/start_detection", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Start detection API working")
            logger.info(f"Message: {data.get('message')}")
        else:
            logger.warning(f"⚠️ Start detection API failed: {response.status_code}")
            logger.warning(f"Response: {response.text}")
    except Exception as e:
        logger.warning(f"⚠️ Start detection API error: {e}")
    
    # Wait a moment
    time.sleep(2)
    
    # Test detection status again
    test_detection_status_api()
    
    # Test stop detection
    try:
        response = requests.post(f"{BASE_URL}/api/stop_detection", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Stop detection API working")
            logger.info(f"Message: {data.get('message')}")
        else:
            logger.warning(f"⚠️ Stop detection API failed: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Stop detection API error: {e}")

def test_health_check_api():
    """Test manual health check API"""
    logger.info("=== Testing Manual Health Check API ===")
    try:
        response = requests.post(f"{BASE_URL}/api/health_check", timeout=30)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Manual health check API working")
            logger.info(f"Message: {data.get('message')}")
            return True
        else:
            logger.warning(f"⚠️ Manual health check API failed: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Manual health check API error: {e}")
        return False

def test_web_interface():
    """Test web interface endpoints"""
    logger.info("=== Testing Web Interface ===")
    
    # Test main page
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Main web page accessible")
            if "System Health Status" in response.text:
                logger.info("✅ Health status section found in HTML")
            else:
                logger.warning("⚠️ Health status section not found in HTML")
        else:
            logger.warning(f"⚠️ Main web page failed: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Main web page error: {e}")
    
    # Test test page
    try:
        response = requests.get(f"{BASE_URL}/test", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Test page accessible")
        else:
            logger.warning(f"⚠️ Test page failed: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Test page error: {e}")

def test_api_response_times():
    """Test API response times"""
    logger.info("=== Testing API Response Times ===")
    
    apis = [
        ("Health Status", f"{BASE_URL}/api/health_status"),
        ("Detection Status", f"{BASE_URL}/api/detection_status"),
        ("Camera Status", f"{BASE_URL}/api/camera_status"),
    ]
    
    for name, url in apis:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                logger.info(f"✅ {name}: {response_time:.1f}ms")
            else:
                logger.warning(f"⚠️ {name}: Failed (status {response.status_code})")
        except Exception as e:
            logger.warning(f"⚠️ {name}: Error - {e}")

def main():
    """Main test function"""
    logger.info("🚀 Starting API Tests")
    
    # Test 1: API Health
    if not test_api_health():
        logger.error("❌ API server not available, stopping tests")
        return
    
    # Test 2: Health Status API
    test_health_status_api()
    
    # Test 3: Detection Status API
    test_detection_status_api()
    
    # Test 4: Camera Control APIs
    test_camera_control_apis()
    
    # Test 5: Detection Control APIs
    test_detection_control_apis()
    
    # Test 6: Manual Health Check API
    test_health_check_api()
    
    # Test 7: Web Interface
    test_web_interface()
    
    # Test 8: API Response Times
    test_api_response_times()
    
    logger.info("🎉 All API tests completed!")

if __name__ == "__main__":
    main() 