#!/usr/bin/env python3
"""
Test WebSocket Server for AI Camera v1.3

Simple WebSocket server for testing client connections.
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connected clients
clients = set()

async def handle_client(websocket, path):
    """Handle WebSocket client connection"""
    client_addr = websocket.remote_address
    logger.info(f"New client connected: {client_addr}")
    
    # Add to clients set
    clients.add(websocket)
    
    try:
        async for message in websocket:
            try:
                # Parse JSON message
                message_data = json.loads(message)
                logger.info(f"Received message from {client_addr}: {message_data.get('type', 'unknown')}")
                
                # Process message based on type
                response = await process_message(message_data)
                
                # Send response
                await websocket.send(json.dumps(response))
                logger.info(f"Sent response to {client_addr}: {response['status']}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from {client_addr}: {e}")
                error_response = {
                    'status': 'error',
                    'message': 'Invalid JSON format',
                    'timestamp': datetime.now().isoformat()
                }
                await websocket.send(json.dumps(error_response))
            
            except Exception as e:
                logger.error(f"Error handling message from {client_addr}: {e}")
                error_response = {
                    'status': 'error',
                    'message': f'Server error: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
                try:
                    await websocket.send(json.dumps(error_response))
                except:
                    pass  # Client may have disconnected
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {client_addr}")
    except Exception as e:
        logger.error(f"Error with client {client_addr}: {e}")
    finally:
        # Remove from clients set
        clients.discard(websocket)
        logger.info(f"Client removed: {client_addr}")

async def process_message(message_data):
    """Process incoming message and return response"""
    message_type = message_data.get('type', 'unknown')
    
    if message_type == 'detection_result':
        return {
            'status': 'success',
            'message': 'Detection result received',
            'type': 'detection_response',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'vehicles_count': message_data.get('vehicles_count', 0),
                'plates_count': message_data.get('plates_count', 0)
            }
        }
    
    elif message_type == 'health_check':
        return {
            'status': 'success',
            'message': 'Health check received',
            'type': 'health_response',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'component': message_data.get('component', 'unknown'),
                'status': message_data.get('status', 'unknown')
            }
        }
    
    else:
        return {
            'status': 'success',
            'message': 'Message received',
            'type': 'general_response',
            'timestamp': datetime.now().isoformat(),
            'data': message_data
        }

async def main():
    """Main server function"""
    host = "0.0.0.0"
    port = 8765
    
    logger.info(f"Starting WebSocket server on {host}:{port}")
    
    try:
        async with websockets.serve(handle_client, host, port):
            logger.info(f"WebSocket server listening on ws://{host}:{port}")
            logger.info("Press Ctrl+C to stop")
            
            # Keep server running
            await asyncio.Future()  # Run forever
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
