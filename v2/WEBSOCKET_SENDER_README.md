# 🔗 AI Camera WebSocket System - Complete Guide

ระบบ WebSocket แบบสมบูรณ์สำหรับ AI Camera ที่ประกอบด้วย Server และ Client สำหรับการส่งข้อมูลผลการตรวจจับยานพาหนะ (Detection) และ Health Monitor

## 🏗️ สถาปัตยกรรมระบบ

```
┌─────────────────┐    WebSocket     ┌─────────────────┐
│   AI Camera     │ ───────────────> │  WebSocket      │
│   (Client)      │    ws://IP:8765  │  Server         │
│                 │                  │                 │
│ • Detection     │                  │ • Data Storage  │
│ • Health Monitor│                  │ • Processing    │
│ • Image Process │                  │ • Validation    │
└─────────────────┘                  └─────────────────┘

┌─────────────────┐
│   Web Interface │
│   (Management)  │
│ • Start/Stop    │
│ • Monitoring    │
│ • Statistics    │
└─────────────────┘
```

## 📦 ส่วนประกอบของระบบ

### 🔗 WebSocket Client (Sender)
- **`websocket_sender.py`** - ส่งข้อมูลไปยัง server
- **`websocket_manager.py`** - จัดการ background process
- **`run_websocket_sender.sh`** - Script สำหรับจัดการ standalone

### 🌐 WebSocket Server
- **`websocket_server.py`** - รับและประมวลผลข้อมูล
- **`run_websocket_server.sh`** - Script สำหรับจัดการ server
- **`websocket_server.db`** - ฐานข้อมูลสำหรับเก็บข้อมูลที่รับ

### 🚀 Production Management
- **`run_production_extended.sh`** - จัดการทุก service แบบรวม
- **`install_all_services.sh`** - ติดตั้ง systemd services
- **Systemd Services** - สำหรับ production deployment

### 🎮 Web Interface
- **`templates/websocket.html`** - หน้าจัดการ WebSocket sender
- **API endpoints** - ควบคุมผ่าน REST API

## 📋 สิ่งที่ระบบทำได้

### ✅ WebSocket Sender (Client)
- ตรวจสอบข้อมูล Detection ที่ยังไม่ส่ง (`sent_to_server = 0`)  
- ตรวจสอบข้อมูล Health Monitor ที่ยังไม่ส่ง
- บีบอัดและแปลงรูปภาพเป็น Base64 ก่อนส่ง
- ส่งข้อมูลผ่าน WebSocket ไปยัง server
- อัพเดตสถานะเป็น `sent_to_server = 1` เมื่อส่งสำเร็จ
- ระบบ retry อัตโนมัติ

### ✅ WebSocket Server
- รับข้อมูลจาก clients หลายตัวพร้อมกัน
- ตรวจสอบความถูกต้องของข้อมูลและรูปภาพ
- บันทึกข้อมูลลงฐานข้อมูล SQLite
- ส่งการตอบกลับ (acknowledgment) กลับไปยัง client
- รองรับการเชื่อมต่อแบบ concurrent
- ระบบ logging และ monitoring

### ✅ Management & Monitoring
- Web interface สำหรับจัดการ
- Systemd service support
- Comprehensive logging
- Real-time statistics
- Health checking

## ⚙️ การติดตั้งและตั้งค่า

### 1. ติดตั้ง Dependencies

```bash
cd /home/camuser/aicamera/v2
source ../venv_hailo/bin/activate
pip install -r requirements.txt
```

### 2. ตรวจสอบการตั้งค่าใน .env.production

```bash
# WebSocket Server URL (แก้ไข IP ให้ตรงกับ server ที่ใช้จริง)
WEBSOCKET_SERVER_URL = "ws://100.95.46.128:8765"
DB_PATH = "db/lpr_data.db"
CHECKPOINT_ID = "1"
WEBSOCKET_LOG_FILE = "log/websocket_sender.log"
```

### 3. เลือกวิธีการติดตั้ง

#### 🎯 แบบ Production (แนะนำ)

```bash
# ติดตั้ง systemd services ทั้งหมด
sudo ./install_all_services.sh

# เริ่มระบบแบบครบครัน
./run_production_extended.sh start

# ตรวจสอบสถานะทั้งหมด
./run_production_extended.sh status
```

#### 🧪 แบบ Development/Testing

```bash
# เริ่ม WebSocket Server
./run_websocket_server.sh start

# เริ่ม Main Application
python app.py

# เริ่ม WebSocket Sender (ใน terminal อื่น)
./run_websocket_sender.sh start
```

