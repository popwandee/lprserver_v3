import socketio
import time
import base64
import cv2
import os
import numpy as np
from picamera2 import Picamera2
from io import BytesIO
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# สร้าง Socket.IO client
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)
SAVE_DIR = "/home/camuser/aicamera/captured_images"

def capture_image():
    """
    ถ่ายภาพจากกล้อง Picamera2 และแปลงเป็น Base64 string

    Returns:
        str: รูปภาพที่ถูกเข้ารหัสเป็น base64 string
    """
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration())
    picam2.start()
    time.sleep(2)  # รอให้กล้องปรับแสง

    # ถ่ายภาพ
    frame = picam2.capture_array()
    picam2.close()

    # แปลงภาพเป็น JPEG และ Base64
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    # สร้างชื่อไฟล์ตาม timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"plate_{timestamp}.jpg"
    image_path = os.path.join(SAVE_DIR, image_filename)

    return jpg_as_text


def send_image_to_server(image_b64):
    """
    ส่งรูปภาพ (base64) ไปยัง LPRServer ผ่าน Socket.IO

    Args:
        image_b64 (str): ข้อมูลภาพแบบ base64 string
    """
    timestamp = datetime.now().isoformat()
    payload = {
        'timestamp': timestamp,
        'image': image_b64
    }
    try:
        sio.emit('debug_event', payload)
        logging.info(f"[{timestamp}] ส่งข้อมูลภาพสำเร็จ")
    except Exception as e:
        logging.info(f"[{timestamp}] ส่งข้อมูลล้มเหลว: {e}")


@sio.event
def connect():
    logging.info("[✓] Socket.IO connected to server\n")

@sio.event
def disconnect():
    logging.info("[x] Disconnected from server\n")
    
@sio.event
def connect_error(data):
    logging.info("[x] Connection failed:", data)

@sio.on('debug_response')
def on_response(data):
    logging.info(f">>> Received response from server: {data}\n")


def main():
    """
    ฟังก์ชันหลัก:
        - เชื่อมต่อกับ LPRServer
        - ถ่ายภาพ
        - ส่งภาพไปยังเซิร์ฟเวอร์
        - แสดงผลลัพธ์ในคอนโซล
    """
    try:
        sio.connect("http://lprserver.tail605477.ts.net:1337")
        if sio.get_sid() is None:
            print("⚠️ ไม่สามารถรับ session ID จากเซิร์ฟเวอร์ อาจมีปัญหาการเชื่อมต่อ")
            return
        else:
            print(f"✅ เชื่อมต่อกับเซิร์ฟเวอร์สำเร็จ SID: {sio.get_sid()}")
        
    except Exception as e:
        logging.info(f"ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์: {e}")
        return
     # ถ่ายภาพและส่ง
    logging.info("กำลังถ่ายภาพ...")
    img_b64 = capture_image()
    logging.info("ถ่ายภาพเสร็จแล้ว กำลังส่งภาพไปยังเซิร์ฟเวอร์...")
    send_image_to_server(img_b64)

    # ปิดการเชื่อมต่อ
    sio.disconnect()
    logging.info("ปิดการเชื่อมต่อเรียบร้อย")
if __name__ == '__main__':
    main()