# Database Setup Guide for LPR Server v3

## 🗄️ คู่มือการตั้งค่าฐานข้อมูล PostgreSQL สำหรับ LPR Server v3

### 📋 **ภาพรวมฐานข้อมูล**

ฐานข้อมูล PostgreSQL ถูกออกแบบมาเพื่อรองรับการจัดเก็บและบริหารจัดการข้อมูลจาก AI Camera (Edge) อย่างครบถ้วนและมีประสิทธิภาพ
export DATABASE_URL="postgresql://lpruser:your_actual_password@localhost:5432/lprserver_v3"
   export TEST_DATABASE_URL="postgresql://lpruser:your_actual_password@localhost:5432/lprserver_v3_test"
#### **🎯 วัตถุประสงค์**
- จัดเก็บข้อมูลการตรวจจับจาก AI Camera
- บริหารจัดการข้อมูลจุดตรวจสอบและกล้อง
- วิเคราะห์และแสดงผลสถิติ
- จัดการ blacklist และการแจ้งเตือน
- บันทึกการทำงานของระบบ

### 🏗️ **โครงสร้างฐานข้อมูล**

#### **📊 ตารางหลัก (9 ตาราง)**

1. **checkpoints** - จุดตรวจสอบต่างๆ ในระบบ
2. **cameras** - กล้อง AI ที่ติดตั้งในแต่ละจุด
3. **detections** - ข้อมูลการตรวจจับจาก AI Camera
4. **vehicles** - ข้อมูลรถที่ตรวจพบ
5. **plates** - ข้อมูลป้ายทะเบียนที่อ่านได้
6. **health_logs** - ข้อมูลสุขภาพของกล้อง
7. **blacklist** - รายชื่อป้ายทะเบียนที่ต้องเฝ้าระวัง
8. **analytics** - ข้อมูลสถิติและวิเคราะห์
9. **system_logs** - บันทึกการทำงานของระบบ

#### **👁️ Views (3 views)**

1. **daily_statistics** - สถิติรายวันของแต่ละจุดตรวจสอบ
2. **recent_detections** - การตรวจจับล่าสุดพร้อมข้อมูลป้ายทะเบียน
3. **camera_health** - สถานะสุขภาพของกล้องทั้งหมด

#### **🔍 Indexes (18 indexes)**

สร้าง indexes สำหรับ performance ที่ดีขึ้นในทุกตารางหลัก

### 🚀 **วิธีการติดตั้ง**

#### **1. ติดตั้ง PostgreSQL**

```bash
# อัปเดต package list
sudo apt update

# ติดตั้ง PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# เริ่มต้น service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### **2. ตั้งค่าฐานข้อมูล**

```bash
# รัน script ติดตั้งอัตโนมัติ
python setup_postgresql_database.py
```

#### **3. ติดตั้งด้วย SQL โดยตรง**

```bash
# เชื่อมต่อ PostgreSQL
sudo -u postgres psql

# สร้างฐานข้อมูล
CREATE DATABASE lprserver_v3;
CREATE USER lpruser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lprserver_v3 TO lpruser;

