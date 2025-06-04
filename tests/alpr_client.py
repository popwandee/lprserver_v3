import socketio
import time
import base64
import cv2
import os
import random
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image
import io
# สร้าง Socket.IO client
sio = socketio.Client()

# URL ของ LPRServer
SERVER_URL = "http://lprserver.tail605477.ts.net:1337/"

# Flag บอกว่าได้รับ response แล้วหรือยัง
response_received = False
def compress_and_encode_image(image_path, max_size=(640, 480), quality=50):
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img.thumbnail(max_size)  # ลดขนาด
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)  # ลด quality
        buffer.seek(0)
        img_bytes = buffer.read()
        return base64.b64encode(img_bytes).decode('utf-8')
def get_base64_size(base64_string):
    """คำนวณขนาด (byte) ของข้อมูล base64"""
    try:
        decoded_data = base64.b64decode(base64_string)
        return len(decoded_data)
    except Exception as e:
        print(f"❌ Error decoding base64: {e}")
        return 0
    
# ฟังก์ชันถ่ายภาพและเข้ารหัส base64
def capture_image_b64():
    """
    ถ่ายภาพจากกล้อง Picamera2 และแปลงเป็น base64

    Returns:
        tuple: (base64 string, ชื่อไฟล์ภาพ)
    """
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration())
    
    try:
        picam2.start()
        time.sleep(2)

        frame = picam2.capture_array()
    except Exception as e:
        print(f"❌ ไม่สามารถถ่ายภาพได้: {e}")
        return None, None
    finally:
        # ปิดกล้องหลังจากถ่ายภาพ    
        picam2.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"plate_{timestamp}.jpg"

    _, buffer = cv2.imencode('.jpg', frame)
    image_b64 = base64.b64encode(buffer).decode('utf-8')
    size = get_base64_size(image_b64)
    print(f"📏 ขนาดภาพ base64 (หลัง decode): {size / 1024:.2f} KB")
    return image_b64, filename, buffer


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
@sio.on('debug_response')
def on_response(data):
    global response_received
    print("🎯 ได้รับผลตอบกลับจาก server:")
    print(f"  data: {data}")

    response_received = True
    sio.disconnect() # ปิด socket หลังได้รับ response

# รับข้อมูลตอบกลับจากเซิร์ฟเวอร์
@sio.on('lpr_response')
def on_response(data):
    global response_received
    print("🎯 ได้รับผลตอบกลับจาก server:")
    print(f"  status: {data['status']}")
    print(f"  message: {data['message']}")
    print(f"  saved_path: {data.get('saved_path')}")

    response_received = True
    sio.disconnect() # ปิด socket หลังได้รับ response

def main():
    global response_received
    try:
        sio.connect(SERVER_URL, namespaces=['/'])
        if sio.get_sid() is None:
            print("⚠️ ไม่สามารถรับ session ID จากเซิร์ฟเวอร์ อาจมีปัญหาการเชื่อมต่อ")
            return
        else:
            print(f"✅ เชื่อมต่อกับเซิร์ฟเวอร์สำเร็จ SID: {sio.get_sid()}")
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์: {e}")
        return

    image_b64, filename , image_binary = capture_image_b64()
    if not image_b64 or not filename:
        print("⚠️ ไม่สามารถถ่ายภาพได้ หรือภาพเข้ารหัส base64 ไม่ถูกต้อง ยกเลิกการส่งข้อมูล")
        return
    
    mock_data = generate_mock_data()

    payload = {
        "license_plate": mock_data["license_plate"],
        "image_name": filename,
        #"image_b64": image_b64,
        "image_b64": image_binary, # ใช้ binary แทน base64 ชั่วคราว
        "location_lat": mock_data["location_lat"],
        "location_lon": mock_data["location_lon"],
        "info": mock_data["info"]
    }

    #sio.emit('debug_event', payload, binary=True)
    sio.emit('lpr_detection', payload)
    print("📤 ส่งภาพและข้อมูลไปยัง server แล้ว รอผลตอบกลับ...")
    sio.wait()  # รอ event ก่อน disconnect

    # ✅ รอ response 10 วินาที ไม่ให้ disconnect เร็วเกินไป
    #timeout = 10
    #start = time.time()
    #while not response_received and time.time() - start < timeout:
    #    time.sleep(0.1)

    #if not response_received:
    #    print("⚠️ ไม่ได้รับการตอบกลับจาก server ภายในระยะเวลา")

if __name__ == "__main__":
    main()
