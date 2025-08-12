# Deployment Guide: Raspberry Pi 5 + Camera Module 3 + Hailo-8 AI HAT+

เวอร์ชัน: 3.0  
สถานะ: Template พร้อมสำหรับติดตั้ง Production

---

## สารบัญ
- ภาพรวมระบบ
- ฮาร์ดแวร์ที่ใช้
- การเตรียมฮาร์ดแวร์ (Assembly)
- การเตรียมระบบปฏิบัติการ (OS)
- การติดตั้งไดรเวอร์/เฟิร์มแวร์ (Camera, Hailo-8)
- การติดตั้งซอฟต์แวร์ระบบ (ALPR Server & Web)
- การตั้งค่า Nginx + Systemd
- การทดสอบระบบ
- Troubleshooting
- ภาคผนวก (คำสั่งที่ใช้บ่อย, Health Checks)

---

## ภาพรวมระบบ
- Raspberry Pi 5 ทำหน้าที่ Edge Node รัน AI Inference (ผ่าน Hailo-8) และส่งข้อมูลไปยัง LPR Server v3
- กล้อง Camera Module 3 ต่อผ่าน CSI
- Hailo-8 AI HAT+ (26 TOPS) ต่อผ่าน PCIe หรือ HAT+ slot

> [ภาพประกอบ: แผนผังการเชื่อมต่อ]

---

## ฮาร์ดแวร์ที่ใช้
- Raspberry Pi 5 (RAM 8GB แนะนำ)
- MicroSD Card (32GB+ หรือ SSD via USB 3.0)
- Power Supply 27W USB-C (ทางการ)
- Camera Module 3 (Wide/Standard ตามการใช้งาน)
- Hailo-8 AI HAT+ (26TOPs)
- Heatsink/Fan สำหรับระบายความร้อน
- สาย LAN หรือ Wi-Fi

---

## การเตรียมฮาร์ดแวร์ (Assembly)
1) ปิดเครื่อง, ถอดปลั๊ก  
2) ติดตั้ง Heatsink/Fan บน RPi5  
3) ใส่ Hailo-8 AI HAT+ บน Header/HAT+ ตามคู่มือ พร้อมยึดสกรู  
4) เชื่อมต่อ Camera Module 3 กับพอร์ต CSI (ระวังทิศทาง Flat cable)  
5) ใส่ MicroSD/SSD และต่อไฟเลี้ยง  

> [ภาพประกอบ: ขั้นตอนประกอบอุปกรณ์]

---

## การเตรียมระบบปฏิบัติการ (OS)
1) ดาวน์โหลด Raspberry Pi OS (64-bit) ล่าสุดจากเว็บทางการ  
2) ใช้ Raspberry Pi Imager เขียนภาพลง MicroSD/SSD (เปิด SSH, ตั้งค่า Wi-Fi/Locale ตามต้องการ)  
3) บูตเครื่อง รอระบบตั้งค่าครั้งแรกให้เสร็จ  
4) อัปเดตระบบ:
```bash
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

---

## การติดตั้งไดรเวอร์/เฟิร์มแวร์
### Camera Module 3
1) เปิดใช้งาน camera overlay (ถ้าไม่เปิดโดยค่าเริ่มต้น):
```bash
sudo raspi-config
# Interface Options → Enable Camera
sudo reboot
```
2) ทดสอบกล้อง:
```bash
libcamera-hello -t 2000
```

### Hailo-8 AI HAT+
1) ติดตั้ง Hailo software suite (ตามคู่มือทางการ Hailo-8):
```bash
# ตัวอย่าง (โปรดอ้างอิงเอกสาร Hailo ล่าสุด)
wget https://hailo.ai/.../hailo-suite.deb
sudo apt install ./hailo-suite.deb
```
2) ตรวจสอบอุปกรณ์ Hailo:
```bash
hailo inspect devices
```
3) ติดตั้งโมเดล/Runtime ที่ระบบ ALPR ใช้ (หากกำหนดไว้)

> หมายเหตุ: กรณีใช้ PCIe อาจต้องตรวจสอบ enable PCIe ใน config และ kernel modules

---

## การติดตั้งซอฟต์แวร์ระบบ (ALPR Server & Web)
1) เตรียมไดเรกทอรีโค้ด (สมมติ /home/pi/lprserver_v3):
```bash
sudo apt install -y python3-venv python3-pip git nginx sqlite3
cd /home/pi
git clone https://your-repo/lprserver_v3.git
cd lprserver_v3
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
2) ตั้งค่า .env และโครงสร้างไฟล์:
```bash
mkdir -p database logs storage/images /var/log/lprserver
cat > .env << 'EOF'
FLASK_CONFIG=production
DATABASE_URL=sqlite:////home/pi/lprserver_v3/database/lprserver.db
SECRET_KEY=change-me-in-production
EOF
```
3) สร้าง/อัปเกรดฐานข้อมูล (ถ้ามีสคริปต์จัดเตรียม):
```bash
python -c "from src.app import create_app; app=create_app('production'); ctx=app.app_context(); ctx.push(); from src.models import db; db.create_all(); print('DB ready')"
```

