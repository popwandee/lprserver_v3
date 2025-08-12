# LPR Server v3 - Architecture Overview

## สถาปัตยกรรมที่ปรับปรุงแล้ว (Enhanced Architecture)

ระบบ LPR Server v3 ได้รับการปรับปรุงให้เป็นไปตามมาตรฐานที่กำหนดไว้ใน DEVELOPMENT_GUIDE.md โดยใช้แนวคิดหลัก 3 ประการ:

### 1. Absolute Imports Pattern
- **ไฟล์**: `src/core/import_helper.py`
- **หน้าที่**: จัดการ import paths ให้ชัดเจนและสม่ำเสมอ
- **ประโยชน์**: ลดปัญหา circular imports, ง่ายต่อการ refactor

### 2. Dependency Injection (DI)
- **ไฟล์**: `src/core/dependency_container.py`
- **หน้าที่**: จัดการ dependencies ระหว่าง components
- **ประโยชน์**: ลด coupling, ง่ายต่อการ testing

### 3. Flask Blueprints
- **โครงสร้าง**: `src/web/blueprints/`
- **หน้าที่**: แบ่งส่วนการทำงานของ Web UI ตามหน้าที่
- **ประโยชน์**: Modular design, ง่ายต่อการ maintain

## โครงสร้างไฟล์ (File Structure)

```
lprserver_v3/
├── src/
│   ├── core/
│   │   ├── import_helper.py          # Absolute imports management
│   │   ├── dependency_container.py   # DI container
│   │   ├── models/                   # Database models
│   │   │   ├── __init__.py
│   │   │   ├── lpr_record.py
│   │   │   ├── camera.py
│   │   │   ├── blacklist_plate.py
│   │   │   └── health_check.py
│   │   └── utils/                    # Utility functions
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── websocket_service.py      # WebSocket communication
│   │   ├── blacklist_service.py      # Blacklist management
│   │   ├── health_service.py         # Health monitoring
│   │   └── database_service.py       # Database operations
│   ├── web/                          # Web interface layer
│   │   ├── blueprints/
│   │   │   ├── main.py               # Main routes
│   │   │   ├── api.py                # API endpoints
│   │   │   └── health.py             # Health monitoring endpoints
│   │   └── static/                   # Static files
│   ├── constants.py                  # Application constants
│   └── app.py                        # Application factory
├── config.py                         # Configuration management
├── wsgi.py                          # WSGI entry point
├── requirements.txt                  # Python dependencies
└── README.md                        # Project documentation
```

## Service Layer Architecture

### 1. WebSocket Service (`websocket_service.py`)
**หน้าที่**: จัดการการสื่อสารกับ Edge AI Cameras
- รับข้อมูล LPR จากกล้องผ่าน WebSocket port 8765
- จัดการการลงทะเบียนกล้อง
- บันทึกข้อมูลลงฐานข้อมูล
- ส่งข้อมูล real-time ไปยัง dashboard

### 2. Blacklist Service (`blacklist_service.py`)
**หน้าที่**: จัดการรถ Blacklist
- เพิ่ม/ลบรถจาก blacklist
- ตรวจสอบรถที่ตรวจจับได้กับ blacklist
- ส่งการแจ้งเตือนเมื่อพบรถ blacklist
- สถิติ blacklist

### 3. Health Service (`health_service.py`)
**หน้าที่**: ตรวจสอบสถานะระบบ
- ตรวจสอบฐานข้อมูล
- ตรวจสอบพื้นที่จัดเก็บไฟล์
- ตรวจสอบทรัพยากรระบบ
- ตรวจสอบการเชื่อมต่อกล้อง
- ตรวจสอบสถานะ services

### 4. Database Service (`database_service.py`)
**หน้าที่**: จัดการฐานข้อมูล
- การเชื่อมต่อฐานข้อมูล
- การทำความสะอาดข้อมูลเก่า
- การ optimize ฐานข้อมูล
- การ backup และ restore

## Health Monitoring System

### Real-time Monitoring
- **WebSocket Events**: ส่งข้อมูลสถานะแบบ real-time
- **Periodic Checks**: ตรวจสอบทุก 5 นาที
- **Dashboard Integration**: แสดงผลบน Web UI

### Health Check Components
1. **Database Connectivity**: ตรวจสอบการเชื่อมต่อฐานข้อมูล
2. **Disk Space**: ตรวจสอบพื้นที่จัดเก็บไฟล์
3. **System Resources**: ตรวจสอบ CPU และ Memory
4. **Camera Connectivity**: ตรวจสอบการเชื่อมต่อกล้อง
5. **Service Status**: ตรวจสอบสถานะ services

