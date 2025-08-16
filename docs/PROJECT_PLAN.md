## LPR Server v3 – แผนพัฒนาโปรเจกต์แบบลำดับขั้นตอน

### บทสรุป
โค้ดปัจจุบันเชื่อมต่อฐานข้อมูลผ่าน SQLAlchemy และปรับ API/Template เพื่อให้สอดคล้องกับ UI ได้มากขึ้น รวมถึงรองรับ PostgreSQL ตามค่า `DATABASE_URL` ใน environment. เอกสารนี้สรุปงานที่ต้องทำต่อเพื่อให้ระบบสมบูรณ์ พร้อมเกณฑ์ยอมรับงาน (acceptance criteria) และลำดับการพัฒนาแบบเป็นเฟส (milestone).

### สถานะปัจจุบัน (หลังปรับแก้ล่าสุด)
- เพิ่ม API ให้รองรับการใช้งานของ UI:
  - GET /api/records รองรับ `limit`
  - GET /api/statistics (เพิ่ม `blacklist_count`)
  - GET /api/statistics/daily, GET /api/statistics/camera
  - GET /api/alerts/recent, GET /api/cameras/status
  - GET /api/records/<id>/image สำหรับเรียกรูป
  - POST /api/records แปลง `confidence` เป็นเปอร์เซ็นต์ 0–100 อัตโนมัติ
  - GET /api/blacklist ปรับ field mapping ให้สอดคล้อง UI
  - GET /api/blacklist/statistics จัดรูปแบบค่าสถิติตามที่ UI ใช้
- Template context: แสดงชนิดฐานข้อมูลจริง (`db_engine`) บนหน้าเว็บ
- ORM ที่ใช้งานจริง: `lpr_records`, `cameras`, `blacklist_plates`, `health_checks`
- Blueprint บางส่วนยังอิง service ที่ยังไม่มีของจริง: `detection_service`, `map_service`
- สคีมา PostgreSQL ใน `database_schema.sql` ละเอียดกว่าของ ORM ปัจจุบัน (มี `detections`, `vehicles`, `plates`, ฯลฯ) ยังไม่ได้ผูกเข้ากับ UI

### หลักการพัฒนา
- Parity ก่อน: ให้ UI/UX ปัจจุบันทำงานครบกับข้อมูลจริงบน PostgreSQL (ปิด mock และช่องว่างของ service)
- Database-first ภายหลัง: ขยาย ORM ให้ครอบคลุมสคีมาเต็มของ PostgreSQL แล้วค่อย refactor UI/Services ตาม
- คุณภาพ: เพิ่มชุดทดสอบ, ตรวจสอบประสิทธิภาพ, CI/CD
- เอกสารและ Deployment: ปรับ README/Docs, Docker/Compose, โปรไฟล์ Dev/Test/Prod

### แผนงานตามลำดับขั้นตอน (Roadmap)

#### เฟส 1: Core API ↔ UI Parity (ความสำคัญสูง)
- Implement `DetectionService` (DB-backed)
- Implement `MapService` (DB-backed)
- แทนที่ mock API ใน `aicamera.py` ด้วยข้อมูลจริงจาก `cameras`
- ทำความสะอาดและทำให้ endpoint ที่ UI เรียกใช้งานทำงานครบ (retry/validation/pagination)
- Acceptance:
  - Dashboard โหลดสถิติ, สถานะกล้อง, การแจ้งเตือนล่าสุด, บันทึกล่าสุด ได้ถูกต้อง
  - หน้า Records/Blacklist ใช้งานได้ครบ (ค้นหา/รายการ/สถิติ/ดูรายละเอียด)

#### เฟส 2: ขยาย ORM ให้ครอบคลุมสคีมา PostgreSQL เต็ม
- ออกแบบ/สร้าง ORM models สำหรับ: `checkpoints`, `detections`, `vehicles`, `plates`, `health_logs`, `analytics`, `system_logs`
- สร้าง migration scripts (เช่น Alembic) สำหรับการย้ายข้อมูล/แก้สคีมา
- อัปเดต Services ให้ใช้โมเดลใหม่และเพิ่ม endpoint/aggregation ที่จำเป็น
- Acceptance:
  - สามารถจัดเก็บ/ดึงข้อมูล `detections` พร้อม `vehicles/plates` ได้ครบ
  - Analytics พื้นฐาน (daily/camera) ทำจากตารางจริงหรือ view ได้

#### เฟส 3: Real-time Ingestion & Unified Communication
- ผสาน WebSocket/MQTT ingestion กับ DB write (batch/bulk/async)
- เพิ่ม backpressure/retry และ idempotency keys
- ส่ง Event/UI refresh ผ่าน SocketIO ให้ dashboard
- Acceptance:
  - รับข้อมูลเข้าระบบแบบ real-time และอัปเดต UI ได้ทันที

#### เฟส 4: คุณภาพระบบ (Quality & Performance)
- ชุดทดสอบ: unit/integration/API contracts
- Static check/format: flake8, black, isort (หรือเทียบเท่า), pre-commit hooks
- Benchmark พื้นฐาน: throughput ของ ingestion และ latency ของ endpoint สำคัญ
- Acceptance:
  - Coverage ตามเป้าหมาย (เช่น >= 60–70%)
  - เกณฑ์ประสิทธิภาพขั้นต่ำผ่าน (กำหนดตามสเปคเครื่องจริง)

#### เฟส 5: CI/CD และ Deployment
- GitHub Actions: test + lint + build docker
- Dockerfile + docker-compose สำหรับ dev/test/prod
- เอกสารการตั้งค่า environment (ตัวอย่าง `.env`) และการ deploy
- Acceptance:
  - pipeline ผ่านอัตโนมัติ, image สร้างสำเร็จ, compose ขึ้นได้ทั้ง dev/prod

#### เฟส 6: Observability & Ops
- โครงสร้าง Logging/Tracing/Health endpoints
- Metrics (Prometheus/Grafana) และ Alerting เบื้องต้น
- Acceptance:
  - มองเห็นสุขภาพระบบ, มี metrics หลัก และ healthcheck พร้อมใช้ในโปรดักชัน

### การตั้งค่าป้ายกำกับ (Labels)
- Area: `area:api`, `area:ui`, `area:db`, `area:realtime`, `area:devops`, `area:docs`
- Type: `type:feature`, `type:bug`, `type:improvement`, `type:chore`
- Priority: `P0`, `P1`, `P2`
- Size/Estimate: `size:S`, `size:M`, `size:L`

### ความเสี่ยงและการบรรเทา
- ความไม่ตรงกันของสคีมากับ ORM: ใช้ Alembic migration และออกแบบ mapping ชัดเจน
- ปริมาณข้อมูลสูง: เพิ่ม index, batch insert, และ background jobs
- ความพร้อมของเครื่องมือ Edge: จำลองโหลดด้วย test clients และทำ contract ชัดเจน

### เกณฑ์สำเร็จของโปรเจกต์
- UI ทุกหน้าโหลดจากฐานข้อมูลจริง (PostgreSQL) โดยไม่มี mock
- ข้อมูล real-time ถูก ingest และสะท้อนบน dashboard
- ชุดทดสอบ, CI/CD, และเอกสารใช้งานพร้อมสำหรับโปรดักชัน
