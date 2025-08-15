# WebSocket Sender Communication Specification

## 📡 WebSocket Sender Communication Requirements

### 🔧 **1. Socket.IO Events ที่ต้องการ**

#### **Connection Events:**
```javascript
// Client -> Server
'camera_register' - สำหรับ camera ลงทะเบียน
{
  "camera_id": "1",
  "checkpoint_id": "1", 
  "timestamp": "2024-12-19T10:00:00Z"
}

// Server -> Client  
'connect' - เมื่อ client เชื่อมต่อสำเร็จ
'disconnect' - เมื่อ client ตัดการเชื่อมต่อ
'error' - เมื่อเกิดข้อผิดพลาด
```

#### **Data Transmission Events:**
```javascript
// Client -> Server
'lpr_data' - สำหรับส่งข้อมูล LPR detection
{
  "type": "detection_result",
  "camera_id": "1",
  "checkpoint_id": "1",
  "timestamp": "2024-12-19T10:00:00Z",
  "vehicles_count": 1,
  "plates_count": 1,
  "ocr_results": ["ABC1234"],
  "vehicle_detections": [...],
  "plate_detections": [...],
  "processing_time_ms": 150,
  "annotated_image": "base64_encoded_image_data",
  "cropped_plates": ["base64_plate1", "base64_plate2"]
}

'health_status' - สำหรับส่งข้อมูล health check
{
  "type": "health_check",
  "camera_id": "1", 
  "checkpoint_id": "1",
  "timestamp": "2024-12-19T10:00:00Z",
  "component": "camera",
  "status": "healthy",
  "message": "Camera working normally",
  "details": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  }
}

'ping' - สำหรับทดสอบการเชื่อมต่อ
{
  "type": "test",
  "message": "Hello from AI Camera",
  "timestamp": "2024-12-19T10:00:00Z"
}
```

#### **Server Response Events:**
```javascript
// Server -> Client
'pong' - response สำหรับ ping
'lpr_response' - response สำหรับ lpr_data
'health_response' - response สำหรับ health_status
```

---

### 🌐 **2. REST API Endpoints ที่ต้องการ**

#### **Base URL:** `http://100.95.46.128:8765`

#### **Endpoints:**

**1. Camera Registration:**
```
POST /api/cameras/register
Content-Type: application/json

{
  "camera_id": "1",
  "checkpoint_id": "1",
  "timestamp": "2024-12-19T10:00:00Z"
}

Response: 200 OK
{
  "success": true,
  "message": "Camera registered successfully",
  "camera_id": "1"
}
```

**2. LPR Detection Data:**
```
POST /api/detection
Content-Type: application/json

{
  "type": "detection_result",
  "camera_id": "1",
  "checkpoint_id": "1", 
  "timestamp": "2024-12-19T10:00:00Z",
  "vehicles_count": 1,
  "plates_count": 1,
  "ocr_results": ["ABC1234"],
  "vehicle_detections": [...],
  "plate_detections": [...],
  "processing_time_ms": 150,
  "annotated_image": "base64_encoded_image_data",
  "cropped_plates": ["base64_plate1", "base64_plate2"]
}

Response: 200 OK
{
  "success": true,
  "message": "Detection data received",
  "detection_id": "uuid_here"
}
```

**3. Health Check Data:**
```
POST /api/health
Content-Type: application/json

{
  "type": "health_check",
  "camera_id": "1",
  "checkpoint_id": "1",
  "timestamp": "2024-12-19T10:00:00Z", 
  "component": "camera",
  "status": "healthy",
  "message": "Camera working normally",
  "details": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  }
}

Response: 200 OK
{
  "success": true,
  "message": "Health data received",
  "health_id": "uuid_here"
}
```

**4. Test Connection:**
```
GET /api/test
Response: 200 OK
{
  "success": true,
  "message": "Server is running",
  "timestamp": "2024-12-19T10:00:00Z"
}
```

**5. Statistics (existing):**
```
GET /api/statistics
Response: 200 OK
{
  "success": true,
  "data": {
    "total_detections": 1234,
    "total_cameras": 5,
    "last_update": "2024-12-19T10:00:00Z"
  }
}
```

---

### 🔄 **3. Fallback Strategy**

**Priority Order:**
1. **Socket.IO** (Primary) - Real-time communication
2. **REST API** (Fallback) - When Socket.IO unavailable

**Detection Logic:**
- Try Socket.IO connection first
- If Socket.IO fails, fallback to REST API
- If both fail, retry after delay

