#!/usr/bin/env python3
"""
Test Client for LPR Server WebSocket
ใช้สำหรับทดสอบการเชื่อมต่อและส่งข้อมูล LPR
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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected to LPR Server")

@sio.event
def disconnect():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Disconnected from LPR Server")

@sio.event
def status(data):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {data}")

@sio.event
def lpr_response(data):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] LPR Response: {data}")

@sio.event
def error(data):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {data}")

def send_test_data():
    """Send test LPR data"""
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
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending LPR data: {plate_number} from {camera_id}")
    sio.emit('lpr_data', data)

def main():
    """Main test function"""
    print("=== LPR Server WebSocket Test Client ===")
    print("Connecting to ws://localhost:8765")
    
    try:
        # Connect to WebSocket server
        sio.connect('http://localhost:8765')
        
        # Register camera
        camera_id = 'TEST_CAM'
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Registering camera: {camera_id}")
        sio.emit('camera_register', {'camera_id': camera_id})
        
        # Send test data every 5 seconds
        print("Sending test data every 5 seconds... (Press Ctrl+C to stop)")
        
        while True:
            time.sleep(5)
            send_test_data()
            
    except KeyboardInterrupt:
        print("\nStopping test client...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if sio.connected:
            sio.disconnect()
        print("Test client stopped")

if __name__ == '__main__':
    main()
