#!/usr/bin/env python3
"""
Test Script for LPR WebSocket Server API Endpoints
ใช้สำหรับทดสอบ API endpoints ของ WebSocket Server
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8765"
API_BASE = f"{BASE_URL}/api"

def test_server_status():
    """ทดสอบสถานะเซิร์ฟเวอร์"""
    print("=== ทดสอบสถานะเซิร์ฟเวอร์ ===")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ เซิร์ฟเวอร์ทำงานปกติ")
            print(f"   ข้อความ: {data.get('message')}")
            print(f"   สถานะ: {data.get('status')}")
            print(f"   พอร์ต: {data.get('port')}")
            return True
        else:
            print(f"❌ เซิร์ฟเวอร์ไม่ตอบสนอง (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้: {e}")
        return False

def test_statistics_api():
    """ทดสอบ API สถิติ"""
    print("\n=== ทดสอบ API สถิติ ===")
    
    try:
        response = requests.get(f"{API_BASE}/statistics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ได้รับข้อมูลสถิติ")
            print(f"   จำนวนรายการทั้งหมด: {data.get('total_records', 0)}")
            print(f"   รายการวันนี้: {data.get('today_records', 0)}")
            print(f"   กล้องที่ไม่ซ้ำ: {data.get('unique_cameras', 0)}")
            print(f"   กล้องที่ใช้งาน: {data.get('active_cameras', 0)}")
            print(f"   รายการ blacklist: {data.get('blacklist_count', 0)}")
            print(f"   ไคลเอนต์ที่เชื่อมต่อ: {data.get('connected_clients', 0)}")
            print(f"   เวลา: {data.get('timestamp')}")
            return data
        else:
            print(f"❌ ไม่สามารถดึงข้อมูลสถิติได้ (HTTP {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการดึงข้อมูลสถิติ: {e}")
        return None

def test_records_api():
    """ทดสอบ API รายการ"""
    print("\n=== ทดสอบ API รายการ ===")
    
    try:
        # ทดสอบดึงรายการทั้งหมด
        response = requests.get(f"{API_BASE}/records?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ได้รับข้อมูลรายการ")
            print(f"   จำนวนรายการทั้งหมด: {data.get('total_count', 0)}")
            print(f"   จำนวนที่ส่งกลับ: {data.get('returned_count', 0)}")
            
            records = data.get('records', [])
            if records:
                print(f"   รายการล่าสุด:")
                for i, record in enumerate(records[-3:], 1):  # แสดง 3 รายการล่าสุด
                    print(f"     {i}. {record.get('plate_number')} จาก {record.get('camera_id')} ({record.get('confidence')}%)")
            else:
                print(f"   ไม่มีรายการ")
            
            return data
        else:
            print(f"❌ ไม่สามารถดึงข้อมูลรายการได้ (HTTP {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการดึงข้อมูลรายการ: {e}")
        return None

def test_cameras_api():
    """ทดสอบ API กล้อง"""
    print("\n=== ทดสอบ API กล้อง ===")
    
    try:
        response = requests.get(f"{API_BASE}/cameras", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ได้รับข้อมูลกล้อง")
            print(f"   จำนวนกล้องทั้งหมด: {data.get('total_cameras', 0)}")
            
            cameras = data.get('cameras', [])
            if cameras:
                print(f"   รายการกล้อง:")
                for camera in cameras:
                    print(f"     - {camera.get('camera_id')}: {camera.get('detection_count', 0)} detections")
            else:
                print(f"   ไม่มีกล้องที่ลงทะเบียน")
            
            return data
        else:
            print(f"❌ ไม่สามารถดึงข้อมูลกล้องได้ (HTTP {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการดึงข้อมูลกล้อง: {e}")
        return None

def test_websocket_info():
    """ทดสอบข้อมูล WebSocket"""
    print("\n=== ทดสอบข้อมูล WebSocket ===")
    
    try:
        response = requests.get(f"{BASE_URL}/websocket", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ได้รับข้อมูล WebSocket")
            print(f"   ข้อความ: {data.get('message')}")
            print(f"   URL เชื่อมต่อ: {data.get('connection_url')}")
            print(f"   Events: {', '.join(data.get('events', []))}")
            return True
        else:
            print(f"❌ ไม่สามารถดึงข้อมูล WebSocket ได้ (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการดึงข้อมูล WebSocket: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("=== ทดสอบ API Endpoints ของ LPR WebSocket Server ===")
    print(f"URL เซิร์ฟเวอร์: {BASE_URL}")
    print(f"เวลาเริ่มทดสอบ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ทดสอบสถานะเซิร์ฟเวอร์
    if not test_server_status():
        print("\n❌ เซิร์ฟเวอร์ไม่ทำงาน กรุณาตรวจสอบ WebSocket service")
        return
    
    # ทดสอบ API endpoints
    test_statistics_api()
    test_records_api()
    test_cameras_api()
    test_websocket_info()
    
    print(f"\n✅ การทดสอบเสร็จสิ้น")
    print(f"เวลาเสร็จสิ้น: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
