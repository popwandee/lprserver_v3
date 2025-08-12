# LPR Server v3 - Development Guide

## ภาพรวมและแนวคิดหลัก (Context Engineering)

ระบบ LPR Server นี้จะทำหน้าที่เป็นศูนย์กลางในการรวบรวม จัดการ วิเคราะห์ และแสดงผลข้อมูลที่ได้จากกล้อง AI Camera หลายตัวที่ติดตั้งอยู่ในพื้นที่ต่างๆ

1. **Dependency Injection (DI)** - สำหรับการจัดการ Dependencies ระหว่าง Components
2. **Flask Blueprints** - สำหรับการแบ่งส่วนการทำงานของ Web UI
3. **Absolute Imports** - สำหรับการจัดการ imports ที่ชัดเจนและสม่ำเสมอ

โปรเจกต์นี้จะใช้ Design Pattern แบบ Dependency Injection เพื่อจัดการ Class ต่างๆ และใช้ Flask Blueprints สำหรับการแบ่งส่วนการทำงานของ Web UI เพื่อเพิ่ม Modularization โดยมี `/core/dependency_container.py` กำกับ module dependencies และใช้ absolute imports ผ่าน `import_helper.py`

## 1. Absolute Imports Pattern

### 1.1 แนวคิดหลัก

Absolute Imports ช่วยให้เราสามารถ:
- ใช้ import paths ที่ชัดเจนและสม่ำเสมอ
- ลดปัญหา circular imports
- ทำให้ code อ่านง่ายและเข้าใจง่าย
- รองรับการ refactor และการย้ายไฟล์ได้ดี
Flask Blueprints ช่วยให้เราสามารถ:
- แบ่ง Application เป็นส่วนๆ ตามหน้าที่
- จัดการ Routes แยกกัน
- สร้าง Modular Web UI
- ง่ายต่อการ Maintain และ Scale
Dependency Injection ช่วยให้เราสามารถ:
- แยก Dependencies ออกจาก Class
- ทำให้ Testing ง่ายขึ้น
- ลดการ Coupling ระหว่าง Components
- จัดการ Lifecycle ของ Services ได้ดีขึ้น

### Service Layer
Services เป็นชั้นกลางที่จัดการ Business Logic ใช้ absolute imports:
### 8.1 Modularity
- แต่ละ Component มีหน้าที่ชัดเจน
- สามารถพัฒนาและทดสอบแยกกันได้
- ง่ายต่อการเพิ่มหรือลบฟีเจอร์
- **Absolute imports ทำให้ dependencies ชัดเจน**

### 8.2 Maintainability
- Code มีโครงสร้างชัดเจน
- Dependencies ถูกจัดการอย่างเป็นระบบ
- ง่ายต่อการ Debug และ Troubleshoot
- **Import paths ชัดเจนและเข้าใจง่าย**

### 8.3 Scalability
- สามารถเพิ่ม Components ใหม่ได้ง่าย
- Blueprints ช่วยจัดการ Routes ได้ดี
- DI ช่วยจัดการ Dependencies ได้อย่างมีประสิทธิภาพ
- **Absolute imports รองรับการขยายระบบได้ดี**

### 8.4 Testability
- Components สามารถ Mock ได้ง่าย
- Unit Testing ทำได้สะดวก
- Integration Testing มีโครงสร้างชัดเจน
- **Import validation ช่วยตรวจสอบ dependencies**

### 8.5 Health Monitoring Benefits
- **Comprehensive Monitoring**: ครอบคลุมทุก component หลัก
- **Real-time Status**: สถานะแบบ real-time ผ่าน WebSocket
- **Auto-startup Coordination**: ประสานงานกับ auto-startup sequence
- **Detailed Logging**: บันทึก logs อย่างละเอียดในฐานข้อมูล
- **Error Prevention**: ป้องกันข้อผิดพลาดด้วย validation patterns

## 9. Best Practices

