# LPR Server v3

ระบบ LPR Server v3 เป็นระบบจัดการข้อมูลการอ่านป้ายทะเบียนรถยนต์ ที่รับข้อมูลจาก Edge Camera ผ่าน WebSocket และแสดงผลในรูปแบบตาราง

## คุณสมบัติหลัก

- ✅ รับข้อมูลจาก Edge Camera ผ่าน WebSocket (Port 8765)
- ✅ บันทึกข้อมูลลงฐานข้อมูล SQLite
- ✅ บันทึกภาพลงใน storage directory
- ✅ แสดงผลในรูปแบบตารางพร้อมการกรองข้อมูล
- ✅ แดชบอร์ดแสดงสถิติการใช้งาน
- ✅ REST API สำหรับการเข้าถึงข้อมูล
- ✅ Real-time updates ผ่าน WebSocket
- ✅ ระบบจัดการด้วย systemd service
- ✅ Reverse proxy ด้วย nginx
- ✅ ระบบจัดการ Blacklist สำหรับป้ายทะเบียน
- ✅ การตรวจจับและแจ้งเตือนป้ายทะเบียนที่อยู่ใน blacklist
- ✅ สถิติการใช้งานแบบ real-time
- ✅ Health monitoring system

## โครงสร้างโปรเจกต์

```
lprserver_v3/
├── src/                    # Source code
│   ├── app.py             # Flask application factory
│   ├── web/               # Web application
│   │   └── blueprints/    # Flask blueprints
│   │       ├── main.py    # Main web routes
│   │       └── api.py     # API routes
│   ├── services/          # Business logic services
│   │   ├── websocket_service.py  # WebSocket handling
│   │   ├── blacklist_service.py  # Blacklist management
│   │   ├── health_service.py     # Health monitoring
│   │   └── database_service.py   # Database operations
│   └── core/              # Core components
│       ├── models/        # Database models
│       │   ├── lpr_record.py     # LPR Record model
│       │   ├── blacklist_plate.py # Blacklist model
│       │   ├── camera.py         # Camera model
│       │   └── health_check.py   # Health check model
│       ├── dependency_container.py # Dependency injection
│       └── import_helper.py      # Import utilities
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── dashboard.html     # Dashboard page
│   ├── records.html       # Records table page
│   └── blacklist.html     # Blacklist management page
├── storage/               # File storage
│   └── images/            # LPR images
├── logs/                  # Application logs
├── database/              # Database files
├── nginx/                 # Nginx configuration
│   └── lprserver.conf     # Nginx config
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── run.py                 # Development server
├── wsgi.py                # Production WSGI entry
├── websocket_server.py    # WebSocket server
├── setup.sh               # Setup script
├── lprserver.service      # Main service
├── lprserver-websocket.service  # WebSocket service
└── README.md              # This file
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

3. **ตรวจสอบสถานะ**
   ```bash
   sudo systemctl status lprserver.service
   sudo systemctl status lprserver-websocket.service
   sudo systemctl status nginx
   ```

## การใช้งาน

### Web Interface

- **หน้าแรก**: http://localhost
- **แดชบอร์ด**: http://localhost/dashboard
- **รายการบันทึก**: http://localhost/records
- **จัดการ Blacklist**: http://localhost/blacklist

### WebSocket Server

- **Port**: 8765
- **Protocol**: WebSocket
- **Events**:
  - `camera_register`: ลงทะเบียนกล้อง
  - `lpr_data`: ส่งข้อมูล LPR

### API Endpoints

#### LPR Records
- `GET /api/records` - ดึงรายการบันทึก
- `GET /api/records/<id>` - ดึงบันทึกเฉพาะ
- `POST /api/records` - สร้างบันทึกใหม่
- `GET /api/statistics` - ดึงสถิติระบบ

#### Blacklist Management
- `GET /api/blacklist` - ดึงรายการ blacklist
- `POST /api/blacklist` - เพิ่มป้ายทะเบียนใน blacklist
- `DELETE /api/blacklist/<id>` - ลบป้ายทะเบียนจาก blacklist
- `GET /api/blacklist/statistics` - ดึงสถิติ blacklist
- `GET /api/blacklist/detections` - ดึงการตรวจจับ blacklist

## การส่งข้อมูลจาก Edge Camera

### การเชื่อมต่อ WebSocket

```javascript
const socket = io('ws://your-server:8765');

// ลงทะเบียนกล้อง
socket.emit('camera_register', {
    camera_id: 'CAM001'
});

