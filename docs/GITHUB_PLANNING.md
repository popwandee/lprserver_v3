## GitHub Project Planning – LPR Server v3

เอกสารนี้กำหนดโครงสร้าง Project/Milestones/Issues/Tasks สำหรับนำขึ้น GitHub Projects

### Projects
- Project: LPR Server v3 Roadmap (Kanban)
  - Columns: Backlog, In Progress, Review, Done

### Milestones
1) M1 – Core API ↔ UI Parity
- เป้าหมาย: ให้หน้า Dashboard/Records/Blacklist ใช้งานกับ DB จริงครบ
- ระยะเวลา: 2 สัปดาห์

2) M2 – ORM & DB Expansion
- เป้าหมาย: ขยาย ORM ให้ครอบคลุมสคีมาเต็ม และ migration พร้อมใช้
- ระยะเวลา: 3 สัปดาห์

3) M3 – Real-time & Unified Communication
- เป้าหมาย: เชื่อม ingestion real-time กับ DB + UI
- ระยะเวลา: 2 สัปดาห์

4) M4 – Quality & Performance
- เป้าหมาย: Test/Lint/Benchmark พื้นฐาน พร้อมใช้งาน
- ระยะเวลา: 2 สัปดาห์

5) M5 – CI/CD & Deployment
- เป้าหมาย: Pipeline + Docker/Compose สำหรับ dev/prod
- ระยะเวลา: 2 สัปดาห์

6) M6 – Observability & Ops
- เป้าหมาย: Logging/Tracing/Health/Metrics พร้อม
- ระยะเวลา: 2 สัปดาห์

### Labels
- area: `area:api`, `area:ui`, `area:db`, `area:realtime`, `area:devops`, `area:docs`
- type: `type:feature`, `type:bug`, `type:improvement`, `type:chore`
- priority: `P0`, `P1`, `P2`
- size: `size:S`, `size:M`, `size:L`

### Issues & Tasks (CSV Template)
ไฟล์ CSV ต่อไปนี้ช่วย import เป็น Issues ใน GitHub ได้ โดยใส่ Milestone/Labels/Assignees ทีหลังตามความเหมาะสม

Columns: Title, Body, Labels, Milestone

```csv
Title,Body,Labels,Milestone
Implement DetectionService,"สร้างบริการเชื่อมต่อ DB สำหรับดึง/บันทึก detection และ endpoints ที่เกี่ยวข้อง","area:api;area:db;type:feature;P0;size:L","M1 – Core API ↔ UI Parity"
Implement MapService,"สร้างบริการข้อมูลแผนที่/การติดตาม และ endpoints","area:api;area:db;type:feature;P0;size:L","M1 – Core API ↔ UI Parity"
Replace mock in aicamera API with DB,"แทนที่ข้อมูล mock ใน aicamera.py ให้ดึงจาก cameras","area:api;area:db;type:improvement;P0;size:M","M1 – Core API ↔ UI Parity"
Harden /api endpoints (validation/pagination),"เพิ่ม validation, error handling, pagination มาตรฐาน","area:api;type:improvement;P1;size:M","M1 – Core API ↔ UI Parity"
Create ORM models for full PostgreSQL schema,"เพิ่ม models: checkpoints,detections,vehicles,plates,health_logs,analytics,system_logs","area:db;type:feature;P0;size:L","M2 – ORM & DB Expansion"
Introduce Alembic migrations,"ตั้งค่า Alembic และสร้าง migration scripts เบื้องต้น","area:db;area:devops;type:feature;P1;size:M","M2 – ORM & DB Expansion"
Update services to use new models,"อัปเดต service ให้ใช้โมเดลใหม่ + aggregation","area:api;area:db;type:improvement;P1;size:L","M2 – ORM & DB Expansion"
Integrate real-time ingestion with DB,"ผสาน WebSocket/MQTT ingestion กับการเขียน DB","area:realtime;area:db;type:feature;P0;size:L","M3 – Real-time & Unified Communication"
Emit UI events via SocketIO,"ส่ง event ไป UI เมื่อมีข้อมูลใหม่/alert","area:realtime;area:ui;type:feature;P1;size:M","M3 – Real-time & Unified Communication"
Add unit/integration tests,"เพิ่มชุดทดสอบสำคัญสำหรับ models/services/endpoints","area:docs;type:feature;P1;size:L","M4 – Quality & Performance"
Add lint/format & pre-commit,"ตั้งค่า flake8 black isort pre-commit","area:devops;type:chore;P2;size:S","M4 – Quality & Performance"
Benchmark key paths,"ทดสอบ throughput/latency เบื้องต้นและบันทึกผล","area:devops;type:improvement;P2;size:M","M4 – Quality & Performance"
Add GitHub Actions CI,"เพิ่ม workflow สำหรับ test+lint/build docker","area:devops;type:feature;P1;size:M","M5 – CI/CD & Deployment"
Add Dockerfile & docker-compose,"เตรียม container สำหรับ dev/prod + README","area:devops;type:feature;P1;size:M","M5 – CI/CD & Deployment"
Write deployment docs,"เขียนคู่มือการ deploy และ env config","area:docs;type:improvement;P2;size:S","M5 – CI/CD & Deployment"
Add health/logging/metrics endpoints,"เพิ่ม endpoint/handler สำหรับ health/logging/metrics","area:devops;type:feature;P1;size:M","M6 – Observability & Ops"
Add monitoring stack (optional),"รวม Prometheus/Grafana และ alerting เบื้องต้น","area:devops;type:improvement;P2;size:M","M6 – Observability & Ops"
```

### วิธีใช้งาน
- สร้าง Project ใน GitHub: Projects → New → Kanban → ตั้งชื่อ “LPR Server v3 Roadmap”
- สร้าง Milestones ตามด้านบนในหน้า Issues → Milestones
- Import Issues จาก CSV: ไปที่ Issues → “Import issues” (ผ่าน GitHub CLI/3rd party) หรือสร้างด้วยมือ แล้วผูก Milestone/Labels
- ตั้งค่า Labels ในหน้า Issues → Labels

