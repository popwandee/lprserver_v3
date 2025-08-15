# Edge Communication Guide

## 📡 การสื่อสารระหว่าง Edge AI Camera และ LPR Server

### 🔧 **การตั้งค่า Server**

#### **1. เริ่มต้น WebSocket Server**
```bash
# เริ่มต้น server ที่ port 8765
python websocket_server.py
```

#### **2. ตรวจสอบ Server Status**
```bash
# ตรวจสอบการทำงานของ server
curl http://localhost:8765/api/test
```

### 🌐 **SocketIO Communication (Primary)**

#### **การเชื่อมต่อ SocketIO**
```javascript
// ใช้ Socket.IO client
const socket = io('http://localhost:8765');

socket.on('connect', () => {
    console.log('Connected to LPR Server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from LPR Server');
});
```

#### **1. Camera Registration**
```javascript
// ลงทะเบียน camera
socket.emit('camera_register', {
    camera_id: "camera_001",
    checkpoint_id: "checkpoint_001",
    timestamp: "2024-12-19T10:00:00Z"
});

// รับ response
socket.on('camera_register', (data) => {
    console.log('Camera registered:', data);
    // Response: { success: true, message: "Camera registered successfully", ... }
});
```

#### **2. ส่งข้อมูล LPR Detection**
```javascript
// ส่งข้อมูลการตรวจจับ
socket.emit('lpr_data', {
    type: "detection_result",
    camera_id: "camera_001",
    checkpoint_id: "checkpoint_001",
    timestamp: "2024-12-19T10:00:00Z",
    vehicles_count: 1,
    plates_count: 1,
    ocr_results: ["ABC1234"],
    vehicle_detections: [
        {
            bbox: [100, 100, 200, 200],
            confidence: 0.95,
            class: "car"
        }
    ],
    plate_detections: [
        {
            bbox: [150, 150, 180, 170],
            confidence: 0.92,
            text: "ABC1234"
        }
    ],
    processing_time_ms: 150,
    annotated_image: "base64_encoded_image_data",
    cropped_plates: ["base64_plate1", "base64_plate2"]
});

// รับ response
socket.on('lpr_response', (data) => {
    console.log('LPR data received:', data);
    // Response: { success: true, detection_id: "uuid", ... }
});
```

#### **3. ส่งข้อมูล Health Status**
```javascript
// ส่งข้อมูล health check
socket.emit('health_status', {
    type: "health_check",
    camera_id: "camera_001",
    checkpoint_id: "checkpoint_001",
    timestamp: "2024-12-19T10:00:00Z",
    component: "camera",
    status: "healthy",
    message: "Camera working normally",
    details: {
        cpu_usage: 45.2,
        memory_usage: 67.8,
        disk_usage: 23.1
    }
});

// รับ response
socket.on('health_response', (data) => {
    console.log('Health status received:', data);
    // Response: { success: true, health_id: "uuid", ... }
});
```

#### **4. ทดสอบการเชื่อมต่อ (Ping/Pong)**
```javascript
// ส่ง ping
socket.emit('ping', {
    type: "test",
    message: "Hello from AI Camera",
    timestamp: "2024-12-19T10:00:00Z"
});

// รับ pong
socket.on('pong', (data) => {
    console.log('Pong received:', data);
    // Response: { success: true, message: "pong", ... }
});
```

#### **5. เข้าร่วม Dashboard และ Health Monitoring**
```javascript
// เข้าร่วม dashboard room
socket.emit('join_dashboard');

// เข้าร่วม health monitoring room
socket.emit('join_health_room');

// รับ real-time updates
socket.on('new_detection', (data) => {
    console.log('New detection:', data);
});

socket.on('health_update', (data) => {
    console.log('Health update:', data);
});
```

### 🔄 **REST API Communication (Fallback)**

#### **Base URL:** `http://localhost:8765`

#### **1. ทดสอบการเชื่อมต่อ**
```bash
curl -X GET http://localhost:8765/api/test
```

#### **2. ลงทะเบียน Camera**
```bash
curl -X POST http://localhost:8765/api/cameras/register \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "camera_001",
    "checkpoint_id": "checkpoint_001",
    "timestamp": "2024-12-19T10:00:00Z"
  }'
```

#### **3. ส่งข้อมูล LPR Detection**
```bash
curl -X POST http://localhost:8765/api/detection \
  -H "Content-Type: application/json" \
  -d '{
    "type": "detection_result",
    "camera_id": "camera_001",
    "checkpoint_id": "checkpoint_001",
    "timestamp": "2024-12-19T10:00:00Z",
    "vehicles_count": 1,
    "plates_count": 1,
    "ocr_results": ["ABC1234"],
    "vehicle_detections": [
      {
        "bbox": [100, 100, 200, 200],
        "confidence": 0.95,
        "class": "car"
      }
    ],
    "plate_detections": [
      {
        "bbox": [150, 150, 180, 170],
        "confidence": 0.92,
        "text": "ABC1234"
      }
    ],
    "processing_time_ms": 150,
    "annotated_image": "base64_encoded_image_data",
    "cropped_plates": ["base64_plate1", "base64_plate2"]
  }'
```

#### **4. ส่งข้อมูล Health Status**
```bash
curl -X POST http://localhost:8765/api/health \
  -H "Content-Type: application/json" \
  -d '{
    "type": "health_check",
    "camera_id": "camera_001",
    "checkpoint_id": "checkpoint_001",
    "timestamp": "2024-12-19T10:00:00Z",
    "component": "camera",
    "status": "healthy",
    "message": "Camera working normally",
    "details": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 23.1
    }
  }'
```

