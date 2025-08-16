# คู่มือผู้ใช้ - การเข้าถึง LPR Server ผ่าน Tailscale VPN

## ภาพรวม

เอกสารนี้เป็นคู่มือสำหรับผู้ใช้ที่ต้องการเข้าถึงระบบ LPR Server v3 ที่ติดตั้งบน local server ผ่านเครือข่าย VPN Tailscale

### ข้อมูลระบบ
- **Server URL**: `lprser.tailxxxxxx.ts.net`
- **Web Interface**: `http://lprser.tailxxxxxx.ts.net`
- **WebSocket Server**: `ws://lprser.tailxxxxxx.ts.net:8765`
- **API Base URL**: `http://lprser.tailxxxxxx.ts.net/api`

---

## 1. การติดตั้ง Tailscale

### 1.1 Windows

#### ขั้นตอนการติดตั้ง
1. **ดาวน์โหลด Tailscale**
   - ไปที่ https://tailscale.com/download
   - เลือก "Windows" และดาวน์โหลดไฟล์ .exe

2. **ติดตั้ง Tailscale**
   ```bash
   # รันไฟล์ที่ดาวน์โหลด
   TailscaleInstaller.exe
   ```

3. **ลงทะเบียนและเข้าสู่ระบบ**
   - เปิด Tailscale application
   - คลิก "Sign in"
   - เลือก "Sign in with Google" หรือ "Sign in with Microsoft"
   - อนุญาตการเข้าถึงเมื่อถูกถาม

4. **ตรวจสอบการเชื่อมต่อ**
   ```bash
   # เปิด Command Prompt และตรวจสอบ
   tailscale status
   ```

#### การกำหนดค่า
```bash
# เปิด Tailscale admin console
# ไปที่ https://login.tailscale.com/admin/machines
# ตรวจสอบว่าเครื่องของคุณแสดงในรายการ
```

### 1.2 macOS

#### ขั้นตอนการติดตั้ง
1. **ดาวน์โหลด Tailscale**
   ```bash
   # ใช้ Homebrew
   brew install tailscale
   
   # หรือดาวน์โหลดจากเว็บไซต์
   # https://tailscale.com/download
   ```

2. **เริ่มต้น Tailscale**
   ```bash
   sudo tailscale up
   ```

3. **ลงทะเบียนและเข้าสู่ระบบ**
   - เปิด Tailscale application
   - คลิก "Sign in"
   - เลือก "Sign in with Google" หรือ "Sign in with Microsoft"

4. **ตรวจสอบการเชื่อมต่อ**
   ```bash
   tailscale status
   ```

#### การกำหนดค่า
```bash
# เปิด Tailscale admin console
open https://login.tailscale.com/admin/machines
```

### 1.3 Linux (Ubuntu/Debian)

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

#### การกำหนดค่า
```bash
# เปิด Tailscale admin console ใน browser
xdg-open https://login.tailscale.com/admin/machines
```

### 1.4 Android

#### ขั้นตอนการติดตั้ง
1. **ดาวน์โหลด Tailscale**
   - เปิด Google Play Store
   - ค้นหา "Tailscale"
   - ติดตั้งแอปพลิเคชัน

2. **ลงทะเบียนและเข้าสู่ระบบ**
   - เปิด Tailscale app
   - คลิก "Sign in"
   - เลือก "Sign in with Google" หรือ "Sign in with Microsoft"

3. **ตรวจสอบการเชื่อมต่อ**
   - เปิด Tailscale app
   - ตรวจสอบสถานะการเชื่อมต่อ

### 1.5 iOS

#### ขั้นตอนการติดตั้ง
1. **ดาวน์โหลด Tailscale**
   - เปิด App Store
   - ค้นหา "Tailscale"
   - ติดตั้งแอปพลิเคชัน

2. **ลงทะเบียนและเข้าสู่ระบบ**
   - เปิด Tailscale app
   - คลิก "Sign in"
   - เลือก "Sign in with Google" หรือ "Sign in with Microsoft"

3. **ตรวจสอบการเชื่อมต่อ**
   - เปิด Tailscale app
   - ตรวจสอบสถานะการเชื่อมต่อ

---

## 2. การกำหนดค่า Browser

