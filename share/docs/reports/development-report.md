# LPR Server v3 - รายงานการพัฒนา
## License Plate Recognition System

---

## สารบัญ
1. [แนวคิดในการออกแบบสถาปัตยกรรม](#แนวคิดในการออกแบบสถาปัตยกรรม)
2. [โครงสร้างระบบ](#โครงสร้างระบบ)
3. [องค์ประกอบที่สำคัญในระบบ](#องค์ประกอบที่สำคัญในระบบ)
4. [การพัฒนาระบบ](#การพัฒนาระบบ)
5. [คำแนะนำและคู่มือในการใช้งาน](#คำแนะนำและคู่มือในการใช้งาน)
6. [คำแนะนำและคู่มือในการพัฒนาต่อยอด](#คำแนะนำและคู่มือในการพัฒนาต่อยอด)
7. [การบำรุงรักษา](#การบำรุงรักษา)
8. [อื่น ๆ ที่เกี่ยวข้องเพิ่มเติม](#อื่น-ๆ-ที่เกี่ยวข้องเพิ่มเติม)

---

## แนวคิดในการออกแบบสถาปัตยกรรม

### 1.1 หลักการออกแบบ (Design Principles)

#### 1.1.1 Modular & Scalable Architecture
- **แนวคิด**: ระบบถูกออกแบบให้เป็นโมดูลอิสระ สามารถขยายและบำรุงรักษาได้ง่าย
- **ประโยชน์**: 
  - ง่ายต่อการอัปเกรดและบำรุงรักษา
  - รองรับการขยายฟีเจอร์ใหม่
  - แยกความรับผิดชอบของแต่ละส่วน

#### 1.1.2 Edge-to-Cloud Architecture
- **แนวคิด**: ข้อมูลถูกประมวลผลที่ Edge (กล้อง) และส่งไปยัง Cloud (เซิร์ฟเวอร์)
- **Flow**: Camera → Preprocessing → OCR Engine → Database
- **ประโยชน์**:
  - ลดภาระของเซิร์ฟเวอร์
  - ประมวลผลแบบ Real-time
  - รองรับการทำงานแบบ Offline

#### 1.1.3 Microservice-inspired UI
- **แนวคิด**: UI แสดงแต่ละฟังก์ชันเป็น Service Block แยกกัน
- **ประโยชน์**:
  - ง่ายต่อการเข้าใจและใช้งาน
  - แสดงสถานะของแต่ละส่วนได้ชัดเจน
  - เหมาะสำหรับ Edge Computing

### 1.2 สถาปัตยกรรมระบบ (System Architecture)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Edge Camera   │    │  WebSocket      │    │   Flask App     │
│                 │    │  Server         │    │                 │
│ • Image Capture │───▶│ • Real-time     │───▶│ • API Endpoints │
│ • OCR Processing│    │   Communication │    │ • Web Interface │
│ • Data Send     │    │ • Data Relay    │    │ • Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Nginx Proxy   │    │   SQLite DB     │
                       │                 │    │                 │
                       │ • Load Balancer │    │ • LPR Records   │
                       │ • Static Files  │    │ • Camera Info   │
                       │ • SSL/TLS       │    │ • System Logs   │
                       └─────────────────┘    └─────────────────┘
```

### 1.3 Theme Design Philosophy

#### 1.3.1 Dark Mode + Neon Accents
- **สีหลัก**: Soft Neutrals (#F4F6F8, #ECECEC)
- **สีเน้น**: Gentle Accents (#A3D9A5, #FCE38A, #F38181)
- **ประโยชน์**: 
  - อ่านง่ายในห้องควบคุม
  - ให้ความรู้สึกทันสมัย
  - ลดความเมื่อยล้าของสายตา

#### 1.3.2 Minimalist + Data-Centric UI
- **แนวคิด**: เน้นข้อมูลและผลลัพธ์เป็นหลัก
- **Typography**: Inter, Roboto Mono
- **Layout**: Grid-based, Responsive Design

---

## โครงสร้างระบบ

### 2.1 โครงสร้างไฟล์ (File Structure)

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
│   │   ├── index.html             # AI Camera overview
│   │   ├── cameras.html           # Camera management
│   │   └── camera_settings.html   # Camera settings
│   ├── detection/                 # Detection templates
│   │   ├── index.html             # Detection overview
│   │   ├── records.html           # Detection records
│   │   ├── statistics.html        # Detection statistics
│   │   └── alerts.html            # Detection alerts
│   ├── map/                       # Map templates
│   ├── system/                    # System templates
│   ├── user/                      # User templates
│   └── report/                    # Report templates
├── storage/                       # File storage
│   └── images/                    # LPR images
├── logs/                          # Application logs
├── database/                      # Database files
├── nginx/                         # Nginx configuration
│   └── lprserver.conf             # Nginx config
├── config.py                      # Application configuration
├── requirements.txt               # Python dependencies
├── run.py                         # Development server
├── wsgi.py                        # Production WSGI entry
├── websocket_server.py            # WebSocket server
├── setup.sh                       # Setup script
├── test_client.py                 # WebSocket test client
├── test_system.py                 # System test script
├── lprserver.service              # Main service
├── lprserver-websocket.service    # WebSocket service
├── .gitignore                     # Git ignore file
├── README.md                      # Documentation
├── DEVELOPMENT_GUIDE.md           # Development guide
├── DEVELOPMENT_REPORT.md          # This file
└── coding_rule.md                 # Original requirements
```

### 2.2 โครงสร้างฐานข้อมูล (Database Schema)

#### 2.2.1 ตารางหลัก
- **lpr_records**: บันทึกการตรวจจับป้ายทะเบียน
- **cameras**: ข้อมูลกล้อง
- **blacklist_plates**: รายการรถที่ถูกแบน
- **health_checks**: บันทึกการตรวจสอบสถานะระบบ

#### 2.2.2 Models ที่ใช้
- **LPRRecord**: จัดการข้อมูลการตรวจจับป้ายทะเบียน
- **Camera**: จัดการข้อมูลกล้อง
- **BlacklistPlate**: จัดการข้อมูล blacklist
- **HealthCheck**: จัดการข้อมูลการตรวจสอบสถานะระบบ

### 2.3 โครงสร้าง Blueprint

#### 2.3.1 Main Routes (`/`)
- **หน้าที่**: หน้าแรกและแดชบอร์ดหลัก
- **Routes**:
  - `/` - หน้าแรก
  - `/dashboard` - แดชบอร์ด
  - `/records` - รายการบันทึก
  - `/blacklist` - จัดการ blacklist

#### 2.3.2 API Routes (`/api`)
- **หน้าที่**: REST API สำหรับการเข้าถึงข้อมูล
- **Routes**:
  - `GET /api/records` - ดึงรายการบันทึก LPR (พร้อม pagination และ filtering)
  - `GET /api/records/<id>` - ดึงบันทึก LPR เฉพาะ
  - `POST /api/records` - สร้างบันทึก LPR ใหม่
  - `GET /api/statistics` - ดึงสถิติระบบ
  - `GET /api/blacklist` - ดึงรายการ blacklist
  - `POST /api/blacklist` - เพิ่มป้ายทะเบียนใน blacklist
  - `DELETE /api/blacklist/<id>` - ลบป้ายทะเบียนจาก blacklist
  - `GET /api/blacklist/statistics` - ดึงสถิติ blacklist
  - `GET /api/blacklist/detections` - ดึงการตรวจจับ blacklist

#### 2.3.3 AI Camera Manager (`/aicamera`)
- **หน้าที่**: จัดการกล้อง AI และการเชื่อมต่อ
- **Routes**:
  - `/` - ภาพรวม
  - `/cameras` - จัดการกล้อง
  - `/cameras/<id>/settings` - ตั้งค่ากล้อง

#### 2.3.4 Detection Manager (`/detection`)
- **หน้าที่**: จัดการข้อมูลการตรวจจับ
- **Routes**:
  - `/` - ภาพรวม
  - `/records` - รายการบันทึก
  - `/statistics` - สถิติ
  - `/alerts` - การแจ้งเตือน

#### 2.3.5 Map Manager (`/map`)
- **หน้าที่**: ติดตามรถและวิเคราะห์เส้นทาง
- **Routes**:
  - `/` - ภาพรวม
  - `/tracking` - ติดตามรถ
  - `/analytics` - วิเคราะห์
  - `/locations` - จัดการตำแหน่ง

#### 2.3.6 System Manager (`/system`)
- **หน้าที่**: จัดการระบบและตรวจสอบสถานะ
- **Routes**:
  - `/` - ภาพรวม
  - `/logs` - System Logs
  - `/monitoring` - Monitoring
  - `/health` - Health Check

#### 2.3.7 User Manager (`/user`)
- **หน้าที่**: จัดการผู้ใช้และสิทธิ์
- **Routes**:
  - `/` - ภาพรวม
  - `/login` - เข้าสู่ระบบ
  - `/profile` - โปรไฟล์
  - `/users` - จัดการผู้ใช้

#### 2.3.8 Report Manager (`/report`)
- **หน้าที่**: สร้างและจัดการรายงาน
- **Routes**:
  - `/` - ภาพรวม
  - `/generator` - สร้างรายงาน
  - `/templates` - เทมเพลต
  - `/scheduled` - รายงานที่กำหนดเวลา

#### 2.3.9 Health Manager (`/health`)
- **หน้าที่**: ตรวจสอบสถานะระบบ
- **Routes**:
  - `/` - ภาพรวมสถานะ
  - `/check` - ตรวจสอบสถานะ
  - `/logs` - บันทึกการตรวจสอบ

---

## องค์ประกอบที่สำคัญในระบบ

### 3.1 Core Components

#### 3.1.1 Flask Application Factory
```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(aicamera_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(health_bp)
    
    return app
```

#### 3.1.2 WebSocket Server
- **Port**: 8765
- **Protocol**: Socket.IO
- **Features**: Real-time communication with Edge Cameras

#### 3.1.3 Nginx Configuration
- **Reverse Proxy**: Port 80 → Unix Socket
- **Static Files**: Images, CSS, JS
- **SSL/TLS**: Ready for HTTPS

### 3.2 Systemd Services

#### 3.2.1 lprserver.service
```ini
[Unit]
Description=LPR Server v3 - Main Flask Application
After=network.target

[Service]
Type=notify
User=devuser
WorkingDirectory=/home/devuser/lprserver_v3
Environment=PATH=/home/devuser/lprserver_v3/venv/bin
Environment=FLASK_CONFIG=production
Environment=PYTHONPATH=/home/devuser/lprserver_v3:/home/devuser/lprserver_v3/src
ExecStart=/home/devuser/lprserver_v3/venv/bin/gunicorn --workers 4 --bind unix:/tmp/lprserver.sock wsgi:app

[Install]
WantedBy=multi-user.target
```

#### 3.2.2 lprserver-websocket.service
```ini
[Unit]
Description=LPR Server v3 - WebSocket Server
After=network.target

[Service]
Type=simple
User=devuser
WorkingDirectory=/home/devuser/lprserver_v3
Environment=PATH=/home/devuser/lprserver_v3/venv/bin
Environment=FLASK_CONFIG=production
Environment=PYTHONPATH=/home/devuser/lprserver_v3:/home/devuser/lprserver_v3/src
ExecStart=/home/devuser/lprserver_v3/venv/bin/python websocket_server.py

[Install]
WantedBy=multi-user.target
```

### 3.3 Frontend Components

#### 3.3.1 Base Template (base.html)
- **Responsive Design**: Bootstrap 5
- **Dark Mode**: CSS Variables + JavaScript Toggle
- **Navigation**: Dropdown menus for each module
- **Global Functions**: Loading, Alerts, Theme Toggle

#### 3.3.2 Data-Centric UI Components
- **Module Cards**: แสดงสถานะของแต่ละโมดูล
- **Flow Diagrams**: แสดง Edge-to-Cloud Architecture
- **Status Indicators**: สีเขียว/เหลือง/แดง
- **Metric Cards**: แสดงข้อมูลสถิติ

---

## การพัฒนาระบบ

### 4.1 Development Environment

#### 4.1.1 Prerequisites
```bash
# Python 3.8+
# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt
```

#### 4.1.2 Key Dependencies
```
Flask==2.3.3
Flask-SocketIO==5.3.6
SQLAlchemy==2.0.21
gunicorn==21.2.0
python-socketio==5.8.0
```

### 4.2 Development Workflow

#### 4.2.1 Blueprint Development
1. สร้าง Blueprint file ใน `src/web/blueprints/`
2. กำหนด Routes และ API endpoints
3. สร้าง Templates ใน `templates/<blueprint_name>/`
4. Register Blueprint ใน `src/app.py`

#### 4.2.2 Template Development
1. Extend `base.html`
2. ใช้ CSS Variables สำหรับ Theme
3. Implement Responsive Design
4. Add JavaScript for interactivity

### 4.3 Testing Strategy

#### 4.3.1 Unit Testing
- Test individual Blueprint functions
- Mock external dependencies
- Test API endpoints

#### 4.3.2 Integration Testing
- Test WebSocket communication
- Test database operations
- Test systemd services

#### 4.3.3 UI Testing
- Test responsive design
- Test Dark Mode toggle
- Test form submissions

#### 4.3.4 System Testing
- **test_system.py** - ทดสอบระบบทั้งหมด
  - Web Interface Testing
  - API Endpoints Testing
  - WebSocket Communication Testing
  - Database Operations Testing
  - Performance Testing

#### 4.3.5 Manual Testing
- การทดสอบการเพิ่มข้อมูล blacklist
- การทดสอบการตรวจจับป้ายทะเบียนที่อยู่ใน blacklist
- การทดสอบการอัปเดตสถิติการตรวจจับ
- การทดสอบ WebSocket connections
- การทดสอบ API responses

---

## คำแนะนำและคู่มือในการใช้งาน

### 5.1 การเข้าถึงระบบ

#### 5.1.1 Web Interface
- **URL**: http://localhost หรือ http://your-server-ip
- **Port**: 80 (HTTP) หรือ 5000 (Development)
- **Browser**: Chrome, Firefox, Safari, Edge

#### 5.1.2 API Endpoints
- **Base URL**: http://localhost/api หรือ http://your-server-ip/api
- **Authentication**: ไม่จำเป็น (สำหรับการทดสอบ)

#### 5.1.3 WebSocket Server
- **URL**: ws://localhost:8765 หรือ ws://your-server-ip:8765
- **Protocol**: Socket.IO v4

#### 5.1.4 Demo Credentials
- **Admin**: admin / admin123
- **User**: user / user123

### 5.2 การใช้งานโมดูลต่างๆ

#### 5.2.1 Main Routes (`/`)
1. **หน้าแรก**: ภาพรวมระบบและสถิติ
2. **แดชบอร์ด**: แสดงสถิติแบบ real-time
3. **รายการบันทึก**: ดูข้อมูลการตรวจจับ LPR
4. **จัดการ Blacklist**: เพิ่ม/ลบ/ดูรายการ blacklist

#### 5.2.2 API Routes (`/api`)
1. **Records API**: จัดการข้อมูลการตรวจจับ LPR
2. **Blacklist API**: จัดการรายการ blacklist
3. **Statistics API**: ดึงสถิติระบบ

#### 5.2.3 AI Camera Manager (`/aicamera`)
1. **ภาพรวม**: ดูสถานะกล้องทั้งหมด
2. **จัดการกล้อง**: เพิ่ม/แก้ไข/ลบกล้อง
3. **ตั้งค่า**: ปรับความละเอียด, FPS, ความไว

#### 5.2.4 Detection Manager (`/detection`)
1. **ภาพรวม**: สถิติการตรวจจับ
2. **รายการบันทึก**: ดูข้อมูลการตรวจจับ
3. **สถิติ**: กราฟและแผนภูมิ
4. **การแจ้งเตือน**: ระบบแจ้งเตือนอัตโนมัติ

#### 5.2.5 Map Manager (`/map`)
1. **ติดตามรถ**: ค้นหาและติดตามรถ
2. **วิเคราะห์**: วิเคราะห์เส้นทางและพฤติกรรม
3. **จัดการตำแหน่ง**: กำหนดจุดกล้อง

#### 5.2.6 System Manager (`/system`)
1. **System Logs**: ดูบันทึกระบบ
2. **Monitoring**: ตรวจสอบสถานะ
3. **Health Check**: ตรวจสอบสุขภาพระบบ

#### 5.2.7 User Manager (`/user`)
1. **เข้าสู่ระบบ**: Authentication
2. **โปรไฟล์**: จัดการข้อมูลส่วนตัว
3. **จัดการผู้ใช้**: สำหรับ Admin

#### 5.2.8 Report Manager (`/report`)
1. **สร้างรายงาน**: เลือกประเภทและช่วงเวลา
2. **เทมเพลต**: บันทึกและใช้เทมเพลต
3. **ประวัติ**: ดูรายงานที่สร้างไว้

#### 5.2.9 Health Manager (`/health`)
1. **ภาพรวมสถานะ**: ดูสถานะระบบทั้งหมด
2. **ตรวจสอบสถานะ**: ตรวจสอบสถานะแบบ manual
3. **บันทึกการตรวจสอบ**: ดูประวัติการตรวจสอบ

### 5.3 การตั้งค่าขั้นสูง

#### 5.3.1 Dark Mode
- คลิกปุ่ม Theme Toggle (มุมขวาบน)
- การตั้งค่าจะถูกบันทึกใน Local Storage

#### 5.3.2 การกรองข้อมูล
- ใช้ตัวกรองในแต่ละหน้า
- สามารถส่งออกข้อมูลได้
- รองรับการกรองตาม Camera ID, ป้ายทะเบียน, วันที่

#### 5.3.3 การแจ้งเตือน
- ระบบจะแจ้งเตือนอัตโนมัติเมื่อพบป้ายทะเบียนที่อยู่ใน blacklist
- สามารถตั้งค่าระดับการแจ้งเตือนได้

#### 5.3.4 Real-time Updates
- WebSocket connection สำหรับข้อมูลแบบ real-time
- อัปเดตสถิติอัตโนมัติ
- การแจ้งเตือนแบบ real-time

---

## คำแนะนำและคู่มือในการพัฒนาต่อยอด

### 6.1 การเพิ่ม Blueprint ใหม่

#### 6.1.1 สร้าง Blueprint
```python
# src/web/blueprints/new_module.py
from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

new_module_bp = Blueprint('new_module', __name__, url_prefix='/new_module')

@new_module_bp.route('/')
def index():
    return render_template('new_module/index.html')

@new_module_bp.route('/api/data')
def api_get_data():
    # API logic here
    return jsonify({'success': True, 'data': []})
```

#### 6.1.2 Register Blueprint
```python
# src/app.py
from web.blueprints.new_module import new_module_bp
app.register_blueprint(new_module_bp)
```

#### 6.1.3 สร้าง Templates
```
templates/new_module/
├── index.html
├── detail.html
└── settings.html
```

#### 6.1.4 ใช้ Dependency Container
```python
# ใช้ dependency container สำหรับ services
from core.dependency_container import get_service

@new_module_bp.route('/api/data')
def api_get_data():
    service = get_service('your_service_name')
    data = service.get_data()
    return jsonify({'success': True, 'data': data})
```

### 6.2 การเพิ่ม API Endpoints

#### 6.2.1 RESTful API Pattern
```python
from flask import Blueprint, request, jsonify
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

@blueprint.route('/api/resource', methods=['GET'])
def get_resources():
    # Get all resources with pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    # Implementation here
    return jsonify({'success': True, 'data': []})

@blueprint.route('/api/resource/<id>', methods=['GET'])
def get_resource(id):
    # Get specific resource
    pass

@blueprint.route('/api/resource', methods=['POST'])
def create_resource():
    # Create new resource
    data = request.get_json()
    # Implementation here
    return jsonify({'success': True, 'id': 1}), 201

@blueprint.route('/api/resource/<id>', methods=['PUT'])
def update_resource(id):
    # Update resource
    pass

@blueprint.route('/api/resource/<id>', methods=['DELETE'])
def delete_resource(id):
    # Delete resource
    pass
```

#### 6.2.2 Error Handling Pattern
```python
from flask import jsonify
from core.models import db

@blueprint.route('/api/resource', methods=['POST'])
def create_resource():
    try:
        # Implementation here
        db.session.commit()
        return jsonify({'success': True, 'id': 1}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
```

### 6.3 การเพิ่ม WebSocket Events

#### 6.3.1 Event Handlers
```python
from flask_socketio import emit, join_room, leave_room
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

@socketio.on('connect')
def handle_connect(sid=None, environ=None):
    print(f'Client connected: {sid}')
    emit('status', {'message': 'Connected to LPR Server'})

@socketio.on('disconnect')
def handle_disconnect(sid=None):
    print(f'Client disconnected: {sid}')

@socketio.on('custom_event')
def handle_custom_event(data):
    # Handle custom event
    emit('response_event', {'status': 'success'})

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    join_room(room)
    emit('status', {'message': f'Joined room: {room}'})
```

#### 6.3.2 Service Integration
```python
# ใช้ dependency container สำหรับ services
from core.dependency_container import get_service

@socketio.on('custom_event')
def handle_custom_event(data):
    service = get_service('your_service_name')
    result = service.process_data(data)
    emit('response_event', result)
```

### 6.4 การปรับแต่ง Theme

#### 6.4.1 CSS Variables
```css
:root {
    --bg-primary: #F4F6F8;
    --text-primary: #333333;
    --status-success: #A3D9A5;
    --status-warning: #FCE38A;
    --status-error: #F38181;
}
```

#### 6.4.2 Dark Mode
```css
body.dark-mode {
    --bg-primary: #2E2E2E;
    --text-primary: #DADADA;
}
```

### 6.5 การเพิ่ม Database Models

#### 6.5.1 SQLAlchemy Models
```python
from datetime import datetime
from typing import Optional, Dict, Any
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.models import db

class NewModel(db.Model):
    __tablename__ = 'new_table'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<NewModel {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

#### 6.5.2 Register Model
```python
# src/core/models/__init__.py
from .new_model import NewModel

__all__ = ['db', 'Camera', 'LPRRecord', 'BlacklistPlate', 'HealthCheck', 'NewModel']
```

### 6.6 การเพิ่ม Systemd Service

#### 6.6.1 Service File
```ini
[Unit]
Description=New Service
After=network.target

[Service]
Type=simple
User=devuser
WorkingDirectory=/home/devuser/lprserver_v3
Environment=PATH=/home/devuser/lprserver_v3/venv/bin
Environment=FLASK_CONFIG=production
Environment=PYTHONPATH=/home/devuser/lprserver_v3:/home/devuser/lprserver_v3/src
ExecStart=/home/devuser/lprserver_v3/venv/bin/python /path/to/your/script.py

[Install]
WantedBy=multi-user.target
```

#### 6.6.2 Install Service
```bash
# Copy service file
sudo cp new-service.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable new-service.service
sudo systemctl start new-service.service

# Check status
sudo systemctl status new-service.service
```

---

## การบำรุงรักษา

### 7.1 การตรวจสอบสถานะระบบ

#### 7.1.1 Systemd Services
```bash
# ตรวจสอบสถานะ
sudo systemctl status lprserver.service
sudo systemctl status lprserver-websocket.service
sudo systemctl status nginx.service

# ดู logs
sudo journalctl -u lprserver.service -f
sudo journalctl -u lprserver-websocket.service -f

# ใช้ manage_services.sh script
./manage_services.sh status
./manage_services.sh logs
```

#### 7.1.2 Web Interface
```bash
# ตรวจสอบ web interface
curl -I http://localhost
curl -I http://localhost/dashboard
curl -I http://localhost/api/statistics
```

#### 7.1.3 WebSocket Server
```bash
# ตรวจสอบ WebSocket server
netstat -tlnp | grep 8765
curl -I http://localhost:8765
```

#### 7.1.2 Nginx Logs
```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### 7.2 การบำรุงรักษาฐานข้อมูล

#### 7.2.1 Database Backup
```bash
# Backup SQLite database
cp /home/devuser/lprserver_v3/database/lprserver.db \
   /home/devuser/lprserver_v3/database/lprserver.db.backup.$(date +%Y%m%d)

# หรือใช้ script
./manage_services.sh backup
```

#### 7.2.2 Database Maintenance
```sql
-- Clean old records (older than 30 days)
DELETE FROM lpr_records WHERE timestamp < datetime('now', '-30 days');

-- Clean old health checks (older than 7 days)
DELETE FROM health_checks WHERE timestamp < datetime('now', '-7 days');

-- Clean old blacklist entries (expired)
DELETE FROM blacklist_plates WHERE expiry_date < datetime('now') AND expiry_date IS NOT NULL;

-- Optimize database
VACUUM;
```

#### 7.2.3 Database Integrity Check
```bash
# ตรวจสอบ integrity ของฐานข้อมูล
sqlite3 /home/devuser/lprserver_v3/database/lprserver.db "PRAGMA integrity_check;"

# ตรวจสอบ schema
sqlite3 /home/devuser/lprserver_v3/database/lprserver.db ".schema"
```

### 7.3 การบำรุงรักษาไฟล์

#### 7.3.1 Log Rotation
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/lprserver

/home/devuser/lprserver_v3/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 devuser devuser
}
```

#### 7.3.2 Image Storage Cleanup
```bash
# Remove old images (older than 90 days)
find /home/devuser/lprserver_v3/storage/images -type f -mtime +90 -delete
```

### 7.4 การอัปเดตระบบ

#### 7.4.1 Code Updates
```bash
# Pull latest code
cd /home/devuser/lprserver_v3
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Test system
python test_system.py

# Restart services
sudo systemctl restart lprserver.service
sudo systemctl restart lprserver-websocket.service

# หรือใช้ manage_services.sh script
./manage_services.sh restart
```

#### 7.4.2 System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Restart services if needed
sudo systemctl restart nginx.service

# Check all services
./manage_services.sh status
```

#### 7.4.3 Database Migration (if needed)
```bash
# Backup database before migration
cp /home/devuser/lprserver_v3/database/lprserver.db \
   /home/devuser/lprserver_v3/database/lprserver.db.backup.$(date +%Y%m%d)

# Run migration script (if available)
python migrate_database.py

# Verify database integrity
sqlite3 /home/devuser/lprserver_v3/database/lprserver.db "PRAGMA integrity_check;"
```

### 7.5 การแก้ไขปัญหา

#### 7.5.1 Common Issues

**ปัญหา**: 502 Bad Gateway
```bash
# ตรวจสอบ Nginx configuration
sudo nginx -t

# ตรวจสอบ Unix socket
ls -la /tmp/lprserver.sock

# ตรวจสอบ service status
sudo systemctl status lprserver.service

# ตรวจสอบ logs
sudo journalctl -u lprserver.service -f
```

**ปัญหา**: WebSocket connection failed
```bash
# ตรวจสอบ WebSocket service
sudo systemctl status lprserver-websocket.service

# ตรวจสอบ port 8765
netstat -tlnp | grep 8765

# ตรวจสอบ logs
sudo journalctl -u lprserver-websocket.service -f
```

**ปัญหา**: Database errors
```bash
# ตรวจสอบ database permissions
ls -la /home/devuser/lprserver_v3/database/

# ตรวจสอบ database integrity
sqlite3 /home/devuser/lprserver_v3/database/lprserver.db "PRAGMA integrity_check;"

# ตรวจสอบ database schema
sqlite3 /home/devuser/lprserver_v3/database/lprserver.db ".tables"
```

**ปัญหา**: Import errors
```bash
# ตรวจสอบ Python path
echo $PYTHONPATH

# ตรวจสอบ virtual environment
which python
python -c "import sys; print(sys.path)"
```

**ปัญหา**: Blacklist system errors
```bash
# ตรวจสอบ blacklist service
python -c "from src.services.blacklist_service import BlacklistService; print('OK')"

# ตรวจสอบ database models
python -c "from core.models.blacklist_plate import BlacklistPlate; print('OK')"
```

#### 7.5.2 Performance Monitoring

**CPU Usage**
```bash
# Monitor CPU usage
htop

# Check specific process
ps aux | grep gunicorn
ps aux | grep python | grep websocket
```

**Memory Usage**
```bash
# Check memory usage
free -h

# Check specific service memory
sudo systemctl show lprserver.service --property=MemoryCurrent
sudo systemctl show lprserver-websocket.service --property=MemoryCurrent
```

**Disk Usage**
```bash
# Check disk usage
df -h

# Check specific directory
du -sh /home/devuser/lprserver_v3/storage/
du -sh /home/devuser/lprserver_v3/database/
du -sh /home/devuser/lprserver_v3/logs/
```

**Network Usage**
```bash
# Check network connections
netstat -tlnp | grep :5000
netstat -tlnp | grep :8765
netstat -tlnp | grep :80
```

**Application Performance**
```bash
# Test API response time
time curl -s http://localhost/api/statistics

# Test WebSocket connection
python test_client.py
```

---

## อื่น ๆ ที่เกี่ยวข้องเพิ่มเติม

### 8.1 Security Considerations

#### 8.1.1 Authentication & Authorization
- Implement proper user authentication
- Role-based access control (RBAC)
- Session management
- Password policies

#### 8.1.2 Network Security
- HTTPS/SSL implementation
- Firewall configuration
- Network segmentation
- VPN access for remote management

#### 8.1.3 Data Security
- Database encryption
- Backup encryption
- Log file protection
- API rate limiting

### 8.2 Performance Optimization

#### 8.2.1 Database Optimization
- Index optimization
- Query optimization
- Connection pooling
- Database partitioning

#### 8.2.2 Web Server Optimization
- Nginx caching
- Gzip compression
- Static file serving
- Load balancing

#### 8.2.3 Application Optimization
- Code profiling
- Memory optimization
- Async processing
- Caching strategies

### 8.3 Scalability Planning

#### 8.3.1 Horizontal Scaling
- Load balancer setup
- Multiple application instances
- Database clustering
- Microservices architecture

#### 8.3.2 Vertical Scaling
- Server resource upgrades
- Database optimization
- Application optimization
- Caching layers

### 8.4 Monitoring & Alerting

#### 8.4.1 System Monitoring
- CPU, Memory, Disk monitoring
- Network monitoring
- Application performance monitoring
- Database monitoring

#### 8.4.2 Alerting System
- Email notifications
- SMS notifications
- Slack/Teams integration
- Escalation procedures

### 8.5 Disaster Recovery

#### 8.5.1 Backup Strategy
- Database backups
- Configuration backups
- Code backups
- Off-site storage

#### 8.5.2 Recovery Procedures
- System restore procedures
- Database recovery
- Service restoration
- Data validation

### 8.6 Compliance & Regulations

#### 8.6.1 Data Privacy
- GDPR compliance
- Data retention policies
- User consent management
- Data anonymization

#### 8.6.2 Security Standards
- ISO 27001 compliance
- SOC 2 compliance
- Industry-specific regulations
- Regular security audits

### 8.7 Documentation Standards

#### 8.7.1 Code Documentation
- API documentation
- Code comments
- Architecture documentation
- Deployment guides

#### 8.7.2 User Documentation
- User manuals
- Admin guides
- Troubleshooting guides
- FAQ sections

### 8.8 Testing Strategy

#### 8.8.1 Automated Testing
- Unit tests
- Integration tests
- End-to-end tests
- Performance tests

#### 8.8.2 Manual Testing
- User acceptance testing
- Security testing
- Usability testing
- Compatibility testing

---

## สถานะระบบล่าสุด

### ✅ ระบบทำงานได้อย่างสมบูรณ์ (อัปเดตล่าสุด: 12 สิงหาคม 2025)

#### การแก้ไขปัญหาที่สำคัญ:
1. **WebSocket Event Handlers** - แก้ไขปัญหา parameter mismatch ใน `handle_connect` และ `handle_disconnect`
2. **BlacklistService Methods** - เพิ่ม class method `get_active_blacklist` และแก้ไขการเรียกใช้ instance methods
3. **API Endpoints** - แก้ไขการเรียกใช้ services ผ่าน dependency container
4. **Database Operations** - เพิ่ม imports ที่จำเป็นสำหรับ `db`, `timedelta`, และ `db.func`

#### ฟีเจอร์ที่ทำงานได้:
- ✅ **WebSocket Server** - รับข้อมูลจาก Edge Camera
- ✅ **LPR Data Processing** - บันทึกและประมวลผลข้อมูลป้ายทะเบียน
- ✅ **Blacklist System** - จัดการและตรวจจับป้ายทะเบียนที่อยู่ใน blacklist
- ✅ **Real-time Dashboard** - แสดงสถิติแบบ real-time
- ✅ **REST API** - ทุก endpoints ทำงานได้ปกติ
- ✅ **Web Interface** - หน้าเว็บทุกหน้าทำงานได้

#### การทดสอบที่ผ่าน:
- ✅ การเพิ่มข้อมูล blacklist
- ✅ การตรวจจับป้ายทะเบียนที่อยู่ใน blacklist
- ✅ การอัปเดตสถิติการตรวจจับ
- ✅ WebSocket connections
- ✅ API responses

### 🚀 พร้อมใช้งานสำหรับ Production

ระบบพร้อมใช้งานสำหรับการรับข้อมูลจาก Edge Camera และการจัดการ blacklist อย่างสมบูรณ์

## สรุป

LPR Server v3 ได้รับการออกแบบและพัฒนาตามหลักการของ Modular & Scalable Architecture โดยใช้เทคโนโลยีที่ทันสมัยและเหมาะสมสำหรับระบบ License Plate Recognition ที่ต้องการความเสถียร ความเร็ว และความสามารถในการขยายตัว

### สถาปัตยกรรมที่ใช้:
- **Flask Blueprints** - สำหรับการแบ่งส่วนการทำงานของ Web UI
- **Dependency Injection** - สำหรับการจัดการ Dependencies ระหว่าง Components
- **Absolute Imports** - สำหรับการจัดการ imports ที่ชัดเจนและสม่ำเสมอ
- **Service Layer** - สำหรับ Business Logic
- **WebSocket Server** - สำหรับการสื่อสารแบบ Real-time

### โครงสร้างโมดูลที่ทำงานได้:
- **Main Routes** (`/`) - หน้าแรก, แดชบอร์ด, รายการบันทึก, จัดการ blacklist
- **API Routes** (`/api`) - REST API สำหรับการเข้าถึงข้อมูล
- **AI Camera** (`/aicamera`) - จัดการกล้อง AI และการเชื่อมต่อ
- **Detection** (`/detection`) - จัดการข้อมูลการตรวจจับ
- **Map** (`/map`) - ติดตามรถและวิเคราะห์เส้นทาง
- **System** (`/system`) - จัดการระบบและตรวจสอบสถานะ
- **User** (`/user`) - จัดการผู้ใช้และสิทธิ์
- **Report** (`/report`) - สร้างและจัดการรายงาน
- **Health** (`/health`) - ตรวจสอบสถานะระบบ

### ฟีเจอร์หลักที่ทำงานได้:
- ✅ **WebSocket Server** - รับข้อมูลจาก Edge Camera
- ✅ **LPR Data Processing** - บันทึกและประมวลผลข้อมูลป้ายทะเบียน
- ✅ **Blacklist System** - จัดการและตรวจจับป้ายทะเบียนที่อยู่ใน blacklist
- ✅ **Real-time Dashboard** - แสดงสถิติแบบ real-time
- ✅ **REST API** - ทุก endpoints ทำงานได้ปกติ
- ✅ **Web Interface** - หน้าเว็บทุกหน้าทำงานได้

### การทดสอบที่ผ่าน:
- ✅ การเพิ่มข้อมูล blacklist
- ✅ การตรวจจับป้ายทะเบียนที่อยู่ใน blacklist
- ✅ การอัปเดตสถิติการตรวจจับ
- ✅ WebSocket connections
- ✅ API responses

การพัฒนาต่อไปควรเน้นที่การเพิ่มฟีเจอร์ใหม่ การปรับปรุงประสิทธิภาพ และการเพิ่มความปลอดภัยของระบบ เพื่อให้ระบบสามารถรองรับการใช้งานในระดับ Production ได้อย่างเต็มที่

---

**เอกสารนี้จัดทำขึ้นเพื่อใช้เป็นคู่มือในการพัฒนา บำรุงรักษา และพัฒนาต่อยอด LPR Server v3**

**เวอร์ชัน**: 3.0  
**วันที่**: 12 สิงหาคม 2025  
**ผู้จัดทำ**: Development Team  
**สถานะ**: Final Version - อัปเดตล่าสุด 12 สิงหาคม 2025
