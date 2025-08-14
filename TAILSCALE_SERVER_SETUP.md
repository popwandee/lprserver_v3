# คู่มือการตั้งค่า Tailscale Server สำหรับ LPR Server

## ภาพรวม

เอกสารนี้เป็นคู่มือสำหรับผู้ดูแลระบบในการตั้งค่า Tailscale Server เพื่อให้ผู้ใช้สามารถเข้าถึง LPR Server v3 ผ่านเครือข่าย VPN ได้

### ข้อมูลระบบ
- **Server Hostname**: `lprser`
- **Tailscale Domain**: `lprser.tailxxxxxx.ts.net`
- **Web Interface**: `http://lprser.tailxxxxxx.ts.net`
- **WebSocket Server**: `ws://lprser.tailxxxxxx.ts.net:8765`
- **API Base URL**: `http://lprser.tailxxxxxx.ts.net/api`

---

## 1. การติดตั้ง Tailscale บน Server

### 1.1 Ubuntu/Debian Server

#### ขั้นตอนการติดตั้ง
1. **เพิ่ม Tailscale repository**
   ```bash
   curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
   curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
   ```

2. **ติดตั้ง Tailscale**
   ```bash
   sudo apt update
   sudo apt install tailscale
   ```

3. **เริ่มต้น Tailscale**
   ```bash
   sudo tailscale up
   ```

4. **ตรวจสอบการเชื่อมต่อ**
   ```bash
   tailscale status
   ```

#### การตั้งค่า Hostname
```bash
# ตั้งค่า hostname
sudo hostnamectl set-hostname lprser

# ตรวจสอบ hostname
hostname

# รีสตาร์ท Tailscale เพื่อใช้ hostname ใหม่
sudo tailscale down
sudo tailscale up
```

### 1.2 การตั้งค่า Tailscale Admin Console

#### 1. เข้าสู่ Tailscale Admin Console
- ไปที่ https://login.tailscale.com/admin/machines
- เข้าสู่ระบบด้วย Google หรือ Microsoft account

#### 2. ตรวจสอบเครื่อง Server
- ตรวจสอบว่าเครื่อง `lprser` แสดงในรายการ
- ตรวจสอบ IP address และสถานะการเชื่อมต่อ

#### 3. ตั้งค่า DNS Name
- คลิกที่เครื่อง `lprser`
- ไปที่ "DNS" tab
- ตั้งค่า DNS name เป็น `lprser.tailxxxxxx.ts.net`

#### 4. ตั้งค่า Access Control
- ไปที่ "Access Control" tab
- ตั้งค่า permissions สำหรับผู้ใช้

---

## 2. การตั้งค่า Firewall

### 2.1 การเปิด Ports ที่จำเป็น

#### สำหรับ LPR Server
```bash
# เปิด port 80 (HTTP)
sudo ufw allow 80/tcp

# เปิด port 5000 (Flask development)
sudo ufw allow 5000/tcp

# เปิด port 8765 (WebSocket)
sudo ufw allow 8765/tcp

# เปิด port สำหรับ Tailscale
sudo ufw allow 41641/udp
sudo ufw allow 41641/tcp
```

#### ตรวจสอบ Firewall Status
```bash
# ตรวจสอบสถานะ firewall
sudo ufw status

# ตรวจสอบ ports ที่เปิดอยู่
sudo netstat -tlnp
```

### 2.2 การตั้งค่า Nginx

#### ตรวจสอบ Nginx Configuration
```bash
# ตรวจสอบ configuration
sudo nginx -t

# ตรวจสอบ status
sudo systemctl status nginx

# ดู configuration file
sudo cat /etc/nginx/sites-available/lprserver
```

#### การตั้งค่า WebSocket Proxy
```nginx
# เพิ่มใน nginx configuration
location /socket.io/ {
    proxy_pass http://localhost:8765;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## 3. การตั้งค่า DNS

### 3.1 การตั้งค่า Tailscale DNS

#### เปิดใช้งาน Tailscale DNS
```bash
# เปิดใช้งาน Tailscale DNS
sudo tailscale up --accept-dns

# ตรวจสอบ DNS settings
tailscale status
```

#### ตรวจสอบ DNS Resolution
```bash
# ทดสอบ DNS resolution
nslookup lprser.tailxxxxxx.ts.net

# ทดสอบ ping
ping lprser.tailxxxxxx.ts.net
```

### 3.2 การตั้งค่า Local DNS (Optional)

#### ตั้งค่า /etc/hosts
```bash
# แก้ไขไฟล์ /etc/hosts
sudo nano /etc/hosts

