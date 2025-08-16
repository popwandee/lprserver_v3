# LPR Server v3 - Installation and Setup Guide

## ภาพรวม

คู่มือการติดตั้งและตั้งค่าระบบ LPR Server v3 พร้อมระบบ Unified Communication ที่รองรับ WebSocket, REST API, และ MQTT

## ข้อกำหนดระบบ (System Requirements)

### Hardware Requirements
- **CPU**: 2 cores หรือมากกว่า
- **RAM**: 4GB หรือมากกว่า
- **Storage**: 20GB หรือมากกว่า
- **Network**: การเชื่อมต่ออินเทอร์เน็ต

### Software Requirements
- **OS**: Ubuntu 22.04 LTS หรือใหม่กว่า
- **Python**: 3.11 หรือใหม่กว่า
- **PostgreSQL**: 16 หรือใหม่กว่า
- **Git**: สำหรับการ clone repository

## การติดตั้ง (Installation)

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/lprserver_v3.git
cd lprserver_v3
```

### 2. ติดตั้ง Dependencies

```bash
# สร้าง virtual environment
python3 -m venv venv

# เปิดใช้งาน virtual environment
source venv/bin/activate

# ติดตั้ง Python packages
pip install -r requirements.txt
```

### 3. ตั้งค่าฐานข้อมูล PostgreSQL

#### 3.1 ติดตั้ง PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### 3.2 สร้าง User และ Database

```bash
# เข้าไปใน PostgreSQL
sudo -u postgres psql

# สร้าง user
CREATE USER lpruser WITH PASSWORD 'admin88366';

# สร้าง database
CREATE DATABASE lprserver_v3 OWNER lpruser;

# ให้สิทธิ์
GRANT ALL PRIVILEGES ON DATABASE lprserver_v3 TO lpruser;

# ออกจาก PostgreSQL
\q
```

#### 3.3 ตั้งค่า Authentication

แก้ไขไฟล์ `/etc/postgresql/16/main/pg_hba.conf`:

```bash
sudo sed -i 's/md5/scram-sha-256/g' /etc/postgresql/16/main/pg_hba.conf
sudo systemctl reload postgresql
```

### 4. ตั้งค่า Environment Variables

สร้างไฟล์ `.env`:

```bash
# Flask Configuration
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://lpruser:admin88366@localhost:5432/lprserver_v3

# File Storage Configuration
IMAGE_STORAGE_PATH=storage/images

# WebSocket Configuration
SOCKETIO_ASYNC_MODE=eventlet

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/lprserver.log

# Health Monitoring Configuration
HEALTH_CHECK_INTERVAL_MINUTES=5
HEALTH_CHECK_RETENTION_DAYS=7

# Database Cleanup Configuration
DATA_RETENTION_DAYS=30
HEALTH_CHECK_RETENTION_DAYS=7

# System Configuration
RECORDS_PER_PAGE=20
MAX_IMAGE_SIZE=10485760  # 10MB in bytes

# Security Configuration
SECRET_KEY_MIN_LENGTH=32
PASSWORD_MIN_LENGTH=8

# Network Configuration
WEBSOCKET_PORT=8765
DEFAULT_HTTP_PORT=5000
DEFAULT_NGINX_PORT=80

# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=lpruser
MQTT_PASSWORD=admin88366
MQTT_CLIENT_ID=lprserver_v3
MQTT_TLS_ENABLED=false
```

### 5. สร้าง Directories

```bash
# สร้าง directories ที่จำเป็น
mkdir -p storage/images
mkdir -p logs
mkdir -p database
```

### 6. ตั้งค่า Python Path

```bash
export PYTHONPATH="${PYTHONPATH}:/home/devuser/lprserver_v3/src"
```

## การทดสอบ (Testing)

### 1. ทดสอบการเชื่อมต่อฐานข้อมูล

```bash
PGPASSWORD=admin88366 psql -h localhost -U lpruser -d lprserver_v3 -c "SELECT version();"
```

### 2. ทดสอบระบบพื้นฐาน

```bash
python test_simple_communication.py
```

### 3. ทดสอบระบบเต็มรูปแบบ

```bash
python test_unified_communication.py --test-type all --verbose
```

## การตั้งค่า MQTT Broker (Optional)

### ติดตั้ง Mosquitto MQTT Broker

```bash
sudo apt install mosquitto mosquitto-clients

# ตั้งค่า authentication
sudo mosquitto_passwd -c /etc/mosquitto/passwd lpruser
# ใส่รหัสผ่าน: admin88366

# แก้ไขไฟล์ config
sudo nano /etc/mqtt/mosquitto.conf

# เพิ่มบรรทัดต่อไปนี้:
allow_anonymous false
password_file /etc/mosquitto/passwd
listener 1883

# รีสตาร์ท service
sudo systemctl restart mosquitto
```

## การตั้งค่า WebSocket Server

### 1. เริ่ม WebSocket Server

```bash
python wsgi.py
```

### 2. ทดสอบ WebSocket Connection

```bash
python test_client.py
```

## การตั้งค่า Systemd Services

### 1. สร้าง Service Files

#### LPR Server Service

```bash
sudo nano /etc/systemd/system/lprserver.service
```

เนื้อหา:
```ini
[Unit]
Description=LPR Server v3
After=network.target postgresql.service

[Service]
Type=simple
User=devuser
WorkingDirectory=/home/devuser/lprserver_v3
Environment=PATH=/home/devuser/lprserver_v3/venv/bin
ExecStart=/home/devuser/lprserver_v3/venv/bin/python wsgi.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### WebSocket Service