## 🎮 การจัดการระบบ

### 📊 Production Management

```bash
# เริ่มทุกอย่าง
./run_production_extended.sh start

# หยุดทุกอย่าง  
./run_production_extended.sh stop

# รีสตาร์ททุกอย่าง
./run_production_extended.sh restart

# รีสตาร์ทเฉพาะ WebSocket services
./run_production_extended.sh restart-websocket

# ดูสถานะโดยละเอียด
./run_production_extended.sh status

# ดู logs แบบ interactive
./run_production_extended.sh logs
```

### 🔧 Individual Service Management

```bash
# WebSocket Server
./run_websocket_server.sh {start|stop|restart|status|logs|test}

# WebSocket Sender  
./run_websocket_sender.sh {start|stop|restart|status}

# Main Application
./run_production.sh {start|stop|restart|status|logs}
```

### 🛠️ Systemd Service Management

```bash
# เริ่ม services
sudo systemctl start websocket-server
sudo systemctl start websocket-sender

# ตรวจสอบสถานะ
sudo systemctl status websocket-server websocket-sender

# ดู logs
sudo journalctl -u websocket-server -f
sudo journalctl -u websocket-sender -f

# ตั้งค่าเริ่มอัตโนมัติ
sudo systemctl enable websocket-server websocket-sender

# หยุด services
sudo systemctl stop websocket-sender websocket-server
```

## 🌐 การใช้งานผ่าน Web Interface

### 📱 AI Camera Management
- **Main Dashboard**: `http://localhost/`
- **Detection Results**: `http://localhost/detection`
- **Health Monitor**: `http://localhost/health`
- **WebSocket Management**: `http://localhost/websocket`

### 🔗 WebSocket Management Features
- Start/Stop WebSocket sender
- ดูสถิติข้อมูลที่ยังไม่ส่ง
- ติดตามกิจกรรมแบบ real-time
- ตรวจสอบการเชื่อมต่อ server

## 📡 API Endpoints

### 🔧 WebSocket Sender Control
```bash
# ดูสถานะ
GET /api/websocket_status

# เริ่ม sender
POST /api/start_websocket_sender

# หยุด sender
POST /api/stop_websocket_sender

# รีสตาร์ท sender
POST /api/restart_websocket_sender

# ดูข้อมูลที่ยังไม่ส่ง
GET /api/websocket_unsent_data
```

### 📊 Main Application APIs
```bash
# Camera control
GET /api/camera_status
POST /api/start_camera
POST /api/stop_camera

# Detection control  
GET /api/detection_status
POST /api/start_detection
POST /api/stop_detection

# Health monitoring
GET /api/health_status
POST /api/run_health_check
```

## 📋 รูปแบบข้อมูลที่ส่ง

### 🚗 Detection Data
```json
{
  "table": "lpr_detection",
  "action": "insert",
  "data": {
    "license_plate": "ABC1234",
    "confidence": 95.5,
    "checkpoint_id": "1",
    "timestamp": "2024-08-06T10:30:00",
    "hostname": "aicamera",
    "vehicle_type": "",
    "vehicle_color": "",
    "latitude": "",
    "longitude": "",
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
    "exposure_time": 0.033,
    "analog_gain": 1.0,
    "lux": 250
  }
}
```

### 🏥 Health Monitor Data
```json
{
  "table": "health_monitor",
  "action": "insert", 
  "data": {
    "checkpoint_id": "1",
    "hostname": "aicamera",
    "timestamp": "2024-08-06T10:30:00",
    "component": "camera",
    "status": "PASS",
    "message": "Camera working normally",
    "system_info": {
      "python_version": "3.9.2",
      "platform": "linux",
      "memory_usage": "45%",
      "cpu_usage": "12%"
    }
  }
}
```

### 📨 Server Response
```json
{
  "status": "success",
  "message": "Data saved successfully",
  "record_id": 12345,
  "table": "lpr_detection",
  "action": "insert"
}
```

## 🔍 การตรวจสอบระบบ

### 📊 Database Queries

```sql
-- ตรวจสอบข้อมูล Client (sender)
SELECT COUNT(*) FROM detection_results WHERE sent_to_server = 0;
SELECT COUNT(*) FROM health_checks WHERE sent_to_server = 0;

-- ตรวจสอบข้อมูล Server (receiver)  
SELECT COUNT(*) FROM lpr_detections;
SELECT COUNT(*) FROM health_monitors;

-- ดูข้อมูลล่าสุดที่ server รับ
SELECT * FROM lpr_detections ORDER BY received_at DESC LIMIT 5;
SELECT * FROM health_monitors ORDER BY received_at DESC LIMIT 5;
```

