# send_socket.py
import socketio
import requests
from datetime import datetime
import socket
import io
import os
from dotenv import load_dotenv
import sqlite3
import time
import asyncio
import websockets
import json
import logging
from PIL import Image
import numpy as np
import base64

env_path = os.path.join(os.path.dirname(__file__), 'src', '.env.production')
load_dotenv(env_path)

# Configure logging
LOG_FILE = os.getenv("WEBSOCKET_LOG_FILE")
if not os.path.exists(LOG_FILE):
    logging.critical(f"Log file '{LOG_FILE}' does not exist or cannot be created.")
    os.makedirs(LOG_FILE, exist_ok=True)

logging.basicConfig(filename=LOG_FILE,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger()

# ใช้ตัวแปรจาก .env.production
SERVER_URL = os.getenv("SERVER_URL")

logging.info(f"LOG_FILE: {LOG_FILE}")
logging.info(f"SERVER_URL: {SERVER_URL}")

def check_image_type(image_input):
    """Determines if the input is a NumPy array or a file path."""
    if isinstance(image_input, np.ndarray):
        return "NumPy array"
    elif isinstance(image_input, str) and os.path.exists(image_input):
        return "File path"
    else:
        return "Unknown format"

def load_image(image_path):
    """Loads image from path as a NumPy array."""
    try:
        img = Image.open(image_path).convert('RGB')
        return np.array(img)
    except Exception as e:
        logger.error(f"Image loading failed: {e}")
        return None

def compress_image_bytes(image_array, max_size=(640, 640), quality=50):
    """
    รับ numpy image array แล้วบีบอัดและแปลงเป็น binary JPEG
    """
    try:
        img = Image.fromarray(image_array).convert('RGB')
        img.thumbnail(max_size)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
        # Convert binary to Base64 string
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
        logger.debug("รับ numpy image array แล้วบีบอัดและแปลงเป็น base64 endcode เรียบร้อย.")
        return  image_base64 # buffer.getvalue()  กรณีต้องการ return as binary
    except Exception as e:
        logger.error(f"การบีบอัดรูปภาพล้มเหลว: {e}")
        return None

async def send_data(payload):
    """Sends data over WebSocket and returns response."""
    print(f"SERVER_URL is :{SERVER_URL}")
    logging.debug("Attempting WebSocket connection to SERVER_URL...")

    try:
        async with websockets.connect(SERVER_URL) as websocket:
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            print(f"Server response: {response}")
            return response
    except Exception as e:
        logger.critical(f"WebSocket connection failed: {e}")
        return None

async def check_new_license_plates():
    logging.debug("Starting WebSocket connection...")
    logging.debug("Initializing database connection...")

    """เช็กข้อมูลใหม่ใน SQLite และส่งไปยังเซิร์ฟเวอร์"""
    db_path = os.getenv("DB_PATH")

    logging.debug(f"DB_PATH...{db_path}")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        while True:
            cursor.execute(
                """SELECT id,license_plate, vehicle_image_path, license_plate_image_path, cropped_image_path, timestamp, location, hostname 
                FROM lpr_data WHERE sent_to_server = 0 
                ORDER BY timestamp DESC LIMIT 1"""
                )
            result = cursor.fetchone()
            
            logging.debug(f"database execution result...{result}")

            if result:
                id,plate, vehicle_image,license_plate_image,cropped_image, timestamp,location, hostname = result

                if isinstance(license_plate_image, np.ndarray):
                    image_base64  = compress_image_bytes(license_plate_image, max_size=(640, 640), quality=50)
                    logging.info(f"ภาพ : {license_plate_image} เป็นภาพ numpy array, compress image")
                    logging.info(f"📏 ขนาดภาพ JPEG บีบอัด: {len(image_base64 ) / 1024:.2f} KB")
                elif isinstance(license_plate_image, str) and os.path.exists(license_plate_image):
                    logging.info(f"Image path: {license_plate_image} -> Load image and compress image")
                    image_binary  = load_image(license_plate_image)
                    image_base64  = compress_image_bytes(image_binary , max_size=(640, 640), quality=50)
                    logging.info(f"📏 ขนาดภาพ JPEG บีบอัด: {len(image_base64 ) / 1024:.2f} KB")
                else:
                    logger.error(f"Skipping compression due to image load failure: {license_plate_image}")
                    image_base64  = ""

                lat, lon =  location.split(",")
                logging.info(f"type of image:{type(image_base64)}")
                payload = {
                    "table": "lpr_detection",
                    "data": {
                        "license_plate": plate,
                        "checkpoint_id": os.getenv("CHECKPOINT_ID"),
                        "timestamp": timestamp,
                        "hostname" : hostname,
                        "vehicle_type": " ",
                        "vehicle_color": " ",
                        "latitude": lat,
                        "longitude": lon,
                        "image": image_base64 
                    }
                }
                logging.debug(f"Payload being sent: {json.dumps(payload, indent=2)}")

                sent_result = await send_data(payload)
                sent_result_dict = json.loads(sent_result)
                logging.info(f"result of send data to server {sent_result_dict['status']}")
                if sent_result_dict['status'] == 'success' :
                    cursor.execute("UPDATE lpr_data SET sent_to_server = 1 WHERE id = ?", (id,))
                    conn.commit()
                    logger.info(f"✅ Plate {plate} sent successfully at {timestamp}.")
                elif sent_result_dict['status'] == 'error':
                    logging.error(f"Failed to send plate {plate} at {timestamp}\n{sent_result_dict['message']}")
                else:
                    logging.info(f"Failed to send plate {plate} at {timestamp}\n⚠️ Failed to send {plate}, logged for retry.")
            else:
                logging.info("No result from the database.")
            await asyncio.sleep(5)

async def main():
    logging.info("def main() execution starting check new license plate.")
    await check_new_license_plates()
if __name__ == "__main__":
    logging.info("Script execution started.")
    asyncio.run(main())

