# LPR Server v3 - Systemd Setup Guide

## ภาพรวม

ระบบ LPR Server v3 ใช้ systemd services 2 ตัว:
1. **lprserver.service** - Main Flask application (Gunicorn) - รับผิดชอบ Web UI และ REST API
2. **lprserver-websocket.service** - WebSocket server - รับผิดชอบการสื่อสารกับ Edge AI Cameras

### สถานะระบบล่าสุด (อัปเดต: 12 สิงหาคม 2025)
- ✅ **ระบบทำงานได้อย่างสมบูรณ์**
- ✅ **WebSocket Event Handlers** - แก้ไขปัญหา parameter mismatch
- ✅ **BlacklistService Methods** - เพิ่ม class method และแก้ไขการเรียกใช้
- ✅ **API Endpoints** - แก้ไขการเรียกใช้ services ผ่าน dependency container
- ✅ **Database Operations** - เพิ่ม imports ที่จำเป็น

## การติดตั้งและตั้งค่า Auto Start

### 1. ติดตั้ง Services

```bash
# ให้สิทธิ์การรัน script
chmod +x manage_services.sh

# ติดตั้งและเปิดใช้งาน services
./manage_services.sh install
```

คำสั่งนี้จะ:
- คัดลอก service files ไปยัง `/etc/systemd/system/`
- ตรวจสอบและ migrate จาก `websocket_server.service` เก่า (ถ้ามี)
- เปิดใช้งาน services ให้เริ่มต้นอัตโนมัติเมื่อ boot

### 2. ตรวจสอบการติดตั้ง

```bash
# ตรวจสอบสถานะ services
./manage_services.sh status
```

### 3. เริ่มต้น Services

```bash
# เริ่มต้น services
./manage_services.sh start
```

## การจัดการ Services

### ตรวจสอบสถานะ
```bash
./manage_services.sh status
```

### ดู Logs
```bash
# ดู logs แบบ real-time
./manage_services.sh logs

# หรือดู logs แบบ manual
sudo journalctl -u lprserver.service -f
sudo journalctl -u lprserver-websocket.service -f
```

### รีสตาร์ท Services
```bash
./manage_services.sh restart
```

### หยุด Services
```bash
./manage_services.sh stop
```

### เปิด/ปิด Auto Start
```bash
# เปิดใช้งาน auto start
./manage_services.sh enable

# ปิดใช้งาน auto start
./manage_services.sh disable
```

## การ Migrate จาก Service เก่า

หากคุณมี `websocket_server.service` เก่าอยู่:

```bash
# Migrate จาก service เก่า
./manage_services.sh migrate
```

หรือเมื่อรัน `install` จะถามให้ migrate อัตโนมัติ

## การตรวจสอบระบบ

### 1. ตรวจสอบ Services
```bash
# ตรวจสอบสถานะ
systemctl status lprserver.service
systemctl status lprserver-websocket.service

# ตรวจสอบว่า enabled หรือไม่
systemctl is-enabled lprserver.service
systemctl is-enabled lprserver-websocket.service
```

### 2. ตรวจสอบ Ports
```bash
# ตรวจสอบ WebSocket port 8765
netstat -tlnp | grep 8765

# ตรวจสอบ Unix socket
ls -la /tmp/lprserver.sock
```

### 3. ตรวจสอบ Nginx
```bash
# ตรวจสอบ nginx status
sudo systemctl status nginx

# ตรวจสอบ nginx config
sudo nginx -t

# ดู nginx logs
sudo tail -f /var/log/nginx/lprserver_access.log
```

## การแก้ไขปัญหา

### 1. Service ไม่เริ่มต้น
```bash
# ตรวจสอบ logs
sudo journalctl -u lprserver.service -n 50
sudo journalctl -u lprserver-websocket.service -n 50

# ตรวจสอบ permissions
ls -la /home/devuser/lprserver_v3/
ls -la /tmp/lprserver.sock
```

### 2. Permission Issues
```bash
# แก้ไข permissions
sudo chown -R devuser:devgroup /home/devuser/lprserver_v3
sudo chmod +x /home/devuser/lprserver_v3/websocket_server.py
sudo chmod +x /home/devuser/lprserver_v3/wsgi.py
```