1. **ใช้ Absolute Imports** สำหรับทุก module
2. **ใช้ DI Container** สำหรับการจัดการ Dependencies ทั้งหมด
3. **แยก Business Logic** ไปไว้ใน Service Layer
4. **ใช้ Blueprints** สำหรับการจัดการ Routes ตามหน้าที่
5. **เขียน Documentation** สำหรับแต่ละ Component
6. **ทำ Unit Testing** สำหรับทุก Component
7. **ใช้ Logging** อย่างเหมาะสม
8. **จัดการ Error** อย่างเป็นระบบ
9. **Validate Imports** ในการ startup
10. **Health Monitoring Integration** สำหรับทุก component ใหม่
### สถาปัตยกรรม (Architecture)
- **Edge Computing Camera**: Raspberry Pi 5 + Hailo AI Accelerator + Camera Module 3
- **LPR Server**: ศูนย์กลางในการรับข้อมูล บันทึก จัดการฐานข้อมูล และให้บริการ Web Interface

### การไหลของข้อมูล (Data Flow)
ข้อมูลภาพและผลการตรวจจับจาก Edge Computing Camera จะถูกส่งมายัง LPR Server ผ่านช่องทางการสื่อสารแบบ Real-time websocket หรือ API

### เทคโนโลยีที่ใช้ (Technology Stack)
- **Server OS**: Ubuntu Server
- **Web Framework**: Flask
- **WSGI Server**: Gunicorn (Unix Socket)
- **Reverse Proxy**: Nginx
- **Database**: SQLite (สำหรับ LPR Server)
- **Real-time Communication**: Socket.IO
- **Security**: UFW Firewall

### หลักการพัฒนา (Development Principles)
- **Modular Design**: แยกส่วนประกอบต่างๆ ออกจากกันอย่างชัดเจน
- **Scalability**: รองรับจำนวนกล้อง AI Camera ที่เพิ่มขึ้น
- **Security First**: เน้นความปลอดภัยของข้อมูลและการสื่อสาร
- **Performance Optimization**: เพิ่มประสิทธิภาพในการรับ-ส่งข้อมูล
- **User-Centric UI**: ออกแบบ Dashboard ให้ใช้งานง่าย
- **Robustness & Monitoring**: มีกลไกการตรวจสอบสถานะระบบ

## ลำดับขั้นตอนการพัฒนา (Development Milestones)

### Milestone 1: การจัดการข้อมูลและการแสดงผลหลัก
**เป้าหมาย**: สร้างรากฐานที่แข็งแกร่งสำหรับการรับ จัดเก็บ และแสดงผลข้อมูลจากหลายกล้อง

#### Task 1.1: การปรับปรุงฐานข้อมูลสำหรับ Multi-Camera
- ✅ **Sub-task 1.1.1**: ออกแบบ Schema เพิ่มเติม
  - เพิ่มฟิลด์ `camera_id` ในตาราง `lpr_records`
  - สร้างตาราง `cameras` สำหรับเก็บข้อมูลของกล้องแต่ละตัว
  - สร้างตาราง `health_checks` สำหรับการตรวจสอบสถานะ
  - สร้างตาราง `blacklist_plates` สำหรับการจัดการรถ Blacklist

- ✅ **Sub-task 1.1.2**: การสร้าง Index และ Optimization
  - สร้าง Index บนคอลัมน์ที่ใช้บ่อยในการค้นหา
  - เพิ่มประสิทธิภาพการดึงข้อมูล

- ⏳ **Sub-task 1.1.3**: นโยบายการจัดเก็บข้อมูล
  - กำหนดกลไกสำหรับการจัดเก็บข้อมูล
  - การลบข้อมูลเก่าและการ Archive

#### Task 1.2: การรับข้อมูลจาก AI Camera
- ✅ **Sub-task 1.2.1**: WebSocket Server
  - รับข้อมูลจาก Edge Camera ผ่าน WebSocket port 8765
  - บันทึกข้อมูลลงฐานข้อมูล
  - บันทึกภาพลงใน storage directory

- ✅ **Sub-task 1.2.2**: การประกันข้อมูล
  - Implement error handling
  - การ validate ข้อมูล

#### Task 1.3: การแสดงผลบน Web UI Dashboard
- ✅ **Sub-task 1.3.1**: ตารางแสดงผลรวมแบบ Pagination, Filter, Search, Sorting
  - API endpoints สำหรับการค้นหา กรอง จัดเรียง
  - การแบ่งหน้า (pagination)

- ✅ **Sub-task 1.3.2**: การปรับปรุง Frontend UI
  - หน้า Dashboard แสดงสถิติ
  - หน้าตารางแสดงรายการบันทึก
  - ระบบกรองข้อมูล

### Milestone 2: การแสดงผลขั้นสูงและฟังก์ชันเฉพาะทาง
**เป้าหมาย**: เพิ่มฟังก์ชันการแสดงผลเชิงพื้นที่และการจัดการรถ Blacklist