---

### 📋 **4. Data Format Standards**

#### **Common Fields (ทุก request):**
```json
{
  "camera_id": "1",           // AI Camera ID
  "checkpoint_id": "1",       // Checkpoint ID  
  "timestamp": "ISO8601",     // UTC timestamp
  "type": "detection_result"  // Data type
}
```

#### **Detection Result Fields:**
```json
{
  "vehicles_count": 1,        // จำนวนรถที่ตรวจพบ
  "plates_count": 1,          // จำนวนป้ายทะเบียนที่ตรวจพบ
  "ocr_results": ["ABC1234"], // ผลการอ่านป้ายทะเบียน
  "vehicle_detections": [...], // รายละเอียดการตรวจจับรถ
  "plate_detections": [...],   // รายละเอียดการตรวจจับป้าย
  "processing_time_ms": 150,   // เวลาประมวลผล (ms)
  "annotated_image": "base64", // ภาพที่ annotate แล้ว
  "cropped_plates": ["base64"] // ภาพป้ายทะเบียนที่ crop
}
```

#### **Health Check Fields:**
```json
{
  "component": "camera",      // Component name
  "status": "healthy",        // Status: healthy/warning/error
  "message": "Description",   // Status description
  "details": {                // Detailed metrics
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  }
}
```

---

### 🚀 **5. Implementation Steps สำหรับ Server**

1. **เพิ่ม Socket.IO endpoints:**
   - `camera_register`
   - `lpr_data` 
   - `health_status`
   - `ping`/`pong`

2. **เพิ่ม REST API endpoints:**
   - `POST /api/cameras/register`
   - `POST /api/detection`
   - `POST /api/health`
   - `GET /api/test`

3. **รองรับ Data Format:**
   - JSON format ที่กำหนด
   - Base64 encoding สำหรับ images
   - ISO8601 timestamp

4. **Error Handling:**
   - Return appropriate HTTP status codes
   - JSON error responses
   - Logging สำหรับ debugging

---

### 📝 **6. Testing Commands**

**Test Socket.IO:**
```bash
# Test connection
curl -X GET http://100.95.46.128:8765/api/test

# Test statistics
curl -X GET http://100.95.46.128:8765/api/statistics
```

**Test REST API:**
```bash
# Test detection data
curl -X POST http://100.95.46.128:8765/api/detection \
  -H "Content-Type: application/json" \
  -d '{"type":"detection_result","camera_id":"1","checkpoint_id":"1","timestamp":"2024-12-19T10:00:00Z","vehicles_count":1,"plates_count":1}'

# Test health data  
curl -X POST http://100.95.46.128:8765/api/health \
  -H "Content-Type: application/json" \
  -d '{"type":"health_check","camera_id":"1","checkpoint_id":"1","timestamp":"2024-12-19T10:00:00Z","component":"camera","status":"healthy","message":"Test"}'
```

---

### 🔧 **7. WebSocket Sender Configuration**

**Current Configuration:**
- **Server URL:** `http://100.95.46.128:8765`
- **Auto-start:** Enabled
- **Connection Timeout:** 30 seconds
- **Retry Interval:** 60 seconds
- **Max Retries:** 5

**Fallback Behavior:**
- Tries Socket.IO first (converts HTTP to WebSocket URL)
- Falls back to REST API if Socket.IO fails
- Logs all connection attempts and failures

---

### 📊 **8. Expected Data Flow**

1. **Camera Registration:**
   ```
   AI Camera → Server: camera_register event
   Server → AI Camera: connect confirmation
   ```

2. **Detection Data:**
   ```
   AI Camera → Server: lpr_data event (Socket.IO) or POST /api/detection (REST)
   Server → AI Camera: lpr_response or HTTP 200 OK
   ```

3. **Health Monitoring:**
   ```
   AI Camera → Server: health_status event (Socket.IO) or POST /api/health (REST)
   Server → AI Camera: health_response or HTTP 200 OK
   ```

4. **Connection Testing:**
   ```
   AI Camera → Server: ping event (Socket.IO) or GET /api/test (REST)
   Server → AI Camera: pong or HTTP 200 OK
   ```

---

**สรุป:** ต้องการให้ server รองรับทั้ง Socket.IO events และ REST API endpoints ตามที่กำหนดข้างต้น เพื่อให้ websocket_sender สามารถส่งข้อมูลได้ทั้งสองวิธีและมี fallback mechanism ที่ทำงานได้อย่างมีประสิทธิภาพครับ
