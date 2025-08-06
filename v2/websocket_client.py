import asyncio
import websockets
import json
import logging
from datetime import datetime
import os # For checking if image files exist

from config import WEBSOCKET_SERVER_URL, SENDER_INTERVAL, IMAGE_SAVE_DIR
from database_manager import DatabaseManager # We'll use this to fetch unsent data

logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.websocket = None
        self.running = False
        self.reconnect_attempt = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5 # seconds

    async def connect(self):
        """
        Establishes a WebSocket connection to the server.
        Handles reconnection attempts.
        """
        if self.websocket and not self.websocket.closed:
            logger.info("WebSocket already connected.")
            return True

        self.reconnect_attempt = 0
        while self.running and self.reconnect_attempt < self.max_reconnect_attempts:
            logger.info(f"Attempting to connect to WebSocket server: {WEBSOCKET_SERVER_URL} (Attempt {self.reconnect_attempt + 1}/{self.max_reconnect_attempts})")
            try:
                self.websocket = await websockets.connect(WEBSOCKET_SERVER_URL)
                logger.info("Successfully connected to WebSocket server.")
                self.reconnect_attempt = 0 # Reset on successful connection
                return True
            except (websockets.exceptions.ConnectionClosedOK,
                    websockets.exceptions.ConnectionClosedError,
                    ConnectionRefusedError, OSError) as e:
                logger.error(f"WebSocket connection failed: {e}. Retrying in {self.reconnect_delay} seconds...")
                self.reconnect_attempt += 1
                await asyncio.sleep(self.reconnect_delay)
            except Exception as e:
                logger.error(f"An unexpected error occurred during WebSocket connection: {e}. Retrying...")
                self.reconnect_attempt += 1
                await asyncio.sleep(self.reconnect_delay)
        
        if not self.running:
            logger.info("WebSocket connection attempts stopped because the client is no longer running.")
        else:
            logger.error(f"Failed to connect to WebSocket server after {self.max_reconnect_attempts} attempts.")
        return False

    async def send_detection(self, detection_data):
        """
        Sends a single detection result to the WebSocket server.
        Includes image data (base64 encoded) if files exist.
        """
        if not self.websocket or self.websocket.close:
            logger.warning("WebSocket not connected. Cannot send detection.")
            return False

        payload = detection_data.copy()
        
        # Add image data if files exist
        original_image_path = os.path.join(IMAGE_SAVE_DIR, payload.get('original_image_filename', ''))
        processed_image_path = os.path.join(IMAGE_SAVE_DIR, payload.get('processed_image_filename', ''))
        lp_image_path = os.path.join(IMAGE_SAVE_DIR, payload.get('lp_image_filename', ''))

        payload['original_image_b64'] = None
        payload['processed_image_b64'] = None
        payload['lp_image_b64'] = None

        try:
            if os.path.exists(original_image_path):
                with open(original_image_path, "rb") as f:
                    payload['original_image_b64'] = f.read().hex() # Or base64.b64encode(f.read()).decode('utf-8')
            if os.path.exists(processed_image_path):
                with open(processed_image_path, "rb") as f:
                    payload['processed_image_b64'] = f.read().hex() # Or base64.b64encode(f.read()).decode('utf-8')
            if os.path.exists(lp_image_path):
                with open(lp_image_path, "rb") as f:
                    payload['lp_image_b64'] = f.read().hex() # Or base64.b64encode(f.read()).decode('utf-8')
            
            # Remove filenames from payload if images are sent as b64
            payload.pop('original_image_filename', None)
            payload.pop('processed_image_filename', None)
            payload.pop('lp_image_filename', None)

            await self.websocket.send(json.dumps(payload))
            logger.info(f"Sent detection_id {detection_data['id']} to server.")
            return True
        except websockets.exceptions.ConnectionClosedOK:
            logger.warning("WebSocket connection closed while sending. Will attempt to reconnect.")
            self.websocket = None
            return False
        except Exception as e:
            logger.error(f"Error sending detection_id {detection_data['id']}: {e}")
            return False
    
    async def send_health_check(self, check_data):
        """
        Sends a single health check result to the WebSocket server.
        """
        if not self.websocket or not self.websocket.open:
            logger.warning("WebSocket not connected. Cannot send health check.")
            return False

        try:
            payload = check_data.copy()
            payload['type'] = 'health_check' # Add a type identifier for the server
            await self.websocket.send(json.dumps(payload))
            logger.info(f"Sent health_check_id {check_data['id']} for {check_data['component']} to server.")
            return True
        except websockets.exceptions.ConnectionClosedOK:
            logger.warning("WebSocket connection closed while sending health check. Will attempt to reconnect.")
            self.websocket = None
            return False
        except Exception as e:
            logger.error(f"Error sending health_check_id {check_data['id']}: {e}")
            return False
    
    async def run(self):
        """
        Main loop for the WebSocket client thread.
        Continuously checks for unsent detections and sends them.
        """
        self.running = True
        logger.info("WebSocket sender thread started.")
        while self.running:
            if not self.websocket or self.websocket.close:
                await self.connect()
                if not self.websocket or self.websocket.close:
                    await asyncio.sleep(self.reconnect_delay)
                    continue
            # --- Send Detections ---
            unsent_detections = self.db_manager.get_unsent_detections()
            
            if unsent_detections:
                logger.info(f"Found {len(unsent_detections)} unsent detections.")
                for detection in unsent_detections:
                    if await self.send_detection(detection):
                        self.db_manager.update_detection_sent_status(detection['id'])
                    else:
                        logger.warning(f"Failed to send detection {detection['id']}. Will retry later.")
                        # If sending fails, break and wait for next interval to retry
                        break
            # --- Send Health Checks ---
            unsent_health_checks = self.db_manager.get_unsent_health_checks()
            if unsent_health_checks:
                logger.info(f"Found {len(unsent_health_checks)} unsent health checks.")
                for health_check in unsent_health_checks:
                    if await self.send_health_check(health_check):
                        self.db_manager.update_health_check_sent_status(health_check['id'])
                    else:
                        logger.warning(f"Failed to send health check {health_check['id']}. Will retry later.")
                        break # Stop processing this batch if one fails
            if not unsent_detections and not unsent_health_checks:
                logger.debug("No unsent detections or health checks found.")

            await asyncio.sleep(SENDER_INTERVAL)
        
        logger.info("WebSocket sender thread stopped.")
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed.")

    async def stop(self):
        """Stops the WebSocket client thread gracefully."""
        logger.info("Stopping WebSocket client thread...")
        self.running = False
        # Give some time for the run loop to detect `self.running = False`
        # and for any pending sends to complete before potentially closing the loop.
        await asyncio.sleep(SENDER_INTERVAL + 1) # Wait a bit longer than interval