#### Task 2.1: การแสดงจุดติดตั้งกล้องบนแผนที่
- ⏳ **Sub-task 2.1.1**: Database Schema สำหรับกล้อง
- ⏳ **Sub-task 2.1.2**: API สำหรับข้อมูลกล้อง
- ⏳ **Sub-task 2.1.3**: การรวมแผนที่ใน Web UI
- ⏳ **Sub-task 2.1.4**: การจัดการข้อมูลกล้องผ่าน UI

#### Task 2.2: การแสดงเส้นทาง/จุดที่รถคันที่ระบุผ่านบนแผนที่
- ✅ **Sub-task 2.2.1**: การเก็บข้อมูลตำแหน่งรถ
  - เพิ่มฟิลด์ `location_lat`, `location_lon` ใน LPRRecord
- ⏳ **Sub-task 2.2.2**: การแสดงผลบนแผนที่

#### Task 2.3: การจัดการรถ Blacklist
- ✅ **Sub-task 2.3.1**: Database Schema สำหรับ Blacklist
  - สร้างตาราง `blacklist_plates`
- ✅ **Sub-task 2.3.2**: API สำหรับ Blacklist
  - CRUD operations สำหรับ Blacklist
- ✅ **Sub-task 2.3.3**: การตรวจจับและแจ้งเตือน Blacklist
  - Logic ตรวจสอบ Blacklist
  - Real-time notifications
- ✅ **Sub-task 2.3.4**: Web UI สำหรับ Blacklist
  - หน้าจัดการ Blacklist
  - การแจ้งเตือน

### Milestone 3: การปรับใช้และการบำรุงรักษาในสภาพแวดล้อมจริง
**เป้าหมาย**: ทำให้ระบบ LPR Server พร้อมใช้งานในสภาพแวดล้อมจริง

#### Task 3.1: การปรับใช้แบบ Scalable Deployment
- ✅ **Sub-task 3.1.1**: การกำหนดค่า Gunicorn Worker
  - ตั้งค่า systemd services
  - ใช้ Gunicorn กับ Unix Socket

#### Task 3.2: การตรวจสอบและบำรุงรักษาระบบ
- ⏳ **Sub-task 3.2.1**: การตรวจสอบ Health Check ของ Server
- ⏳ **Sub-task 3.2.2**: Dashboard สรุปภาพรวม
- ⏳ **Sub-task 3.2.3**: ระบบแจ้งเตือน

## กฎและแนวทางในการใช้ตัวแปร (Variable Mapping)

### 1. การตั้งชื่อ (Naming Conventions)

#### Backend (Python)
- ใช้ `snake_case` สำหรับตัวแปร, ฟังก์ชัน, และไฟล์
- ใช้ `PascalCase` สำหรับคลาส
- ใช้ `UPPER_CASE` สำหรับค่าคงที่

```python
# ตัวอย่าง
license_plate_text = "กข1234"
def get_detection_data_paginated():
    pass

class DetectionThread:
    pass

IMAGE_SAVE_DIR = "/storage/images"
```

#### Backend (SQL Query/Database)
- ใช้ `snake_case` สำหรับชื่อตารางและชื่อคอลัมน์

```sql
-- ตัวอย่าง
CREATE TABLE detection_results (
    license_plate_text VARCHAR(20),
    lp_confidence FLOAT,
    camera_metadata JSON
);
```

#### Frontend (JavaScript)
- ใช้ `camelCase` สำหรับตัวแปรและฟังก์ชัน
- ใช้ `PascalCase` สำหรับคลาส/คอมโพเนนต์

```javascript
// ตัวอย่าง
const licensePlateText = "กข1234";
function getDetectionData() {
    // ...
}

class DetectionTableComponent {
    // ...
}
```

#### Middle (API JSON Payload)
- ใช้ `snake_case` สำหรับ Key ใน JSON payload

```json
{
    "license_plate_text": "กข1234",
    "lp_confidence": 0.95,
    "camera_id": "CAM001"
}
```

#### Configuration Files (.env)
- ใช้ `UPPER_CASE_WITH_UNDERSCORES`

```bash
# ตัวอย่าง
WEBSOCKET_SERVER_URL=ws://localhost:8765
DB_PATH=/path/to/database
```

### 2. การทำ Variable Mapping ระหว่าง Layer

