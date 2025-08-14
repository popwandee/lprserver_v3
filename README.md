# LPR Server v3 - Enhanced Architecture

## ภาพรวม (Overview)

LPR Server v3 ได้รับการปรับปรุงสถาปัตยกรรมให้เป็นไปตามมาตรฐานที่กำหนดไว้ใน DEVELOPMENT_GUIDE.md โดยใช้แนวคิดหลัก 3 ประการ:
1. **Absolute Imports Pattern** - จัดการ import paths ให้ชัดเจน
2. **Dependency Injection (DI)** - ลด coupling ระหว่าง components
3. **Flask Blueprints** - Modular design สำหรับ Web UI

### ระบบหลัก
- ✅ รับข้อมูลจาก Edge Camera ผ่าน WebSocket (Port 8765)
- ✅ บันทึกข้อมูลลงฐานข้อมูล SQLite
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
- **In-Memory Storage**: เก็บข้อมูลในหน่วยความจำ (สำหรับ demo)

### การรองรับ Client Types
- ✅ **Socket.IO Clients**: Real-time communication สำหรับ cameras และ dashboards
- ✅ **REST API Clients**: HTTP endpoints สำหรับ data retrieval และ monitoring
- ✅ **Unified Architecture**: ใช้ Flask + SocketIO ร่วมกัน
- ✅ **Comprehensive Endpoints**: ครอบคลุมการใช้งานหลักทั้งหมด


## การติดตั้ง (Installation)

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
### 1. Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum install python3 python3-pip nginx
```

### 2. Clone และ Setup
```bash
# Clone repository
git clone <repository-url>
cd lprserver_v3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copy environment configuration
cp env.example .env

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

# Edit configuration
nano .env
```

**Configuration Options:**
```bash
# Flask Configuration
FLASK_CONFIG=production
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False


# Database Configuration
DATABASE_URL=sqlite:///lprserver.db

# File Storage
IMAGE_STORAGE_PATH=storage/images

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

# Health Monitoring
HEALTH_CHECK_INTERVAL_MINUTES=5
DATA_RETENTION_DAYS=30
```

## การใช้งาน (Usage)

### Development Mode
```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python run.py
```

### Production Deployment
```bash
# Setup systemd services
sudo ./setup.sh

# Start services
sudo systemctl start lprserver
sudo systemctl start lprserver-websocket
sudo systemctl start nginx

# Enable auto-start
sudo systemctl enable lprserver
sudo systemctl enable lprserver-websocket
sudo systemctl enable nginx
```

## สถาปัตยกรรม (Architecture)

### Service Layer
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  WebSocket      │    │   Blacklist     │    │     Health      │
│   Service       │    │    Service      │    │    Service      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   Service       │
                    └─────────────────┘
```

### Web Interface
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main          │    │      API        │    │     Health      │
│  Blueprint      │    │   Blueprint     │    │   Blueprint     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Flask App     │
                    └─────────────────┘
```

## API Endpoints

### Main Routes (`/`)
- `GET /` - Dashboard
- `GET /records` - LPR Records
- `GET /cameras` - Camera Management

### API Routes (`/api`)
- `GET /api/records` - Get LPR records (with pagination)
- `POST /api/records` - Create new LPR record
- `GET /api/cameras` - Get camera list
- `POST /api/cameras` - Register new camera
- `GET /api/blacklist` - Get blacklist entries
- `POST /api/blacklist` - Add to blacklist
- `DELETE /api/blacklist/<id>` - Remove from blacklist

### Health Routes (`/health`)
- `GET /health/status` - System health status
- `POST /health/check` - Perform health check
- `GET /health/history` - Health check history
- `GET /health/database/stats` - Database statistics
- `POST /health/database/cleanup` - Clean old data
- `POST /health/database/optimize` - Optimize database

## WebSocket Events

### Camera Communication (Port 8765)
```javascript
// Connect to WebSocket server
const socket = io('ws://localhost:8765');

// Register camera
socket.emit('camera_register', {
    camera_id: 'CAM001'
});

// Send LPR data
socket.emit('lpr_data', {
    camera_id: 'CAM001',
    plate_number: 'กข1234',
    confidence: 0.95,
    image_data: 'base64_encoded_image',
    location_lat: 13.7563,
    location_lon: 100.5018
});
```

### Dashboard Updates
```javascript
// Join dashboard room
socket.emit('join_dashboard');

// Listen for updates
socket.on('new_lpr_record', (data) => {
    console.log('New LPR record:', data);
});

socket.on('blacklist_alert', (data) => {
    console.log('Blacklist alert:', data);
});

socket.on('health_update', (data) => {
    console.log('Health update:', data);
});
```

### Health Monitoring
```javascript
// Join health monitoring room
socket.emit('join_health_room');

// Request health check
socket.emit('request_health_check');

// Listen for health updates
socket.on('health_check_result', (data) => {
    console.log('Health check result:', data);
});
```

## Health Monitoring

### Real-time Monitoring
ระบบจะตรวจสอบสถานะทุก 5 นาที (ปรับได้ใน configuration):

1. **Database Connectivity** - ตรวจสอบการเชื่อมต่อฐานข้อมูล
2. **Disk Space** - ตรวจสอบพื้นที่จัดเก็บไฟล์
3. **System Resources** - ตรวจสอบ CPU และ Memory
4. **Camera Connectivity** - ตรวจสอบการเชื่อมต่อกล้อง
5. **Service Status** - ตรวจสอบสถานะ services

### Health Status Levels
- **PASS** - ระบบทำงานปกติ
- **WARNING** - มีปัญหาเล็กน้อย
- **FAIL** - มีปัญหาสำคัญ

### Monitoring Dashboard
```bash
# Check system status
curl http://localhost/health/status