# เพิ่มบรรทัดนี้
100.x.y.z lprser.tailxxxxxx.ts.net lprser
```

---

## 4. การตั้งค่า SSL/TLS (Optional)

### 4.1 การใช้ Let's Encrypt

#### ติดตั้ง Certbot
```bash
# ติดตั้ง certbot
sudo apt install certbot python3-certbot-nginx

# ขอ certificate
sudo certbot --nginx -d lprser.tailxxxxxx.ts.net

# ตั้งค่า auto-renewal
sudo crontab -e
# เพิ่มบรรทัดนี้
0 12 * * * /usr/bin/certbot renew --quiet
```

#### การตั้งค่า Nginx สำหรับ HTTPS
```nginx
server {
    listen 443 ssl;
    server_name lprser.tailxxxxxx.ts.net;
    
    ssl_certificate /etc/letsencrypt/live/lprser.tailxxxxxx.ts.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lprser.tailxxxxxx.ts.net/privkey.pem;
    
    location / {
        proxy_pass http://unix:/tmp/lprserver.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /socket.io/ {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name lprser.tailxxxxxx.ts.net;
    return 301 https://$server_name$request_uri;
}
```

---

## 5. การตั้งค่า Monitoring

### 5.1 การตรวจสอบสถานะ

#### สร้าง Monitoring Script
```bash
#!/bin/bash
# /usr/local/bin/monitor-lprserver.sh

# ตรวจสอบ Tailscale status
echo "=== Tailscale Status ==="
tailscale status

# ตรวจสอบ LPR Server services
echo "=== LPR Server Services ==="
sudo systemctl status lprserver.service --no-pager
sudo systemctl status lprserver-websocket.service --no-pager

# ตรวจสอบ Nginx
echo "=== Nginx Status ==="
sudo systemctl status nginx --no-pager

# ตรวจสอบ ports
echo "=== Open Ports ==="
sudo netstat -tlnp | grep -E ':(80|5000|8765)'

# ตรวจสอบ disk space
echo "=== Disk Space ==="
df -h

# ตรวจสอบ memory usage
echo "=== Memory Usage ==="
free -h
```

#### ตั้งค่า Cron Job
```bash
# แก้ไข crontab
sudo crontab -e

# เพิ่มบรรทัดนี้เพื่อตรวจสอบทุก 5 นาที
*/5 * * * * /usr/local/bin/monitor-lprserver.sh >> /var/log/lprserver-monitor.log 2>&1
```

### 5.2 การตั้งค่า Logging

#### ตั้งค่า Log Rotation
```bash
# สร้างไฟล์ logrotate configuration
sudo nano /etc/logrotate.d/lprserver

# เพิ่มเนื้อหานี้
/var/log/lprserver*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload lprserver.service
    endscript
}
```

---

## 6. การตั้งค่า Security

### 6.1 การตั้งค่า Access Control

#### ตั้งค่า Tailscale ACLs
```json
// tailscale ACLs configuration
{
  "tagOwners": {
    "tag:lprserver": ["admin@company.com"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:lprserver"],
      "dst": ["lprser.tailxxxxxx.ts.net:80", "lprser.tailxxxxxx.ts.net:8765"]
    }
  ]
}
```

#### ตั้งค่า Firewall Rules
```bash
# จำกัดการเข้าถึงเฉพาะ Tailscale network
sudo ufw deny from any to any port 80
sudo ufw allow from 100.64.0.0/10 to any port 80
sudo ufw allow from 100.64.0.0/10 to any port 8765
```

### 6.2 การตั้งค่า Authentication

#### ตั้งค่า Basic Authentication (Optional)
```nginx
# เพิ่มใน nginx configuration
location / {
    auth_basic "LPR Server Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    proxy_pass http://unix:/tmp/lprserver.sock;
    # ... other settings
}
```

#### สร้าง Password File
```bash
# สร้าง password file
sudo htpasswd -c /etc/nginx/.htpasswd username
```

---

## 7. การทดสอบระบบ

### 7.1 การทดสอบการเชื่อมต่อ

#### ทดสอบจาก Server
```bash
# ทดสอบ HTTP
curl -I http://lprser.tailxxxxxx.ts.net

# ทดสอบ API
curl http://lprser.tailxxxxxx.ts.net/api/statistics

# ทดสอบ WebSocket
curl -I http://lprser.tailxxxxxx.ts.net:8765
```

#### ทดสอบจาก Client
```bash
# ทดสอบ ping
ping lprser.tailxxxxxx.ts.net

# ทดสอบ traceroute
traceroute lprser.tailxxxxxx.ts.net

