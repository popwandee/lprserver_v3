# WebSocket Server สำหรับระบบ AI Camera

## 🎯 วัตถุประสงค์ (Objectives)

WebSocket Server นี้ถูกออกแบบมาเพื่อ:

1. **รับข้อมูลการตรวจจับป้ายทะเบียน (LPR Detection)** จากกล้อง AI
2. **รับข้อมูลการตรวจสอบสุขภาพระบบ (Health Monitor)** จากอุปกรณ์ต่างๆ
3. **จัดเก็บข้อมูลในฐานข้อมูล SQLite** เพื่อการวิเคราะห์และติดตาม
4. **ให้บริการ WebSocket** ที่เชื่อมต่อแบบ Real-time
5. **รองรับการเชื่อมต่อหลาย Client** พร้อมกัน
6. **ตรวจสอบความถูกต้องของข้อมูล** ก่อนบันทึก

## ⚙️ การทำงาน (Functionality)

### ระบบหลัก
- **WebSocket Server**: ทำงานบนพอร์ต 8765
- **ฐานข้อมูล SQLite**: เก็บข้อมูล LPR และ Health Monitor
- **ระบบ Logging**: บันทึกการทำงานและข้อผิดพลาด
- **การตรวจสอบข้อมูล**: ตรวจสอบรูปภาพและข้อมูลก่อนบันทึก
- **Systemd Service**: ทำงานเป็นระบบบริการอัตโนมัติ

### โครงสร้างฐานข้อมูล

#### ตาราง lpr_detections
```sql
- id: รหัสอ้างอิง
- license_plate: ป้ายทะเบียน
- confidence: ความแม่นยำ
- checkpoint_id: รหัสจุดตรวจ
- timestamp: เวลาที่ตรวจจับ
- hostname: ชื่อเครื่อง
- vehicle_type: ประเภทยานพาหนะ
- vehicle_color: สีรถ
- latitude/longitude: พิกัด GPS
- image_data: รูปภาพ (Base64)
- exposure_time: เวลาเปิดรับแสง
- analog_gain: การขยายสัญญาณ
- lux: ความสว่าง
- received_at: เวลาที่ได้รับข้อมูล
```

#### ตาราง health_monitors
```sql
- id: รหัสอ้างอิง
- checkpoint_id: รหัสจุดตรวจ
- hostname: ชื่อเครื่อง
- timestamp: เวลาที่ตรวจสอบ
- component: ส่วนประกอบที่ตรวจสอบ
- status: สถานะ (PASS/FAIL)
- message: ข้อความ
- system_info: ข้อมูลระบบ (JSON)
- received_at: เวลาที่ได้รับข้อมูล
```

## 🚀 วิธีการใช้งาน (Usage Methods)

### 1. การเริ่มต้นเซิร์ฟเวอร์

#### วิธีที่ 1: ใช้ Systemd Service (แนะนำสำหรับ Production)
```bash
# เริ่มต้นเซิร์ฟเวอร์
sudo systemctl start websocket_server.service

# เปิดใช้งานอัตโนมัติเมื่อบูตระบบ
sudo systemctl enable websocket_server.service

# ตรวจสอบสถานะ
sudo systemctl status websocket_server.service
```

#### วิธีที่ 2: ใช้ Script (แนะนำสำหรับ Development)
```bash
cd /home/devuser/lprserver_v2/websocket_server
./run_websocket_server.sh start
```

#### วิธีที่ 3: รันโดยตรง
```bash
cd /home/devuser/lprserver_v2/websocket_server
source ../venv-django/bin/activate
python websocket_server.py
```

### 2. การตรวจสอบสถานะ
```bash
# ตรวจสอบสถานะ Systemd Service
sudo systemctl status websocket_server.service

# ตรวจสอบสถานะด้วย Script
./run_websocket_server.sh status

# ตรวจสอบพอร์ต
netstat -tlnp | grep 8765
# หรือ
ss -tlnp | grep 8765

# ตรวจสอบ Process
ps aux | grep websocket_server.py
```

