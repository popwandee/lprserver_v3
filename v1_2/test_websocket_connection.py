#!/usr/bin/env python3
"""
WebSocket Connection Test Script
Tests the connection between websocket_sender and websocket_server
"""

import asyncio
import websockets
import json
import base64
import logging
import argparse
from datetime import datetime
from PIL import Image
import io
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_image():
    """Create a small test image and return base64 encoded data"""
    try:
        # Create a simple test image
        img = Image.new('RGB', (100, 50), color='red')
        
        # Add some text or pattern
        import random
        pixels = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if (i + j) % 10 == 0:
                    pixels[i, j] = (255, 255, 255)  # White dots
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=80)
        img_bytes = buffer.getvalue()
        
        return base64.b64encode(img_bytes).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Failed to create test image: {e}")
        return None

async def test_lpr_detection(websocket, test_id):
    """Test sending LPR detection data"""
    
    test_image = create_test_image()
    
    message = {
        "table": "lpr_detection",
        "action": "insert",
        "data": {
            "license_plate": f"TST{test_id:03d}",
            "confidence": 85.5 + (test_id % 10),
            "checkpoint_id": "test_checkpoint",
            "timestamp": datetime.now().isoformat(),
            "hostname": "test-client",
            "vehicle_type": "car",
            "vehicle_color": "blue",
            "latitude": "13.7563",
            "longitude": "100.5018",
            "image": test_image,
            "exposure_time": 0.033,
            "analog_gain": 1.2,
            "lux": 150 + (test_id % 100)
        }
    }
    
    logger.info(f"Sending LPR detection test {test_id}...")
    await websocket.send(json.dumps(message))
    
    response = await websocket.recv()
    response_data = json.loads(response)
    
    if response_data.get('status') == 'success':
        logger.info(f"✅ LPR detection test {test_id} successful: {response_data.get('message')}")
        return True
    else:
        logger.error(f"❌ LPR detection test {test_id} failed: {response_data}")
        return False

async def test_health_monitor(websocket, test_id):
    """Test sending health monitor data"""
    
    components = ['camera', 'database', 'network', 'storage', 'cpu']
    statuses = ['PASS', 'PASS', 'PASS', 'WARN', 'FAIL']
    
    component = components[test_id % len(components)]
    status = statuses[test_id % len(statuses)]
    
    message = {
        "table": "health_monitor",
        "action": "insert",
        "data": {
            "checkpoint_id": "test_checkpoint",
            "hostname": "test-client",
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "status": status,
            "message": f"Test {test_id}: {component} status check",
            "system_info": {
                "python_version": "3.9.2",
                "platform": "linux",
                "test_run": test_id,
                "memory_usage": f"{45 + (test_id % 30)}%",
                "cpu_usage": f"{10 + (test_id % 20)}%"
            }
        }
    }
    
    logger.info(f"Sending health monitor test {test_id}...")
    await websocket.send(json.dumps(message))
    
    response = await websocket.recv()
    response_data = json.loads(response)
    
    if response_data.get('status') == 'success':
        logger.info(f"✅ Health monitor test {test_id} successful: {response_data.get('message')}")
        return True
    else:
        logger.error(f"❌ Health monitor test {test_id} failed: {response_data}")
        return False

async def run_connection_test(server_url, num_tests=5, test_type='both'):
    """Run WebSocket connection tests"""
    
    logger.info(f"Starting WebSocket connection test")
    logger.info(f"Server URL: {server_url}")
    logger.info(f"Number of tests: {num_tests}")
    logger.info(f"Test type: {test_type}")
    
    successful_tests = 0
    failed_tests = 0
    
    try:
        async with websockets.connect(server_url, timeout=10) as websocket:
            logger.info("✅ WebSocket connection established successfully")
            
            for i in range(num_tests):
                test_id = i + 1
                logger.info(f"\n--- Running test {test_id}/{num_tests} ---")
                
                try:
                    if test_type in ['both', 'lpr']:
                        if await test_lpr_detection(websocket, test_id):
                            successful_tests += 1
                        else:
                            failed_tests += 1
                    
                    if test_type in ['both', 'health']:
                        if await test_health_monitor(websocket, test_id + 100):
                            successful_tests += 1
                        else:
                            failed_tests += 1
                    
                    # Small delay between tests
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Test {test_id} failed with exception: {e}")
                    failed_tests += 1
            
        logger.info(f"\n=== Test Results ===")
        logger.info(f"✅ Successful tests: {successful_tests}")
        logger.info(f"❌ Failed tests: {failed_tests}")
        logger.info(f"Success rate: {(successful_tests/(successful_tests+failed_tests)*100):.1f}%")
        
        return successful_tests > 0 and failed_tests == 0
        
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"❌ WebSocket connection closed: {e}")
        return False
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"❌ WebSocket error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

async def test_server_availability(server_url):
    """Test if WebSocket server is available"""
    try:
        logger.info(f"Testing server availability: {server_url}")
        
        async with websockets.connect(server_url, timeout=5) as websocket:
            logger.info("✅ Server is available and accepting connections")
            
            # Send a simple ping message
            ping_message = {
                "table": "health_monitor",
                "action": "insert",
                "data": {
                    "checkpoint_id": "ping_test",
                    "hostname": "test-client",
                    "timestamp": datetime.now().isoformat(),
                    "component": "connection_test",
                    "status": "PASS",
                    "message": "Ping test"
                }
            }
            
            await websocket.send(json.dumps(ping_message))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get('status') == 'success':
                logger.info("✅ Server responded correctly to ping")
                return True
            else:
                logger.warning(f"⚠️ Server responded with error: {response_data}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Server availability test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='WebSocket Connection Test')
    parser.add_argument('--url', default='ws://localhost:8765', 
                       help='WebSocket server URL (default: ws://localhost:8765)')
    parser.add_argument('--tests', type=int, default=3,
                       help='Number of test iterations (default: 3)')
    parser.add_argument('--type', choices=['both', 'lpr', 'health'], default='both',
                       help='Type of tests to run (default: both)')
    parser.add_argument('--ping-only', action='store_true',
                       help='Only test server availability (ping test)')
    
    args = parser.parse_args()
    
    logger.info("🧪 WebSocket Connection Test Tool")
    logger.info("================================")
    
    async def run_tests():
        if args.ping_only:
            success = await test_server_availability(args.url)
        else:
            success = await run_connection_test(args.url, args.tests, args.type)
        
        if success:
            logger.info("\n🎉 All tests passed successfully!")
            return 0
        else:
            logger.error("\n💥 Some tests failed!")
            return 1
    
    try:
        exit_code = asyncio.run(run_tests())
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"\n💥 Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()