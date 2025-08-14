# คู่มือการใช้งาน Tailscale สำหรับ LPR Server - Quick Start

## ภาพรวม

เอกสารนี้เป็นคู่มือสรุปสำหรับการใช้งาน Tailscale กับ LPR Server v3

### ข้อมูลระบบ
- **Server URL**: `lprser.tailxxxxxx.ts.net`
- **Web Interface**: `http://lprser.tailxxxxxx.ts.net`
- **WebSocket**: `ws://lprser.tailxxxxxx.ts.net:8765`

---

## สำหรับผู้ใช้ (End Users)

### 1. การติดตั้ง Tailscale

#### Windows
1. ดาวน์โหลดจาก https://tailscale.com/download
2. ติดตั้งและลงทะเบียนด้วย Google/Microsoft
3. ตรวจสอบ: `tailscale status`

#### macOS
```bash
brew install tailscale
sudo tailscale up
```

#### Linux
```bash
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt update && sudo apt install tailscale
sudo tailscale up
```

#### Mobile
- **Android**: ติดตั้งจาก Google Play Store
- **iOS**: ติดตั้งจาก App Store

### 2. การเข้าถึงระบบ

#### Web Interface
เปิด browser และไปที่: `http://lprser.tailxxxxxx.ts.net`

#### API Testing
```bash
# ทดสอบการเชื่อมต่อ
curl http://lprser.tailxxxxxx.ts.net/api/statistics

# ทดสอบ blacklist
curl http://lprser.tailxxxxxx.ts.net/api/blacklist
```

#### WebSocket Testing
```javascript
// เปิด browser console และรัน
const socket = io('ws://lprser.tailxxxxxx.ts.net:8765');
socket.on('connect', () => console.log('Connected!'));
```

### 3. การแก้ไขปัญหาเบื้องต้น

#### ไม่สามารถเชื่อมต่อได้
```bash
# ตรวจสอบ Tailscale status
tailscale status

# รีสตาร์ท Tailscale
sudo tailscale down && sudo tailscale up
```

#### ไม่สามารถเข้าถึงเว็บได้
```bash
# ทดสอบ ping
ping lprser.tailxxxxxx.ts.net

# ทดสอบ HTTP
curl -I http://lprser.tailxxxxxx.ts.net
```

---

## สำหรับผู้ดูแลระบบ (System Administrators)

### 1. การติดตั้งบน Server

#### ติดตั้ง Tailscale
```bash
# Ubuntu/Debian
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt update && sudo apt install tailscale

# ตั้งค่า hostname
sudo hostnamectl set-hostname lprser
sudo tailscale up
```

#### ตั้งค่า DNS
1. ไปที่ https://login.tailscale.com/admin/machines
2. คลิกที่เครื่อง `lprser`
3. ไปที่ "DNS" tab
4. ตั้งค่า DNS name เป็น `lprser.tailxxxxxx.ts.net`

### 2. การตั้งค่า Firewall

#### เปิด Ports
```bash
sudo ufw allow 80/tcp
sudo ufw allow 5000/tcp
sudo ufw allow 8765/tcp
sudo ufw allow 41641/udp
sudo ufw allow 41641/tcp
```

#### ตรวจสอบ
```bash
sudo ufw status
sudo netstat -tlnp | grep -E ':(80|5000|8765)'
```

### 3. การตั้งค่า Nginx

#### WebSocket Proxy
```nginx
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

### 4. การตรวจสอบระบบ

#### Monitoring Script
```bash
#!/bin/bash
echo "=== Tailscale Status ==="
tailscale status

echo "=== Services Status ==="
sudo systemctl status lprserver.service --no-pager
sudo systemctl status lprserver-websocket.service --no-pager
sudo systemctl status nginx --no-pager

echo "=== Network Test ==="
curl -I http://lprser.tailxxxxxx.ts.net
curl http://lprser.tailxxxxxx.ts.net/api/statistics
```

#### ตั้งค่า Auto Monitoring
```bash
# เพิ่มใน crontab
*/5 * * * * /usr/local/bin/monitor-lprserver.sh >> /var/log/lprserver-monitor.log 2>&1
```

### 5. การ Backup

#### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backup/lprserver"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /home/devuser/lprserver_v3/database/lprserver.db $BACKUP_DIR/lprserver_$DATE.db
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /home/devuser/lprserver_v3/config.py /etc/nginx/sites-available/lprserver

# ลบ backup เก่า (7 วัน)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

---

## การทดสอบระบบ

### 1. ทดสอบการเชื่อมต่อ

#### จาก Server
```bash
# ทดสอบ HTTP
curl -I http://lprser.tailxxxxxx.ts.net

