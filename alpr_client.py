import socketio
import time
import base64
import cv2
import os
import random
from datetime import datetime
from picamera2 import Picamera2

# สร้าง Socket.IO client
sio = socketio.Client()

# URL ของ LPRServer
SERVER_URL = "http://lprserver.tail605477.ts.net:1337/"

# ฟังก์ชันถ่ายภาพและเข้ารหัส base64
def capture_image_b64():
    """
    ถ่ายภาพจากกล้อง Picamera2 และแปลงเป็น base64

    Returns:
        tuple: (base64 string, ชื่อไฟล์ภาพ)
    """
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration())
    picam2.start()
    time.sleep(2)

    frame = picam2.capture_array()
    picam2.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"plate_{timestamp}.jpg"

    _, buffer = cv2.imencode('.jpg', frame)
    image_b64 = base64.b64encode(buffer).decode('utf-8')

    return image_b64, filename


def generate_mock_data():
    """
    สร้างข้อมูลจำลอง

    Returns:
        dict
    """
    return {
        "license_plate": f"TEST{random.randint(1000, 9999)}",
        "location_lat": round(random.uniform(18.7, 18.9), 6),
        "location_lon": round(random.uniform(98.9, 99.1), 6),
        "info": "Mock image from Raspberry Pi"
    }


# รับข้อมูลตอบกลับจากเซิร์ฟเวอร์
@sio.on('lpr_response', namespace='/socket.io/')
def on_response(data):
    print("🎯 ได้รับผลตอบกลับจาก server:")
    print(f"  status: {data['status']}")
    print(f"  message: {data['message']}")
    print(f"  saved_path: {data.get('saved_path')}")


def main():
    try:
        sio.connect(SERVER_URL, namespaces=['/socket.io/'])
        print("✅ เชื่อมต่อกับเซิร์ฟเวอร์สำเร็จ")
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์: {e}")
        return

    image_b64, filename = capture_image_b64()
    mock_data = generate_mock_data()

    payload = {
        "license_plate": mock_data["license_plate"],
        "image_name": filename,
        "image_b64": image_b64,
        "location_lat": mock_data["location_lat"],
        "location_lon": mock_data["location_lon"],
        "info": mock_data["info"]
    }

    sio.emit('lpr_detection', payload, namespace='/socket.io/')
    print("📤 ส่งภาพและข้อมูลไปยัง server แล้ว รอผลตอบกลับ...")

    # รอผลตอบกลับเล็กน้อย
    time.sleep(3)
    sio.disconnect()


if __name__ == "__main__":
    main()