#### Database <-> Backend (Python)
```python
# คอลัมน์ license_plate_text ในฐานข้อมูล
# map เป็น detection_data["license_plate_text"] ใน Python
```

#### Backend (Python) <-> Middle (API JSON)
```python
# Python Dictionary
detection_data = {
    "license_plate_text": "กข1234",
    "confidence": 0.95
}

# JSON Response
{
    "license_plate_text": "กข1234",
    "confidence": 0.95
}
```

#### Middle (API JSON) <-> Frontend (JavaScript)
```javascript
// JSON Key license_plate_text (จาก API)
// map เป็น data.licensePlateText ใน JavaScript
fetch('/api/records')
    .then(response => response.json())
    .then(data => {
        console.log(data.license_plate_text); // ใช้ snake_case จาก API
    });
```

### 3. การใช้ค่าคงที่และ Enum
```python
# ใช้ค่าคงที่แทน Magic Strings
from src.constants import HEALTH_STATUS_PASS, HEALTH_STATUS_FAIL

if health_status == HEALTH_STATUS_PASS:
    # ...
```

### 4. Centralized Configuration
```python
# ใช้ไฟล์ config.py และ .env
from config import Config

app.config.from_object(Config)
```

### 5. Type Hinting (Python)
```python
def process_frame(self, frame: np.ndarray) -> None:
    """Process camera frame"""
    pass

def get_detection_data(self, camera_id: str) -> List[Dict]:
    """Get detection data for camera"""
    pass
```

## มาตรฐานในการเขียน Python และ SQL Query

### 1. มาตรฐานการเขียน Python

#### PEP 8 Compliance
```python
# ใช้ snake_case สำหรับตัวแปรและฟังก์ชัน
def get_detection_data_paginated(page: int = 1, per_page: int = 20):
    """Get paginated detection data"""
    pass

# ความยาวบรรทัดสูงสุด 79 ตัวอักษร
long_variable_name = (
    "This is a very long string that needs to be "
    "split across multiple lines"
)
```

#### Docstrings and Comments
```python
def process_lpr_detection(lpr_record: LPRRecord) -> bool:
    """
    Process LPR detection and check for blacklist.
    
    Args:
        lpr_record: LPR record to process
        
    Returns:
        bool: True if blacklisted, False otherwise
        
    Raises:
        DatabaseError: If database operation fails
    """
    # Check if plate is blacklisted
    blacklist_entry = BlacklistService.check_blacklist(lpr_record.plate_number)
    
    if blacklist_entry:
        # Mark record as blacklisted
        lpr_record.is_blacklisted = True
        return True
    
    return False
```

#### Error Handling
```python
try:
    record = LPRRecord(
        camera_id=camera_id,
        plate_number=plate_number,
        confidence=confidence
    )
    db.session.add(record)
    db.session.commit()
except SQLAlchemyError as e:
    db.session.rollback()
    logger.error(f"Database error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise
```

