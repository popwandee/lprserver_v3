# LPR Server v3

ระบบ LPR Server v3 เป็นระบบจัดการข้อมูลการอ่านป้ายทะเบียนรถยนต์ ที่รับข้อมูลจาก Edge Camera ผ่าน WebSocket และแสดงผลในรูปแบบตาราง

## คุณสมบัติหลัก

### ระบบหลัก
- ✅ รับข้อมูลจาก Edge Camera ผ่าน WebSocket (Port 8765)
- ✅ บันทึกข้อมูลลงฐานข้อมูล PostgreSQL
- ✅ บันทึกภาพลงใน storage directory
- ✅ แสดงผลในรูปแบบตารางพร้อมการกรองข้อมูล
- ✅ แดชบอร์ดแสดงสถิติการใช้งานแบบ real-time
- ✅ REST API สำหรับการเข้าถึงข้อมูล
- ✅ Real-time updates ผ่าน WebSocket

### ระบบจัดการ
- ✅ ระบบจัดการด้วย systemd service
- ✅ Reverse proxy ด้วย nginx
- ✅ Service management script (`manage_services.sh`)
- ✅ Health monitoring system

### ระบบ Blacklist
- ✅ ระบบจัดการ Blacklist สำหรับป้ายทะเบียน
- ✅ การตรวจจับและแจ้งเตือนป้ายทะเบียนที่อยู่ใน blacklist
- ✅ สถิติการตรวจจับ blacklist แบบ real-time
- ✅ การจัดการ blacklist ผ่าน Web Interface และ API

### โมดูลเพิ่มเติม
- ✅ AI Camera Management
- ✅ Detection Management
- ✅ Map and Tracking
- ✅ System Management
- ✅ User Management
- ✅ Report Generation
- ✅ Health Monitoring

### การทดสอบ
- ✅ ระบบทดสอบอัตโนมัติ (`test_system.py`)
- ✅ WebSocket test client (`test_client.py`, `simple_test_client.py`)
- ✅ API test client (`test_api.py`)
- ✅ Performance testing
- ✅ Database integrity checking

## สถาปัตยกรรมระบบ

### WebSocket Server Architecture
```
WebSocket Server (Port 8765)
├── Flask Application
├── SocketIO Server
├── REST API Endpoints
└── In-Memory Data Storage
```

### เทคโนโลยีที่ใช้
- **Flask**: Web framework สำหรับ HTTP endpoints
- **Flask-SocketIO**: WebSocket server สำหรับ real-time communication
- **PostgreSQL**: ฐานข้อมูลหลักสำหรับจัดเก็บข้อมูล
- **SQLAlchemy**: ORM สำหรับจัดการฐานข้อมูล

### การรองรับ Client Types
- ✅ **Socket.IO Clients**: Real-time communication สำหรับ cameras และ dashboards
- ✅ **REST API Clients**: HTTP endpoints สำหรับ data retrieval และ monitoring
- ✅ **Unified Architecture**: ใช้ Flask + SocketIO ร่วมกัน
- ✅ **Comprehensive Endpoints**: ครอบคลุมการใช้งานหลักทั้งหมด

## โครงสร้างโปรเจกต์

