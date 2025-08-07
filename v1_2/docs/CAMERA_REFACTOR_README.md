# Camera Configuration Refactor

## การเปลี่ยนแปลงหลัก

### 1. สร้างไฟล์ `camera_config.py` ใหม่
- รวมการตั้งค่ากล้องทั้งหมดไว้ในที่เดียว
- ลดความซ้ำซ้อนของการตั้งค่า resolution ในหลายไฟล์
- แยกการตั้งค่าสำหรับ detection และ video feed

### 2. สลับการใช้ Stream
- **Detection**: ใช้ **main stream** (ความละเอียดสูงกว่า) สำหรับการตรวจจับที่แม่นยำ
- **Video Feed**: ใช้ **lores stream** (ความละเอียดต่ำกว่า) สำหรับการแสดงผล

### 3. การตั้งค่า Resolution
```python
# Detection ใช้ main stream (ความละเอียดสูงกว่า)
DETECTION_RESOLUTION = (640, 640)

# Video feed ใช้ lores stream (ความละเอียดต่ำกว่า)  
VIDEO_FEED_RESOLUTION = (640, 640)
```

## ไฟล์ที่เปลี่ยนแปลง

### ไฟล์ใหม่
- `camera_config.py` - รวมการตั้งค่ากล้องทั้งหมด

### ไฟล์ที่อัปเดต
- `app.py` - ใช้ config ใหม่, สลับการใช้ stream
- `detection_thread.py` - ใช้ main stream สำหรับ detection
- `camera_state.json` - ใช้การตั้งค่าใหม่

## ประโยชน์ของการเปลี่ยนแปลง

1. **ลดความซ้ำซ้อน**: การตั้งค่า resolution อยู่ในที่เดียว
2. **ประสิทธิภาพดีขึ้น**: Detection ใช้ความละเอียดสูงกว่า
3. **การบำรุงรักษาง่ายขึ้น**: แก้ไขการตั้งค่าในที่เดียว
4. **ความชัดเจน**: แยกการใช้งาน stream ตามวัตถุประสงค์

## การใช้งาน

### การเปลี่ยน Resolution
แก้ไขใน `camera_config.py`:
```python
DETECTION_RESOLUTION = (1280, 720)  # สำหรับ detection
VIDEO_FEED_RESOLUTION = (640, 480)  # สำหรับ video feed
```

### การเปลี่ยนการตั้งค่ากล้องอื่นๆ
แก้ไขใน `camera_config.py`:
```python
DEFAULT_BRIGHTNESS = 0.0
DEFAULT_CONTRAST = 1.0
# ... etc
```

## การทดสอบ

1. รันแอปพลิเคชัน: `./run_app.sh`
2. ตรวจสอบ logs ว่าการตั้งค่า stream ถูกต้อง
3. ทดสอบ detection และ video feed
4. ตรวจสอบประสิทธิภาพการตรวจจับ 