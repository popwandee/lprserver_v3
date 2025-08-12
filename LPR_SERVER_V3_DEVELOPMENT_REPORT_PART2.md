---

## องค์ประกอบที่สำคัญในระบบ

### 3.1 Core Components

#### 3.1.1 Flask Application Factory
```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(aicamera_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    
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

---

## คำแนะนำและคู่มือในการใช้งาน

### 5.1 การเข้าถึงระบบ

#### 5.1.1 Web Interface
- **URL**: http://localhost หรือ http://your-server-ip
- **Port**: 80 (HTTP)
- **Browser**: Chrome, Firefox, Safari, Edge

#### 5.1.2 Demo Credentials
- **Admin**: admin / admin123
- **User**: user / user123

### 5.2 การใช้งานโมดูลต่างๆ

#### 5.2.1 AI Camera Manager
1. **ภาพรวม**: ดูสถานะกล้องทั้งหมด
2. **จัดการกล้อง**: เพิ่ม/แก้ไข/ลบกล้อง
3. **ตั้งค่า**: ปรับความละเอียด, FPS, ความไว

#### 5.2.2 Detection Manager
1. **รายการบันทึก**: ดูข้อมูลการตรวจจับ
2. **สถิติ**: กราฟและแผนภูมิ
3. **การแจ้งเตือน**: ระบบแจ้งเตือนอัตโนมัติ

#### 5.2.3 Map Manager
1. **ติดตามรถ**: ค้นหาและติดตามรถ
2. **วิเคราะห์**: วิเคราะห์เส้นทางและพฤติกรรม
3. **จัดการตำแหน่ง**: กำหนดจุดกล้อง

#### 5.2.4 System Manager
1. **System Logs**: ดูบันทึกระบบ
2. **Monitoring**: ตรวจสอบสถานะ
3. **Health Check**: ตรวจสอบสุขภาพระบบ

#### 5.2.5 User Manager
1. **เข้าสู่ระบบ**: Authentication
2. **โปรไฟล์**: จัดการข้อมูลส่วนตัว
3. **จัดการผู้ใช้**: สำหรับ Admin

#### 5.2.6 Report Manager
1. **สร้างรายงาน**: เลือกประเภทและช่วงเวลา
2. **เทมเพลต**: บันทึกและใช้เทมเพลต
3. **ประวัติ**: ดูรายงานที่สร้างไว้

### 5.3 การตั้งค่าขั้นสูง

#### 5.3.1 Dark Mode
- คลิกปุ่ม Theme Toggle (มุมขวาบน)
- การตั้งค่าจะถูกบันทึกใน Local Storage

#### 5.3.2 การกรองข้อมูล
- ใช้ตัวกรองในแต่ละหน้า
- สามารถส่งออกข้อมูลได้

#### 5.3.3 การแจ้งเตือน
- ระบบจะแจ้งเตือนอัตโนมัติ
- สามารถตั้งค่าระดับการแจ้งเตือนได้

---

## คำแนะนำและคู่มือในการพัฒนาต่อยอด

### 6.1 การเพิ่ม Blueprint ใหม่

#### 6.1.1 สร้าง Blueprint
```python
# src/web/blueprints/new_module.py
from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit

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

### 6.2 การเพิ่ม API Endpoints

#### 6.2.1 RESTful API Pattern
```python
@blueprint.route('/api/resource', methods=['GET'])
def get_resources():
    # Get all resources
    pass

@blueprint.route('/api/resource/<id>', methods=['GET'])
def get_resource(id):
    # Get specific resource
    pass

@blueprint.route('/api/resource', methods=['POST'])
def create_resource():
    # Create new resource
    pass

@blueprint.route('/api/resource/<id>', methods=['PUT'])
def update_resource(id):
    # Update resource
    pass

@blueprint.route('/api/resource/<id>', methods=['DELETE'])
def delete_resource(id):
    # Delete resource
    pass
```

### 6.3 การเพิ่ม WebSocket Events

#### 6.3.1 Event Handlers
```python
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('custom_event')
def handle_custom_event(data):
    # Handle custom event
    emit('response_event', {'status': 'success'})
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
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NewModel(Base):
    __tablename__ = 'new_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
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
WorkingDirectory=/path/to/service
ExecStart=/path/to/executable

[Install]
WantedBy=multi-user.target
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
```

#### 7.2.2 Database Maintenance
```sql
-- Clean old records (older than 30 days)
DELETE FROM lpr_records WHERE created_at < datetime('now', '-30 days');

-- Clean old logs (older than 7 days)
DELETE FROM system_logs WHERE timestamp < datetime('now', '-7 days');

-- Optimize database
VACUUM;
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

# Restart services
sudo systemctl restart lprserver.service
sudo systemctl restart lprserver-websocket.service
```

#### 7.4.2 System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Restart services if needed
sudo systemctl restart nginx.service
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
```

**ปัญหา**: WebSocket connection failed
```bash
# ตรวจสอบ WebSocket service
sudo systemctl status lprserver-websocket.service

# ตรวจสอบ port 8765
netstat -tlnp | grep 8765
```

**ปัญหา**: Database errors
```bash
# ตรวจสอบ database permissions
ls -la /home/devuser/lprserver_v3/database/

# ตรวจสอบ database integrity
sqlite3 /home/devuser/lprserver_v3/database/lprserver.db "PRAGMA integrity_check;"
```

#### 7.5.2 Performance Monitoring

**CPU Usage**
```bash
# Monitor CPU usage
htop

# Check specific process
ps aux | grep gunicorn
```

**Memory Usage**
```bash
# Check memory usage
free -h

# Check specific service memory
sudo systemctl show lprserver.service --property=MemoryCurrent
```

**Disk Usage**
```bash
# Check disk usage
df -h

# Check specific directory
du -sh /home/devuser/lprserver_v3/storage/
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

## สรุป

LPR Server v3 ได้รับการออกแบบและพัฒนาตามหลักการของ Modular & Scalable Architecture โดยใช้เทคโนโลยีที่ทันสมัยและเหมาะสมสำหรับระบบ License Plate Recognition ที่ต้องการความเสถียร ความเร็ว และความสามารถในการขยายตัว

ระบบประกอบด้วย 6 โมดูลหลัก (AI Camera, Detection, Map, System, User, Report) ที่ทำงานร่วมกันอย่างเป็นระบบ พร้อมกับ UI ที่ออกแบบให้ใช้งานง่าย มีความสวยงาม และรองรับการใช้งานบนอุปกรณ์ต่างๆ

การพัฒนาต่อไปควรเน้นที่การเพิ่มฟีเจอร์ใหม่ การปรับปรุงประสิทธิภาพ และการเพิ่มความปลอดภัยของระบบ เพื่อให้ระบบสามารถรองรับการใช้งานในระดับ Production ได้อย่างเต็มที่

---

**เอกสารนี้จัดทำขึ้นเพื่อใช้เป็นคู่มือในการพัฒนา บำรุงรักษา และพัฒนาต่อยอด LPR Server v3**

**เวอร์ชัน**: 3.0  
**วันที่**: 12 สิงหาคม 2025  
**ผู้จัดทำ**: Development Team  
**สถานะ**: Draft for Google Docs Editing
