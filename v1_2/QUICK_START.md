# 🚀 Quick Start Guide - AI Camera WebSocket System

เริ่มใช้งานระบบ WebSocket สำหรับ AI Camera ได้ทันทีใน 5 นาที!

## 📋 Pre-requisites

- ✅ Python 3.9+ พร้อม virtual environment ที่ `/home/camuser/aicamera/venv_hailo`
- ✅ SQLite3 
- ✅ Port 8765 ว่าง (สำหรับ WebSocket server)
- ✅ Port 80, 8000 ว่าง (สำหรับ web interface)

## 🎯 Option 1: Production Setup (แนะนำ)

### 1. ติดตั้ง Dependencies
```bash
cd /home/camuser/aicamera/v2
source ../venv_hailo/bin/activate
pip install -r requirements.txt
```

### 2. ติดตั้ง System Services
```bash
# ติดตั้ง systemd services (ต้องใช้ sudo)
sudo ./install_all_services.sh
```

### 3. เริ่มระบบทั้งหมด
```bash
# เริ่ม production services
./run_production_extended.sh start
```

### 4. ตรวจสอบสถานะ
```bash
# ดูสถานะทั้งหมด
./run_production_extended.sh status

# ดู web interface
# เปิด browser ไปที่: http://localhost
```

**🎉 เสร็จแล้ว! ระบบพร้อมใช้งาน**

---

## 🧪 Option 2: Development/Testing

### 1. เริ่ม WebSocket Server
```bash
cd /home/camuser/aicamera/v2
source ../venv_hailo/bin/activate

# เริ่ม server
./run_websocket_server.sh start
```

### 2. เริ่ม Main Application
```bash
# ใน terminal อื่น
cd /home/camuser/aicamera/v2
source ../venv_hailo/bin/activate
python app.py
```

### 3. เริ่ม WebSocket Sender (ทดสอบ)
```bash
# ใน terminal อื่น
./run_websocket_sender.sh start
```

### 4. ทดสอบการเชื่อมต่อ
```bash
# ทดสอบ WebSocket connection
./test_websocket_connection.py --ping-only

# ทดสอบส่งข้อมูลจริง
./test_websocket_connection.py --tests 3
```

---

## 🔧 การตั้งค่าที่จำเป็น

### แก้ไข `.env.production`
```bash
# ตั้งค่า WebSocket Server URL
WEBSOCKET_SERVER_URL = "ws://YOUR_SERVER_IP:8765"

# ตัวอย่าง
WEBSOCKET_SERVER_URL = "ws://100.95.46.128:8765"  # สำหรับ remote server
WEBSOCKET_SERVER_URL = "ws://localhost:8765"       # สำหรับ local testing
```

---

## ✅ การตรวจสอบว่าระบบทำงานปกติ

### 1. ตรวจสอบ Services
```bash
# แบบ production
./run_production_extended.sh status

# แบบ standalone
./run_websocket_server.sh status
./run_websocket_sender.sh status
```

### 2. ตรวจสอบ Ports
```bash
# ตรวจสอบว่า ports เปิดอยู่
netstat -tlnp | grep -E ":(80|8000|8765)"

# ควรเห็น:
# :80    - Nginx
# :8000  - Gunicorn  
# :8765  - WebSocket Server
```

### 3. ตรวจสอบ Database
```bash
# ดูข้อมูลที่ยังไม่ส่ง
sqlite3 db/lpr_data.db "SELECT COUNT(*) FROM detection_results WHERE sent_to_server = 0;"

# ดูข้อมูลที่ server รับแล้ว
sqlite3 websocket_server.db "SELECT COUNT(*) FROM lpr_detections;"
```

### 4. ตรวจสอบ Logs
```bash
# ดู logs แบบ real-time
tail -f log/websocket_server.log
tail -f log/websocket_sender.log

# หรือใช้ production script
./run_production_extended.sh logs
```

---

## 🌐 การเข้าถึงระบบ

| Service | URL | Description |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost/ | หน้าหลักของ AI Camera |
| **Detection Results** | http://localhost/detection | ผลการตรวจจับยานพาหนะ |
| **Health Monitor** | http://localhost/health | สถานะสุขภาพระบบ |
| **WebSocket Management** | http://localhost/websocket | จัดการ WebSocket sender |
| **WebSocket Server** | ws://localhost:8765 | WebSocket endpoint |

---

## 🆘 แก้ไขปัญหาเบื้องต้น

### ❌ "Connection refused" 
```bash
# ตรวจสอบว่า WebSocket server ทำงานอยู่
./run_websocket_server.sh status

# เริ่ม server ใหม่
./run_websocket_server.sh restart
```

### ❌ "Port already in use"
```bash
# หา process ที่ใช้ port
sudo lsof -i :8765

# หยุด process (ถ้าจำเป็น)
sudo kill -9 PID_NUMBER
```

### ❌ "Database locked"
```bash
# ตรวจสอบ permissions
ls -la db/lpr_data.db websocket_server.db

# แก้ไข permissions
sudo chown camuser:camuser db/lpr_data.db websocket_server.db
```

### ❌ "Virtual environment not found"
```bash
# ตรวจสอบ path
ls -la /home/camuser/aicamera/venv_hailo/

# สร้าง virtual environment ใหม่ (ถ้าจำเป็น)
cd /home/camuser/aicamera
python3 -m venv venv_hailo
source venv_hailo/bin/activate
pip install -r v2/requirements.txt
```

---

## 🎮 คำสั่งที่ใช้บ่อย

```bash
# ดูสถานะทั้งหมด
./run_production_extended.sh status

# รีสตาร์ททั้งหมด
./run_production_extended.sh restart

# รีสตาร์ทเฉพาะ WebSocket
./run_production_extended.sh restart-websocket

# ทดสอบการเชื่อมต่อ
./test_websocket_connection.py --ping-only

# ทำความสะอาดฐานข้อมูล
./cleanup_old_data.sh cleanup-all

# ดู logs
./run_production_extended.sh logs
```

---

## 📞 ต้องการความช่วยเหลือ?

1. **ดู Logs**: `./run_production_extended.sh logs`
2. **ตรวจสอบสถานะ**: `./run_production_extended.sh status`  
3. **ทดสอบเชื่อมต่อ**: `./test_websocket_connection.py`
4. **อ่านคู่มือฉบับเต็ม**: [WEBSOCKET_SENDER_README.md](WEBSOCKET_SENDER_README.md)

---

**🚀 ขั้นตอนนี้ควรใช้เวลาไม่เกิน 5 นาที ระบบจะพร้อมใช้งานทันที!**