#!/usr/bin/env python3
"""
WebSocket Sender for LPR Detection and Health Monitor Data
Monitors SQLite database for unsent records and sends them to LPR Server via WebSocket
"""

import asyncio
import websockets
import json
import sqlite3
import logging
import os
import time
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
import base64
from PIL import Image
import numpy as np
import threading

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env.production')
load_dotenv(env_path)

# Configuration from environment
WEBSOCKET_SERVER_URL = os.getenv("WEBSOCKET_SERVER_URL")  
DB_PATH = os.getenv("DB_PATH", "db/lpr_data.db")
CHECKPOINT_ID = os.getenv("CHECKPOINT_ID", "1")
WEBSOCKET_LOG_FILE = os.getenv("WEBSOCKET_LOG_FILE", "log/websocket_sender.log")
CHECK_INTERVAL = 5  # seconds

# Setup logging
log_dir = os.path.dirname(WEBSOCKET_LOG_FILE)
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(WEBSOCKET_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebSocketSender:
    def __init__(self):
        self.running = False
        self.db_path = DB_PATH
        self.websocket_url = WEBSOCKET_SERVER_URL
        self.checkpoint_id = CHECKPOINT_ID
        
        # Validate configuration
        if not self.websocket_url:
            raise ValueError("WEBSOCKET_SERVER_URL not configured in .env.production")
        
        logger.info(f"WebSocket Sender initialized")
        logger.info(f"Server URL: {self.websocket_url}")
        logger.info(f"Database: {self.db_path}")
        logger.info(f"Checkpoint ID: {self.checkpoint_id}")
    
    def get_db_connection(self):
        """Create database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def compress_image_base64(self, image_path, max_size=(640, 480), quality=75):
        """
        Load and compress image to base64 string
        """
        try:
            if not os.path.exists(image_path):
                logger.warning(f"Image file not found: {image_path}")
                return None
            
            # Load and resize image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if needed
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality)
                img_bytes = buffer.getvalue()
                
                # Encode to base64
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                logger.debug(f"Image compressed: {image_path} -> {len(img_base64)/1024:.1f}KB")
                return img_base64
                
        except Exception as e:
            logger.error(f"Image compression failed for {image_path}: {e}")
            return None
    
    async def send_websocket_data(self, payload):
        """Send data via WebSocket and return response"""
        try:
            logger.debug(f"Connecting to WebSocket: {self.websocket_url}")
            
            async with websockets.connect(self.websocket_url) as websocket:
                # Send data
                message = json.dumps(payload, ensure_ascii=False)
                await websocket.send(message)
                logger.debug(f"Data sent to server")
                
                # Wait for response
                response = await websocket.recv()
                logger.debug(f"Server response: {response}")
                
                return json.loads(response) if response else None
                
        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"WebSocket connection closed: {e}")
            return None
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"WebSocket error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"WebSocket send failed: {e}")
            return None
    
    async def process_detection_records(self):
        """Process unsent detection records"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Get unsent detection records with related metadata
            query = """
            SELECT 
                dr.id,
                dr.frame_id,
                dr.license_plate_text,
                dr.lp_confidence,
                dr.lp_image_filename,
                cm.timestamp,
                cm.image_filename,
                cm.exposure_time,
                cm.analog_gain,
                cm.lux
            FROM detection_results dr
            LEFT JOIN camera_metadata cm ON dr.frame_id = cm.frame_id
            WHERE dr.sent_to_server = 0
            ORDER BY cm.timestamp DESC
            LIMIT 10
            """
            
            cursor.execute(query)
            records = cursor.fetchall()
            
            if not records:
                logger.debug("No unsent detection records found")
                return
            
            logger.info(f"Found {len(records)} unsent detection records")
            
            for record in records:
                try:
                    # Process image if available
                    image_base64 = None
                    if record['lp_image_filename']:
                        # Try different possible paths
                        possible_paths = [
                            record['lp_image_filename'],
                            os.path.join('captured_images', record['lp_image_filename']),
                            os.path.join('v2/captured_images', record['lp_image_filename'])
                        ]
                        
                        for path in possible_paths:
                            if os.path.exists(path):
                                image_base64 = self.compress_image_base64(path)
                                break
                    
                    # Prepare payload for LPR server
                    payload = {
                        "table": "lpr_detection",
                        "action": "insert",
                        "data": {
                            "license_plate": record['license_plate_text'] or "",
                            "confidence": float(record['lp_confidence'] or 0),
                            "checkpoint_id": self.checkpoint_id,
                            "timestamp": record['timestamp'] or datetime.now().isoformat(),
                            "hostname": os.getenv('HOSTNAME', 'aicamera'),
                            "vehicle_type": "",
                            "vehicle_color": "",
                            "latitude": "",
                            "longitude": "",
                            "image": image_base64,
                            "exposure_time": record['exposure_time'],
                            "analog_gain": record['analog_gain'],
                            "lux": record['lux']
                        }
                    }
                    
                    # Send to server
                    response = await self.send_websocket_data(payload)
                    
                    if response and response.get('status') == 'success':
                        # Update sent status
                        cursor.execute(
                            "UPDATE detection_results SET sent_to_server = 1, sent_timestamp = ? WHERE id = ?",
                            (datetime.now().isoformat(), record['id'])
                        )
                        conn.commit()
                        logger.info(f"Detection record {record['id']} sent successfully: {record['license_plate_text']}")
                        
                    elif response and response.get('status') == 'error':
                        logger.error(f"Server rejected detection record {record['id']}: {response.get('message', 'Unknown error')}")
                        
                    else:
                        logger.warning(f"Failed to send detection record {record['id']}: Invalid response")
                    
                    # Small delay between records
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing detection record {record['id']}: {e}")
                    continue
            
        except sqlite3.Error as e:
            logger.error(f"Database error processing detection records: {e}")
        finally:
            conn.close()
    
    async def process_health_records(self):
        """Process unsent health check records"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Get unsent health records
            query = """
            SELECT id, timestamp, component, status, message
            FROM health_checks
            WHERE sent_to_server = 0
            ORDER BY timestamp DESC
            LIMIT 20
            """
            
            cursor.execute(query)
            records = cursor.fetchall()
            
            if not records:
                logger.debug("No unsent health records found")
                return
            
            logger.info(f"Found {len(records)} unsent health records")
            
            for record in records:
                try:
                    # Prepare payload for health monitoring server
                    payload = {
                        "table": "health_monitor",
                        "action": "insert",
                        "data": {
                            "checkpoint_id": self.checkpoint_id,
                            "hostname": os.getenv('HOSTNAME', 'aicamera'),
                            "timestamp": record['timestamp'],
                            "component": record['component'],
                            "status": record['status'],
                            "message": record['message'] or "",
                            "system_info": {
                                "python_version": sys.version.split()[0],
                                "platform": sys.platform
                            }
                        }
                    }
                    
                    # Send to server
                    response = await self.send_websocket_data(payload)
                    
                    if response and response.get('status') == 'success':
                        # Update sent status
                        cursor.execute(
                            "UPDATE health_checks SET sent_to_server = 1, sent_timestamp = ? WHERE id = ?",
                            (datetime.now().isoformat(), record['id'])
                        )
                        conn.commit()
                        logger.info(f"Health record {record['id']} sent successfully: {record['component']} - {record['status']}")
                        
                    elif response and response.get('status') == 'error':
                        logger.error(f"Server rejected health record {record['id']}: {response.get('message', 'Unknown error')}")
                        
                    else:
                        logger.warning(f"Failed to send health record {record['id']}: Invalid response")
                    
                    # Small delay between records
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing health record {record['id']}: {e}")
                    continue
            
        except sqlite3.Error as e:
            logger.error(f"Database error processing health records: {e}")
        finally:
            conn.close()
    
    async def check_and_send_data(self):
        """Main loop to check and send unsent data"""
        logger.info("Starting data check and send loop...")
        
        while self.running:
            try:
                # Process detection records
                await self.process_detection_records()
                
                # Process health records  
                await self.process_health_records()
                
                # Wait before next check
                await asyncio.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(CHECK_INTERVAL)
    
    def start(self):
        """Start the WebSocket sender"""
        self.running = True
        logger.info("WebSocket Sender started")
    
    def stop(self):
        """Stop the WebSocket sender"""
        self.running = False
        logger.info("WebSocket Sender stopped")
    
    async def run(self):
        """Run the sender with proper signal handling"""
        self.start()
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            await self.check_and_send_data()
        except Exception as e:
            logger.error(f"Critical error in sender: {e}")
        finally:
            logger.info("WebSocket Sender shutdown complete")

# Standalone service functions
async def run_websocket_sender():
    """Run WebSocket sender as standalone service"""
    sender = WebSocketSender()
    await sender.run()

def main():
    """Main entry point"""
    logger.info("Starting WebSocket Sender Service...")
    logger.info(f"WebSocket URL: {WEBSOCKET_SERVER_URL}")
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    
    try:
        asyncio.run(run_websocket_sender())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {e}")
    finally:
        logger.info("WebSocket Sender Service stopped")

if __name__ == "__main__":
    main()