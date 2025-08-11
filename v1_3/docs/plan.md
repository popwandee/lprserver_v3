ศึกษา ARCHITECTURE.md โครงสร้างของโปรเจกต์ และ CONTEXT_ENGINEERING.md แล้วพัฒนาฟังก์ชั่น Health monitor Sub-Task 2.4.1 และ Sub-Task 2.4.2 โดยใช้มาตรฐาน PEP8 และข้อกำหนดใน updated_variable_mapping_diagram.md และ VARIABLE_MANAGEMENT.md เพื่อให้เข้ากันได้กับระบบที่ดี และไม่เกิดปัญหา conflict ดังนี้
  
 Sub-Task 2.4.1: พัฒนา Class HealthMonitor
 Context Engineering: Class HealthMonitor ทำหน้าที่ตรวจสอบสถานะของส่วนประกอบต่างๆ ของระบบเป็นระยะเวลา. การตรวจสอบประกอบด้วย: สถานะกล้อง, 
 พื้นที่ดิสก์ที่ใช้บันทึกภาพ, สถานะ CPU และ RAM เช่น อุณหภูมิ, ปริมาณการใช้, พื้นที่ว่าง, ความครบถ้วนของไฟล์โมเดล Detection, ความสามารถในการ Import AI Model, การเชื่อมต่อฐานข้อมูล และการเชื่อมต่อเครือข่ายภายนอก (เช่น Google DNS) และ WebSocket Server.
▪ "พัฒนา Class HealthMonitor โดยมี Method init ที่ Initialize เชื่อมต่อ Database. Implement Method ย่อยๆ สำหรับการตรวจสอบแต่ละส่วนประกอบ: check_camera() (ตรวจสอบว่ากล้องพร้อมใช้งานได้ และ Streaming อยู่หรือไม่), check_disk_space() (ตรวจสอบพื้นที่ว่างในดิสก์ที่ใช้บันทึกรูปภาพ), check_cpu_ram() , check_model_loading() (ตรวจสอบว่าไฟล์โมเดล Detection ครบถ้วนตาม Path ที่กำหนด), check_easyocr_init() (ตรวจสอบว่าสามารถ Import EasyOCR ได้), check_database_connection() (ตรวจสอบว่าการเชื่อมต่อฐานข้อมูลยังทำงานอยู่) และ check_network_connectivity() (ตรวจสอบการเชื่อมต่อเครือข่ายภายนอก Googel DNS และ WebSocket Server)."

Sub-Task 2.4.2: บันทึกผลการตรวจสอบลงในตาราง health_checks
▪ Context Engineering: ผลการตรวจสอบ Health Check ทั้งหมดจะถูกบันทึกในตาราง health_checks ในฐานข้อมูลผ่าน DatabaseManager. แต่ละ Method การตรวจสอบใน HealthMonitor ควรใช้ฟังก์ชันช่วยเหลือ _log_result เพื่อบันทึกผล.
▪"ใน Class HealthMonitor, ตรวจสอบให้แน่ใจว่าแต่ละ Method การตรวจสอบ (check_camera, check_disk_space, ฯลฯ) เรียกใช้ Method self._log_result() เพื่อบันทึกผลการตรวจสอบ (Timestamp, Component, Status ('PASS'/'FAIL'), Message) ลงในตาราง health_checks ผ่าน DatabaseManager.insert_health_check_result()".

ออกแบบ และสร้าง web UI /health สำหรับแสดงผลสถานะระบบในภาพรวมทั้งหมด
พัฒนาฟังก์ชั่น Health monitor ตามที่ระบุใน plan.md โดยเริ่มจากการพัฒนาคลาส HealthMonitor และเพิ่มตาราง health_checks ในฐานข้อมูล

สร้างตาราง health_checks ใน DatabaseManager:
เพิ่ม method สำหรับบันทึกผลการตรวจสอบใน DatabaseManager:
พัฒนาคลาส HealthService สำหรับจัดการ business logic:
เพิ่ม import ที่ขาดหายไปใน HealthService:
ลงทะเบียน HealthService ใน DI container:
พัฒนาคลาส Health Blueprint สำหรับ web interface:
สร้าง template สำหรับ health dashboard:


### 🏥 System Health
class HealthStatusAPI {
    + success: bool
    + health: dict
    + timestamp: str
    --
    **Health Fields:**
    + overall_status: str
    + components: dict
    --
    **System Health Fields:**
    + cpu_usage: float
    + memory_usage: dict
    + disk_usage: dict
    + uptime: float
    + last_check: str
}