```
lprserver_v3/
├── src/                           # Source code
│   ├── app.py                     # Flask application factory
│   ├── web/                       # Web application
│   │   └── blueprints/            # Flask blueprints
│   │       ├── __init__.py        # Blueprints package
│   │       ├── main.py            # Main web routes
│   │       ├── api.py             # API routes
│   │       ├── aicamera.py        # AI Camera management
│   │       ├── detection.py       # Detection management
│   │       ├── map.py             # Map and tracking
│   │       ├── system.py          # System management
│   │       ├── user.py            # User management
│   │       ├── report.py          # Report generation
│   │       └── health.py          # Health monitoring
│   ├── services/                  # Business logic services
│   │   ├── __init__.py            # Services package
│   │   ├── websocket_service.py   # WebSocket handling
│   │   ├── blacklist_service.py   # Blacklist management
│   │   ├── health_service.py      # Health monitoring
│   │   └── database_service.py    # Database operations
│   └── core/                      # Core components
│       ├── models/                # Database models
│       │   ├── __init__.py        # Models package
│       │   ├── lpr_record.py      # LPR Record model
│       │   ├── blacklist_plate.py # Blacklist model
│       │   ├── camera.py          # Camera model
│       │   └── health_check.py    # Health check model
│       ├── dependency_container.py # Dependency injection
│       ├── import_helper.py       # Import utilities
│       └── utils/                 # Utility functions
├── templates/                     # HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   ├── dashboard.html             # Dashboard page
│   ├── records.html               # Records table page
│   ├── blacklist.html             # Blacklist management page
│   ├── aicamera/                  # AI Camera templates
│   ├── detection/                 # Detection templates
│   ├── map/                       # Map templates
│   ├── system/                    # System templates
│   ├── user/                      # User templates
│   └── report/                    # Report templates
├── storage/                       # File storage
│   └── images/                    # LPR images
├── logs/                          # Application logs
├── database/                      # Database files
├── config.py                      # Application configuration
├── requirements.txt               # Python dependencies
├── run.py                         # Development server
├── wsgi.py                        # Production WSGI entry
├── websocket_server.py            # WebSocket server (Port 8765)
├── setup.sh                       # Setup script
├── manage_services.sh             # Service management script
├── test_system.py                 # System test script
├── test_client.py                 # WebSocket test client
├── simple_test_client.py          # Simple WebSocket test client
├── test_api.py                    # API test client
├── lprserver.service              # Main service
├── lprserver-websocket.service    # WebSocket service
├── lprserver.conf                 # Nginx configuration
├── env.example                    # Environment variables example
├── coding_rule.md                 # Development guidelines
├── DEVELOPMENT_REPORT.md          # Development report
├── DEVELOPMENT_GUIDE.md           # Development guide
├── DEPLOYMENT_GUIDE_RPI5.md       # Raspberry Pi 5 deployment guide
├── SYSTEMD_SETUP.md               # Systemd setup guide
├── USER_MANUAL_AI_CAMERA.md       # AI Camera user manual
├── DEVELOPER_DOCUMENTATION_ALPR.md # Developer documentation
├── ARCHITECTURE_ANALYSIS.md       # Architecture analysis
└── README.md                      # This file
```

## การติดตั้ง

### ข้อกำหนดระบบ

- Ubuntu 20.04 หรือใหม่กว่า
- Python 3.8 หรือใหม่กว่า
- nginx
- systemd

### ขั้นตอนการติดตั้ง

1. **Clone โปรเจกต์**
   ```bash
   git clone <repository-url>
   cd lprserver_v3
   ```

2. **รัน setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Script นี้จะ:
   - สร้าง virtual environment
   - ติดตั้ง dependencies
   - สร้างฐานข้อมูล
   - ตั้งค่า systemd services
   - ตั้งค่า nginx
   - เริ่มต้นระบบ
   - ทดสอบระบบ

3. **ตรวจสอบการติดตั้ง**
   ```bash
   # ตรวจสอบสถานะ services
   ./manage_services.sh status
   
   # ทดสอบระบบ
   python test_system.py
   
   # ทดสอบ WebSocket server
   python simple_test_client.py
   
   # ทดสอบ API endpoints
   python test_api.py
   
   # ตรวจสอบ web interface
   curl -I http://localhost
   ```

4. **ตรวจสอบสถานะ**
   ```bash
   sudo systemctl status lprserver.service
   sudo systemctl status lprserver-websocket.service
   sudo systemctl status nginx
   ```

## การใช้งาน

### Web Interface

#### หน้าหลัก
- **หน้าแรก**: http://localhost
- **แดชบอร์ด**: http://localhost/dashboard
- **รายการบันทึก**: http://localhost/records
- **จัดการ Blacklist**: http://localhost/blacklist