#### **5. ดูข้อมูล Statistics**
```bash
curl -X GET http://localhost:8765/api/statistics
```

#### **6. ดูข้อมูล Cameras**
```bash
curl -X GET http://localhost:8765/api/cameras
```

#### **7. ดูข้อมูล Records**
```bash
curl -X GET http://localhost:8765/api/records?limit=10
```

### 🚀 **Fallback Strategy Implementation**

#### **Python Example (Edge Device)**
```python
import socketio
import requests
import time
from datetime import datetime

class EdgeCommunicator:
    def __init__(self, server_url="http://localhost:8765"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.camera_id = "camera_001"
        self.checkpoint_id = "checkpoint_001"
        self.socketio_connected = False
        
        # Setup SocketIO handlers
        self.setup_socketio()
    
    def setup_socketio(self):
        @self.sio.event
        def connect():
            print("SocketIO connected")
            self.socketio_connected = True
        
        @self.sio.event
        def disconnect():
            print("SocketIO disconnected")
            self.socketio_connected = False
    
    def connect_socketio(self):
        """Try to connect via SocketIO"""
        try:
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"SocketIO connection failed: {e}")
            return False
    
    def send_detection_data(self, detection_data):
        """Send detection data with fallback"""
        if self.socketio_connected:
            # Try SocketIO first
            try:
                self.sio.emit('lpr_data', detection_data)
                return True
            except Exception as e:
                print(f"SocketIO send failed: {e}")
                self.socketio_connected = False
        
        # Fallback to REST API
        try:
            response = requests.post(
                f"{self.server_url}/api/detection",
                json=detection_data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"REST API send failed: {e}")
            return False
    
    def send_health_data(self, health_data):
        """Send health data with fallback"""
        if self.socketio_connected:
            try:
                self.sio.emit('health_status', health_data)
                return True
            except Exception as e:
                print(f"SocketIO health send failed: {e}")
                self.socketio_connected = False
        
        try:
            response = requests.post(
                f"{self.server_url}/api/health",
                json=health_data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"REST API health send failed: {e}")
            return False

# Usage example
communicator = EdgeCommunicator()

# Try SocketIO connection
if communicator.connect_socketio():
    print("Using SocketIO for communication")
else:
    print("Using REST API for communication")

# Send detection data
detection_data = {
    "type": "detection_result",
    "camera_id": "camera_001",
    "checkpoint_id": "checkpoint_001",
    "timestamp": datetime.now().isoformat(),
    "vehicles_count": 1,
    "plates_count": 1,
    "ocr_results": ["ABC1234"]
}

success = communicator.send_detection_data(detection_data)
print(f"Detection data sent: {success}")
```

### 📊 **Data Format Standards**

#### **Common Fields (ทุก request)**
```json
{
  "camera_id": "string",      // AI Camera ID
  "checkpoint_id": "string",  // Checkpoint ID
  "timestamp": "ISO8601",     // UTC timestamp
  "type": "string"           // Data type
}
```

#### **Detection Result Fields**
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

#### **Health Check Fields**
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

### 🧪 **Testing**

#### **Run Test Client**
```bash
# ทดสอบ endpoint ทั้งหมด
python test_edge_communication.py
```

#### **Manual Testing**
```bash
# ทดสอบ REST API
curl http://localhost:8765/api/test

# ทดสอบ SocketIO (ใช้ browser console)
# เปิด http://localhost:8765 และใช้ browser console
```

### 📝 **Error Handling**

#### **SocketIO Errors**
```javascript
socket.on('error', (data) => {
    console.error('SocketIO error:', data);
    // Fallback to REST API
});
```

#### **REST API Errors**
```javascript
// HTTP status codes
// 200: Success
// 400: Bad Request (missing fields)
// 500: Server Error
```

### 🔧 **Configuration**

#### **Server Configuration**
```python
# config.py
WEBSOCKET_PORT = 8765
SOCKETIO_ASYNC_MODE = 'eventlet'
```

#### **Client Configuration**
```python
# Edge device configuration
SERVER_URL = "http://100.95.46.128:8765"  # Production server
SOCKETIO_TIMEOUT = 30  # seconds
REST_API_TIMEOUT = 10  # seconds
RETRY_INTERVAL = 60    # seconds
MAX_RETRIES = 5
```

### 📋 **Monitoring และ Debugging**

#### **Server Logs**
```bash
# ดู server logs
tail -f logs/lprserver.log
```

#### **Real-time Monitoring**
```javascript
// เข้าร่วม monitoring rooms
socket.emit('join_dashboard');
socket.emit('join_health_room');

// รับ real-time updates
socket.on('new_detection', console.log);
socket.on('health_update', console.log);
socket.on('camera_status', console.log);
```

### 🎯 **Best Practices**

1. **Always implement fallback mechanism**
2. **Use proper error handling**
3. **Implement retry logic with exponential backoff**
4. **Monitor connection status**
5. **Log all communication attempts**
6. **Validate data before sending**
7. **Use proper timestamps (ISO8601)**
8. **Implement health monitoring**
9. **Test both SocketIO and REST API**
10. **Monitor server performance**

---

**สรุป:** ระบบรองรับการสื่อสารทั้ง SocketIO (primary) และ REST API (fallback) ตามข้อกำหนดที่กำหนดไว้ โดย edge device จะพยายามเชื่อมต่อ SocketIO ก่อน และหากไม่สำเร็จจะใช้ REST API เป็น fallback mechanism
