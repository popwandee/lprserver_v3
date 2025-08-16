#!/usr/bin/env python3
"""
Simple Test Client for LPR WebSocket Server
ใช้สำหรับทดสอบการส่งข้อมูลไปยัง WebSocket Server
"""

import socketio
import time
import json
import base64
from datetime import datetime

# Create SocketIO client
sio = socketio.Client()

# Test data
test_cameras = ['CAM001', 'CAM002', 'CAM003']
test_plates = ['กข1234', 'คง5678', 'จฉ9012', 'ชซ3456', 'ญฎ7890']
test_locations = ['ประตูหน้า', 'ประตูหลัง', 'ลานจอดรถ']

# Create a simple test image (1x1 pixel JPEG)
test_image_data = base64.b64encode(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9').decode('utf-8')

@sio.event
def connect():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ เชื่อมต่อสำเร็จ")

@sio.event
def disconnect():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ตัดการเชื่อมต่อ")

@sio.event
def status(data):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 สถานะ: {data}")

@sio.event
def lpr_response(data):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 ตอบกลับ LPR: {data}")

@sio.event
def error(data):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ข้อผิดพลาด: {data}")

@sio.event
def pong(data):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🏓 ได้รับ pong: {data}")

def send_test_data():
    """ส่งข้อมูลทดสอบ LPR"""
    import random
    
    camera_id = random.choice(test_cameras)
    plate_number = random.choice(test_plates)
    confidence = round(random.uniform(60, 95), 1)
    location = random.choice(test_locations)
    
    data = {
        'camera_id': camera_id,
        'plate_number': plate_number,
        'confidence': confidence,
        'image_data': f'data:image/jpeg;base64,{test_image_data}',
        'location': location
    }
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📤 ส่งข้อมูล LPR: {plate_number} จาก {camera_id}")
    sio.emit('lpr_data', data)

def test_ping():
    """ทดสอบ ping"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🏓 ส่ง ping...")
    sio.emit('ping')

def main():
    """ฟังก์ชันหลัก"""
    print("=== ทดสอบ WebSocket Client ===")
    print("เชื่อมต่อไปยัง ws://localhost:8765")
    
    try:
        # เชื่อมต่อ WebSocket server
        sio.connect('http://localhost:8765')
        
        # รอสักครู่
        time.sleep(1)
        
        # ทดสอบ ping
        test_ping()
        time.sleep(1)
        
        # ลงทะเบียนกล้อง
        camera_id = 'TEST_CAM'
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📹 ลงทะเบียนกล้อง: {camera_id}")
        sio.emit('camera_register', {'camera_id': camera_id})
        time.sleep(1)
        
        # เข้าร่วม dashboard
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 เข้าร่วม dashboard...")
        sio.emit('join_dashboard')
        time.sleep(1)
        
        # ส่งข้อมูลทดสอบทุก 3 วินาที
        print("📤 ส่งข้อมูลทดสอบทุก 3 วินาที... (กด Ctrl+C เพื่อหยุด)")
        
        while True:
            time.sleep(3)
            send_test_data()
            
    except KeyboardInterrupt:
        print("\n🛑 หยุดการทดสอบ...")
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")
    finally:
        if sio.connected:
            sio.disconnect()
        print("✅ หยุดการทดสอบแล้ว")

if __name__ == '__main__':
    main()