# ทดสอบ HTTP
curl -I http://lprser.tailxxxxxx.ts.net
```

### 7.2 การทดสอบ Performance

#### ทดสอบ Response Time
```bash
# ทดสอบ API response time
time curl -s http://lprser.tailxxxxxx.ts.net/api/statistics

# ทดสอบ WebSocket connection
python test_client.py
```

#### ทดสอบ Load
```bash
# ทดสอบ load ด้วย ab
ab -n 100 -c 10 http://lprser.tailxxxxxx.ts.net/api/statistics
```

---

## 8. การบำรุงรักษา

### 8.1 การอัปเดตระบบ

#### อัปเดต Tailscale
```bash
# อัปเดต Tailscale
sudo apt update
sudo apt upgrade tailscale

# รีสตาร์ท Tailscale
sudo systemctl restart tailscaled
```

#### อัปเดต LPR Server
```bash
# อัปเดต code
cd /home/devuser/lprserver_v3
git pull

# อัปเดต dependencies
source venv/bin/activate
pip install -r requirements.txt

# รีสตาร์ท services
sudo systemctl restart lprserver.service
sudo systemctl restart lprserver-websocket.service
```

### 8.2 การ Backup

#### Backup Configuration
```bash
#!/bin/bash
# /usr/local/bin/backup-lprserver.sh

BACKUP_DIR="/backup/lprserver"
DATE=$(date +%Y%m%d_%H%M%S)

# สร้าง backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp /home/devuser/lprserver_v3/database/lprserver.db $BACKUP_DIR/lprserver_$DATE.db

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /home/devuser/lprserver_v3/config.py \
    /home/devuser/lprserver_v3/lprserver.conf \
    /etc/nginx/sites-available/lprserver

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /home/devuser/lprserver_v3/logs/

# ลบ backup เก่า (เก็บไว้ 7 วัน)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

#### ตั้งค่า Auto Backup
```bash
# เพิ่มใน crontab
sudo crontab -e

# Backup ทุกวันเวลา 2:00 AM
0 2 * * * /usr/local/bin/backup-lprserver.sh
```

---

## 9. การแก้ไขปัญหา

### 9.1 ปัญหาที่พบบ่อย

#### Tailscale ไม่เชื่อมต่อ
```bash
# ตรวจสอบ Tailscale status
tailscale status

# รีสตาร์ท Tailscale
sudo systemctl restart tailscaled
sudo tailscale up

# ตรวจสอบ logs
sudo journalctl -u tailscaled -f
```

#### DNS ไม่ทำงาน
```bash
# ตรวจสอบ DNS resolution
nslookup lprser.tailxxxxxx.ts.net

# รีสตาร์ท DNS service
sudo systemctl restart systemd-resolved

# ตรวจสอบ /etc/resolv.conf
cat /etc/resolv.conf
```

#### WebSocket ไม่ทำงาน
```bash
# ตรวจสอบ WebSocket service
sudo systemctl status lprserver-websocket.service

# ตรวจสอบ port
sudo netstat -tlnp | grep 8765

# ตรวจสอบ firewall
sudo ufw status
```

### 9.2 การตรวจสอบ Logs

#### ตรวจสอบ System Logs
```bash
# ตรวจสอบ system logs
sudo journalctl -f

# ตรวจสอบ nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# ตรวจสอบ LPR Server logs
tail -f /home/devuser/lprserver_v3/logs/app.log
```

---

## 10. การติดต่อผู้ดูแลระบบ

### 10.1 ข้อมูลการติดต่อ
- **Email**: admin@company.com
- **Phone**: +66-xxx-xxx-xxxx
- **Support Hours**: 8:00 AM - 6:00 PM (GMT+7)

### 10.2 ข้อมูลที่ต้องเตรียมเมื่อติดต่อ
1. **ข้อมูลระบบ**
   - Server OS และ Version
   - Tailscale Version
   - LPR Server Version

2. **ข้อมูลปัญหา**
   - คำอธิบายปัญหาที่เกิดขึ้น
   - Error messages
   - ขั้นตอนที่ทำก่อนเกิดปัญหา

3. **ข้อมูลการทดสอบ**
   - ผลลัพธ์จาก monitoring script
   - ผลลัพธ์จาก ping และ curl tests
   - Log files ที่เกี่ยวข้อง

---

## 11. เอกสารอ้างอิง

- [Tailscale Documentation](https://tailscale.com/kb/)
- [LPR Server Documentation](DEVELOPMENT_REPORT.md)
- [System Administration Guide](SYSTEMD_SETUP.md)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**เวอร์ชัน**: 1.0  
**วันที่**: 12 สิงหาคม 2025  
**ผู้จัดทำ**: System Administration Team  
**สถานะ**: Final Version
