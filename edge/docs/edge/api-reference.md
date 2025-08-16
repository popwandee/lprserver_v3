# AI Camera Edge System - API Reference

**Version:** 1.0.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Category:** API Documentation  
**Status:** Active

## Overview

API Reference สำหรับ AI Camera Edge System ครอบคลุม REST API endpoints และ WebSocket interfaces

## Base URL

- **Development:** `http://localhost:5000`
- **Production:** `http://aicamera1:5000` (via Tailscale)

## Authentication

API ใช้ Tailscale authentication โดยอัตโนมัติ

## REST API Endpoints

### Health Check

#### GET /health
ตรวจสอบสถานะของระบบ

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-16T10:30:00Z",
  "version": "1.3.0",
  "services": {
    "camera": "running",
    "ai_processor": "running",
    "network": "connected"
  }
}
```

### Camera Control

#### GET /api/camera/status
ตรวจสอบสถานะกล้อง

**Response:**
```json
{
  "status": "active",
  "resolution": "1920x1080",
  "fps": 30,
  "device": "/dev/video0"
}
```

#### POST /api/camera/start
เริ่มการทำงานกล้อง

**Response:**
```json
{
  "success": true,
  "message": "Camera started successfully"
}
```

#### POST /api/camera/stop
หยุดการทำงานกล้อง

**Response:**
```json
{
  "success": true,
  "message": "Camera stopped successfully"
}
```

### AI Processing

#### POST /api/ai/process
ประมวลผลภาพด้วย AI

**Request:**
```json
{
  "image_data": "base64_encoded_image",
  "confidence_threshold": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "detections": [
    {
      "bbox": [100, 100, 200, 200],
      "confidence": 0.95,
      "class": "person"
    }
  ],
  "processing_time": 0.045
}
```

#### GET /api/ai/status
ตรวจสอบสถานะ AI processor

**Response:**
```json
{
  "status": "ready",
  "model_loaded": true,
  "device": "hailo-8",
  "inference_count": 1234
}
```

### System Information

#### GET /api/system/info
ข้อมูลระบบ

**Response:**
```json
{
  "hostname": "aicamera1",
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "temperature": 52.3,
  "uptime": "2 days, 3 hours"
}
```

#### GET /api/system/logs
ดู logs ระบบ

**Query Parameters:**
- `lines` (optional): จำนวนบรรทัด (default: 100)
- `level` (optional): log level (debug, info, warning, error)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-08-16T10:30:00Z",
      "level": "INFO",
      "message": "Camera initialized successfully"
    }
  ]
}
```

## WebSocket API

### Connection

**URL:** `ws://aicamera1:8765`

### Events

#### camera_frame
ส่งข้อมูล frame จากกล้อง

**Data:**
```json
{
  "event": "camera_frame",
  "data": {
    "frame_id": 12345,
    "timestamp": "2024-08-16T10:30:00Z",
    "image_data": "base64_encoded_image",
    "detections": [
      {
        "bbox": [100, 100, 200, 200],
        "confidence": 0.95,
        "class": "person"
      }
    ]
  }
}
```

#### system_status
ส่งสถานะระบบ

**Data:**
```json
{
  "event": "system_status",
  "data": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "temperature": 52.3,
    "camera_status": "active",
    "ai_status": "ready"
  }
}
```

#### error
ส่งข้อผิดพลาด

**Data:**
```json
{
  "event": "error",
  "data": {
    "error_code": "CAMERA_ERROR",
    "message": "Camera device not found",
    "timestamp": "2024-08-16T10:30:00Z"
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `CAMERA_ERROR` | ข้อผิดพลาดเกี่ยวกับกล้อง |
| `AI_MODEL_ERROR` | ข้อผิดพลาดเกี่ยวกับ AI model |
| `NETWORK_ERROR` | ข้อผิดพลาดเกี่ยวกับเครือข่าย |
| `SYSTEM_ERROR` | ข้อผิดพลาดระบบ |
| `VALIDATION_ERROR` | ข้อผิดพลาดการตรวจสอบข้อมูล |

## Rate Limiting

- **REST API:** 100 requests/minute
- **WebSocket:** ไม่จำกัด

## Examples

### Python Client Example

```python
import requests
import websocket
import json

# REST API Example
def get_system_status():
    response = requests.get('http://aicamera1:5000/api/system/info')
    return response.json()

def process_image(image_data):
    payload = {
        'image_data': image_data,
        'confidence_threshold': 0.5
    }
    response = requests.post('http://aicamera1:5000/api/ai/process', json=payload)
    return response.json()

# WebSocket Example
def on_message(ws, message):
    data = json.loads(message)
    if data['event'] == 'camera_frame':
        print(f"Received frame {data['data']['frame_id']}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

# Connect to WebSocket
ws = websocket.WebSocketApp(
    "ws://aicamera1:8765",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.run_forever()
```

### JavaScript Client Example

```javascript
// REST API Example
async function getSystemStatus() {
    const response = await fetch('http://aicamera1:5000/api/system/info');
    return await response.json();
}

async function processImage(imageData) {
    const payload = {
        image_data: imageData,
        confidence_threshold: 0.5
    };
    
    const response = await fetch('http://aicamera1:5000/api/ai/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// WebSocket Example
const ws = new WebSocket('ws://aicamera1:8765');

ws.onopen = function(event) {
    console.log('WebSocket connection opened');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.event === 'camera_frame') {
        console.log(`Received frame ${data.data.frame_id}`);
        // Process frame data
    } else if (data.event === 'system_status') {
        console.log('System status:', data.data);
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function(event) {
    console.log('WebSocket connection closed');
};
```

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [WebSocket Documentation](https://websockets.readthedocs.io/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Note:** เอกสารนี้จะได้รับการอัปเดตเมื่อมีการเปลี่ยนแปลงใน API specification
