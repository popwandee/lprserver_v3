#!/usr/bin/env python3
"""
WebSocket Server for LPR Detection and Health Monitor Data
Receives data from websocket_sender.py and responds appropriately
This is a mock server for testing and development purposes
"""

import asyncio
import websockets
import json
import logging
import os
import signal
import sqlite3
from datetime import datetime
from pathlib import Path
import base64
from PIL import Image
import io

# Configuration
SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 8765
DB_PATH = "websocket_server.db"
LOG_FILE = "log/websocket_server.log"
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB max image size

# Setup logging
os.makedirs("log", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebSocketServer:
    def __init__(self):
        self.clients = set()
        self.running = False
        self.server = None
        
        # Initialize database
        self.init_database()
        
        logger.info(f"WebSocket Server initialized")
        logger.info(f"Server will listen on {SERVER_HOST}:{SERVER_PORT}")
        logger.info(f"Database: {DB_PATH}")
        logger.info(f"Log file: {LOG_FILE}")
    
    def init_database(self):
        """Initialize SQLite database for storing received data"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Table for LPR detections
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lpr_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_plate TEXT,
                    confidence REAL,
                    checkpoint_id TEXT,
                    timestamp TEXT,
                    hostname TEXT,
                    vehicle_type TEXT,
                    vehicle_color TEXT,
                    latitude TEXT,
                    longitude TEXT,
                    image_data TEXT,  -- Base64 encoded image
                    exposure_time REAL,
                    analog_gain REAL,
                    lux REAL,
                    received_at TEXT,
                    processed INTEGER DEFAULT 0
                )
            ''')
            
            # Table for health monitor data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_monitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkpoint_id TEXT,
                    hostname TEXT,
                    timestamp TEXT,
                    component TEXT,
                    status TEXT,
                    message TEXT,
                    system_info TEXT,  -- JSON string
                    received_at TEXT,
                    processed INTEGER DEFAULT 0
                )
            ''')
            
            # Table for server statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    total_connections INTEGER,
                    active_connections INTEGER,
                    messages_received INTEGER,
                    messages_processed INTEGER,
                    errors INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def save_lpr_detection(self, data):
        """Save LPR detection data to database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO lpr_detections (
                    license_plate, confidence, checkpoint_id, timestamp, hostname,
                    vehicle_type, vehicle_color, latitude, longitude, image_data,
                    exposure_time, analog_gain, lux, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('license_plate', ''),
                data.get('confidence', 0),
                data.get('checkpoint_id', ''),
                data.get('timestamp', ''),
                data.get('hostname', ''),
                data.get('vehicle_type', ''),
                data.get('vehicle_color', ''),
                data.get('latitude', ''),
                data.get('longitude', ''),
                data.get('image', ''),  # Base64 image data
                data.get('exposure_time', 0),
                data.get('analog_gain', 0),
                data.get('lux', 0),
                datetime.now().isoformat()
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Saved LPR detection: {data.get('license_plate', 'N/A')} from {data.get('hostname', 'unknown')}")
            return record_id
            
        except sqlite3.Error as e:
            logger.error(f"Failed to save LPR detection: {e}")
            return None
    
    def save_health_monitor(self, data):
        """Save health monitor data to database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_monitors (
                    checkpoint_id, hostname, timestamp, component, status, 
                    message, system_info, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('checkpoint_id', ''),
                data.get('hostname', ''),
                data.get('timestamp', ''),
                data.get('component', ''),
                data.get('status', ''),
                data.get('message', ''),
                json.dumps(data.get('system_info', {})),
                datetime.now().isoformat()
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Saved health monitor: {data.get('component', 'N/A')} - {data.get('status', 'N/A')} from {data.get('hostname', 'unknown')}")
            return record_id
            
        except sqlite3.Error as e:
            logger.error(f"Failed to save health monitor: {e}")
            return None
    
    def validate_image_data(self, image_data):
        """Validate base64 image data"""
        if not image_data:
            return True  # Empty image is OK
        
        try:
            # Check size
            if len(image_data) > MAX_IMAGE_SIZE:
                logger.warning(f"Image data too large: {len(image_data)} bytes")
                return False
            
            # Try to decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Try to open as image
            with Image.open(io.BytesIO(image_bytes)) as img:
                logger.debug(f"Valid image: {img.format} {img.size}")
                return True
                
        except Exception as e:
            logger.warning(f"Invalid image data: {e}")
            return False
    
    def process_message(self, message_data):
        """Process incoming WebSocket message"""
        try:
            table = message_data.get('table', '')
            action = message_data.get('action', '')
            data = message_data.get('data', {})
            
            if table == 'lpr_detection' and action == 'insert':
                # Validate image data if present
                image_data = data.get('image', '')
                if image_data and not self.validate_image_data(image_data):
                    return {
                        'status': 'error',
                        'message': 'Invalid image data',
                        'table': table,
                        'action': action
                    }
                
                # Save to database
                record_id = self.save_lpr_detection(data)
                if record_id:
                    return {
                        'status': 'success',
                        'message': f'LPR detection saved successfully',
                        'record_id': record_id,
                        'table': table,
                        'action': action
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Failed to save LPR detection',
                        'table': table,
                        'action': action
                    }
            
            elif table == 'health_monitor' and action == 'insert':
                # Save to database
                record_id = self.save_health_monitor(data)
                if record_id:
                    return {
                        'status': 'success',
                        'message': f'Health monitor data saved successfully',
                        'record_id': record_id,
                        'table': table,
                        'action': action
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Failed to save health monitor data',
                        'table': table,
                        'action': action
                    }
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown table/action: {table}/{action}',
                    'table': table,
                    'action': action
                }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'status': 'error',
                'message': f'Processing error: {str(e)}'
            }
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        client_addr = websocket.remote_address
        logger.info(f"New client connected: {client_addr}")
        
        # Add to clients set
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                try:
                    # Parse JSON message
                    message_data = json.loads(message)
                    logger.debug(f"Received message from {client_addr}: {message_data.get('table', 'unknown')}")
                    
                    # Process message
                    response = self.process_message(message_data)
                    
                    # Send response
                    await websocket.send(json.dumps(response))
                    logger.debug(f"Sent response to {client_addr}: {response['status']}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from {client_addr}: {e}")
                    error_response = {
                        'status': 'error',
                        'message': 'Invalid JSON format'
                    }
                    await websocket.send(json.dumps(error_response))
                
                except Exception as e:
                    logger.error(f"Error handling message from {client_addr}: {e}")
                    error_response = {
                        'status': 'error', 
                        'message': f'Server error: {str(e)}'
                    }
                    try:
                        await websocket.send(json.dumps(error_response))
                    except:
                        pass  # Client may have disconnected
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_addr}")
        except Exception as e:
            logger.error(f"Unexpected error with client {client_addr}: {e}")
        finally:
            # Remove from clients set
            self.clients.discard(websocket)
            logger.info(f"Client removed: {client_addr}")
    
    def get_server_stats(self):
        """Get server statistics"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM lpr_detections")
            lpr_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM health_monitors")
            health_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'active_connections': len(self.clients),
                'total_lpr_records': lpr_count,
                'total_health_records': health_count,
                'server_running': self.running,
                'uptime': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting server stats: {e}")
            return {}
    
    async def start_server(self):
        """Start WebSocket server"""
        try:
            self.running = True
            logger.info(f"Starting WebSocket server on {SERVER_HOST}:{SERVER_PORT}")
            
            # Start server
            self.server = await websockets.serve(
                self.handle_client,
                SERVER_HOST,
                SERVER_PORT,
                ping_interval=30,
                ping_timeout=10
            )
            
            logger.info(f"✅ WebSocket server started successfully")
            logger.info(f"Server is listening on ws://{SERVER_HOST}:{SERVER_PORT}")
            
            # Keep server running
            await self.server.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    def stop_server(self):
        """Stop WebSocket server"""
        logger.info("Stopping WebSocket server...")
        self.running = False
        
        if self.server:
            self.server.close()
            logger.info("WebSocket server stopped")

# Signal handlers
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    if 'server_instance' in globals():
        server_instance.stop_server()

# Statistics endpoint (simple HTTP server for monitoring)
async def stats_handler(request):
    """Simple HTTP handler for server statistics"""
    try:
        stats = server_instance.get_server_stats()
        response_body = json.dumps(stats, indent=2)
        return web.Response(
            text=response_body,
            content_type='application/json'
        )
    except Exception as e:
        return web.Response(
            text=f"Error: {str(e)}",
            status=500
        )

async def main():
    """Main server function"""
    global server_instance
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create server instance
    server_instance = WebSocketServer()
    
    try:
        # Start WebSocket server
        await server_instance.start_server()
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
    finally:
        server_instance.stop_server()
        logger.info("WebSocket server shutdown complete")

if __name__ == "__main__":
    logger.info("Starting WebSocket Server for LPR Detection and Health Monitor")
    logger.info(f"Server configuration:")
    logger.info(f"  Host: {SERVER_HOST}")
    logger.info(f"  Port: {SERVER_PORT}")
    logger.info(f"  Database: {DB_PATH}")
    logger.info(f"  Log file: {LOG_FILE}")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
    finally:
        logger.info("WebSocket Server stopped")