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

## 🎯 ภาพรวมระบบ

AI Camera v1.3 เป็นระบบกล้องอัจฉริยะที่พัฒนาบน Flask framework ใช้สำหรับ:
- การตรวจจับวัตถุแบบเรียลไทม์
- การประมวลผลภาพด้วย AI
- การจัดการฐานข้อมูล
- การแสดงผลผ่านเว็บอินเตอร์เฟส

### คุณสมบัติหลัก
- ✅ ระบบเว็บที่เสถียร (Flask + Gunicorn + Nginx)
- ✅ การจัดการ service แบบ systemd
- ✅ Virtual environment management
- ✅ Health monitoring
- ✅ WebSocket support
- ✅ Modular architecture

## 🏗️ สถาปัตยกรรม

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

### โครงสร้างไฟล์
```
/home/camuser/aicamera/
├── v1_3/                          # โปรเจคหลัก
│   ├── src/                       # Source code
│   │   ├── app.py                 # Flask application
│   │   ├── config.py              # Configuration settings
│   │   ├── web/                   # Web interface
│   │   │   ├── templates/         # HTML templates
│   │   │   └── static/            # CSS, JS, Images
│   │   ├── components/            # AI components
│   │   │   ├── camera_handler.py  # Camera management
│   │   │   ├── detection_processor.py # AI detection
│   │   │   └── health_monitor.py  # System monitoring
│   │   ├── database/              # Database layer
│   │   │   └── database_manager.py
│   │   └── utils/                 # Utility functions
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # This file
├── gunicorn_config.py             # Gunicorn configuration
├── systemd_service/               # Systemd service files
│   └── aicamera_v1.3.service
├── setup_env.sh                   # Environment setup script
└── venv_hailo/                    # Virtual environment
```

## 🚀 การติดตั้ง

### ข้อกำหนดระบบ
- Raspberry Pi (ARM64)
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
แก้ไขใน `v1_3/src/config.py`:
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

### Gunicorn Configuration
แก้ไขใน `gunicorn_config.py`:
```python
# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
bind = "unix:/tmp/aicamera.sock"
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
**อาการ**: `ModuleNotFoundError: No module named 'v1'`

**การแก้ไข**:
- ตรวจสอบว่า directory ชื่อ `v1_3` ไม่ใช่ `v1.3`
- ตรวจสอบ `__init__.py` files ในทุก directory
- ใช้ relative imports ในไฟล์ Python

#### 3. Template Not Found
**อาการ**: `jinja2.exceptions.TemplateNotFound: index.html`

**การแก้ไข**:
- ตรวจสอบ path ใน `app.py`:
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

# ลบ security restrictions ใน systemd service
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

### การ Debug

#### 1. ตรวจสอบ Log Files
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

#### 2. ตรวจสอบ Process
```bash
# ตรวจสอบ process ที่ทำงาน
ps aux | grep gunicorn
ps aux | grep nginx

# ตรวจสอบ port และ socket
netstat -tlnp | grep :80
ls -la /tmp/aicamera.sock
```

#### 3. ตรวจสอบ Configuration
```bash
# ตรวจสอบ nginx config
sudo nginx -t

# ตรวจสอบ systemd service
sudo systemctl cat aicamera_v1.3.service

# ตรวจสอบ gunicorn config
python3 -c "import gunicorn_config; print('Config OK')"
```

## 🛠️ การพัฒนา

### การเพิ่ม Component ใหม่

1. **สร้างไฟล์ใน `components/`**
```python
# v1_3/src/components/new_component.py
import logging
from ..config import CONFIG_VARIABLE

logger = logging.getLogger(__name__)

class NewComponent:
    def __init__(self):
        self.logger = logger
    
    def process(self, data):
        # Your logic here
        pass
```

2. **เพิ่มใน `app.py`**
```python
from .components.new_component import NewComponent

# Initialize component
new_component = NewComponent()

# Use in route
@app.route('/new_endpoint')
def new_endpoint():
    result = new_component.process(data)
    return jsonify(result)
```

### การเพิ่ม API Endpoint

```python
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
# ใน database_manager.py
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
```

## 📞 การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:

1. ตรวจสอบ log files ก่อน
2. ดูส่วน "การแก้ไขปัญหา" ในเอกสารนี้
3. ตรวจสอบ GitHub Issues
4. ติดต่อทีมพัฒนา

---

**เวอร์ชัน**: 1.3  
**อัปเดตล่าสุด**: August 7, 2025  
**ผู้พัฒนา**: AI Camera Team