#### GET `/health/system`
รับสถานะสุขภาพระบบ

**Response:**
```json
{
    "success": true,
    "health": {
        "overall_status": "healthy",
        "components": {
            "camera": {
                "status": "healthy",
                "initialized": true,
                "streaming": true,
                "last_check": "2025-08-09T18:36:57.390144"
            },
            "detection": {
                "status": "healthy", 
                "models_loaded": true,
                "last_check": "2025-08-09T18:36:57.390144"
            },
            "database": {
                "status": "healthy",
                "connected": true,
                "last_check": "2025-08-09T18:36:57.390144"
            },
            "system": {
                "status": "healthy",
                "cpu_usage": 15.5,
                "memory_usage": {
                    "used": 2048,
                    "total": 8192,
                    "percentage": 25.0
                },
                "disk_usage": {
                    "used": 50000,
                    "total": 200000,
                    "percentage": 25.0
                },
                "uptime": 86400.5,
                "last_check": "2025-08-09T18:36:57.390144"
            }
        }
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### GET `/health/logs`
รับ system logs

**Query Parameters:**
- `level` (optional): log level (DEBUG, INFO, WARNING, ERROR)
- `limit` (optional): จำนวน log entries (default: 100, max: 1000)

**Response:**
```json
{
    "success": true,
    "data": {
        "logs": [
            {
                "timestamp": "2025-08-09T18:36:57.390144",
                "level": "INFO",
                "module": "camera_manager",
                "message": "Camera started successfully",
                "details": {}
            }
        ],
        "total_count": 1500,
        "level_filter": "INFO",
        "limit": 100
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```
{
  "success": true,
  "timestamp": "2025-08-10T13:50:58.158085",
  "data": {
    "overall_status": "critical",
    "last_check": "2025-08-10T13:50:58.158081",
    "components": {
      "camera": {
        "status": "unhealthy",
        "initialized": true,
        "streaming": true,
        "frame_count": 0,
        "average_fps": 0.0,
        "uptime": 342.024412,
        "auto_start_enabled": true,
        "last_check": null
      },
      "database": {
        "status": "unhealthy",
        "connected": true,
        "database_path": "/home/camuser/aicamera/db/lpr_data.db",
        "last_check": null
      },
      "detection": {
        "status": "unhealthy",
        "models_loaded": false,
        "easyocr_available": false,
        "detection_active": false,
        "auto_start": true,
        "last_check": null
      },
      "system": {
        "status": "healthy",
        "last_check": "2025-08-10T13:50:58.158050"
      }
    },
    "system": {
      "cpu_usage": 34.3,
      "cpu_count": 4,
      "memory_usage": {
        "used": 4.15,
        "total": 15.84,
        "percentage": 27.1
      },
      "disk_usage": {
        "used": 18.74,
        "total": 57.44,
        "percentage": 32.6
      },
      "uptime": 354.1
    }
  }
}

ps aux | grep gunicorn
camuser@aicamera1:~/aicamera $ ps aux | grep gunicorn
your 131072x1 screen size is bogus. expect trouble
camuser      837  0.0  0.1  33888 22272 ?        Ss   15:01   0:00 gunicorn: master [aicamera_v1.3]
camuser     1044 30.6 18.0 6423584 2990800 ?     SLl  15:01   2:00 gunicorn: worker [aicamera_v1.3]
camuser    15728  0.0  0.0   6240  1600 pts/1    S+   15:07   0:00 grep --color=auto gunicorn

kill -HUP 837

systemd → gunicorn → nginx → camera start → detection start → health monitor start

ตรวจสอบการแสดงผลข้อมูลเหล่านี้ในหน้า main dashboard ว่ามีการใช้ตัวแปรถูกต้องหรือไม่ เป็นไปตามกฎ variable_management.md และ updated_variable_mapping_diagram.puml หรือไม่ ได้แก่ข้อมูลดังนี้
CPU Architecture: Loading...
AI Accelerator: Test AI Accelerator
OS & Kernel: Loading...
RAM: Loading...
Disk: Loading...
โดยไม่เปลี่ยนแปลงแก้ไขส่วนอื่น หากจำเป็นต้องแก้ไขให้แจ้งให้ทราบก่อน

1.modify camera to display meta data instead of frame count or avg fps
add websocket
2.
create LPR web server to manage with cursor background
Create AICAMERA Standalone for demo