### 3. Virtual Environment Issues
```bash
# ตรวจสอบ virtual environment
ls -la /home/devuser/lprserver_v3/venv/bin/python

# สร้าง virtual environment ใหม่ (ถ้าจำเป็น)
cd /home/devuser/lprserver_v3
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Database Issues
```bash
# ตรวจสอบ database
ls -la /home/devuser/lprserver_v3/*.db

# สร้าง database ใหม่ (ถ้าจำเป็น)
cd /home/devuser/lprserver_v3
source venv/bin/activate
python3 -c "
from src.app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database created successfully')
"
```

## การตั้งค่า Boot Order

### 1. ตรวจสอบ Dependencies
```bash
# ตรวจสอบ service dependencies
systemctl list-dependencies lprserver.service
systemctl list-dependencies lprserver-websocket.service
```

### 2. ตั้งค่า Boot Order (ถ้าจำเป็น)
```bash
# แก้ไข service files เพื่อตั้งค่า dependencies
sudo systemctl edit lprserver.service
sudo systemctl edit lprserver-websocket.service
```

## การ Monitor และ Maintenance

### 1. ตั้งค่า Log Rotation
```bash
# สร้าง logrotate config
sudo tee /etc/logrotate.d/lprserver << EOF
/var/log/lprserver/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 devuser devgroup
}
EOF
```

### 2. ตั้งค่า Health Check
```bash
# สร้าง health check script
cat > /home/devuser/lprserver_v3/health_check.sh << 'EOF'
#!/bin/bash
# Health check script

# Check if services are running
if ! systemctl is-active --quiet lprserver.service; then
    echo "lprserver.service is not running"
    exit 1
fi

if ! systemctl is-active --quiet lprserver-websocket.service; then
    echo "lprserver-websocket.service is not running"
    exit 1
fi

# Check if web interface is accessible
if ! curl -f http://localhost/ > /dev/null 2>&1; then
    echo "Web interface is not accessible"
    exit 1
fi

echo "All services are running normally"
exit 0
EOF

chmod +x /home/devuser/lprserver_v3/health_check.sh
```

### 3. ตั้งค่า Cron Job สำหรับ Health Check
```bash
# เพิ่ม cron job
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/devuser/lprserver_v3/health_check.sh") | crontab -
```

## การ Backup และ Recovery

### 1. Backup Configuration
```bash
# Backup service files
sudo cp /etc/systemd/system/lprserver.service /home/devuser/lprserver_v3/backup/
sudo cp /etc/systemd/system/lprserver-websocket.service /home/devuser/lprserver_v3/backup/

# Backup nginx config
sudo cp /etc/nginx/sites-available/lprserver /home/devuser/lprserver_v3/backup/
```

### 2. Backup Database
```bash
# Backup SQLite database
cp /home/devuser/lprserver_v3/*.db /home/devuser/lprserver_v3/backup/
```

### 3. Recovery Procedure
```bash
# Restore services
sudo cp /home/devuser/lprserver_v3/backup/lprserver.service /etc/systemd/system/
sudo cp /home/devuser/lprserver_v3/backup/lprserver-websocket.service /etc/systemd/system/
sudo systemctl daemon-reload
./manage_services.sh restart
```

## สรุป

หลังจากรัน `./manage_services.sh install` และ `./manage_services.sh start` แล้ว:

1. ✅ **Services จะเริ่มต้นอัตโนมัติเมื่อ boot**
2. ✅ **Web Interface**: http://localhost
3. ✅ **WebSocket Server**: ws://localhost:8765
4. ✅ **API Endpoints**: http://localhost/api
5. ✅ **Logs**: ดูได้ผ่าน `./manage_services.sh logs`

### คำสั่งที่ใช้บ่อย:
```bash
./manage_services.sh status    # ตรวจสอบสถานะ
./manage_services.sh logs      # ดู logs
./manage_services.sh restart   # รีสตาร์ท
./manage_services.sh stop      # หยุด services
```

ระบบจะทำงานอัตโนมัติและพร้อมใช้งานในสภาพแวดล้อมจริง!