---

## การตั้งค่า Nginx + Systemd
### Nginx
1) วางไฟล์ config `lprserver.conf` ที่ `/etc/nginx/sites-available/` และลิงก์ไป `sites-enabled/`:
```bash
sudo cp lprserver.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/lprserver.conf /etc/nginx/sites-enabled/lprserver.conf
sudo nginx -t && sudo systemctl reload nginx
```
2) ตรวจสอบว่าไม่มีไฟล์ config เก่าทับพอร์ต 80

### Systemd Services
1) สร้างไฟล์ service (แก้ path เป็นของผู้ใช้ `pi`):
`/etc/systemd/system/lprserver.service`
```ini
[Unit]
Description=LPR Server v3 - Main Flask Application
After=network.target

[Service]
Type=notify
User=pi
WorkingDirectory=/home/pi/lprserver_v3
Environment=PATH=/home/pi/lprserver_v3/venv/bin
Environment=FLASK_CONFIG=production
Environment=PYTHONPATH=/home/pi/lprserver_v3:/home/pi/lprserver_v3/src
ExecStart=/home/pi/lprserver_v3/venv/bin/gunicorn --workers 2 --bind unix:/tmp/lprserver.sock wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/lprserver-websocket.service`
```ini
[Unit]
Description=LPR Server v3 - WebSocket Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/lprserver_v3
Environment=PATH=/home/pi/lprserver_v3/venv/bin
Environment=FLASK_CONFIG=production
Environment=PYTHONPATH=/home/pi/lprserver_v3:/home/pi/lprserver_v3/src
ExecStart=/home/pi/lprserver_v3/venv/bin/python websocket_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```
2) Enable & Start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lprserver.service lprserver-websocket.service nginx.service
```

---

## การทดสอบระบบ
```bash
# ตรวจสอบสถานะ services
systemctl status lprserver.service lprserver-websocket.service nginx.service --no-pager

# ทดสอบ HTTP
curl -I http://localhost
curl -I http://localhost/aicamera/
```
- เปิดเบราว์เซอร์จากเครื่องลูกข่าย: `http://<ip-of-pi>`
- ตรวจสอบหน้า Cameras/Records/Reports

---

## Troubleshooting
- 502 Bad Gateway → ตรวจสอบ Nginx config, Unix socket, Gunicorn
- Database URI error → ตรวจ `.env` ค่า `DATABASE_URL`
- Werkzeug production warning → ตั้งค่า `allow_unsafe_werkzeug=True` ใน dev เท่านั้น
- WebSocket 400 → ตรวจสอบพอร์ต 8765 และ CORS/Proxy

คำสั่งตรวจสอบที่มีประโยชน์:
```bash
sudo journalctl -u lprserver.service -f
sudo journalctl -u lprserver-websocket.service -f
sudo tail -f /var/log/nginx/error.log
ls -la /tmp/lprserver.sock
ss -tlnp | grep 80
```

---

## ภาคผนวก
### Health Checks
- `/health` endpoint (HTTP)
- System Logs ที่ `/system/logs`

### บันทึกประสิทธิภาพเบื้องต้น
- ตั้งค่า swap/thermal, ใช้พัดลม, วางเครื่องในที่ระบายอากาศดี
- ปรับ worker=2 บน RPi5 (เริ่มต้น) และปรับตาม load จริง
