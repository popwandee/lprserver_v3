# LPR Server v3 : User Manual

เวอร์ชัน: 3.0  
สถานะ: อัปเดตล่าสุด 14 สิงหาคม 2025  
ระบบ: LPR Server v3

### สถานะระบบล่าสุด
- ✅ **WebSocket Server** - รับข้อมูลจาก Edge Camera ได้ปกติ (Port 8765)
- ✅ **REST API** - รองรับทั้ง Socket.IO และ HTTP API endpoints
- ✅ **Unified Architecture** - Flask + SocketIO ร่วมกัน
- ✅ **Real-time Dashboard** - แสดงสถิติแบบ real-time
- ✅ **Web Interface** - หน้าเว็บทุกหน้าทำงานได้
- ✅ **Client Support** - รองรับ client หลายประเภท

### สถาปัตยกรรมใหม่
```
WebSocket Server (Port 8765)
├── Flask Application
├── SocketIO Server
├── REST API Endpoints
└── In-Memory Data Storage
```

---

## สารบัญ
- บทนำ
- สถาปัตยกรรมระบบ
- บทบาทผู้ใช้งานและสิทธิ์การเข้าถึง
- แนวทางการใช้งานภาพรวม (Quick Start)
- การใช้งานโมดูลหลัก
  - หน้าแรก (Dashboard / Home)
  - AI Camera Manager
    - ภาพรวม (Overview)
    - จัดการกล้อง (Cameras)
    - ตั้งค่ากล้อง (Settings)
  - Detection Manager
    - รายการบันทึก (Records)
    - สถิติ (Statistics)
    - การแจ้งเตือน (Alerts)
  - Map Manager
    - ติดตามรถ (Tracking)
    - วิเคราะห์ (Analytics)
    - จัดการตำแหน่ง (Locations)
  - System Manager
    - System Logs
    - Monitoring
    - Health Check
  - User Manager
    - เข้าสู่ระบบ (Login)
    - โปรไฟล์ (Profile)
    - จัดการผู้ใช้ (Users & Roles)
  - Report Manager
    - สร้างรายงาน (Generator)
    - เทมเพลต (Templates)
    - ประวัติ/กำหนดเวลา (History/Scheduled)
- การเชื่อมต่อระบบ
  - WebSocket Connection
  - REST API Usage
  - Client Integration
- คำถามที่พบบ่อย (FAQ)
- ภาคผนวก (คำอธิบายสถานะ, ไอคอน, สี)

---

## บทนำ
เอกสารนี้เป็นคู่มือการใช้งานระบบ AI Camera (ALPR) สำหรับผู้ใช้ปลายทางทุกประเภท เพื่อช่วยให้ใช้งานระบบได้อย่างมีประสิทธิภาพ และเข้าใจการทำงานของโมดูลต่างๆ อย่างรวดเร็ว

ระบบ LPR Server v3 รองรับทั้ง Socket.IO และ REST API อย่างครบถ้วน:
- **Socket.IO**: Real-time communication สำหรับ cameras และ dashboards
- **REST API**: HTTP endpoints สำหรับ data retrieval และ monitoring
- **Unified Architecture**: ใช้ Flask + SocketIO ร่วมกัน
- **Comprehensive Endpoints**: ครอบคลุมการใช้งานหลักทั้งหมด

> หมายเหตุ: ส่วนต่างๆ มีพื้นที่สำหรับแทรกภาพหน้าจอของระบบจริง เพื่อช่วยอธิบายขั้นตอน

---

## สถาปัตยกรรมระบบ

### WebSocket Server (Port 8765)
ระบบใช้ WebSocket server ที่ port 8765 สำหรับการสื่อสารแบบ real-time:

#### Events ที่รองรับ
- `connect`: เมื่อ client เชื่อมต่อ
- `disconnect`: เมื่อ client ตัดการเชื่อมต่อ
- `camera_register`: ลงทะเบียนกล้อง
- `lpr_data`: ส่งข้อมูล LPR detection
- `ping`: ทดสอบการเชื่อมต่อ
- `join_dashboard`: เข้าร่วม dashboard room