# Perform health check
curl -X POST http://localhost/health/check

# Get health history
curl http://localhost/health/history?hours=24
```

## Database Management

### Automatic Cleanup
ระบบจะทำความสะอาดข้อมูลเก่าอัตโนมัติ:

```bash
# Clean old data (default: 30 days)
curl -X POST http://localhost/health/database/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'

# Optimize database
curl -X POST http://localhost/health/database/optimize

# Get database statistics
curl http://localhost/health/database/stats
```

### Manual Maintenance
```bash
# Backup database
cp lprserver.db backup/lprserver_$(date +%Y%m%d_%H%M%S).db

# Check database size
ls -lh lprserver.db

# View recent records
sqlite3 lprserver.db "SELECT * FROM lpr_records ORDER BY timestamp DESC LIMIT 10;"
```

## Logging

### Log Files
- **Application Logs**: `logs/lprserver.log`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `journalctl -u lprserver`

### Log Levels
- **DEBUG**: รายละเอียดสำหรับการพัฒนา
- **INFO**: ข้อมูลทั่วไป
- **WARNING**: คำเตือน
- **ERROR**: ข้อผิดพลาด

### Log Rotation
- ขนาดไฟล์สูงสุด: 10MB
- จำนวนไฟล์: 10 ไฟล์
- การหมุนเวียน: อัตโนมัติ

## Troubleshooting

### Common Issues

#### 1. WebSocket Connection Failed
```bash
# Check WebSocket service
sudo systemctl status lprserver-websocket

# Check port availability
netstat -tlnp | grep 8765

# Check firewall
sudo ufw status
```

#### 2. Database Connection Error
```bash
# Check database file
ls -la lprserver.db

# Check permissions
sudo chown www-data:www-data lprserver.db

# Recreate database
rm lprserver.db
python -c "from src.app import create_app; app = create_app(); app.app_context().push(); from src.app import db; db.create_all()"
```

#### 3. Health Check Failures
```bash
# Check system resources
htop
df -h

# Check service status
sudo systemctl status lprserver
sudo systemctl status nginx

# View health logs
tail -f logs/lprserver.log | grep health
```

### Performance Optimization

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

#### 1. Database Optimization
```bash
# Add indexes for better performance
sqlite3 lprserver.db "
CREATE INDEX IF NOT EXISTS idx_lpr_records_timestamp ON lpr_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_lpr_records_camera_id ON lpr_records(camera_id);
CREATE INDEX IF NOT EXISTS idx_lpr_records_plate_number ON lpr_records(plate_number);
"
```

#### 2. System Optimization
```bash
# Increase file descriptors
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize nginx
sudo nano /etc/nginx/nginx.conf
# Add: worker_connections 1024;
```

## Development

### Code Structure

```
src/
├── core/                    # Core functionality
│   ├── import_helper.py     # Absolute imports
│   ├── dependency_container.py  # DI container
│   └── models/              # Database models
├── services/                # Business logic
│   ├── websocket_service.py
│   ├── blacklist_service.py
│   ├── health_service.py
│   └── database_service.py
└── web/                     # Web interface
    └── blueprints/          # Flask blueprints
```

### Adding New Features

#### 1. New Service
```python
# src/services/new_service.py
from core.import_helper import setup_absolute_imports


#### ทดสอบระบบทั้งหมด
```bash
# ทดสอบระบบอัตโนมัติ
setup_absolute_imports()

class NewService:
    def __init__(self):
        self.db_session = None
    
    def initialize(self, db_session):
        self.db_session = db_session
```

#### 2. Register Service
```python
# src/core/dependency_container.py
def register_services():
    from services.new_service import NewService
    container.register('new_service', NewService)
```

#### 3. New Blueprint
```python
# src/web/blueprints/new_feature.py
from flask import Blueprint
from core.import_helper import setup_absolute_imports

setup_absolute_imports()

new_feature_bp = Blueprint('new_feature', __name__)

@new_feature_bp.route('/new-endpoint')
def new_endpoint():
    return {'message': 'New feature'}
```

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python test_system.py

# Test WebSocket connection
python test_client.py
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

## Security

### Best Practices
1. **Environment Variables**: ใช้ .env files สำหรับ sensitive data
2. **Input Validation**: ตรวจสอบข้อมูล input ทุกครั้ง
3. **SQL Injection Prevention**: ใช้ parameterized queries
4. **File Upload Security**: ตรวจสอบไฟล์ที่อัปโหลด
5. **HTTPS**: ใช้ SSL/TLS ใน production

### Firewall Configuration
```bash
# Allow HTTP and WebSocket
sudo ufw allow 80/tcp
sudo ufw allow 8765/tcp

# Allow SSH (if needed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

## Support

### Documentation
- **Development Guide**: `DEVELOPMENT_GUIDE.md`
- **Architecture Overview**: `ARCHITECTURE_OVERVIEW.md`
- **API Documentation**: ดูใน code comments

### Logs and Monitoring
- **Application Logs**: `logs/lprserver.log`
- **Health Status**: `http://localhost/health/status`
- **System Status**: `sudo systemctl status lprserver`

### Contact
สำหรับคำถามหรือปัญหาการใช้งาน กรุณาติดต่อทีมพัฒนา

