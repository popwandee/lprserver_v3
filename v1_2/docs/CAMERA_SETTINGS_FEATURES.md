# ฟีเจอร์การตั้งค่ากล้อง AI Camera v2

## คุณสมบัติใหม่

### 1. การควบคุมแสงสว่าง (Brightness Control)
- **ช่วงค่า**: -1.0 ถึง 1.0
- **ค่าเริ่มต้น**: 0.0
- **การใช้งาน**: ปรับความสว่างของภาพ
  - ค่าติดลบ = ภาพมืดลง
  - ค่าบวก = ภาพสว่างขึ้น

### 2. การควบคุมคอนทราสต์ (Contrast Control)
- **ช่วงค่า**: 0.0 ถึง 2.0
- **ค่าเริ่มต้น**: 1.0
- **การใช้งาน**: ปรับความคมชัดของภาพ
  - ค่าต่ำ = ภาพนุ่มนวล
  - ค่าสูง = ภาพคมชัด

### 3. การควบคุมความอิ่มตัวของสี (Saturation Control)
- **ช่วงค่า**: 0.0 ถึง 2.0
- **ค่าเริ่มต้น**: 1.0
- **การใช้งาน**: ปรับความเข้มของสี
  - ค่าต่ำ = ภาพขาวดำ
  - ค่าสูง = สีเข้มขึ้น

### 4. การควบคุมความคมชัด (Sharpness Control)
- **ช่วงค่า**: 0.0 ถึง 4.0
- **ค่าเริ่มต้น**: 1.0
- **การใช้งาน**: ปรับความคมชัดของขอบภาพ
  - ค่าต่ำ = ภาพนุ่มนวล
  - ค่าสูง = ขอบคมชัด

### 5. การควบคุมระยะโฟกัส (Focus Control)
- **ช่วงค่า**: 0.0 ถึง 1.0
- **ค่าเริ่มต้น**: 0.0
- **การใช้งาน**: ปรับระยะโฟกัสของกล้อง
  - ค่าต่ำ = โฟกัสใกล้
  - ค่าสูง = โฟกัสไกล

### 6. การควบคุมสมดุลแสงขาว (AWB Mode)
- **ช่วงค่า**: 0-8
- **ค่าเริ่มต้น**: 0 (Auto)
- **ตัวเลือก**:
  - 0 = Auto (อัตโนมัติ)
  - 1 = Fluorescent (แสงไฟนีออน)
  - 2 = Incandescent (แสงไฟไส้)
  - 3 = Tungsten (แสงไฟทังสเตน)
  - 4 = Horizon (แสงพระอาทิตย์ตก)
  - 5 = Daylight (แสงกลางวัน)
  - 6 = Cloudy (แสงเมฆ)
  - 7 = Shade (แสงร่มเงา)
  - 8 = Custom (กำหนดเอง)

## การใช้งาน

### ผ่านหน้าเว็บ
1. เปิดเบราว์เซอร์ไปที่ `http://localhost:5000`
2. คลิก "Show Settings" เพื่อแสดงฟอร์มการตั้งค่า
3. ปรับค่าโดยใช้ slider หรือ dropdown
4. คลิก "Update Settings" เพื่อใช้งาน
5. คลิก "Reset to Default" เพื่อกลับไปค่าเริ่มต้น
6. คลิก "Load Current" เพื่อโหลดค่าปัจจุบัน

### ผ่าน API

#### ดูการตั้งค่าปัจจุบัน
```bash
curl http://localhost:5000/api/get_camera_settings
```

#### อัปเดตการตั้งค่า
```bash
# ปรับความสว่าง
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"brightness": 0.5}'

# ปรับหลายค่า
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"brightness": 0.3, "contrast": 1.2, "saturation": 1.1}'

# ปรับระยะโฟกัส
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"focus": 0.7}'

# เปลี่ยนโหมด AWB
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"awb_mode": 5}'
```

## การทดสอบ

### ทดสอบฟีเจอร์ใหม่
```bash
python test_camera_settings.py
```

### ทดสอบแอปพลิเคชันทั้งหมด
```bash
python test_simple_app.py
```

## ตัวอย่างการใช้งาน

### 1. ปรับภาพให้สว่างขึ้น
```bash
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"brightness": 0.3, "contrast": 1.1}'
```

### 2. ปรับภาพให้คมชัดขึ้น
```bash
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"sharpness": 2.0, "contrast": 1.3}'
```

### 3. ปรับสีให้เข้มขึ้น
```bash
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"saturation": 1.5}'
```

### 4. ปรับโฟกัสสำหรับวัตถุใกล้
```bash
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"focus": 0.2}'
```

### 5. ปรับแสงสำหรับสภาพแวดล้อมกลางวัน
```bash
curl -X POST http://localhost:5000/api/update_camera_settings \
  -H "Content-Type: application/json" \
  -d '{"awb_mode": 5, "brightness": 0.1}'
```

## ข้อควรระวัง

1. **การตั้งค่าจะมีผลทันที** - การเปลี่ยนแปลงจะเห็นได้ใน video stream ทันที
2. **การตั้งค่าจะถูกเก็บในหน่วยความจำ** - หากรีสตาร์ทแอปพลิเคชัน การตั้งค่าจะกลับไปค่าเริ่มต้น
3. **การตั้งค่าบางอย่างอาจไม่รองรับ** - ขึ้นอยู่กับฮาร์ดแวร์กล้อง
4. **การตั้งค่าที่ไม่ถูกต้องจะถูกปฏิเสธ** - ระบบจะตรวจสอบช่วงค่าที่ถูกต้อง

## การพัฒนาเพิ่มเติม

### ฟีเจอร์ที่อาจเพิ่มในอนาคต
- การบันทึกการตั้งค่าเป็นโปรไฟล์
- การตั้งค่าอัตโนมัติตามสภาพแสง
- การปรับการตั้งค่าตามเวลา
- การตั้งค่าสำหรับการตรวจจับวัตถุเฉพาะ

### การปรับปรุง UI
- การแสดงผลแบบ real-time
- การเปรียบเทียบก่อน-หลัง
- การบันทึกโปรไฟล์การตั้งค่า
- การแชร์การตั้งค่าผ่าน URL 