#### Response Events
- `status`: สถานะการทำงาน
- `lpr_response`: ตอบกลับข้อมูล LPR
- `error`: ข้อผิดพลาด
- `pong`: ตอบกลับ ping

### REST API Endpoints
ระบบมี REST API endpoints สำหรับการดึงข้อมูล:

#### Server Information
- `GET /` - สถานะเซิร์ฟเวอร์
- `GET /websocket` - ข้อมูล WebSocket

#### Statistics API
- `GET /api/statistics` - สถิติข้อมูลทั้งหมด

#### Records API
- `GET /api/records` - รายการ LPR records
  - Query Parameters:
    - `limit`: จำนวนรายการ (default: 20)
    - `camera_id`: กรองตามกล้อง
    - `plate_number`: กรองตามป้ายทะเบียน

#### Cameras API
- `GET /api/cameras` - ข้อมูลกล้องทั้งหมด

---

## บทบาทผู้ใช้งานและสิทธิ์การเข้าถึง
- ผู้ใช้ทั่วไป (User)
  - ดูข้อมูลพื้นฐาน, Records, สถิติภาพรวม
- นักวิเคราะห์ (Analyst)
  - เข้าถึงสถิติเชิงลึก, รายงาน, Analytics
- ผู้จัดการ (Manager)
  - ตั้งค่าระดับโมดูล, ตรวจสอบภาพรวมระบบ, อนุมัติ/กำหนดการรายงาน
- ผู้ดูแลระบบ (Admin)
  - จัดการผู้ใช้/สิทธิ์, การตั้งค่าระบบ, Logs, Health, Monitoring

ตารางสิทธิ์โดยสังเขป (ปรับตามนโยบายองค์กร):
- User: Read-only สำหรับ Records/Statistics
- Analyst: Read+Export, เข้าถึง Analytics/Reports
- Manager: Read/Write บางส่วนของ Settings, Approvals
- Admin: Full Access

---

## แนวทางการใช้งานภาพรวม (Quick Start)
1) เข้าสู่ระบบผ่านเมนู User → Login  
2) เข้าหน้า Home/Dashboard เพื่อตรวจสอบสถิติและสถานะล่าสุด  
3) เข้าดู AI Camera → Cameras เพื่อตรวจสอบสถานะกล้อง  
4) ตรวจสอบ Records/Alerts ที่ Detection → Records/Alerts  
5) ใช้ Map → Tracking เพื่อติดตามเส้นทางรถ  
6) สร้างรายงานที่ Report → Generator

> [ภาพหน้าจอ: หน้าเข้าสู่ระบบ]

---

## การใช้งานโมดูลหลัก

### หน้าแรก (Dashboard / Home)
- แสดงสถิติหลัก: จำนวนรายการวันนี้, กล้องที่ออนไลน์, Blacklist
- บัตรสถิติ (Metric Cards) เน้นอ่านง่าย สีอ่อน สบายตา
- Real-time updates ผ่าน WebSocket connection

> [ภาพหน้าจอ: Dashboard]

---

### AI Camera Manager
#### ภาพรวม (Overview)
- แสดงสถานะกล้องสรุป (Total/Online/Offline)
- การเชื่อมต่อ WebSocket แบบ real-time
- สถิติการตรวจจับแบบ live

#### จัดการกล้อง (Cameras)
- ดูรายการกล้องทั้งหมด
- สถานะการเชื่อมต่อ WebSocket
- ข้อมูลการลงทะเบียนและ last seen

#### ตั้งค่ากล้อง (Settings)
- การกำหนดค่า WebSocket connection
- การตั้งค่า camera registration
- การจัดการ API endpoints

---

## การเชื่อมต่อระบบ

### WebSocket Connection

#### สำหรับ Edge Camera
```python
import socketio

sio = socketio.Client()

# เชื่อมต่อ
sio.connect('http://localhost:8765')

# ลงทะเบียนกล้อง
sio.emit('camera_register', {'camera_id': 'CAM001'})

# ส่งข้อมูล LPR
sio.emit('lpr_data', {
    'camera_id': 'CAM001',
    'plate_number': 'กข1234',
    'confidence': 85.5,
    'location': 'ประตูหน้า',
    'image_data': 'base64_encoded_image'
})
```

