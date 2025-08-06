# Simple AI Camera v2

แอปพลิเคชันกล้อง AI ที่เรียบง่ายและเสถียร สำหรับ Raspberry Pi

## คุณสมบัติ

- ✅ การจัดการกล้องที่เรียบง่ายและเสถียร
- ✅ หน้าเว็บควบคุมที่ใช้งานง่าย
- ✅ API สำหรับควบคุมกล้อง
- ✅ การจัดการฐานข้อมูล
- ✅ การบันทึกภาพ
- ✅ การจัดการข้อผิดพลาดที่ดี

## การติดตั้ง

1. เปิดใช้งาน virtual environment:
```bash
cd /home/camuser/aicamera
source setup_env.sh
cd v2
```

2. ตรวจสอบว่ามีไฟล์ที่จำเป็นครบ:
```bash
ls -la simple_app.py templates/simple_index.html
```

## การใช้งาน

### เริ่มต้นแอปพลิเคชัน

```bash
python simple_app.py
```

แอปพลิเคชันจะเริ่มต้นที่ `http://localhost:5000`

### การใช้งานผ่านหน้าเว็บ

1. เปิดเบราว์เซอร์ไปที่ `http://localhost:5000`
2. คลิก "Start Camera" เพื่อเริ่มต้นกล้อง
3. คลิก "Stop Camera" เพื่อหยุดการสตรีม (กล้องยังคงเริ่มต้นอยู่)
4. คลิก "Close Camera" เพื่อปิดกล้องอย่างสมบูรณ์

### การใช้งานผ่าน API

#### ตรวจสอบสถานะกล้อง
```bash
curl http://localhost:5000/api/camera_status
```

#### เริ่มต้นกล้อง
```bash
curl -X POST http://localhost:5000/api/start_camera
```

#### หยุดการสตรีม
```bash
curl -X POST http://localhost:5000/api/stop_camera
```

#### ปิดกล้อง
```bash
curl -X POST http://localhost:5000/api/close_camera
```

### การทดสอบ

ใช้สคริปต์ทดสอบเพื่อตรวจสอบการทำงาน:

```bash
python test_simple_app.py
```

## โครงสร้างไฟล์

```
v2/
├── simple_app.py              # แอปพลิเคชันหลัก
├── templates/
│   └── simple_index.html      # หน้าเว็บควบคุม
├── test_simple_app.py         # สคริปต์ทดสอบ
├── config.py                  # การตั้งค่า
├── database_manager.py        # การจัดการฐานข้อมูล
├── logging_config.py          # การตั้งค่าการบันทึก
└── camera_state.json          # สถานะกล้อง
```

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

1. **แอปพลิเคชันไม่เริ่มต้น**
   - ตรวจสอบว่า virtual environment เปิดใช้งานแล้ว
   - ตรวจสอบว่ามีไฟล์ที่จำเป็นครบ

2. **กล้องไม่ทำงาน**
   - ตรวจสอบการเชื่อมต่อกล้อง
   - ตรวจสอบสิทธิ์การเข้าถึงกล้อง
   - รีสตาร์ทระบบ

3. **หน้าเว็บไม่แสดง**
   - ตรวจสอบว่าแอปพลิเคชันทำงานที่พอร์ต 5000
   - ตรวจสอบไฟร์วอลล์

### การบันทึก

การบันทึกจะถูกเก็บในโฟลเดอร์ `log/` และแสดงในคอนโซล

## การพัฒนา

### เพิ่มฟีเจอร์ใหม่

1. แก้ไข `simple_app.py` เพื่อเพิ่ม API endpoints
2. แก้ไข `templates/simple_index.html` เพื่อเพิ่ม UI
3. ทดสอบด้วย `test_simple_app.py`

### การตั้งค่า

แก้ไข `config.py` เพื่อเปลี่ยนการตั้งค่าต่างๆ:

- `DEFAULT_RESOLUTION`: ความละเอียดกล้อง
- `DEFAULT_FRAMERATE`: อัตราเฟรม
- `FLASK_PORT`: พอร์ตของแอปพลิเคชัน

## ความแตกต่างจากแอปพลิเคชันเดิม

- **เรียบง่าย**: ไม่มีการจัดการกล้องที่ซับซ้อน
- **เสถียร**: ไม่มีการเริ่มต้นกล้องอัตโนมัติที่อาจทำให้ติดค้าง
- **ควบคุมได้**: ผู้ใช้สามารถควบคุมการเริ่มต้น/หยุดกล้องได้
- **ทดสอบได้**: มีสคริปต์ทดสอบแยกต่างหาก

## การสนับสนุน

หากมีปัญหา กรุณาตรวจสอบ:
1. การบันทึกในคอนโซล
2. ไฟล์บันทึกใน `log/`
3. สถานะกล้องใน `camera_state.json` 


# โครงร่างเอกสาร

## 1. บทนำ  