### 2.1 การตั้งค่า Browser หลัก

#### Chrome/Edge (Windows/macOS/Linux)
1. **เปิด Browser**
2. **ไปที่ URL**: `http://lprser.tailxxxxxx.ts.net`
3. **ตรวจสอบการเชื่อมต่อ**
   - ควรเห็นหน้าแรกของ LPR Server
   - หากไม่สามารถเชื่อมต่อได้ ให้ตรวจสอบ Tailscale status

#### Firefox
1. **เปิด Firefox**
2. **ไปที่ URL**: `http://lprser.tailxxxxxx.ts.net`
3. **หากมีปัญหา SSL**:
   - คลิก "Advanced"
   - คลิก "Accept the Risk and Continue"

#### Safari (macOS/iOS)
1. **เปิด Safari**
2. **ไปที่ URL**: `http://lprser.tailxxxxxx.ts.net`
3. **หากมีปัญหา SSL**:
   - คลิก "Show Details"
   - คลิก "visit this website"

### 2.2 การตั้งค่า Mobile Browser

#### Android (Chrome)
1. **เปิด Chrome**
2. **ไปที่ URL**: `http://lprser.tailxxxxxx.ts.net`
3. **ตรวจสอบการเชื่อมต่อ**

#### iOS (Safari)
1. **เปิด Safari**
2. **ไปที่ URL**: `http://lprser.tailxxxxxx.ts.net`
3. **ตรวจสอบการเชื่อมต่อ**

---

## 3. การใช้งานระบบ

### 3.1 การเข้าถึง Web Interface

#### หน้าหลัก
- **หน้าแรก**: `http://lprser.tailxxxxxx.ts.net`
- **แดชบอร์ด**: `http://lprser.tailxxxxxx.ts.net/dashboard`
- **รายการบันทึก**: `http://lprser.tailxxxxxx.ts.net/records`
- **จัดการ Blacklist**: `http://lprser.tailxxxxxx.ts.net/blacklist`

#### โมดูลเพิ่มเติม
- **AI Camera**: `http://lprser.tailxxxxxx.ts.net/aicamera`
- **Detection**: `http://lprser.tailxxxxxx.ts.net/detection`
- **Map**: `http://lprser.tailxxxxxx.ts.net/map`
- **System**: `http://lprser.tailxxxxxx.ts.net/system`
- **User**: `http://lprser.tailxxxxxx.ts.net/user`
- **Report**: `http://lprser.tailxxxxxx.ts.net/report`
- **Health**: `http://lprser.tailxxxxxx.ts.net/health`

### 3.2 การใช้งาน API

#### API Endpoints
```bash
# ตรวจสอบสถานะระบบ
curl http://lprser.tailxxxxxx.ts.net/api/statistics

# ดึงรายการบันทึก
curl http://lprser.tailxxxxxx.ts.net/api/records

# ดึงรายการ blacklist
curl http://lprser.tailxxxxxx.ts.net/api/blacklist

# เพิ่มข้อมูล blacklist
curl -X POST http://lprser.tailxxxxxx.ts.net/api/blacklist \
  -H "Content-Type: application/json" \
  -d '{"license_plate_text": "กข1234", "reason": "ทดสอบ", "added_by": "admin"}'
```

### 3.3 การทดสอบ WebSocket

#### ทดสอบการเชื่อมต่อ WebSocket
```javascript
// เปิด Browser Console และรันโค้ดนี้
const socket = io('ws://lprser.tailxxxxxx.ts.net:8765');

socket.on('connect', () => {
    console.log('Connected to LPR Server WebSocket');
});

socket.on('disconnect', () => {
    console.log('Disconnected from LPR Server WebSocket');
});

// ลงทะเบียนกล้องทดสอบ
socket.emit('camera_register', {
    camera_id: 'TEST_CAM',
    location: 'Test Location',
    status: 'active'
});
```

---

## 4. การแก้ไขปัญหา

### 4.1 ปัญหาการเชื่อมต่อ Tailscale

#### ตรวจสอบสถานะ Tailscale
```bash
# Windows/Linux/macOS
tailscale status

# Android/iOS
# เปิด Tailscale app และตรวจสอบสถานะ
```