### 🔧 Network Testing

```bash
# ทดสอบการเชื่อมต่อ WebSocket server
./run_websocket_server.sh test

# ตรวจสอบ port ที่เปิดอยู่
netstat -tlnp | grep -E ":(80|8000|8765)"

# ทดสอบ connectivity
ping 100.95.46.128
telnet 100.95.46.128 8765

# ทดสอบ WebSocket connection ด้วย curl
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
     http://100.95.46.128:8765/
```

## 📝 Log Files และ Monitoring

### 📄 Log Locations
- **WebSocket Sender**: `log/websocket_sender.log`
- **WebSocket Server**: `log/websocket_server.log` 
- **Main Application**: `log/app.log`
- **Gunicorn**: `log/gunicorn_error.log`
- **Systemd Services**: `journalctl -u service-name`

### 🔍 Log Monitoring
```bash
# ติดตาม logs แบบ real-time
tail -f log/websocket_sender.log
tail -f log/websocket_server.log

# ดู logs หลาย files พร้อมกัน
multitail log/websocket_sender.log log/websocket_server.log

# ดู systemd service logs
sudo journalctl -u websocket-server -u websocket-sender -f

# กรอง logs ตาม level
grep "ERROR" log/websocket_sender.log
grep "SUCCESS" log/websocket_sender.log
```

## 🚨 การแก้ไขปัญหาที่อาจเกิดขึ้น

### 🔌 ปัญหาการเชื่อมต่อ WebSocket

#### อาการ: "Connection refused" หรือ "Connection failed"

```bash
# 1. ตรวจสอบว่า WebSocket server ทำงานอยู่หรือไม่
./run_websocket_server.sh status

# 2. ตรวจสอบ port 8765
netstat -tlnp | grep 8765

# 3. ตรวจสอบ firewall
sudo ufw status
sudo iptables -L | grep 8765

# 4. ทดสอบการเชื่อมต่อ
telnet localhost 8765
```

#### การแก้ไข:
```bash
# เริ่ม WebSocket server
./run_websocket_server.sh start

# หรือใช้ systemd
sudo systemctl start websocket-server

# ตรวจสอบ logs
tail -f log/websocket_server.log
```

### 🗄️ ปัญหาฐานข้อมูล

#### อาการ: "Database locked" หรือ "Table doesn't exist"

```bash
# 1. ตรวจสอบไฟล์ฐานข้อมูล
ls -la db/lpr_data.db websocket_server.db

# 2. ตรวจสอบ permissions
ls -la db/
chown camuser:camuser db/lpr_data.db

# 3. ตรวจสอบโครงสร้างตาราง
sqlite3 db/lpr_data.db ".schema detection_results"
sqlite3 websocket_server.db ".schema lpr_detections"
```

#### การแก้ไข:
```bash
# สร้างฐานข้อมูลใหม่หากจำเป็น
rm -f websocket_server.db
./run_websocket_server.sh start  # จะสร้างฐานข้อมูลใหม่

# แก้ไข permissions
sudo chown -R camuser:camuser /home/camuser/aicamera/v2
chmod 755 /home/camuser/aicamera/v2
chmod 644 db/*.db
```

### 🌐 ปัญหา Network Configuration

#### อาการ: เชื่อมต่อ localhost ได้แต่ remote ไม่ได้

```bash
# 1. ตรวจสอบการตั้งค่า server
grep "0.0.0.0" websocket_server.py  # ต้องเป็น 0.0.0.0 ไม่ใช่ 127.0.0.1

# 2. ตรวจสอบ firewall
sudo ufw allow 8765
sudo systemctl reload ufw

# 3. ตรวจสอบ network interface
ip addr show
netstat -tlnp | grep 0.0.0.0:8765
```

### 🔄 ปัญหา Service Management

#### อาการ: Services ไม่เริ่มอัตโนมัติ

```bash
# 1. ตรวจสอบ systemd service status
sudo systemctl status websocket-server websocket-sender

# 2. ตรวจสอบ service files
sudo systemctl cat websocket-server
sudo systemctl cat websocket-sender

# 3. เปิดใช้งาน auto-start
sudo systemctl enable websocket-server websocket-sender

# 4. Reload systemd daemon
sudo systemctl daemon-reload
```

### 📊 ปัญหา Performance

#### อาการ: ระบบช้าหรือ memory leak