#### สำหรับ Dashboard Client
```python
# เข้าร่วม dashboard room
sio.emit('join_dashboard')

# รับ real-time updates
@sio.event
def new_detection(data):
    print(f"New detection: {data}")

@sio.event
def camera_status(data):
    print(f"Camera status: {data}")
```

### REST API Usage

#### ดึงสถิติ
```bash
curl http://localhost:8765/api/statistics
```

#### ดึงรายการล่าสุด
```bash
curl "http://localhost:8765/api/records?limit=10"
```

#### ดึงข้อมูลกล้อง
```bash
curl http://localhost:8765/api/cameras
```

### Client Integration

#### JavaScript Client
```javascript
const socket = io('http://localhost:8765');

socket.on('connect', () => {
    console.log('Connected to LPR Server');
});

socket.on('new_detection', (data) => {
    console.log('New detection:', data);
    updateDashboard(data);
});
```

#### Python Client
```python
import requests

# ดึงสถิติ
response = requests.get('http://localhost:8765/api/statistics')
stats = response.json()
print(f"Total records: {stats['total_records']}")
```

---

## การทดสอบระบบ

### ทดสอบ WebSocket
```bash
# ทดสอบ WebSocket client
python simple_test_client.py

# ทดสอบ WebSocket connection
python test_client.py
```

### ทดสอบ API
```bash
# ทดสอบ API endpoints
python test_api.py

# ทดสอบด้วย curl
curl http://localhost:8765/api/statistics
```

### ทดสอบระบบทั้งหมด
```bash
# ทดสอบระบบอัตโนมัติ
python test_system.py
```

---

## คำถามที่พบบ่อย (FAQ)

### Q: ระบบรองรับ client ประเภทใดบ้าง?
A: ระบบรองรับทั้ง Socket.IO clients (สำหรับ real-time) และ REST API clients (สำหรับ data retrieval)

### Q: WebSocket server ทำงานที่ port ไหน?
A: WebSocket server ทำงานที่ port 8765

### Q: ข้อมูลถูกเก็บไว้ที่ไหน?
A: ปัจจุบันใช้ In-Memory storage (ข้อมูลหายเมื่อ restart) สำหรับการพัฒนา

### Q: ระบบรองรับการเชื่อมต่อแบบใด?
A: รองรับทั้ง HTTP และ WebSocket connections

### Q: วิธีการทดสอบการเชื่อมต่อ?
A: ใช้ `simple_test_client.py` สำหรับ WebSocket และ `test_api.py` สำหรับ API

---

## ภาคผนวก

### สถานะระบบ
- 🟢 **Online**: ระบบทำงานปกติ
- 🟡 **Warning**: มีปัญหาเล็กน้อย
- 🔴 **Error**: มีปัญหาที่ต้องแก้ไข
- ⚪ **Offline**: ระบบไม่ทำงาน

### ไอคอนที่ใช้
- 📹 **Camera**: กล้อง AI
- 📊 **Dashboard**: แดชบอร์ด
- 📝 **Records**: รายการบันทึก
- 🗺️ **Map**: แผนที่
- ⚙️ **Settings**: การตั้งค่า
- 👥 **Users**: ผู้ใช้
- 📋 **Reports**: รายงาน

### สีที่ใช้
- 🔵 **Primary**: สีหลัก
- 🟢 **Success**: สำเร็จ
- 🟡 **Warning**: เตือน
- 🔴 **Error**: ข้อผิดพลาด
- ⚪ **Info**: ข้อมูล

---

## สรุป

ระบบ LPR Server v3 รองรับทั้ง Socket.IO และ REST API อย่างครบถ้วน:

✅ **Socket.IO Support**: Real-time communication สำหรับ cameras และ dashboards  
✅ **REST API Support**: HTTP endpoints สำหรับ data retrieval และ monitoring  
✅ **Unified Architecture**: ใช้ Flask + SocketIO ร่วมกัน  
✅ **Comprehensive Endpoints**: ครอบคลุมการใช้งานหลักทั้งหมด  
✅ **Flexible Client Support**: รองรับ client หลายประเภท  

ระบบพร้อมใช้งานสำหรับการพัฒนาและทดสอบ LPR application
