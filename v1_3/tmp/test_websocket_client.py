#!/usr/bin/env python3
"""
Test WebSocket Client for AI Camera v1.3

Simple WebSocket client for testing server connections.
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection(server_url):
    """Test WebSocket connection to server"""
    try:
        logger.info(f"Connecting to {server_url}...")
        
        async with websockets.connect(server_url) as websocket:
            logger.info("Connected successfully!")
            
            # Test detection result message
            detection_data = {
                'type': 'detection_result',
                'timestamp': datetime.now().isoformat(),
                'vehicles_count': 2,
                'plates_count': 1,
                'ocr_results': ['ABC123'],
                'processing_time_ms': 150
            }
            
            logger.info("Sending detection result...")
            await websocket.send(json.dumps(detection_data))
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            logger.info(f"Received response: {response_data}")
            
            # Test health check message
            health_data = {
                'type': 'health_check',
                'timestamp': datetime.now().isoformat(),
                'component': 'camera',
                'status': 'healthy',
                'message': 'Camera working normally'
            }
            
            logger.info("Sending health check...")
            await websocket.send(json.dumps(health_data))
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            logger.info(f"Received response: {response_data}")
            
            logger.info("Test completed successfully!")
            return True
            
    except websockets.exceptions.ConnectionClosed:
        logger.error(f"Connection closed to {server_url}")
        return False
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"WebSocket error: {e}")
        return False
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

async def main():
    """Main test function"""
    # Test local server first
    local_url = "ws://localhost:8765"
    remote_url = "ws://100.95.46.128:8765"
    
    logger.info("=== WebSocket Connection Test ===")
    
    # Test local server
    logger.info(f"\n1. Testing local server: {local_url}")
    local_success = await test_connection(local_url)
    
    if local_success:
        logger.info("✅ Local server test PASSED")
    else:
        logger.info("❌ Local server test FAILED")
    
    # Test remote server
    logger.info(f"\n2. Testing remote server: {remote_url}")
    remote_success = await test_connection(remote_url)
    
    if remote_success:
        logger.info("✅ Remote server test PASSED")
    else:
        logger.info("❌ Remote server test FAILED")
    
    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Local server ({local_url}): {'✅ PASS' if local_success else '❌ FAIL'}")
    logger.info(f"Remote server ({remote_url}): {'✅ PASS' if remote_success else '❌ FAIL'}")
    
    if not local_success and not remote_success:
        logger.error("❌ All connection tests failed!")
        logger.info("💡 Suggestions:")
        logger.info("   - Start local WebSocket server: python test_websocket_server.py")
        logger.info("   - Check remote server status")
        logger.info("   - Verify firewall settings")
    elif local_success and not remote_success:
        logger.warning("⚠️  Local server works but remote server failed")
        logger.info("💡 Remote server may be down or unreachable")
    else:
        logger.info("✅ Connection tests completed")

if __name__ == "__main__":
    asyncio.run(main())