```bash
# 1. ตรวจสอบ resource usage
top -p $(pgrep -f websocket)
ps aux | grep websocket

# 2. ตรวจสอบ database size
du -sh db/lpr_data.db websocket_server.db

# 3. ทำความสะอาดฐานข้อมูล (ข้อมูลเก่า)
sqlite3 db/lpr_data.db "DELETE FROM detection_results WHERE timestamp < date('now', '-30 days');"
sqlite3 websocket_server.db "DELETE FROM lpr_detections WHERE received_at < date('now', '-30 days');"

# 4. Restart services
./run_production_extended.sh restart
```

### 🔧 ปัญหา Configuration

#### อาการ: "Environment variable not found"

```bash
# 1. ตรวจสอบไฟล์ .env.production
cat .env.production | grep WEBSOCKET_SERVER_URL

# 2. ตรวจสอบ path ของไฟล์
ls -la .env.production

# 3. ตรวจสอบ syntax ในไฟล์ config
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv('.env.production')
print('WEBSOCKET_SERVER_URL:', os.getenv('WEBSOCKET_SERVER_URL'))
"
```

## 🎯 Best Practices

### 🚀 Production Deployment

1. **ใช้ Systemd Services**
   ```bash
   sudo ./install_all_services.sh
   sudo systemctl enable websocket-server websocket-sender
   ```

2. **Monitor Resources**
   ```bash
   # ตั้ง log rotation
   sudo logrotate -f /etc/logrotate.conf
   
   # Monitor disk space
   df -h
   du -sh log/
   ```

3. **Security Configuration**
   ```bash
   # ตั้งค่า firewall
   sudo ufw allow from trusted_ip to any port 8765
   
   # ใช้ reverse proxy สำหรับ production
   # (Nginx configuration already included)
   ```

### 🔄 Maintenance Tasks

```bash
# รายวัน - ตรวจสอบ logs
tail -100 log/websocket_sender.log | grep ERROR

# รายสัปดาห์ - ทำความสะอาดฐานข้อมูล
./cleanup_old_data.sh  # สร้าง script นี้เพิ่มเติม

# รายเดือน - อัพเดตระบบ
sudo apt update && sudo apt upgrade
pip install -r requirements.txt --upgrade
```

### 📈 Performance Tuning

```bash
# ปรับแต่งการตั้งค่าใน websocket_sender.py
CHECK_INTERVAL = 5  # วินาที (ลดลงสำหรับ real-time มากขึ้น)

# ปรับแต่งขนาดรูปภาพ  
max_size=(640, 480)  # ลดขนาดเพื่อประหยัด bandwidth
quality=75           # ปรับ quality ตามต้องการ

# ปรับแต่งจำนวนรายการที่ประมวลผลต่อครั้ง
LIMIT 10  # เพิ่มหากต้องการประมวลผลมากขึ้น
```

## 📞 การติดต่อและ Support

### 🐛 การรายงานปัญหา

เมื่อพบปัญหา ให้รวบรวมข้อมูลต่อไปนี้:

```bash
# 1. System information
uname -a
python3 --version
pip list | grep websockets

# 2. Service status
./run_production_extended.sh status

# 3. Recent logs
tail -50 log/websocket_sender.log
tail -50 log/websocket_server.log

# 4. Network configuration
netstat -tlnp | grep -E ":(80|8000|8765)"
ip addr show

# 5. Database status
sqlite3 db/lpr_data.db "SELECT COUNT(*) FROM detection_results WHERE sent_to_server = 0;"
sqlite3 websocket_server.db "SELECT COUNT(*) FROM lpr_detections;"
```

### 📚 เอกสารเพิ่มเติม

- **WebSocket Protocol**: [RFC 6455](https://tools.ietf.org/html/rfc6455)
- **Python websockets library**: [Documentation](https://websockets.readthedocs.io/)
- **Systemd Service Management**: [systemctl manual](https://www.freedesktop.org/software/systemd/man/systemctl.html)
- **SQLite Database**: [SQLite Documentation](https://www.sqlite.org/docs.html)

---

## 🎉 สรุป

ระบบ WebSocket นี้ได้รับการออกแบบมาเพื่อให้มีความเสถียร ยืดหยุ่น และง่ายต่อการจัดการ เหมาะสำหรับใช้งานใน production environment และสามารถ scale ได้ตามความต้องการ

ระบบรองรับทั้งการใช้งานแบบ standalone สำหรับ development และแบบ systemd services สำหรับ production deployment พร้อมด้วย web interface ที่ครบครันสำหรับการจัดการและ monitoring

หากมีคำถามหรือต้องการความช่วยเหลือเพิ่มเติม สามารถตรวจสอบ log files หรือใช้ diagnostic tools ที่มีให้ครับ! 🚀