#### โมดูลเพิ่มเติม
- **AI Camera**: http://localhost/aicamera
- **Detection**: http://localhost/detection
- **Map**: http://localhost/map
- **System**: http://localhost/system
- **User**: http://localhost/user
- **Report**: http://localhost/report
- **Health**: http://localhost/health

### WebSocket Server (Port 8765)

#### Connection
```python
import socketio

sio = socketio.Client()
sio.connect('http://localhost:8765')
```

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

#### ตัวอย่างการใช้งาน
```python
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

### REST API Endpoints

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

#### ตัวอย่างการใช้งาน API
```bash
# ดึงสถิติ
curl http://localhost:8765/api/statistics

# ดึงรายการล่าสุด 10 รายการ
curl "http://localhost:8765/api/records?limit=10"

# ดึงรายการจากกล้องเฉพาะ
curl "http://localhost:8765/api/records?camera_id=CAM001"

# ดึงข้อมูลกล้อง
curl http://localhost:8765/api/cameras
```

### การทดสอบ

#### ทดสอบ WebSocket
```bash
# ทดสอบ WebSocket client
python simple_test_client.py

# ทดสอบ WebSocket connection
python test_client.py
```

#### ทดสอบ API
```bash
# ทดสอบ API endpoints
python test_api.py

# ทดสอบด้วย curl
curl http://localhost:8765/api/statistics
```

#### ทดสอบระบบทั้งหมด
```bash
# ทดสอบระบบอัตโนมัติ
python test_system.py
```

## การจัดการระบบ

### Service Management
```bash
# ตรวจสอบสถานะ
./manage_services.sh status

# เริ่มต้นระบบ
./manage_services.sh start

# หยุดระบบ
./manage_services.sh stop

# รีสตาร์ทระบบ
./manage_services.sh restart
```

### Logs
```bash
# ดู logs ของ WebSocket server
sudo journalctl -u lprserver-websocket.service -f

# ดู logs ของ main server
sudo journalctl -u lprserver.service -f

# ดู nginx logs
sudo tail -f /var/log/nginx/lprserver_access.log
```

## การพัฒนา

### การเพิ่ม WebSocket Events
1. เพิ่ม event handler ใน `websocket_server.py`
2. ทดสอบด้วย `simple_test_client.py`
3. อัปเดตเอกสาร

### การเพิ่ม API Endpoints
1. เพิ่ม route ใน `websocket_server.py`
2. ทดสอบด้วย `test_api.py`
3. อัปเดตเอกสาร

### การทดสอบ
- ใช้ `simple_test_client.py` สำหรับ WebSocket testing
- ใช้ `test_api.py` สำหรับ API testing
- ใช้ `test_system.py` สำหรับ system testing

## ข้อจำกัดและข้อเสนอแนะ

### ข้อจำกัดปัจจุบัน
- ใช้ In-Memory storage (ข้อมูลหายเมื่อ restart)
- ไม่มี authentication/authorization
- ไม่มี rate limiting

### ข้อเสนอแนะการพัฒนา
- เพิ่ม database persistence (SQLite/PostgreSQL)
- เพิ่ม authentication system
- เพิ่ม rate limiting และ security headers
- เพิ่ม API documentation (Swagger/OpenAPI)

## สรุป

ระบบ LPR Server v3 รองรับทั้ง Socket.IO และ REST API อย่างครบถ้วน:

✅ **Socket.IO Support**: Real-time communication สำหรับ cameras และ dashboards  
✅ **REST API Support**: HTTP endpoints สำหรับ data retrieval และ monitoring  
✅ **Unified Architecture**: ใช้ Flask + SocketIO ร่วมกัน  
✅ **Comprehensive Endpoints**: ครอบคลุมการใช้งานหลักทั้งหมด  
✅ **Flexible Client Support**: รองรับ client หลายประเภท  

ระบบพร้อมใช้งานสำหรับการพัฒนาและทดสอบ LPR application