### 3. การดู Log
```bash
# ดู Log ของ Systemd Service
sudo journalctl -u websocket_server.service -f

# ดู Log แบบ Real-time ด้วย Script
./run_websocket_server.sh logs

# ดู Log ไฟล์โดยตรง
tail -f log/websocket_server.log

# ดู Log ย้อนหลัง
sudo journalctl -u websocket_server.service --no-pager -n 50
```

### 4. การหยุดเซิร์ฟเวอร์
```bash
# หยุด Systemd Service
sudo systemctl stop websocket_server.service

# หยุดแบบปกติด้วย Script
./run_websocket_server.sh stop

# หยุดแบบฉุกเฉิน
./run_websocket_server.sh emergency-stop
```

### 5. การรีสตาร์ทเซิร์ฟเวอร์
```bash
# รีสตาร์ท Systemd Service
sudo systemctl restart websocket_server.service

# รีสตาร์ทด้วย Script
./run_websocket_server.sh restart
```

## 🔧 การแก้ไขปัญหา (Troubleshooting)

### ปัญหาที่พบบ่อยและวิธีแก้ไข

#### 1. พอร์ต 8765 ถูกใช้งานอยู่
**อาการ**: `[Errno 98] error while attempting to bind on address ('0.0.0.0', 8765): address already in use`

**วิธีแก้ไข**:
```bash
# หา Process ที่ใช้พอร์ต 8765
sudo netstat -tlnp | grep 8765
# หรือ
sudo ss -tlnp | grep 8765

# หยุด Process ที่ใช้พอร์ต
sudo kill -9 <PID>

# หรือหยุด Systemd Service
sudo systemctl stop websocket_server.service

# เริ่มต้นใหม่
sudo systemctl start websocket_server.service
```

#### 2. Systemd Service Error 203/EXEC
**อาการ**: `status=203/EXEC` ใน systemctl status

**วิธีแก้ไข**:
```bash
# ตรวจสอบว่าไฟล์และสิทธิ์ถูกต้อง
ls -la /home/devuser/lprserver_v2/venv-django/bin/python
ls -la /home/devuser/lprserver_v2/websocket_server/websocket_server.py

# ทดสอบรันด้วยตนเอง
/home/devuser/lprserver_v2/venv-django/bin/python /home/devuser/lprserver_v2/websocket_server/websocket_server.py

# แก้ไขสิทธิ์ถ้าจำเป็น
chmod 755 /home/devuser/lprserver_v2/websocket_server/websocket_server.py
chmod 755 /home/devuser/lprserver_v2/venv-django/bin/python
```

#### 3. ปัญหาสิทธิ์การเข้าถึง
**อาการ**: `Permission denied` errors

**วิธีแก้ไข**:
```bash
# แก้ไขสิทธิ์
chmod 755 /home/devuser/lprserver_v2/websocket_server/
chmod 755 websocket_server.py run_websocket_server.sh
chmod 664 websocket_server.db
chmod 775 log/
chmod 664 log/websocket_server.log

# หรือใช้ Script แก้ไขสิทธิ์
./fix_permissions.sh
```

#### 4. ปัญหาฐานข้อมูลล็อค
**อาการ**: ไฟล์ `websocket_server.db-journal` ปรากฏและหายไป

**วิธีแก้ไข**: ✅ **แก้ไขแล้ว** - ฐานข้อมูลใช้ timeout 30 วินาที
```bash
# ปัญหานี้ได้รับการแก้ไขในโค้ดแล้ว
# การเชื่อมต่อฐานข้อมูลใช้: sqlite3.connect(DB_PATH, timeout=30.0)
# ไม่มีไฟล์ journal เกิดขึ้นระหว่างการทำงานปกติ
```

#### 5. ปัญหา Virtual Environment
**อาการ**: `ModuleNotFoundError` หรือ import errors

**วิธีแก้ไข**:
```bash
# เปิดใช้งาน Virtual Environment
source ../venv-django/bin/activate

# ติดตั้ง Dependencies ที่ขาดหาย
pip install --upgrade pip setuptools wheel
pip install Flask Werkzeug gunicorn websockets python-dotenv Pillow colorlog psutil opencv-python numpy
```