### Health Status Levels
- **PASS**: ระบบทำงานปกติ
- **WARNING**: มีปัญหาเล็กน้อย
- **FAIL**: มีปัญหาสำคัญ

## Deployment Architecture

### Production Setup
```
Systemd Service → Nginx (Port 80) → Gunicorn (Unix Socket) → Flask App
                                    ↓
                              WebSocket Server (Port 8765)
```

### Service Management
- **lprserver.service**: Flask application
- **lprserver-websocket.service**: WebSocket server
- **nginx**: Reverse proxy

### Configuration
- **Environment Variables**: ใช้ .env files
- **Database**: SQLite สำหรับ production
- **Logging**: Rotating file logs
- **Security**: UFW firewall

## API Endpoints

### Main Routes (`/`)
- Dashboard
- LPR Records
- Camera Management

### API Routes (`/api`)
- LPR Records CRUD
- Camera Management
- Blacklist Management
- Statistics

### Health Routes (`/health`)
- System Status
- Health Check
- Database Statistics
- System Cleanup

## WebSocket Events

### Camera Communication
- `camera_register`: ลงทะเบียนกล้อง
- `lpr_data`: ส่งข้อมูล LPR
- `status`: สถานะการเชื่อมต่อ

### Dashboard Updates
- `new_lpr_record`: บันทึก LPR ใหม่
- `blacklist_alert`: แจ้งเตือน blacklist
- `health_update`: อัปเดตสถานะระบบ

### Health Monitoring
- `join_health_room`: เข้าร่วมห้อง health monitoring
- `health_check_result`: ผลการตรวจสอบ
- `health_check_error`: ข้อผิดพลาด

## Best Practices Implemented

### 1. Code Organization
- **Separation of Concerns**: แยก business logic ออกจาก presentation
- **Single Responsibility**: แต่ละ class มีหน้าที่เดียว
- **Dependency Injection**: ลด coupling ระหว่าง components

### 2. Error Handling
- **Comprehensive Logging**: บันทึก logs อย่างละเอียด
- **Graceful Degradation**: ระบบทำงานต่อได้แม้มีปัญหา
- **User-friendly Messages**: ข้อความ error ที่เข้าใจง่าย

### 3. Performance
- **Database Indexing**: สร้าง index สำหรับ queries ที่ใช้บ่อย
- **Connection Pooling**: จัดการ database connections อย่างมีประสิทธิภาพ
- **Caching**: ใช้ caching สำหรับข้อมูลที่ใช้บ่อย

### 4. Security
- **Input Validation**: ตรวจสอบข้อมูล input
- **SQL Injection Prevention**: ใช้ parameterized queries
- **File Upload Security**: ตรวจสอบไฟล์ที่อัปโหลด

### 5. Monitoring
- **Health Checks**: ตรวจสอบสถานะระบบอย่างสม่ำเสมอ
- **Metrics Collection**: รวบรวมข้อมูลสถิติ
- **Alerting**: แจ้งเตือนเมื่อมีปัญหา

## Development Workflow

### 1. Local Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py
```

### 2. Testing
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python test_system.py
```

### 3. Production Deployment
```bash
# Setup systemd services
sudo ./setup.sh

# Start services
sudo systemctl start lprserver
sudo systemctl start lprserver-websocket
sudo systemctl start nginx
```

## Monitoring and Maintenance

### 1. Health Monitoring
- ตรวจสอบสถานะระบบผ่าน `/health/status`
- ดูประวัติการตรวจสอบผ่าน `/health/history`
- รับการแจ้งเตือนแบบ real-time ผ่าน WebSocket

### 2. Database Maintenance
- ทำความสะอาดข้อมูลเก่าผ่าน `/health/database/cleanup`
- Optimize ฐานข้อมูลผ่าน `/health/database/optimize`
- ดูสถิติฐานข้อมูลผ่าน `/health/database/stats`

### 3. Log Management
- Logs ถูกเก็บใน `logs/lprserver.log`
- ใช้ rotating file handler (10MB per file, 10 files)
- Log level ตาม environment

## Conclusion

สถาปัตยกรรมใหม่นี้ให้:
- **Modularity**: ง่ายต่อการเพิ่มหรือลบฟีเจอร์
- **Maintainability**: โค้ดมีโครงสร้างชัดเจน
- **Scalability**: รองรับการขยายระบบ
- **Testability**: ง่ายต่อการเขียน tests
- **Monitoring**: ระบบตรวจสอบที่ครอบคลุม

การปรับปรุงนี้ทำให้ระบบ LPR Server v3 มีความแข็งแกร่งและพร้อมใช้งานในสภาพแวดล้อมจริง
