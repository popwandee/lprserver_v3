# edge_status.py
import sqlite3
import socketio
import psutil
import time
import socket
from datetime import datetime
from src.system_info import gather_system_info
from src.camera_test import test_camera
from src.test_hailo_rpi5 import test_hailo_hardware
from utils.logger import log_status

DB_PATH = "db/lpr_data.db"
CHECK_INTERVAL = 3600  # 1 ชั่วโมง
SERVER_URL = "http://lprserver.tail605477.ts.net:8765"
sio = socketio.Client()

def get_edge_status():
    """ตรวจสอบสถานะ Edge AI Camera"""
    hostname = socket.gethostname()
    return {
        "hostname": hostname,
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "camera_status": test_camera(),
        "hailo_status": test_hailo_hardware(),
        "system_info": gather_system_info(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def log_edge_status():
    """บันทึกสถานะ Edge AI Camera ลง SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edge_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT,
            cpu_usage REAL,
            memory_usage REAL,
            camera_status TEXT,
            hailo_status TEXT,
            system_info TEXT,
            timestamp TEXT
        )
    """)
    status = get_edge_status()
    cursor.execute("""
        INSERT INTO edge_status (hostname, cpu_usage, memory_usage, camera_status, hailo_status, system_info, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        status["hostname"], status["cpu_usage"], status["memory_usage"], 
        status["camera_status"], status["hailo_status"], status["system_info"], status["timestamp"]
    ))
    conn.commit()
    conn.close()
    print(f"✅ บันทึกสถานะ Edge AI Camera: {status}")

def check_and_send_status():
    """ส่งข้อมูลสถานะ Edge AI Camera ไปยังเซิร์ฟเวอร์ผ่าน WebSocket"""
    status = get_edge_status()
    sio.connect(SERVER_URL)
    sio.emit("edge_status", status)
    sio.disconnect()
    print(f"📡 ส่งข้อมูลสถานะ Edge AI Camera ไปยังเซิร์ฟเวอร์แล้ว!")

def main():
    while True:
        log_edge_status()
        check_and_send_status()
        time.sleep(CHECK_INTERVAL)  # รอ 1 ชั่วโมงก่อนทำงานอีกครั้ง

if __name__ == "__main__":
    main()