#### 6. ปัญหา Dependencies
**อาการ**: `No module named 'distutils'` หรือ build errors

**วิธีแก้ไข**:
```bash
# อัปเดต pip และ setuptools
source ../venv-django/bin/activate
pip install --upgrade pip setuptools wheel

# ติดตั้ง Dependencies หลักทีละตัว
pip install Flask Werkzeug gunicorn websockets python-dotenv Pillow colorlog psutil
pip install opencv-python numpy
```

#### 7. ปัญหา Service Conflicts
**อาการ**: มีหลาย Service ใช้พอร์ตเดียวกัน

**วิธีแก้ไข**:
```bash
# ตรวจสอบ Services ทั้งหมด
sudo systemctl list-units --type=service --all | grep -i websocket

# หยุดและลบ Services ที่ไม่ต้องการ
sudo systemctl stop websocket-server.service
sudo systemctl disable websocket-server.service
sudo rm -f /etc/systemd/system/websocket-server.service

# รีโหลด systemd
sudo systemctl daemon-reload
```

### การตรวจสอบและแก้ไขปัญหา

#### ตรวจสอบสถานะระบบ
```bash
# ตรวจสอบสถานะเซิร์ฟเวอร์
sudo systemctl status websocket_server.service

# ตรวจสอบขนาดฐานข้อมูล
ls -lh websocket_server.db

# ตรวจสอบขนาดไฟล์ Log
ls -lh log/websocket_server.log

# ตรวจสอบการใช้ทรัพยากรระบบ
top -p $(pgrep -f websocket_server.py)
```

#### ตรวจสอบฐานข้อมูล
```bash
# ใช้ Python (แนะนำ)
source ../venv-django/bin/activate
python -c "
import sqlite3
conn = sqlite3.connect('websocket_server.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM lpr_detections')
print('LPR records:', cursor.fetchone()[0])
cursor.execute('SELECT COUNT(*) FROM health_monitors')
print('Health records:', cursor.fetchone()[0])
conn.close()
"

# หรือติดตั้ง sqlite3
sudo apt install sqlite3
sqlite3 websocket_server.db
.tables
SELECT COUNT(*) FROM lpr_detections;
SELECT COUNT(*) FROM health_monitors;
```

#### ตรวจสอบเครือข่าย
```bash
# ตรวจสอบว่าพอร์ตกำลังฟังอยู่
netstat -tlnp | grep 8765

# ตรวจสอบการเชื่อมต่อที่ใช้งานอยู่
ss -tlnp | grep 8765

# ทดสอบการเชื่อมต่อ
telnet localhost 8765
```

## 🛠️ การบำรุงรักษา (Maintenance)

### งานบำรุงรักษาปกติ
```bash
# 1. ตรวจสอบสถานะเซิร์ฟเวอร์ทุกวัน
sudo systemctl status websocket_server.service

# 2. ตรวจสอบขนาดไฟล์ Log
ls -lh log/websocket_server.log

# 3. ตรวจสอบขนาดฐานข้อมูล
ls -lh websocket_server.db

# 4. สำรองฐานข้อมูล (ถ้าจำเป็น)
cp websocket_server.db websocket_server.db.backup.$(date +%Y%m%d)

# 5. หมุนเวียน Log (ถ้าจำเป็น)
mv log/websocket_server.log log/websocket_server.log.$(date +%Y%m%d)
```

### การจัดการ Services
```bash
# ตรวจสอบ Services ทั้งหมด
sudo systemctl list-units --type=service --all | grep -i websocket

# ลบ Services ที่ไม่ต้องการ
sudo systemctl stop <service_name>
sudo systemctl disable <service_name>
sudo rm -f /etc/systemd/system/<service_name>
sudo systemctl daemon-reload
```

## 📊 การตรวจสอบประสิทธิภาพ

### การตั้งค่าประสิทธิภาพ
- **Database timeout**: 30 วินาที
- **WebSocket ping interval**: 30 วินาที
- **WebSocket ping timeout**: 10 วินาที
- **Maximum image size**: 5MB