# ตั้งค่า Authentication (สำคัญ!)
# แก้ไขไฟล์ pg_hba.conf เพื่อเปลี่ยนจาก peer เป็น md5
sudo nano /etc/postgresql/*/main/pg_hba.conf
# เปลี่ยนบรรทัด: local   all             all                                     peer
# เป็น:        local   all             all                                     md5

# รีสตาร์ท PostgreSQL
sudo systemctl restart postgresql

# ตั้งค่า Database Owner และ Permissions
sudo -u postgres psql -c "ALTER DATABASE lprserver_v3 OWNER TO lpruser;"
sudo -u postgres psql -c "GRANT CREATE ON SCHEMA public TO lpruser;"
sudo -u postgres psql -c "GRANT USAGE ON SCHEMA public TO lpruser;"

# รัน SQL schema
psql -U lpruser -d lprserver_v3 -h localhost -f database_schema.sql
```

### 📊 **รายละเอียดตาราง**

#### **1. checkpoints**
```sql
CREATE TABLE checkpoints (
    id SERIAL PRIMARY KEY,
    checkpoint_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **2. cameras**
```sql
CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(50) UNIQUE NOT NULL,
    checkpoint_id VARCHAR(50) REFERENCES checkpoints(checkpoint_id),
    name VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    ip_address INET,
    mac_address MACADDR,
    status VARCHAR(20) DEFAULT 'active',
    health_status VARCHAR(20) DEFAULT 'unknown',
    health_details JSONB,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_health_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **3. detections**
```sql
CREATE TABLE detections (
    id SERIAL PRIMARY KEY,
    detection_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    camera_id VARCHAR(50) REFERENCES cameras(camera_id),
    checkpoint_id VARCHAR(50) REFERENCES checkpoints(checkpoint_id),
    timestamp TIMESTAMP NOT NULL,
    vehicles_count INTEGER DEFAULT 0,
    plates_count INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    annotated_image_path VARCHAR(500),
    annotated_image_data BYTEA,
    confidence_score DECIMAL(5,4),
    detection_type VARCHAR(50) DEFAULT 'lpr',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **4. vehicles**
```sql
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    detection_id UUID REFERENCES detections(detection_id) ON DELETE CASCADE,
    vehicle_index INTEGER,
    bbox_x1 INTEGER,
    bbox_y1 INTEGER,
    bbox_x2 INTEGER,
    bbox_y2 INTEGER,
    confidence DECIMAL(5,4),
    vehicle_class VARCHAR(50),
    vehicle_type VARCHAR(50),
    color VARCHAR(50),
    brand VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **5. plates**
```sql
CREATE TABLE plates (
    id SERIAL PRIMARY KEY,
    detection_id UUID REFERENCES detections(detection_id) ON DELETE CASCADE,
    vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE CASCADE,
    plate_index INTEGER,
    plate_number VARCHAR(20) NOT NULL,
    bbox_x1 INTEGER,
    bbox_y1 INTEGER,
    bbox_x2 INTEGER,
    bbox_y2 INTEGER,
    confidence DECIMAL(5,4),
    plate_type VARCHAR(50),
    country VARCHAR(50) DEFAULT 'TH',
    province VARCHAR(100),
    cropped_image_path VARCHAR(500),
    cropped_image_data BYTEA,
    ocr_raw_result TEXT,
    ocr_processed_result VARCHAR(20),
    is_valid BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🔗 **ความสัมพันธ์ระหว่างตาราง**

```
checkpoints (1) ←→ (N) cameras
checkpoints (1) ←→ (N) detections
cameras (1) ←→ (N) detections
detections (1) ←→ (N) vehicles
detections (1) ←→ (N) plates
vehicles (1) ←→ (N) plates
cameras (1) ←→ (N) health_logs
checkpoints (1) ←→ (N) health_logs
checkpoints (1) ←→ (N) analytics
cameras (1) ←→ (N) analytics
plates (N) ←→ (1) blacklist
```

### 📈 **Views สำหรับการวิเคราะห์**

#### **1. daily_statistics**
```sql
SELECT 
    DATE(d.timestamp) as date,
    c.checkpoint_id,
    c.name as checkpoint_name,
    cam.camera_id,
    cam.name as camera_name,
    COUNT(d.id) as total_detections,
    SUM(d.vehicles_count) as total_vehicles,
    SUM(d.plates_count) as total_plates,
    COUNT(DISTINCT p.plate_number) as unique_plates,
    AVG(d.processing_time_ms) as avg_processing_time,
    COUNT(CASE WHEN b.plate_number IS NOT NULL THEN 1 END) as blacklist_hits
FROM detections d
LEFT JOIN checkpoints c ON d.checkpoint_id = c.checkpoint_id
LEFT JOIN cameras cam ON d.camera_id = cam.camera_id
LEFT JOIN plates p ON d.detection_id = p.detection_id
LEFT JOIN blacklist b ON p.plate_number = b.plate_number AND b.is_active = true
GROUP BY DATE(d.timestamp), c.checkpoint_id, c.name, cam.camera_id, cam.name
ORDER BY date DESC, checkpoint_id, camera_id;
```

#### **2. recent_detections**
```sql
SELECT 
    d.detection_id,
    d.timestamp,
    c.checkpoint_id,
    c.name as checkpoint_name,
    cam.camera_id,
    cam.name as camera_name,
    d.vehicles_count,
    d.plates_count,
    d.processing_time_ms,
    p.plate_number,
    p.confidence as plate_confidence,
    v.vehicle_class,
    v.confidence as vehicle_confidence,
    CASE WHEN b.plate_number IS NOT NULL THEN true ELSE false END as is_blacklisted
FROM detections d
LEFT JOIN checkpoints c ON d.checkpoint_id = c.checkpoint_id
LEFT JOIN cameras cam ON d.camera_id = cam.camera_id
LEFT JOIN plates p ON d.detection_id = p.detection_id
LEFT JOIN vehicles v ON d.detection_id = v.detection_id
LEFT JOIN blacklist b ON p.plate_number = b.plate_number AND b.is_active = true
ORDER BY d.timestamp DESC;
```

### 🔧 **การตั้งค่าใน Application**

#### **1. Environment Variables**
```bash
# Database configuration
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=lpruser
export DB_PASSWORD=your_password
export DB_NAME=lprserver_v3
```

#### **2. config.py**
```python
# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    f"postgresql://{os.environ.get('DB_USER', 'lpruser')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'lprserver_v3')}"
```

### 📊 **ตัวอย่างการใช้งาน**

#### **1. เพิ่มข้อมูลการตรวจจับ**
```python
import psycopg2
from datetime import datetime
import uuid

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="lprserver_v3",
    user="lpruser",
    password="your_password"
)
cursor = conn.cursor()

# Insert detection
detection_id = str(uuid.uuid4())
cursor.execute("""
    INSERT INTO detections (detection_id, camera_id, checkpoint_id, timestamp, vehicles_count, plates_count, processing_time_ms)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", (detection_id, 'CAM001', 'CP001', datetime.now(), 1, 1, 150))

# Insert vehicle
cursor.execute("""
    INSERT INTO vehicles (detection_id, vehicle_index, bbox_x1, bbox_y1, bbox_x2, bbox_y2, confidence, vehicle_class)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (detection_id, 0, 100, 100, 200, 200, 0.95, 'car'))

# Insert plate
cursor.execute("""
    INSERT INTO plates (detection_id, vehicle_id, plate_index, plate_number, confidence, country)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (detection_id, 1, 0, 'ABC1234', 0.92, 'TH'))

conn.commit()
cursor.close()
conn.close()
```

#### **2. ดูสถิติรายวัน**
```python
cursor.execute("SELECT * FROM daily_statistics WHERE date = CURRENT_DATE")
daily_stats = cursor.fetchall()
for stat in daily_stats:
    print(f"Date: {stat[0]}, Checkpoint: {stat[2]}, Detections: {stat[5]}")
```

#### **3. ตรวจสอบ blacklist**
```python
cursor.execute("""
    SELECT p.plate_number, p.confidence, b.reason, b.alert_level
    FROM plates p
    JOIN blacklist b ON p.plate_number = b.plate_number
    WHERE b.is_active = true
    ORDER BY p.created_at DESC
    LIMIT 10
""")
blacklist_hits = cursor.fetchall()
```

### 🔍 **การตรวจสอบและบำรุงรักษา**

#### **1. ตรวจสอบสถานะฐานข้อมูล**
```sql
-- ตรวจสอบขนาดฐานข้อมูล
SELECT pg_size_pretty(pg_database_size('lprserver_v3'));

-- ตรวจสอบจำนวน records ในแต่ละตาราง
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY tablename, attname;
```

#### **2. การทำ Backup**
```bash
# Backup ฐานข้อมูล
pg_dump -U lpruser -h localhost lprserver_v3 > lprserver_backup.sql

# Restore ฐานข้อมูล
psql -U lpruser -h localhost lprserver_v3 < lprserver_backup.sql
```

#### **3. การทำ Maintenance**
```sql
-- Analyze tables
ANALYZE detections;
ANALYZE plates;
ANALYZE vehicles;

-- Vacuum tables
VACUUM ANALYZE detections;
VACUUM ANALYZE plates;
VACUUM ANALYZE vehicles;
```

### 📈 **Performance Optimization**

#### **1. Partitioning**
```sql
-- Partition detections table by date
CREATE TABLE detections_2024_01 PARTITION OF detections
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE detections_2024_02 PARTITION OF detections
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

#### **2. Archiving**
```sql
-- Archive old data
INSERT INTO detections_archive 
SELECT * FROM detections 
WHERE created_at < CURRENT_DATE - INTERVAL '1 year';

DELETE FROM detections 
WHERE created_at < CURRENT_DATE - INTERVAL '1 year';
```

### 🔒 **Security**

#### **1. User Permissions**
```sql
-- Create read-only user
CREATE USER lpr_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE lprserver_v3 TO lpr_readonly;
GRANT USAGE ON SCHEMA public TO lpr_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO lpr_readonly;
```

#### **2. SSL Connection**
```python
# Enable SSL in connection
conn = psycopg2.connect(
    host="localhost",
    database="lprserver_v3",
    user="lpruser",
    password="your_password",
    sslmode="require"
)
```

### 📋 **การตรวจสอบ**

#### **1. ตรวจสอบการติดตั้ง**
```bash
# ตรวจสอบ PostgreSQL service
sudo systemctl status postgresql

# ตรวจสอบการเชื่อมต่อ
psql -U lpruser -h localhost -d lprserver_v3 -c "SELECT version();"

# ตรวจสอบตาราง
psql -U lpruser -h localhost -d lprserver_v3 -c "\dt"
```

### 🔧 **การแก้ไขปัญหา (Troubleshooting)**

#### **1. Peer Authentication Failed**
```bash
# ปัญหา: psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL: Peer authentication failed

# วิธีแก้ไข:
# 1. แก้ไขไฟล์ pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# 2. เปลี่ยนบรรทัดนี้:
# local   all             all                                     peer
# เป็น:
# local   all             all                                     md5

# 3. รีสตาร์ท PostgreSQL
sudo systemctl restart postgresql

# 4. ทดสอบการเชื่อมต่อ
psql -U lpruser -d lprserver_v3 -h localhost
```

#### **2. Permission Denied for Schema Public**
```bash
# ปัญหา: ERROR: permission denied for schema public

# วิธีแก้ไข:
sudo -u postgres psql -c "ALTER DATABASE lprserver_v3 OWNER TO lpruser;"
sudo -u postgres psql -c "GRANT CREATE ON SCHEMA public TO lpruser;"
sudo -u postgres psql -c "GRANT USAGE ON SCHEMA public TO lpruser;"
```

#### **3. Extension Creation Failed**
```bash
# ปัญหา: ERROR: permission denied to create extension "uuid-ossp"

# วิธีแก้ไข:
sudo -u postgres psql -d lprserver_v3 -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lprserver_v3 TO lpruser;"
```

#### **2. ตรวจสอบข้อมูล**
```sql
-- ตรวจสอบจำนวน records
SELECT 'checkpoints' as table_name, COUNT(*) as count FROM checkpoints
UNION ALL
SELECT 'cameras', COUNT(*) FROM cameras
UNION ALL
SELECT 'detections', COUNT(*) FROM detections
UNION ALL
SELECT 'plates', COUNT(*) FROM plates;
```

### 🎯 **ประโยชน์ที่ได้รับ**

#### **1. การจัดเก็บข้อมูล**
- จัดเก็บข้อมูลการตรวจจับแบบ real-time
- รองรับข้อมูลภาพและ metadata
- จัดเก็บประวัติการทำงานของระบบ

#### **2. การวิเคราะห์**
- สถิติรายวัน/รายเดือน
- การวิเคราะห์ patterns
- การติดตาม performance

#### **3. การบริหารจัดการ**
- จัดการ blacklist
- ตรวจสอบสุขภาพกล้อง
- บันทึกการทำงานของระบบ

#### **4. การแสดงผล**
- Dashboard แบบ real-time
- รายงานสถิติ
- การแจ้งเตือน

---

**สรุป:** ฐานข้อมูล PostgreSQL ถูกออกแบบมาเพื่อรองรับการทำงานของ LPR Server v3 อย่างครบถ้วน พร้อม performance optimization และ security features ที่เหมาะสม


