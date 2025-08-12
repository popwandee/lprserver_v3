# Developer Documentation: AI Camera (ALPR)

เวอร์ชัน: 3.0  
สถานะ: Onboarding Guide สำหรับนักพัฒนาใหม่

---

## เป้าหมายของเอกสาร
- ช่วยนักพัฒนาใหม่ทำความเข้าใจสถาปัตยกรรม
- ตั้งค่าสภาพแวดล้อมและรันระบบได้ในเวลาอันสั้น
- อธิบายโครงสร้างโค้ด, รูปแบบการพัฒนา, มาตรฐานโค้ด, และแนวทางทดสอบ/ดีพลอย

---

## ภาพรวมสถาปัตยกรรม
- Flask Application (Blueprints) + Gunicorn + Nginx
- WebSocket Server (flask_socketio) สำหรับสื่อสารกับ Edge Cameras
- SQLite (dev) / รองรับ DB อื่นผ่าน SQLAlchemy
- Frontend: Bootstrap 5, Chart.js, DataTables, Font Awesome
- .env สำหรับ config (FLASK_CONFIG, DATABASE_URL, SECRET_KEY)

แผนภาพเชิงแนวคิด:
```
Edge Cameras ──WebSocket──> WebSocket Server ──> Flask App ──> DB
                               ▲                  │
                               └──────Nginx───────┘
```

---

## การตั้งค่าสภาพแวดล้อม (Local Dev)
```bash
# Clone repo
cd /path/to
git clone https://your-repo/lprserver_v3.git
cd lprserver_v3

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Env & folders
cp .env.example .env  # (ถ้ามี) หรือสร้างใหม่
mkdir -p database logs storage/images

# Run (dev)
export FLASK_CONFIG=development
python -m flask run --host=0.0.0.0 --port=5000

# Run websocket (dev)
python websocket_server.py
```

ตัวอย่าง .env (dev):
```env
FLASK_CONFIG=development
DATABASE_URL=sqlite:////absolute/path/to/lprserver.db
SECRET_KEY=dev-secret
```

---

## โครงสร้างโค้ด
```
src/
├── app.py                 # Application factory + blueprint registration
├── core/
│   ├── import_helper.py
│   └── config.py          # Config classes (Development/Production)
├── web/
│   ├── blueprints/
│   │   ├── aicamera.py
│   │   ├── detection.py
│   │   ├── map.py
│   │   ├── system.py
│   │   ├── user.py
│   │   └── report.py
│   └── ...
└── services/              # สำหรับ business logic (mock/stub ได้)

templates/
├── base.html              # Theme, layout, navbar, dark-mode
├── index.html
├── aicamera/
├── detection/
├── map/
├── system/
├── user/
└── report/
```

หลักการแบ่งชั้น:
- Blueprint: จัดการ routing/UI/APIs เฉพาะโดเมน
- Services: ธุรกิจลอจิก แยกจาก web layer (ทดแทนด้วย mock ได้)
- Models: (หากแยกไฟล์) ดูแลโครงสร้างข้อมูล/ORM

---

## มาตรฐานโค้ดและสไตล์
- Python: PEP8, ชื่อฟังก์ชัน/ตัวแปรสื่อความหมาย
- แยก concerns: route บางๆ, ย้าย logic ไป services
- หลีกเลี่ยง inline comments ที่ยาว: อธิบาย “ทำไม” มากกว่า “ทำอะไร”
- Frontend: ใช้ CSS variables ใน `base.html` สำหรับ theme, หลีกเลี่ยงสี hardcode
- ชื่อ route/endpoint ชัดเจน, ใช้ `url_prefix` ของ Blueprint

ตัวอย่าง endpoint (REST-ish):
```python
@bp.route('/api/items', methods=['GET'])
def list_items():
    items = item_service.list()
    return jsonify({'success': True, 'items': items})
```

---

## การทดสอบ (Testing)
### Unit Tests
- แยก services ให้ test ได้ง่าย
- ใช้ pytest (แนะนำ) และ factory pattern สำหรับ app context

ตัวอย่างโครงสร้าง tests:
```
tests/
├── unit/
│   ├── test_services.py
└── integration/
    ├── test_api_routes.py
```

### Integration/UI Tests
- ทดสอบ API กับ DB (sqlite memory)
- ทดสอบ websocket events แบบจำลอง
- ตรวจสอบ UI ผ่าน Playwright/Selenium (ถ้าจำเป็น)

---

## การดีพลอย (Production)
- ใช้ Gunicorn + Unix Socket + Nginx reverse proxy
- ตั้งค่า Systemd ให้ auto-start และ restart on failure
- เก็บ `.env` ในเครื่องเซิร์ฟเวอร์, ตั้ง permission เหมาะสม

เช็คลิสต์ก่อนดีพลอย:
- nginx -t ผ่าน
- /tmp/lprserver.sock ถูกสร้างโดย gunicorn
- DATABASE_URL ชี้ไป path ที่มีสิทธิ์อ่าน/เขียน
- ไดเรกทอรี logs, storage/images มี permission ถูกต้อง

---

## แนวทางเพิ่มฟีเจอร์ใหม่
1) สร้าง blueprint ใหม่หรือเพิ่ม route ในโมดูลที่เกี่ยวข้อง  
2) เพิ่มหน้า template (ขยาย `base.html`)  
3) เพิ่ม service/DAO สำหรับ business logic  
4) เพิ่ม unit tests  
5) อัปเดตเอกสาร (User Manual/Dev Doc)

แนวทาง mock ข้อมูลชั่วคราว:
- ให้ API คืนค่า mock JSON ตามสัญญา (schema) ชั่วคราว
- แยกที่ชั้น service เพื่อสลับเป็นของจริงภายหลังง่าย

---

## Performance & Observability
- เปิด access/error logs ของ Nginx
- บันทึกระบบใน `/var/log/lprserver/` และ `logs/`
- เพิ่ม Metrics endpoint/Health checks
- ใช้ profiling (cProfile) เมื่อจำเป็น

---

## Security Best Practices
- เปิด HTTPS (Let's Encrypt) ใน Nginx สำหรับ internet-facing
- ใช้ strong SECRET_KEY และหมุนเวียนเป็นระยะ
- RBAC ชัดเจน, ตรวจสอบ `login_required`, `admin_required`
- ปกป้องไฟล์ภาพและข้อมูลส่วนบุคคลตามนโยบาย

---

## Roadmap แนะนำ
- ย้าย DB เป็น PostgreSQL เมื่อ scale เพิ่ม
- เพิ่ม Celery/Task queue สำหรับงานหนัก
- เพิ่ม Grafana/Prometheus สำหรับ metrics
- รองรับ Multi-tenant/Org-level RBAC

---

## ภาคผนวก
- ตัวอย่าง Nginx config
- ตัวอย่าง Systemd units
- ตัวอย่าง .env (production)

Production .env ตัวอย่าง:
```env
FLASK_CONFIG=production
DATABASE_URL=sqlite:////home/devuser/lprserver_v3/database/lprserver.db
SECRET_KEY=change-me
```
