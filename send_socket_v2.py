# send_socket.py
import socketio
import requests
from datetime import datetime
import socket
import io
import sqlite3
import time
import asyncio
import websockets
import json
import logging

# Create and configure logger
logging.basicConfig(filename="send_socket_v2.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

sio = socketio.Client()
SERVER_URL = "ws://lprserver.tail605477.ts.net:8765"
# ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต และ IP Address
try:
    # ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("google.com", 80))
    logger.info("✅ เชื่อมต่ออินเทอร์เน็ตสำเร็จ")
except OSError  as e:
    logger.critical(f"❌ ไม่สามารถเชื่อมต่ออินเทอร์เน็ต: {e}")
    exit(1)

# ตรวจสอบ IP Address
try:
    hostname = socket.gethostname() # ใช้สำหรับการระบุว่ามาจากกล้องตัวไหน
    ip_address = socket.gethostbyname(hostname)
    logger.info(f"🌐 IP Address: {ip_address}" )
except OSError as e:
    logger.error(f"❌ ไม่สามารถตรวจสอบ IP Address: {e}")
    exit(1)

# ตรวจสอบตำแหน่งที่ตั้ง
# ใช้ API ip-api.com เพื่อดึงข้อมูลตำแหน่งที่ตั้ง เป็นตำแหน่งคร่าวๆ ไม่แม่นยำ
try:
    response = requests.get("http://ip-api.com/json/")
    location = response.json()
    logger.info(f"🌍 ตำแหน่งที่ตั้ง: {location['lat']}, {location['lon']}"
          f" ({location['city']}, {location['regionName']}, {location['country']})")
    
except requests.RequestException as e:
    logger.error(f"❌ ไม่สามารถดึงข้อมูลตำแหน่งที่ตั้ง: {e}")
    exit(1)

# ตรวจสอบการเชื่อมต่อกับเซิร์ฟเวอร์
try:
    response = requests.get(SERVER_URL)
    if response.status_code == 200:
        logger.info("✅ เชื่อมต่อกับเซิร์ฟเวอร์สำเร็จ")
    else:
        logger.critical(f"❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์: {response.status_code}")
        exit(1)
except requests.RequestException as e:
    logger.critical(f"❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์: {e}")
    exit(1)

######################################################


def compress_image_bytes(image_array, max_size=(640, 640), quality=50):
    """
    รับ numpy image array แล้วบีบอัดและแปลงเป็น binary JPEG
    """
    img = Image.fromarray(image_array).convert('RGB')
    img.thumbnail(max_size)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality)
    return buffer.getvalue()  # return as binary


async def send_data(payload):
    uri = "ws://lprserver.tail605477.ts.net:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(payload))
        response = await websocket.recv()
        print(f"Server response: {response}")
        return response

async def check_new_license_plates():
    """เช็กข้อมูลใหม่ใน SQLite และส่งไปยังเซิร์ฟเวอร์"""
    db_path="lpr_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    while True:
        cursor.execute("SELECT id,license_plate, vehicle_image_path, license_plate_image_path, cropped_image_path, timestamp, location, hostname FROM lpr_data WHERE sent_to_server = 0 ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()

        if result:
            id,plate, vehicle_image,license_plate_image,cropped_image, timestamp,location, hostname = result
            image_binary=compress_image_bytes(license_plate_image, max_size=(640, 640), quality=50)
            print(f"📏 ขนาดภาพ JPEG บีบอัด: {len(image_binary) / 1024:.2f} KB")
            lat, lon =  location.split(",")
            payload1 = {
                "table": "vehicle_lpr_simulation_data",
                "data": {
                    "license_plate": plate,
                    "checkpoint_id": hostname,
                    "timestamp": timestamp,
                    "vehicle_type": " ",
                    "vehicle_color": " ",
                    "latitude": lat,
                    "longitude": lon
                }
            }

            sent_result = await send_data(payload1)

            if sent_result :
                cursor.execute("UPDATE lpr_data SET sent_to_server = 1 WHERE id = ?", (id,))
                conn.commit()

            else:
                logging.critical(f"Failed to send plate {plate} at {timestamp}\n⚠️ Failed to send {plate}, logged for retry.")

async def main():
    await check_new_license_plates()
    await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())

