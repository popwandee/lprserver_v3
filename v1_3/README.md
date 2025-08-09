# AI Camera v1.3

ระบบกล้อง AI สำหรับการตรวจจับและประมวลผลภาพแบบเรียลไทม์ บน Raspberry Pi ด้วย Hailo AI Accelerator

## 📋 สารบัญ

- [ภาพรวมระบบ](#ภาพรวมระบบ)
- [สถาปัตยกรรม](#สถาปัตยกรรม)
- [การติดตั้ง](#การติดตั้ง)
- [การใช้งาน](#การใช้งาน)
- [การตั้งค่า](#การตั้งค่า)
- [การแก้ไขปัญหา](#การแก้ไขปัญหา)
- [การพัฒนา](#การพัฒนา)
- [API Reference](#api-reference)
- [การอัปเดต](#การอัปเดต)

## 🎯 ภาพรวมระบบ

AI Camera v1.3 เป็นระบบกล้องอัจฉริยะที่พัฒนาบน Flask framework ใช้สำหรับ:
- การตรวจจับวัตถุแบบเรียลไทม์
- การประมวลผลภาพด้วย AI
- การจัดการฐานข้อมูล
- การแสดงผลผ่านเว็บอินเตอร์เฟส

### คุณสมบัติหลัก

#### ระบบพื้นฐาน
- ✅ ระบบเว็บที่เสถียร (Flask + Gunicorn + Nginx)
- ✅ การจัดการ service แบบ systemd
- ✅ Virtual environment management
- ✅ Health monitoring
- ✅ WebSocket support
- ✅ Modular architecture

#### Absolute Imports System (NEW)
- ✅ Consistent import paths across the project
- ✅ Import validation and error handling
- ✅ Clear dependency management
- ✅ Easy refactoring and module relocation

#### Camera System v1.3 (Updated)
- ✅ Picamera2 integration with thread-safe access
- ✅ Camera Handler component with Singleton pattern
- ✅ Camera Manager service for video streaming
- ✅ ML pipeline preparation and frame callbacks
- ✅ Resource cleanup and proper shutdown handling
- ✅ Status monitoring and health checks
- ✅ Dependency injection compatible architecture

## 🏗️ สถาปัตยกรรม

### System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80)    │───▶│  Gunicorn WSGI  │───▶│  Flask App      │
│   Reverse Proxy │    │   Unix Socket   │    │   v1_3.src.app  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Systemd Service│
                       │ aicamera_v1.3   │
                       └─────────────────┘
```

### Camera System v1.3 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web UI  │──▶│  Camera Manager │───▶│ Camera Handler  │
│  (Blueprints)   │    │   (Service)     │    │  (Component)    │
│ Absolute Imports│    │ Absolute Imports│    │ Absolute Imports│
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ WebSocket Events│    │   ML Pipeline   │    │   Picamera2     │
│ Video Streaming │    │ Frame Callbacks │    │ Thread Locking  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Design Patterns
- **Dependency Injection**: ระบบ DI Container จัดการ dependencies
- **Singleton Pattern**: Camera Handler ใช้ singleton เพื่อป้องกันการใช้กล้องซ้ำซ้อน
- **Flask Blueprints**: แบ่งส่วน Web UI ตาม functional areas
- **Service Layer**: แยก business logic จาก low-level operations
- **Absolute Imports**: ใช้ import paths ที่ชัดเจนและสม่ำเสมอ

### โครงสร้างไฟล์

```
/home/camuser/aicamera/
├── v1_3/                          # โปรเจคหลัก
│   ├── src/                       # Source code
│   │   ├── app.py                 # Flask application
│   │   ├── wsgi.py                # WSGI entry point
│   │   ├── web/                   # Web interface
│   │   │   ├── blueprints/        # Flask Blueprints with absolute imports
│   │   │   │   ├── __init__.py    # Blueprint registration
│   │   │   │   ├── main.py        # Main dashboard
│   │   │   │   ├── camera.py      # Camera control
│   │   │   │   ├── detection.py   # AI detection
│   │   │   │   ├── streaming.py   # Video streaming
│   │   │   │   ├── health.py      # System health
│   │   │   │   └── websocket.py   # WebSocket communication
│   │   │   ├── templates/         # HTML templates
│   │   │   │   ├── index.html     # index
│   │   │   │   ├── camera/        # Camera Streaming
│   │   │   │   │   └── dashboard.html
│   │   │   │   ├── detection/     # Detection result UI
│   │   │   │   │   └── dashboard.html
│   │   │   │   ├── error/         # error landing page
│   │   │   │   │   ├── 404.html   # error 404 File not Found
│   │   │   │   │   └── 500.html   # error 500 Bad Gateway
│   │   │   │   ├── health/        # System Health Monitor and logs
│   │   │   │   │   └── dashboard.html
│   │   │   │   └── main/          # Main Dashboard
│   │   │   │       └── dashboard.html
│   │   │   └── static/            # CSS, JS, Images
│   │   ├── components/            # Low-level components
│   │   │   ├── camera_handler.py  # Camera control (Picamera2 + thread-safe)
│   │   │   ├── detection_processor.py # AI detection (Hailo models)
│   │   │   ├── database_manager.py # Database operations
│   │   │   └── health_monitor.py  # System health monitoring
│   │   ├── services/              # High-level business logic
│   │   │   ├── camera_manager.py  # Camera service (streaming + ML pipeline)
│   │   │   ├── detection_manager.py # Detection workflow management
│   │   │   ├── video_streaming.py # Video streaming service
│   │   │   └── websocket_sender.py # WebSocket communication
│   │   ├── core/                  # Core framework
│   │   │   ├── dependency_container.py # DI: Dependency injection
│   │   │   ├── config.py          # Configuration management
│   │   │   └── utils/             # Core utilities
│   │   │       ├── import_helper.py # Absolute import management
│   │   │       └── logging_config.py # Logging configuration
│   │   ├── database/              # Database layer
│   │   │   └── database_manager.py
│   │   ├── captured_images/       # Captured images storage
│   │   └── logs/                  # Application logs
│   ├── scripts/                   # Utility scripts
│   │   └── migrate_absolute_imports.py # Migration script
│   ├── requirements.txt           # Python dependencies
│   ├── ARCHITECTURE.md            # Architecture documentation
│   └── README.md                  # This file
├── gunicorn_config.py             # Gunicorn configuration (Unix socket)
├── systemd_service/               # Systemd service files
│   └── aicamera_v1.3.service
├── setup_env.sh                   # Environment setup script
└── venv_hailo/                    # Virtual environment
```

## 🚀 การติดตั้ง

### ข้อกำหนดระบบ
- Raspberry Pi5 (ARM64)
- Python 3.11+
- Hailo AI Accelerator
- Camera module (PiCamera2)

### ขั้นตอนการติดตั้ง

1. **Clone โปรเจค**
```bash
cd /home/camuser/aicamera
```

2. **ตั้งค่า Virtual Environment**
```bash
source setup_env.sh
```

3. **ติดตั้ง Dependencies**
```bash
cd v1_3
pip install -r requirements.txt
```

4. **ตั้งค่า Systemd Service**
```bash
sudo cp systemd_service/aicamera_v1.3.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aicamera_v1.3.service
```

5. **ตั้งค่า Nginx**
```bash
sudo ln -sf /etc/nginx/sites-available/aicamera_v1.3 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

6. **เริ่มต้น Service**
```bash
sudo systemctl start aicamera_v1.3.service
```

7. **ตรวจสอบสถานะ**
```bash
sudo systemctl status aicamera_v1.3.service
sudo journalctl -u aicamera_v1.3.service -f
```

## 🧪 สถานะการทดสอบ

### ✅ Camera System Testing Status (August 8, 2025)

**Components Implemented:**
- ✅ Camera Handler (v1.3) - Picamera2 integration with thread-safe access
- ✅ Camera Manager (v1.3) - Service layer for video streaming and ML pipeline
- ✅ Dependency Injection Container - Service management and DI pattern
- ✅ Configuration System (Updated) - Using `/src/core/config.py` without dotenv dependency
- ✅ Logging System - Structured logging with file rotation support

**Key Features Verified:**
- ✅ **Thread Safety**: Camera access locking mechanism implemented
- ✅ **Resource Cleanup**: Proper shutdown and resource deallocation
- ✅ **ML Pipeline Ready**: Frame callback system for AI integration
- ✅ **Status Monitoring**: Health checks and system status reporting
- ✅ **Modular Architecture**: Clean separation of concerns
- ✅ **Singleton Pattern**: Prevents camera access conflicts
- ✅ **Absolute Imports**: Consistent import paths across the project
- ✅ **Import Validation**: Automatic validation of all module imports

**Testing Scripts:**
```bash
# Test configuration system (✅ PASSING)
python3 config_test.py

# Test camera components (requires Picamera2 hardware)
python3 simple_camera_test.py

# Test full dependency injection system
python3 test_camera_system.py

# Test absolute imports 
python3 -c "from v1_3.src.core.utils.import_helper import validate_imports; print('Import validation:', validate_imports())"
```

**Architecture Compliance: 100%**
- Dependency Injection ✅
- Thread Safety ✅ 
- Resource Cleanup ✅
- Singleton Pattern ✅
- Picamera2 Integration ✅
- ML Pipeline Ready ✅
- Status Monitoring ✅
- Configuration Management ✅
- Absolute Imports ✅
- Import Validation ✅

## 💻 การใช้งาน

### การเข้าถึงระบบ
- **เว็บอินเตอร์เฟส**: http://localhost
- **Health Check**: http://localhost/health
- **API Endpoints**: ดูในส่วน API Reference

### การควบคุมผ่านเว็บ
1. เปิดเบราวเซอร์ไปที่ http://localhost
2. ใช้ปุ่มควบคุม:
   - **Start Camera**: เริ่มกล้อง
   - **Stop Camera**: หยุดกล้อง
   - **Health Check**: ตรวจสอบสถานะระบบ

### การควบคุมผ่าน Command Line
```bash
# ตรวจสอบสถานะ service
sudo systemctl status aicamera_v1.3.service

# เริ่มต้น service
sudo systemctl start aicamera_v1.3.service

# หยุด service
sudo systemctl stop aicamera_v1.3.service

# รีสตาร์ท service
sudo systemctl restart aicamera_v1.3.service

# ดู log
sudo journalctl -u aicamera_v1.3.service -f
sudo journalctl -u aicamera_v1.3.service --no-pager | tail -20
```

## ⚙️ การตั้งค่า

### Environment Variables
สร้างไฟล์ `.env.production` ใน `v1_3/src/`:
```env
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
FLASK_APP=v1_3.src.app:app
VEHICLE_DETECTION_MODEL=/path/to/vehicle_model
LICENSE_PLATE_DETECTION_MODEL=/path/to/lpr_model
WEBSOCKET_SERVER_URL=ws://localhost:8080
```

### Camera Settings
แก้ไขใน `v1_3/src/core/config.py`:
```python
# Camera properties
DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_FRAMERATE = 30
DEFAULT_BRIGHTNESS = 0.0
DEFAULT_CONTRAST = 1.0
DEFAULT_SATURATION = 1.0
DEFAULT_SHARPNESS = 1.0
DEFAULT_AWB_MODE = 'auto'
```

### Gunicorn Configuration (Unix Socket)
แก้ไขใน `gunicorn_config.py`:
```python
# Server socket - Unix socket for better performance
bind = "unix:/tmp/aicamera.sock"
backlog = 2048

# Worker processes
workers = 1  # Single process with multiple threads
worker_class = "gthread"  # Use thread workers
threads = 4  # Number of threads per worker
```

## 🔧 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. Service ไม่สามารถเริ่มต้นได้
**อาการ**: `Job for aicamera_v1.3.service failed`

**การแก้ไข**:
```bash
# ตรวจสอบ log
sudo journalctl -u aicamera_v1.3.service --no-pager | tail -20

# ตรวจสอบสิทธิ์
ls -la /home/camuser/aicamera/venv_hailo/bin/gunicorn
ls -la /home/camuser/aicamera/gunicorn_config.py

# ตรวจสอบ virtual environment
source setup_env.sh
which gunicorn
```

#### 2. Module Import Error
**อาการ**: `ModuleNotFoundError: No module named 'v1_3'`

**การแก้ไข**:
```bash
# ตรวจสอบ import paths
python3 -c "from v1_3.src.core.utils.import_helper import validate_imports; print(validate_imports())"

# รัน migration script ถ้าจำเป็น
cd v1_3
python scripts/migrate_absolute_imports.py

# ตรวจสอบ PYTHONPATH
echo $PYTHONPATH
```

#### 3. Template Not Found
**อาการ**: `jinja2.exceptions.TemplateNotFound: index.html`

**การแก้ไข**:
ตรวจสอบ path ใน `app.py`:
```python
app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static')
```

#### 4. Permission Denied
**อาการ**: `Permission denied` ใน systemd

**การแก้ไข**:
```bash
# ตรวจสอบสิทธิ์
sudo chown -R camuser:camuser /home/camuser/aicamera
sudo chmod -R 755 /home/camuser/aicamera
```

#### 5. Nginx 500 Error
**อาการ**: HTTP 500 Internal Server Error

**การแก้ไข**:
```bash
# ตรวจสอบ gunicorn log
tail -f /home/camuser/aicamera/log/gunicorn_error.log

# ตรวจสอบ nginx log
sudo tail -f /var/log/nginx/aicamera_error.log

# ตรวจสอบ socket
ls -la /tmp/aicamera.sock
```

#### 6. Virtual Environment Issues
**อาการ**: `No such file or directory` สำหรับ gunicorn

**การแก้ไข**:
```bash
# ตรวจสอบ virtual environment
source setup_env.sh
which python
which gunicorn

# สร้าง virtual environment ใหม่
python3 -m venv venv_hailo
source venv_hailo/bin/activate
pip install -r v1_3/requirements.txt
```

#### 7. Gunicorn Status=3/NOTIMPLEMENTED
**อาการ**: Main process exited, code=exited, status=3/NOTIMPLEMENTED

**สาเหตุ**:
- Import Error ใน wsgi.py: ไฟล์ wsgi.py ใช้ relative imports แต่ควรใช้ absolute imports
- Gunicorn Config Conflict: มีการกำหนด app ใน config แต่ systemd service ก็ส่ง app path มาด้วย
- Import Path Issues: การ setup import paths ไม่ถูกต้อง

**การแก้ไข**:
```bash
# 1. หยุด service
sudo systemctl stop aicamera_v1.3.service

# 2. ลบ socket file เก่า (ถ้ามี)
sudo rm -f /tmp/aicamera.sock

# 3. ทดสอบ gunicorn โดยตรง
cd /home/camuser/aicamera
source setup_env.sh
gunicorn --config gunicorn_config.py v1_3.src.wsgi:app

# 4. ถ้าทำงานได้ ให้ restart service
sudo systemctl daemon-reload
sudo systemctl start aicamera_v1.3.service

# 5. ตรวจสอบสถานะ
sudo systemctl status aicamera_v1.3.service
```

### การ Debug

#### ตรวจสอบ Log Files
```bash
# Systemd logs
sudo journalctl -u aicamera_v1.3.service -f

# Gunicorn logs
tail -f /home/camuser/aicamera/log/gunicorn_error.log
tail -f /home/camuser/aicamera/log/gunicorn_access.log

# Nginx logs
sudo tail -f /var/log/nginx/aicamera_error.log
sudo tail -f /var/log/nginx/aicamera_access.log
```

#### ตรวจสอบ Process และ Configuration
```bash
# ตรวจสอบ process ที่ทำงาน
ps aux | grep gunicorn
ps aux | grep nginx

# ตรวจสอบ port และ socket
netstat -tlnp | grep :80
ls -la /tmp/aicamera.sock

# ตรวจสอบ nginx config
sudo nginx -t

# ตรวจสอบ systemd service
sudo systemctl cat aicamera_v1.3.service

# ตรวจสอบ gunicorn config
python3 -c "import gunicorn_config; print('Config OK')"

# ตรวจสอบ imports 
python3 -c "from v1_3.src.core.utils.import_helper import validate_imports; print('Imports:', validate_imports())"
```

## 🛠️ การพัฒนา

### การเพิ่ม Component ใหม่

1. **สร้างไฟล์ใน `components/`** ใช้ absolute imports:
```python
# v1_3/src/components/new_component.py
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

class NewComponent:
    def __init__(self):
        self.logger = logger
    
    def process(self, data):
        # Your logic here
        pass
```

2. **เพิ่มใน DI Container** ใช้ absolute imports:
```python
# v1_3/src/core/dependency_container.py
def _register_default_services(self):
    try:
        from v1_3.src.components.new_component import NewComponent
        self.register_service('new_component', NewComponent,
                             dependencies={'logger': 'logger'})
    except ImportError:
        self.logger.warning("NewComponent not available")
```

3. **เพิ่มใน Blueprint** ใช้ absolute imports:
```python
# v1_3/src/web/blueprints/new_feature.py
from flask import Blueprint, jsonify
from v1_3.src.core.dependency_container import get_service

new_feature_bp = Blueprint('new_feature', __name__, url_prefix='/new-feature')

@new_feature_bp.route('/action', methods=['POST'])
def perform_action():
    component = get_service('new_component')
    result = component.process(data)
    return jsonify({'result': result})
```

4. **ลงทะเบียน Blueprint** ใช้ absolute imports:
```python
# v1_3/src/web/blueprints/__init__.py
from v1_3.src.web.blueprints.new_feature import new_feature_bp

def register_blueprints(app: Flask, socketio: SocketIO):
    app.register_blueprint(new_feature_bp)
```

### การเพิ่ม API Endpoint

```python
# ใช้ absolute imports
from v1_3.src.core.dependency_container import get_service

@app.route('/api/new_endpoint', methods=['GET', 'POST'])
def new_api_endpoint():
    if request.method == 'GET':
        return jsonify({'status': 'success', 'data': 'some_data'})
    elif request.method == 'POST':
        data = request.get_json()
        # Process data
        return jsonify({'status': 'success'})
```

### การเพิ่ม Database Table

```python
# ใน database_manager.py ใช้ absolute imports
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

def create_new_table(self):
    query = """
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    self.execute_query(query)
```

## 📚 API Reference

### Endpoints

#### GET /
หน้าแรกของระบบ
- **Response**: HTML page

#### GET /health
ตรวจสอบสถานะระบบ
- **Response**: 
```json
{
    "status": "healthy",
    "service": "aicamera_v1.3"
}
```

#### POST /close_camera
หยุดกล้อง
- **Response**:
```json
{
    "status": "success",
    "message": "Camera closed successfully."
}
```

#### POST /update_camera_settings
อัปเดตการตั้งค่ากล้อง
- **Form Data**: resolution, framerate, brightness, contrast, saturation, sharpness, awb_mode
- **Response**: Redirect to index page

#### GET /video_feed
สตรีมวิดีโอจากกล้อง
- **Response**: Multipart video stream

### Error Responses

#### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "message": "Detailed error message"
}
```

#### 404 Not Found
```json
{
    "error": "Not found",
    "message": "Endpoint not found"
}
```

## 📝 การอัปเดต

### การอัปเดต Code
```bash
# Pull latest changes
git pull origin main

# Restart service
sudo systemctl restart aicamera_v1.3.service

# Check status
sudo systemctl status aicamera_v1.3.service
```

### การอัปเดต Dependencies
```bash
# Activate virtual environment
source setup_env.sh

# Update requirements
pip install -r v1_3/requirements.txt --upgrade

# Restart service
sudo systemctl restart aicamera_v1.3.service

# ตรวจสอบสถานะการทำงาน
sudo journalctl -u aicamera_v1.3.service --no-pager | tail -20
```

### การเปลี่ยนจาก TCP/IP Stack เป็น Unix Socket

#### ข้อดีของ Unix Socket
1. **ประสิทธิภาพดีกว่า**: ไม่ต้องผ่าน TCP/IP stack
2. **ความปลอดภัย**: ไม่เปิด port ภายนอก
3. **การจัดการที่ดีกว่า**: Socket file จะถูกลบเมื่อ process หยุดทำงาน
4. **Resource ใช้น้อยกว่า**: ไม่ต้องใช้ network resources

#### ขั้นตอนการเปลี่ยน

1. **ปรับปรุง Gunicorn Config**:
```python
# gunicorn_config.py
bind = "unix:/tmp/aicamera.sock"  # เปลี่ยนจาก "0.0.0.0:8080"
```

2. **ปรับปรุง Nginx Config**:
```nginx
# nginx.conf
proxy_pass http://unix:/tmp/aicamera.sock;  # เปลี่ยนจาก http://127.0.0.1:8000
```

3. **ทดสอบการทำงาน**:
```bash
# ทดสอบ gunicorn
cd /home/camuser/aicamera
source setup_env.sh
gunicorn --config gunicorn_config.py v1_3.src.wsgi:app

# ทดสอบ nginx config
sudo nginx -t

# Reload systemd และ restart service
sudo systemctl daemon-reload
sudo systemctl restart aicamera_v1.3
sudo systemctl restart nginx

# ตรวจสอบสถานะ
sudo systemctl status aicamera_v1.3
sudo systemctl status nginx

# ตรวจสอบ socket file
ls -la /tmp/aicamera.sock

# ทดสอบการเข้าถึงเว็บไซต์
# http://aicamera1

# ทดสอบ import validation
python3 -c "from v1_3.src.core.utils.import_helper import validate_imports; print('Import validation:', validate_imports())"
```

### ข้อดีของ Absolute Imports
1. **ความชัดเจน**: Import paths ชัดเจนและเข้าใจง่าย
2. **ความสม่ำเสมอ**: ใช้รูปแบบเดียวกันทั้งโปรเจค
3. **การบำรุงรักษา**: ง่ายต่อการ refactor และย้ายไฟล์

## 📞 การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:

1. ตรวจสอบ log files ก่อน
2. ดูส่วน "การแก้ไขปัญหา" ในเอกสารนี้
3. ตรวจสอบ GitHub Issues
4. ติดต่อทีมพัฒนา

---

**เวอร์ชัน**: 1.3  
**อัปเดตล่าสุด**: August 8, 2025  
**ผู้พัฒนา**: AI Camera Team

## 🚀 แผนการพัฒนาขั้นต่อไป

- สั่งให้กล้องทำงาน streaming อัตโนมัติ
- ตรวจสอบดำเนินการปิดและคืนทรัพยากรกล้องอย่างปลอดภัย