### การตรวจสอบสถิติ
```bash
# ตรวจสอบสถิติเซิร์ฟเวอร์
sudo systemctl status websocket_server.service

# ตรวจสอบจำนวนข้อมูลในฐานข้อมูล
source ../venv-django/bin/activate
python -c "
import sqlite3
conn = sqlite3.connect('websocket_server.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM lpr_detections')
lpr_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM health_monitors')
health_count = cursor.fetchone()[0]
print(f'LPR Records: {lpr_count}')
print(f'Health Records: {health_count}')
conn.close()
"
```

## 📋 คำสั่งอ้างอิงด่วน

### เริ่มต้นเซิร์ฟเวอร์
```bash
# Systemd Service (แนะนำ)
sudo systemctl start websocket_server.service

# Script Method
cd /home/devuser/lprserver_v2/websocket_server
./run_websocket_server.sh start
```

### ตรวจสอบสถานะ
```bash
# Systemd Service
sudo systemctl status websocket_server.service

# Script Method
./run_websocket_server.sh status
```

### ดู Log
```bash
# Systemd Service
sudo journalctl -u websocket_server.service -f

# Script Method
./run_websocket_server.sh logs
```

### หยุดเซิร์ฟเวอร์
```bash
# Systemd Service
sudo systemctl stop websocket_server.service

# Script Method
./run_websocket_server.sh stop
```

### รีสตาร์ทเซิร์ฟเวอร์
```bash
# Systemd Service
sudo systemctl restart websocket_server.service

# Script Method
./run_websocket_server.sh restart
```

### ทดสอบการเชื่อมต่อ
```bash
# ตรวจสอบว่าพอร์ตกำลังฟังอยู่
netstat -tlnp | grep 8765

# ทดสอบการเข้าถึงฐานข้อมูล
source ../venv-django/bin/activate
python -c "import sqlite3; conn = sqlite3.connect('websocket_server.db'); print('Database accessible'); conn.close()"
```

### หยุดฉุกเฉิน
```bash
# ใช้คำสั่งหยุดฉุกเฉิน (แนะนำ)
./run_websocket_server.sh emergency-stop

# หรือฆ่า Process ทั้งหมดด้วยตนเอง
sudo pkill -f websocket_server.py

# หรือฆ่าด้วย PID
sudo kill $(cat websocket_server.pid 2>/dev/null) 2>/dev/null || true
```

## 🔒 ความปลอดภัย

### การตั้งค่าความปลอดภัย
- **Firewall**: เปิดพอร์ต 8765 เฉพาะ IP ที่จำเป็น
- **SSL/TLS**: พิจารณาใช้ WSS สำหรับ Production
- **Authentication**: เพิ่มการยืนยันตัวตนถ้าจำเป็น
- **Rate Limiting**: จำกัดจำนวนการเชื่อมต่อ

### คำสั่ง Firewall
```bash
# เปิดพอร์ต 8765
sudo ufw allow 8765

# เปิดพอร์ตเฉพาะ IP
sudo ufw allow from 192.168.1.0/24 to any port 8765

# ตรวจสอบสถานะ Firewall
sudo ufw status
```

## 📞 การสนับสนุน

หากพบปัญหาหรือมีคำถาม ให้ตรวจสอบเอกสารหลักของ AI Camera หรือติดต่อทีมพัฒนา

**อัปเดตล่าสุด**: สิงหาคม 2025  
**สถานะ**: ✅ ตั้งค่าและทำงานได้สมบูรณ์  
**วิธีที่แนะนำ**: Systemd Service สำหรับ Production, Script สำหรับ Development  
**ฐานข้อมูล**: ✅ ทำงานได้ 3,159+ รายการ LPR, 853+ รายการ Health  
**ปัญหาที่แก้ไขแล้ว**: ✅ ไฟล์ journal ฐานข้อมูล, ✅ ความน่าเชื่อถือของคำสั่งหยุด, ✅ Systemd Service Conflicts 