```bash
sudo nano /etc/systemd/system/lprserver-websocket.service
```

เนื้อหา:
```ini
[Unit]
Description=LPR Server v3 WebSocket
After=network.target postgresql.service

[Service]
Type=simple
User=devuser
WorkingDirectory=/home/devuser/lprserver_v3
Environment=PATH=/home/devuser/lprserver_v3/venv/bin
ExecStart=/home/devuser/lprserver_v3/venv/bin/python websocket_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. เปิดใช้งาน Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable lprserver
sudo systemctl enable lprserver-websocket
sudo systemctl start lprserver
sudo systemctl start lprserver-websocket
```

## การตั้งค่า Nginx (Optional)

### 1. ติดตั้ง Nginx

```bash
sudo apt install nginx
```

### 2. สร้าง Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/lprserver
```

เนื้อหา:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. เปิดใช้งาน Site

```bash
sudo ln -s /etc/nginx/sites-available/lprserver /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## การตรวจสอบสถานะ (Status Check)

### 1. ตรวจสอบ Services

```bash
sudo systemctl status lprserver
sudo systemctl status lprserver-websocket
sudo systemctl status postgresql
sudo systemctl status mosquitto
```

### 2. ตรวจสอบ Logs

```bash
# LPR Server logs
tail -f logs/lprserver.log

# System logs
sudo journalctl -u lprserver -f
sudo journalctl -u lprserver-websocket -f
```

### 3. ตรวจสอบการเชื่อมต่อ

```bash
# ตรวจสอบ WebSocket port
netstat -tlnp | grep 8765

# ตรวจสอบ HTTP port
netstat -tlnp | grep 5000

# ตรวจสอบ MQTT port
netstat -tlnp | grep 1883
```

## การแก้ไขปัญหา (Troubleshooting)

### ปัญหาการเชื่อมต่อฐานข้อมูล

```bash
# ตรวจสอบ PostgreSQL status
sudo systemctl status postgresql

# ตรวจสอบ authentication
sudo grep -E "(local|host)" /etc/postgresql/16/main/pg_hba.conf

# ทดสอบการเชื่อมต่อ
PGPASSWORD=admin88366 psql -h localhost -U lpruser -d lprserver_v3 -c "SELECT 1;"
```

### ปัญหา MQTT Connection

```bash
# ตรวจสอบ Mosquitto status
sudo systemctl status mosquitto

# ทดสอบ MQTT connection
mosquitto_pub -h localhost -u lpruser -P admin88366 -t test/topic -m "test message"
```

### ปัญหา WebSocket Connection

```bash
# ตรวจสอบ WebSocket service
sudo systemctl status lprserver-websocket

# ตรวจสอบ port
netstat -tlnp | grep 8765

# ทดสอบ WebSocket
python test_client.py
```

## การอัพเกรด (Upgrade)

### 1. Backup ข้อมูล

```bash
# Backup database
pg_dump -h localhost -U lpruser lprserver_v3 > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup configuration
cp .env .env.backup
```

### 2. อัพเดต Code

```bash
git pull origin main
pip install -r requirements.txt
```

### 3. รีสตาร์ท Services

```bash
sudo systemctl restart lprserver
sudo systemctl restart lprserver-websocket
```

## การบำรุงรักษา (Maintenance)

### 1. การทำความสะอาดข้อมูลเก่า

```bash
# รัน cleanup script
python cleanup_old_data.py
```

### 2. การ optimize ฐานข้อมูล

```bash
# เข้าไปใน PostgreSQL
sudo -u postgres psql lprserver_v3

# รัน VACUUM
VACUUM ANALYZE;

# ออก
\q
```

### 3. การ backup ข้อมูล

```bash
# สร้าง backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U lpruser lprserver_v3 > backup_$DATE.sql
gzip backup_$DATE.sql
echo "Backup created: backup_$DATE.sql.gz"
EOF

chmod +x backup.sh
```

## การติดตั้งบน Production

### 1. ตั้งค่า Security

```bash
# ปิดการเข้าถึง PostgreSQL จากภายนอก
sudo ufw deny 5432

# เปิดเฉพาะ port ที่จำเป็น
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8765
```

### 2. ตั้งค่า SSL/TLS

```bash
# ติดตั้ง Certbot
sudo apt install certbot python3-certbot-nginx

# สร้าง SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. ตั้งค่า Monitoring

```bash
# ติดตั้ง monitoring tools
sudo apt install htop iotop nethogs

# ตั้งค่า log rotation
sudo nano /etc/logrotate.d/lprserver
```

## สรุป

ระบบ LPR Server v3 พร้อมระบบ Unified Communication ได้รับการติดตั้งและตั้งค่าเรียบร้อยแล้ว ระบบสามารถ:

- ✅ รับข้อมูลจาก Edge Devices ผ่าน WebSocket, REST API, และ MQTT
- ✅ เปลี่ยน protocol อัตโนมัติตามสภาพการเชื่อมต่อ
- ✅ บันทึกข้อมูลลงฐานข้อมูล PostgreSQL แบบรวมศูนย์
- ✅ แสดงผลผ่าน Web Interface แบบ real-time
- ✅ ติดตามสถานะระบบและสุขภาพการเชื่อมต่อ

สำหรับการใช้งานเพิ่มเติม โปรดดูเอกสาร DEVELOPMENT_GUIDE.md และ README.md