- วัตถุประสงค์  
- ขอบเขตการใช้งาน  
- คำศัพท์และตัวย่อที่ใช้ในเอกสาร  

---  

## 2. ภาพรวมระบบ  

- สถาปัตยกรรมโดยรวม  
- กระบวนการทำงาน (Workflow)  
- ข้อกำหนดทางเทคนิค (Requirements)  

---  

## 3. ฮาร์ดแวร์  

### 3.1 อุปกรณ์หลัก  
- บอร์ดประมวลผล (เช่น Raspberry Pi)  
- โมดูลกล้อง (IMX708, IMX219 ฯลฯ)  
- แหล่งแสงอินฟราเรด (IR LEDs)  

### 3.2 ส่วนขยาย  
- PCIe HATs, LTE Module, GNSS Module  
- พอร์ตและการเชื่อมต่อ (GPIO, USB, Ethernet)  

---  

## 4. สถาปัตยกรรมซอฟต์แวร์  

### 4.1 แผนภาพโมดูล (Component Diagram)  
### 4.2 โครงสร้างโฟลเดอร์ในรีโพ (Repository Layout)  
### 4.3 ไลบรารีภายนอกและ Dependencies  

---  

## 5. ไพพ์ไลน์การตรวจจับและอ่านทะเบียน  

### 5.1 Image Preprocessing  
- Denoising, Sharpening, Rotation  
- ปรับแสงและชดเชยสี  

### 5.2 Vehicle Detection Module  
- โมเดลและอัลกอริทึม  
- การตั้งค่าพารามิเตอร์  

### 5.3 License Plate Recognition (LPR)  
- Plate Detection  
- OCR Engine  
- การปรับแต่งไฟล์ Tuning  

---  

## 6. การตรวจสอบสถานะอุปกรณ์ (Device Monitoring)  

- ตรวจสถานะกล้องและ IR LEDs  
- ตรวจวัดอุณหภูมิ, แรงดันไฟ, หน่วยความจำ  
- ระบบ Logging และ Alert  

---  

## 7. การส่งข้อมูลไปยัง LPR Server  

- โครงสร้างข้อมูล (Payload Schema)  
- โปรโตคอลการสื่อสาร (HTTP/MQTT/WebSocket)  
- กลไก Retry และ Queueing  

---  

## 8. เอกสารอ้างอิงโค้ด (API & Class Reference)  

### 8.1 โครงสร้างคลาสหลัก  
- LPRDetector  
- DeviceMonitor  
- DataTransmitter  

### 8.2 เมธอดและฟังก์ชันสำคัญ  
- `detect_vehicle()`  
- `read_plate()`  
- `check_device_status()`  
- `send_to_server()`  

### 8.3 ตัวอย่างการใช้งาน (Usage Examples)  

---  

## 9. การติดตั้งและปรับใช้ (Deployment Guide)  

- การเตรียมสภาพแวดล้อม (Prerequisites)  
- ขั้นตอนการติดตั้ง (Setup Steps)  
- คำสั่ง Git Clone และการ Checkout เวอร์ชัน  
- การใช้งาน Docker / Containerization  
- Continuous Integration / Continuous Deployment (CI/CD)  

---  

## 10. กลยุทธ์จัดการเวอร์ชัน (Version Management)  

- Branching Strategy (Git Flow / Trunk-Based)  
- Release Notes และ CHANGELOG  
- ขั้นตอนอัปเดตโปรดักชัน  

---  

## 11. การทดสอบและประเมินผล  

### 11.1 Unit Tests และ Integration Tests  
### 11.2 Performance Benchmarks  
- เวลา Latency  
- Throughput  
- การใช้ทรัพยากร (CPU, Memory)  

### 11.3 การทดสอบภาคสนาม (Field Trials)  

---  

## 12. ผลการทดลองและวิเคราะห์  

- สรุปผล Accuracy และ Error Rate  
- การวิเคราะห์จุดเด่นจุดด้อย  
- เปรียบเทียบกับระบบเดิม  

---  

## 13. สรุปและข้อเสนอแนะในอนาคต  

- ผลสำเร็จที่ได้  
- ข้อจำกัดของงานวิจัย  
- แนวทางพัฒนาต่อยอด  

---  

## 14. ภาคผนวก  

- ค่า Configuration Parameters  
- โครงสร้าง Data Schema  
- ไดอะแกรม PlantUML / Sequence Diagrams  
- บัญชีคำศัพท์ (Glossary)  
- เอกสารอ้างอิง (References)  

---  

> นอกจากโครงร่างนี้แล้ว คุณอาจเพิ่ม  
> - แผนภาพ Deployment Topology  
> - ตัวอย่าง Log File และขั้นตอนวิเคราะห์  
> - แผนงาน (Roadmap) สำหรับ Milestones ต่อไป  
> - แนวทางการขยายระบบในอนาคต เช่น รองรับกล้องหลายตัวหรือระบบคลาวด์  