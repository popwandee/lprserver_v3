# LPR Server v3 - Enhanced Architecture

## ภาพรวม (Overview)

LPR Server v3 ได้รับการปรับปรุงสถาปัตยกรรมให้เป็นไปตามมาตรฐานที่กำหนดไว้ใน DEVELOPMENT_GUIDE.md โดยใช้แนวคิดหลัก 3 ประการ:

1. **Absolute Imports Pattern** - จัดการ import paths ให้ชัดเจน
2. **Dependency Injection (DI)** - ลด coupling ระหว่าง components
3. **Flask Blueprints** - Modular design สำหรับ Web UI

## การติดตั้ง (Installation)

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