#### การแก้ไขปัญหาการเชื่อมต่อ
1. **รีสตาร์ท Tailscale**
   ```bash
   # Windows
   # เปิด Task Manager และปิด Tailscale process แล้วเปิดใหม่
   
   # macOS/Linux
   sudo tailscale down
   sudo tailscale up
   
   # Android/iOS
   # ปิดและเปิด Tailscale app ใหม่
   ```

2. **ตรวจสอบ Firewall**
   ```bash
   # Windows
   # ตรวจสอบ Windows Firewall
   
   # macOS
   # ตรวจสอบ System Preferences > Security & Privacy > Firewall
   
   # Linux
   sudo ufw status
   ```

### 4.2 ปัญหาการเข้าถึง Web Interface

#### ตรวจสอบการเชื่อมต่อ
```bash
# ทดสอบ ping
ping lprser.tailxxxxxx.ts.net

# ทดสอบ HTTP connection
curl -I http://lprser.tailxxxxxx.ts.net

# ทดสอบ WebSocket connection
curl -I http://lprser.tailxxxxxx.ts.net:8765
```

#### การแก้ไขปัญหา SSL/HTTPS
1. **ใช้ HTTP แทน HTTPS**
   - เปลี่ยน URL จาก `https://` เป็น `http://`

2. **เพิ่ม Security Exception**
   - ใน Browser ให้เพิ่ม security exception สำหรับ domain

### 4.3 ปัญหาการใช้งาน API

#### ตรวจสอบ API Endpoints
```bash
# ทดสอบ API statistics
curl -v http://lprser.tailxxxxxx.ts.net/api/statistics

# ทดสอบ API records
curl -v http://lprser.tailxxxxxx.ts.net/api/records
```

#### การแก้ไขปัญหา CORS
หากมีปัญหา CORS ให้ติดต่อผู้ดูแลระบบเพื่อตั้งค่า CORS headers

### 4.4 ปัญหาการใช้งาน WebSocket

#### ตรวจสอบ WebSocket Server
```bash
# ทดสอบ WebSocket port
telnet lprser.tailxxxxxx.ts.net 8765

# หรือใช้ netcat
nc -zv lprser.tailxxxxxx.ts.net 8765
```

#### การแก้ไขปัญหา WebSocket
1. **ตรวจสอบ Firewall**
   - ตรวจสอบว่า port 8765 เปิดอยู่

2. **ตรวจสอบ Nginx Configuration**
   - ตรวจสอบการตั้งค่า WebSocket proxy ใน Nginx

---

## 5. การตั้งค่าขั้นสูง

### 5.1 การตั้งค่า DNS

#### Windows
```bash
# ตรวจสอบ DNS
nslookup lprser.tailxxxxxx.ts.net

# ตั้งค่า DNS แบบ manual (หากจำเป็น)
# ไปที่ Network Settings > Change adapter options > Properties > Internet Protocol Version 4
```

#### macOS/Linux
```bash
# ตรวจสอบ DNS
nslookup lprser.tailxxxxxx.ts.net

# ตั้งค่า DNS แบบ manual (หากจำเป็น)
# แก้ไขไฟล์ /etc/resolv.conf
```

### 5.2 การตั้งค่า Firewall

#### Windows
```powershell
# เปิด port สำหรับ Tailscale
netsh advfirewall firewall add rule name="Tailscale" dir=in action=allow protocol=any
```

#### macOS
```bash
# เปิด port สำหรับ Tailscale
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Tailscale.app
```

#### Linux
```bash
# เปิด port สำหรับ Tailscale
sudo ufw allow 41641/udp
sudo ufw allow 41641/tcp
```

### 5.3 การตั้งค่า Proxy

#### หากใช้ Corporate Proxy
```bash
# Windows
# ตั้งค่าใน Internet Options > Connections > LAN Settings

# macOS
# ตั้งค่าใน System Preferences > Network > Advanced > Proxies

# Linux
export http_proxy=http://proxy.company.com:8080
export https_proxy=http://proxy.company.com:8080
```

---

## 6. การทดสอบระบบ

### 6.1 การทดสอบการเชื่อมต่อ

#### ทดสอบ Network Connectivity
```bash
# ทดสอบ ping
ping lprser.tailxxxxxx.ts.net

# ทดสอบ traceroute
traceroute lprser.tailxxxxxx.ts.net

# ทดสอบ DNS resolution
nslookup lprser.tailxxxxxx.ts.net
```