#### Logging
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: dict) -> None:
    logger.info(f"Processing data for camera {data.get('camera_id')}")
    
    try:
        # Process data
        logger.debug("Data processed successfully")
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise
```

#### Modularity
```python
# แยก Code ออกเป็น Module และ Class ที่มีหน้าที่เฉพาะเจาะจง
# src/services/websocket_service.py
# src/services/blacklist_service.py
# src/models/lpr_record.py
```

#### Resource Management
```python
def save_image(image_data: bytes, filename: str) -> str:
    """Save image with proper resource management"""
    file_path = None
    try:
        file_path = os.path.join(Config.IMAGE_STORAGE_PATH, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        return file_path
    except IOError as e:
        logger.error(f"Error saving image: {str(e)}")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise
```

### 2. มาตรฐานการเขียน SQL Query

#### Parameterized Queries
```python
# ✅ ถูกต้อง - ใช้ Parameterized Queries
cursor.execute(
    "INSERT INTO detection_results (license_plate_text, confidence) VALUES (?, ?)",
    (license_plate, confidence)
)

# ❌ ผิด - ใช้ String Concatenation
cursor.execute(
    f"INSERT INTO detection_results (license_plate_text) VALUES ('{license_plate}')"
)
```

#### Readability
```sql
-- ใช้ Uppercase สำหรับ SQL Keywords
SELECT 
    dr.license_plate_text,
    dr.confidence,
    c.camera_id
FROM detection_results dr
INNER JOIN cameras c ON dr.camera_id = c.camera_id
WHERE dr.timestamp >= ?
ORDER BY dr.timestamp DESC
LIMIT 20;
```

#### Indexing
```sql
-- สร้าง Index บนคอลัมน์ที่ใช้บ่อย
CREATE INDEX idx_detection_results_timestamp ON detection_results(timestamp);
CREATE INDEX idx_detection_results_license_plate ON detection_results(license_plate_text);
CREATE INDEX idx_detection_results_camera_id ON detection_results(camera_id);
```

#### Transactions
```python
def save_detection_with_image(detection_data: dict, image_data: bytes) -> bool:
    """Save detection with image in transaction"""
    try:
        db.session.begin()
        
        # Save detection record
        record = LPRRecord(**detection_data)
        db.session.add(record)
        db.session.flush()
        
        # Save image
        image_path = save_image(image_data, f"{record.id}.jpg")
        record.image_path = image_path
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Transaction failed: {str(e)}")
        return False
```

#### Foreign Keys
```python
# กำหนด Foreign Key Constraints
class LPRRecord(db.Model):
    camera_id = db.Column(
        db.String(50), 
        db.ForeignKey('cameras.camera_id'), 
        nullable=False
    )
```

#### Explicit Joins
```sql
-- ✅ ถูกต้อง - ใช้ Explicit Joins
SELECT 
    dr.license_plate_text,
    c.name as camera_name
FROM detection_results dr
INNER JOIN cameras c ON dr.camera_id = c.camera_id
WHERE dr.timestamp >= '2024-01-01';

-- ❌ ผิด - ใช้ Comma-separated Table Names
SELECT 
    dr.license_plate_text,
    c.name as camera_name
FROM detection_results dr, cameras c
WHERE dr.camera_id = c.camera_id;
```

## การทดสอบและ Quality Assurance

### Unit Testing
```python
import unittest
from src.services.blacklist_service import BlacklistService

class TestBlacklistService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
    def test_add_to_blacklist(self):
        """Test adding license plate to blacklist"""
        result = BlacklistService.add_to_blacklist(
            license_plate_text="TEST123",
            reason="Test reason",
            added_by="test_user"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('TEST123', result['message'])
```

### Integration Testing
```python
def test_websocket_connection():
    """Test WebSocket connection and data transmission"""
    client = socketio.test_client(app)
    
    # Test connection
    assert client.is_connected()
    
    # Test camera registration
    client.emit('camera_register', {'camera_id': 'TEST_CAM'})
    received = client.get_received()
    assert len(received) > 0
```

### Performance Testing
```python
def test_database_performance():
    """Test database query performance"""
    import time
    
    start_time = time.time()
    records = LPRRecord.query.filter_by(camera_id='CAM001').all()
    end_time = time.time()
    
    # Query should complete within 100ms
    assert (end_time - start_time) < 0.1
```

## การ Deploy และ Production

### Environment Variables
```bash
# .env.production
FLASK_CONFIG=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///lprserver_prod.db
LOG_LEVEL=INFO
```

### Systemd Services
```ini
# /etc/systemd/system/lprserver.service
[Unit]
Description=LPR Server v3
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/devuser/lprserver_v3
Environment=FLASK_CONFIG=production
ExecStart=/home/devuser/lprserver_v3/venv/bin/gunicorn --workers 4 --bind unix:/tmp/lprserver.sock wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://unix:/tmp/lprserver.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io/ {
        proxy_pass http://unix:/tmp/lprserver.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## การบำรุงรักษาและ Monitoring

### Logging Strategy
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Setup application logging"""
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/lprserver.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('LPR Server startup')
```

### Health Monitoring
```python
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check disk space
        disk_usage = shutil.disk_usage(Config.IMAGE_STORAGE_PATH)
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'disk_usage_percent': disk_percent,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

## สรุป

การพัฒนาระบบ LPR Server v3 นี้จะดำเนินการตามลำดับขั้นตอนที่กำหนดไว้ โดยเน้นการสร้างรากฐานที่แข็งแกร่งก่อน แล้วค่อยๆ เพิ่มฟีเจอร์ขั้นสูง การใช้มาตรฐานการเขียนโค้ดที่กำหนดไว้จะช่วยให้ระบบมีความสอดคล้องกัน ง่ายต่อการบำรุงรักษา และมีประสิทธิภาพสูง