# ทดสอบ API
curl http://lprser.tailxxxxxx.ts.net/api/statistics

# ทดสอบ WebSocket
curl -I http://lprser.tailxxxxxx.ts.net:8765
```

#### จาก Client
```bash
# ทดสอบ ping
ping lprser.tailxxxxxx.ts.net

# ทดสอบ HTTP
curl -I http://lprser.tailxxxxxx.ts.net

# ทดสอบ API
curl http://lprser.tailxxxxxx.ts.net/api/blacklist
```

### 2. ทดสอบ Performance

#### Response Time
```bash
time curl -s http://lprser.tailxxxxxx.ts.net/api/statistics
```

#### Load Test
```bash
ab -n 100 -c 10 http://lprser.tailxxxxxx.ts.net/api/statistics
```

---

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. Tailscale ไม่เชื่อมต่อ
```bash
# ตรวจสอบ status
tailscale status

# รีสตาร์ท
sudo systemctl restart tailscaled
sudo tailscale up

# ตรวจสอบ logs
sudo journalctl -u tailscaled -f
```

#### 2. DNS ไม่ทำงาน
```bash
# ตรวจสอบ DNS
nslookup lprser.tailxxxxxx.ts.net

# รีสตาร์ท DNS
sudo systemctl restart systemd-resolved
```

#### 3. WebSocket ไม่ทำงาน
```bash
# ตรวจสอบ service
sudo systemctl status lprserver-websocket.service

# ตรวจสอบ port
sudo netstat -tlnp | grep 8765

# ตรวจสอบ firewall
sudo ufw status
```

#### 4. API ไม่ตอบสนอง
```bash
# ตรวจสอบ Flask service
sudo systemctl status lprserver.service

# ตรวจสอบ logs
tail -f /home/devuser/lprserver_v3/logs/app.log
```

---

## คำสั่งที่ใช้บ่อย

### สำหรับผู้ใช้
```bash
# ตรวจสอบ Tailscale status
tailscale status

# ทดสอบการเชื่อมต่อ
ping lprser.tailxxxxxx.ts.net
curl -I http://lprser.tailxxxxxx.ts.net

# ทดสอบ API
curl http://lprser.tailxxxxxx.ts.net/api/statistics
```

### สำหรับผู้ดูแลระบบ
```bash
# ตรวจสอบ services
sudo systemctl status lprserver.service
sudo systemctl status lprserver-websocket.service
sudo systemctl status nginx

# รีสตาร์ท services
sudo systemctl restart lprserver.service
sudo systemctl restart lprserver-websocket.service
sudo systemctl restart nginx

# ตรวจสอบ logs
sudo journalctl -u lprserver.service -f
sudo journalctl -u lprserver-websocket.service -f
tail -f /var/log/nginx/access.log

# ตรวจสอบ ports
sudo netstat -tlnp | grep -E ':(80|5000|8765)'

# ตรวจสอบ disk space
df -h

# ตรวจสอบ memory
free -h
```

---

## เอกสารเพิ่มเติม

- **[USER_GUIDE_TAILSCALE_ACCESS.md](USER_GUIDE_TAILSCALE_ACCESS.md)** - คู่มือผู้ใช้แบบละเอียด
- **[TAILSCALE_SERVER_SETUP.md](TAILSCALE_SERVER_SETUP.md)** - คู่มือการตั้งค่า Server แบบละเอียด
- **[DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md)** - รายงานการพัฒนา
- **[SYSTEMD_SETUP.md](SYSTEMD_SETUP.md)** - คู่มือการตั้งค่า Systemd

---

**เวอร์ชัน**: 1.0  
**วันที่**: 12 สิงหาคม 2025  
**ผู้จัดทำ**: IT Support Team  
**สถานะ**: Quick Start Guide