#### ทดสอบ Web Interface
```bash
# ทดสอบ HTTP response
curl -I http://lprser.tailxxxxxx.ts.net

# ทดสอบ API endpoints
curl http://lprser.tailxxxxxx.ts.net/api/statistics
```

#### ทดสอบ WebSocket
```bash
# ใช้ test_client.py (หากมี)
python test_client.py

# หรือใช้ browser console
# เปิด browser console และรันโค้ด JavaScript ที่ให้ไว้ข้างต้น
```

### 6.2 การทดสอบ Performance

#### ทดสอบ Response Time
```bash
# ทดสอบ API response time
time curl -s http://lprser.tailxxxxxx.ts.net/api/statistics

# ทดสอบ WebSocket connection time
# ใช้ browser console และวัดเวลาการเชื่อมต่อ
```

---

## 7. การบำรุงรักษา

### 7.1 การอัปเดต Tailscale

#### Windows
- Tailscale จะอัปเดตอัตโนมัติ
- หรือดาวน์โหลดเวอร์ชันใหม่จากเว็บไซต์

#### macOS
```bash
# ใช้ Homebrew
brew upgrade tailscale

# หรือดาวน์โหลดจากเว็บไซต์
```

#### Linux
```bash
# อัปเดต package
sudo apt update
sudo apt upgrade tailscale
```

#### Android/iOS
- อัปเดตผ่าน App Store/Google Play Store

### 7.2 การตรวจสอบ Logs

#### Tailscale Logs
```bash
# Windows
# ตรวจสอบ Event Viewer

# macOS/Linux
tailscale status
tailscale netcheck
```

#### Browser Logs
- เปิด Developer Tools (F12)
- ไปที่ Console tab
- ตรวจสอบ error messages

---

## 8. การติดต่อผู้ดูแลระบบ

### 8.1 ข้อมูลการติดต่อ
- **Email**: admin@company.com
- **Phone**: +66-xxx-xxx-xxxx
- **Support Hours**: 8:00 AM - 6:00 PM (GMT+7)

### 8.2 ข้อมูลที่ต้องเตรียมเมื่อติดต่อ
1. **ข้อมูลระบบ**
   - Operating System และ Version
   - Tailscale Version
   - Browser และ Version

2. **ข้อมูลปัญหา**
   - คำอธิบายปัญหาที่เกิดขึ้น
   - Error messages (หากมี)
   - ขั้นตอนที่ทำก่อนเกิดปัญหา

3. **ข้อมูลการทดสอบ**
   - ผลลัพธ์จาก ping test
   - ผลลัพธ์จาก curl test
   - Screenshot ของ error (หากมี)

---

## 9. คำถามที่พบบ่อย (FAQ)

### Q1: ไม่สามารถเชื่อมต่อ Tailscale ได้
**A**: ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต และลองรีสตาร์ท Tailscale application

### Q2: ไม่สามารถเข้าถึง Web Interface ได้
**A**: ตรวจสอบว่า Tailscale เชื่อมต่อแล้ว และลองใช้ URL ที่ถูกต้อง

### Q3: WebSocket ไม่ทำงาน
**A**: ตรวจสอบว่า port 8765 เปิดอยู่ และไม่ถูกบล็อกโดย firewall

### Q4: API ไม่ตอบสนอง
**A**: ตรวจสอบการเชื่อมต่อและลองใช้ curl command เพื่อทดสอบ

### Q5: หน้าเว็บโหลดช้า
**A**: ตรวจสอบความเร็วอินเทอร์เน็ตและระยะห่างจาก server

---

## 10. เอกสารอ้างอิง

- [Tailscale Documentation](https://tailscale.com/kb/)
- [LPR Server Documentation](DEVELOPMENT_REPORT.md)
- [System Administration Guide](SYSTEMD_SETUP.md)
- [API Documentation](DEVELOPMENT_GUIDE.md)

---

**เวอร์ชัน**: 1.0  
**วันที่**: 12 สิงหาคม 2025  
**ผู้จัดทำ**: IT Support Team  
**สถานะ**: Final Version