// ส่งข้อมูล LPR
socket.emit('lpr_data', {
    camera_id: 'CAM001',
    plate_number: 'กข1234',
    confidence: 85.5,
    image_data: 'base64_encoded_image_data',
    location: 'ประตูหน้า'
});
```

### ตัวอย่างข้อมูล JSON

```json
{
    "camera_id": "CAM001",
    "plate_number": "กข1234",
    "confidence": 85.5,
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "location": "ประตูหน้า"
}
```

## การจัดการระบบ

### ตรวจสอบสถานะ

```bash
# ตรวจสอบสถานะ services
sudo systemctl status lprserver.service
sudo systemctl status lprserver-websocket.service
sudo systemctl status nginx

# ดู logs
sudo journalctl -u lprserver.service -f
sudo journalctl -u lprserver-websocket.service -f
sudo tail -f /var/log/nginx/lprserver_access.log
```

### การรีสตาร์ท

```bash
# รีสตาร์ท services
sudo systemctl restart lprserver.service
sudo systemctl restart lprserver-websocket.service
sudo systemctl restart nginx
```

### การอัปเดต

```bash
# Pull โค้ดใหม่
git pull

# รีสตาร์ท services
sudo systemctl restart lprserver.service
sudo systemctl restart lprserver-websocket.service
```

## การกำหนดค่า

### Environment Variables

- `FLASK_CONFIG`: การกำหนดค่า (development/production)
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: URL ฐานข้อมูล
- `IMAGE_STORAGE_PATH`: Path สำหรับเก็บภาพ
- `LOG_LEVEL`: ระดับ logging

### การกำหนดค่า Nginx

ไฟล์: `/etc/nginx/sites-available/lprserver`

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://unix:/tmp/lprserver.sock;
        # ... other settings
    }
}
```

## การพัฒนา

### Development Mode

```bash
# เปิดใช้งาน development mode
export FLASK_CONFIG=development
export FLASK_DEBUG=true

# รัน development server
python run.py
```

### การทดสอบ

#### ทดสอบ WebSocket Connection
```bash
# ทดสอบ WebSocket connection
python -c "
import socketio
sio = socketio.Client()
sio.connect('http://localhost:8765')
sio.emit('camera_register', {'camera_id': 'TEST_CAM'})
sio.disconnect()
"
```

#### ทดสอบ API Endpoints
```bash
# ทดสอบการเพิ่ม blacklist
curl -X POST http://localhost:5000/api/blacklist \
  -H "Content-Type: application/json" \
  -d '{"license_plate_text": "กข1234", "reason": "ทดสอบระบบ", "added_by": "admin"}'

# ทดสอบการดึงข้อมูล blacklist
curl http://localhost:5000/api/blacklist

# ทดสอบการสร้าง LPR record
curl -X POST http://localhost:5000/api/records \
  -H "Content-Type: application/json" \
  -d '{"camera_id": "CAM001", "plate_number": "กข1234", "confidence": 0.95, "location": "หน้าหอพัก"}'

# ทดสอบการดึงสถิติ
curl http://localhost:5000/api/statistics
curl http://localhost:5000/api/blacklist/statistics
```

#### ทดสอบระบบอัตโนมัติ
```bash
# รัน test script
python test_system.py
```

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

1. **Service ไม่เริ่มต้น**
   ```bash
   sudo journalctl -u lprserver.service -f
   ```

2. **WebSocket Connection Errors**
   ```bash
   # ตรวจสอบ WebSocket service
   sudo journalctl -u lprserver-websocket.service -f
   
   # ตรวจสอบ port 8765
   netstat -tlnp | grep 8765
   ```

3. **API Endpoint Errors**
   ```bash
   # ตรวจสอบ Flask application logs
   tail -f logs/app.log
   
   # ทดสอบ API endpoints
   curl -v http://localhost:5000/api/blacklist
   ```

4. **Database error**
   ```bash
   # ตรวจสอบฐานข้อมูล
   sqlite3 database/lprserver.db ".tables"
   
   # ตรวจสอบ database permissions
   ls -la database/
   ```

5. **Nginx error**
   ```bash
   sudo nginx -t
   sudo tail -f /var/log/nginx/error.log
   ```

6. **Permission error**
   ```bash
   sudo chown -R www-data:www-data /home/devuser/lprserver_v3
   sudo chmod -R 755 /home/devuser/lprserver_v3
   ```

7. **Blacklist System Issues**
   ```bash
   # ตรวจสอบ blacklist service
   python -c "from src.services.blacklist_service import BlacklistService; print('BlacklistService imported successfully')"
   
   # ตรวจสอบ database models
   python -c "from core.models.blacklist_plate import BlacklistPlate; print('BlacklistPlate model loaded')"
   ```

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

## การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ กรุณาเปิด issue ใน repository หรือติดต่อทีมพัฒนา

## License

MIT License
