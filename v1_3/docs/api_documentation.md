# AI Camera v1.3 - API Documentation

## Overview

เอกสาร API สำหรับ AI Camera v1.3 ระบบการจัดการกล้องอัจฉริยะด้วย Hailo AI Accelerator

**Last Updated:** August 9, 2025  
**Version:** 1.3  
**Architecture:** Flask + Gunicorn + Nginx + WebSocket

## Base URL

```
Production: http://localhost (via Nginx reverse proxy)
Development: http://localhost:5000 (direct Gunicorn)
```

## Authentication

ปัจจุบันระบบไม่ต้องการ authentication (Internal network only)

## Standard Response Format

ทุก API response จะใช้ format มาตรฐานตาม `variable_management.md`:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully", 
    "data": {
        // Response data here
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

### Error Response  
```json
{
    "success": false,
    "error": "Error description",
    "error_code": "ERROR_CODE",
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

### Status Response
```json
{
    "success": true,
    "status": {
        "initialized": true,
        "streaming": true,
        "frame_count": 1234,
        "average_fps": 29.5,
        "uptime": 3600.5
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

## Variable Naming Conventions

| Layer | Convention | Example |
|-------|------------|---------|
| **Backend (Python)** | `snake_case` | `camera_status`, `frame_count`, `average_fps` |
| **Frontend (JavaScript)** | `camelCase` | `cameraStatus`, `frameCount`, `averageFps` |
| **API Endpoints** | `snake_case` | `/camera/status`, `/detection/start` |
| **HTML Element IDs** | `kebab-case` | `main-camera-status`, `feature-camera-model` |

## API Endpoints

### 🏠 Main Dashboard

#### GET `/`
หน้า dashboard หลัก

**Response:** HTML Template
```html
<!DOCTYPE html>
<html>
    <head><title>AI Camera v1.3</title></head>
    <body><!-- Dashboard content --></body>
</html>
```

#### GET `/health`
ตรวจสอบสถานะระบบ

**Response:**
```json
{
    "success": true,
    "status": "healthy",
    "service": "aicamera_v1.3",
    "version": "1.3",
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

---

### 📷 Camera Management

#### GET `/camera/status`
รับสถานะกล้องปัจจุบัน

**Response:**
```json
{
    "success": true,
    "status": {
        "initialized": true,
        "streaming": true,
        "frame_count": 1234,
        "average_fps": 29.5,
        "uptime": 3600.5,
        "auto_start_enabled": true,
        "config": {
            "buffer_count": 4,
            "colour_space": "RGB888",
            "controls": {
                "FrameDurationLimits": [33333, 33333],
                "NoiseReductionMode": "Fast"
            },
            "main": {
                "format": "RGB888",
                "framesize": 2764800,
                "preserve_ar": true,
                "size": [1280, 720],
                "stride": 3840
            }
        },
        "camera_handler": {
            "initialized": true,
            "streaming": true,
            "frame_count": 1234,
            "average_fps": 29.5,
            "recording": false,
            "sensor_modes_count": 4,
            "current_config": {
                "main": {
                    "size": [1280, 720],
                    "format": "RGB888"
                },
                "controls": {
                    "FrameDurationLimits": [33333, 33333]
                }
            },
            "camera_properties": {
                "Model": "imx708",
                "Location": 2,
                "ColorFilterArrangement": 0,
                "PixelArraySize": [4608, 2592]
            }
        }
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/camera/start`
เริ่มต้นกล้อง

**Response:**
```json
{
    "success": true,
    "message": "Camera started successfully",
    "status": {
        "initialized": true,
        "streaming": true
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/camera/stop`
หยุดกล้อง

**Response:**
```json
{
    "success": true,
    "message": "Camera stopped successfully", 
    "status": {
        "initialized": true,
        "streaming": false
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/camera/restart`
รีสตาร์ทกล้อง

**Response:**
```json
{
    "success": true,
    "message": "Camera restarted successfully",
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### GET `/camera/config`
รับการตั้งค่ากล้องปัจจุบัน

**Response:**
```json
{
    "success": true,
    "config": {
        "resolution": [1280, 720],
        "framerate": 30,
        "brightness": 0.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "awb_mode": "auto"
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/camera/config`
อัปเดตการตั้งค่ากล้อง

**Request Body:**
```json
{
    "resolution": [1920, 1080],
    "framerate": 30,
    "brightness": 0.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "awb_mode": "auto"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Camera configuration updated successfully",
    "config": {
        "resolution": [1920, 1080],
        "framerate": 30,
        "brightness": 0.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "awb_mode": "auto"
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/camera/capture`
ถ่ายภาพ

**Response:**
```json
{
    "success": true,
    "message": "Image captured successfully",
    "data": {
        "filename": "capture_20250809_183657.jpg",
        "filepath": "/home/camuser/aicamera/v1_3/src/captured_images/capture_20250809_183657.jpg",
        "timestamp": "2025-08-09T18:36:57.390144",
        "size": [1280, 720]
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### GET `/camera/video_feed`
สตรีมวิดีโอ (MJPEG)

**Response:** `multipart/x-mixed-replace` stream
```
Content-Type: multipart/x-mixed-replace; boundary=frame

--frame
Content-Type: image/jpeg

[JPEG image data]
--frame
Content-Type: image/jpeg

[JPEG image data]
--frame
...
```

---

### 🤖 AI Detection Management

#### GET `/detection/status`
รับสถานะการตรวจจับ

**Response:**
```json
{
    "success": true,
    "status": {
        "service_running": true,
        "detection_active": false,
        "detection_processor_status": {
            "models_loaded": true,
            "vehicle_model_available": true,
            "lp_detection_model_available": true,
            "lp_ocr_model_available": true,
            "easyocr_available": true
        },
        "detection_interval": 0.1,
        "confidence_threshold": 0.5,
        "plate_confidence_threshold": 0.7,
        "total_detections": 156,
        "last_detection_time": "2025-08-09T18:30:45.123456"
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/detection/start`
เริ่มการตรวจจับ

**Response:**
```json
{
    "success": true,
    "message": "Detection started successfully",
    "status": {
        "service_running": true,
        "detection_active": true
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/detection/stop`
หยุดการตรวจจับ

**Response:**
```json
{
    "success": true,
    "message": "Detection stopped successfully",
    "status": {
        "service_running": true,
        "detection_active": false
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### GET `/detection/results`
รับผลการตรวจจับ

**Query Parameters:**
- `limit` (optional): จำนวนผลลัพธ์ (default: 50, max: 100)
- `offset` (optional): เริ่มจากตำแหน่ง (default: 0)

**Response:**
```json
{
    "success": true,
    "data": {
        "results": [
            {
                "id": 1,
                "timestamp": "2025-08-09T18:30:45.123456",
                "detections": [
                    {
                        "type": "vehicle",
                        "confidence": 0.95,
                        "bbox": [100, 150, 300, 250],
                        "license_plate": {
                            "text": "ABC-1234",
                            "confidence": 0.87,
                            "bbox": [150, 200, 250, 230]
                        }
                    }
                ],
                "image_path": "/path/to/detection_image.jpg"
            }
        ],
        "total_count": 156,
        "limit": 50,
        "offset": 0
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

#### POST `/detection/configure`
ตั้งค่าการตรวจจับ

**Request Body:**
```json
{
    "detection_interval": 0.1,
    "confidence_threshold": 0.5,
    "plate_confidence_threshold": 0.7,
    "save_images": true,
    "save_to_database": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Detection configuration updated successfully",
    "config": {
        "detection_interval": 0.1,
        "confidence_threshold": 0.5,
        "plate_confidence_threshold": 0.7,
        "save_images": true,
        "save_to_database": true
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

---

### 🏥 System Health

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

---

### 📡 Video Streaming

#### GET `/streaming/video_feed`
รับ video stream (MJPEG)

**Response:** `multipart/x-mixed-replace` stream

#### GET `/streaming/status`
รับสถานะ streaming

**Response:**
```json
{
    "success": true,
    "status": {
        "streaming_active": true,
        "connected_clients": 2,
        "stream_quality": "medium",
        "fps": 30,
        "resolution": [1280, 720]
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

---

## WebSocket Events

### Connection
```javascript
// Connect to WebSocket
const socket = io();

// Connection events
socket.on('connect', function() {
    console.log('Connected to WebSocket server');
});

socket.on('disconnect', function() {
    console.log('Disconnected from WebSocket server');
});
```

### Camera Events

#### Client to Server
```javascript
// Request camera status
socket.emit('camera_status_request', {});

// Camera control
socket.emit('camera_control', {
    command: 'start' // 'start', 'stop', 'restart', 'capture'
});

// Configuration update
socket.emit('camera_config_update', {
    config: {
        resolution: [1920, 1080],
        framerate: 30,
        brightness: 0.0
    }
});
```

#### Server to Client
```javascript
// Camera status updates
socket.on('camera_status_update', function(status) {
    // status object structure same as GET /camera/status
    console.log('Camera status:', status);
});

// Camera control response
socket.on('camera_control_response', function(response) {
    // response: { command: 'start', success: true, message: '...', error: null }
    console.log('Camera control result:', response);
});

// Configuration response
socket.on('camera_config_response', function(response) {
    // response: { success: true, message: '...', config: {...}, error: null }
    console.log('Configuration update result:', response);
});
```

### Detection Events

#### Client to Server
```javascript
// Detection control
socket.emit('detection_control', {
    command: 'start' // 'start', 'stop'
});

// Request detection status
socket.emit('detection_status_request', {});
```

#### Server to Client
```javascript
// Detection status updates
socket.on('detection_status_update', function(status) {
    // status object structure same as GET /detection/status
    console.log('Detection status:', status);
});

// Detection results (real-time)
socket.on('detection_result', function(result) {
    // result: { timestamp: '...', detections: [...], image_path: '...' }
    console.log('New detection result:', result);
});
```

### System Events

#### Server to Client
```javascript
// System health updates
socket.on('system_health_update', function(health) {
    // health object structure same as GET /health/system
    console.log('System health:', health);
});

// System notifications
socket.on('system_notification', function(notification) {
    // notification: { type: 'info'|'warning'|'error', message: '...', timestamp: '...' }
    console.log('System notification:', notification);
});
```

---

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `CAMERA_NOT_INITIALIZED` | Camera not initialized | 500 |
| `CAMERA_NOT_STREAMING` | Camera not streaming | 500 |
| `CAMERA_BUSY` | Camera is busy with another operation | 409 |
| `CONFIGURATION_FAILED` | Configuration update failed | 400 |
| `DETECTION_NOT_AVAILABLE` | AI detection service not available | 503 |
| `MODEL_NOT_LOADED` | AI models not loaded | 503 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `INVALID_PARAMETER` | Invalid parameter provided | 400 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |
| `OPERATION_FAILED` | Generic operation failure | 500 |

---

## Rate Limiting

| Endpoint Category | Limit | Window |
|-------------------|-------|---------|
| Camera Control | 10 requests | 1 minute |
| Status Requests | 60 requests | 1 minute |
| Configuration Updates | 5 requests | 1 minute |
| Detection Control | 10 requests | 1 minute |

---

## Data Types & Validation

### Camera Configuration
```typescript
interface CameraConfig {
    resolution: [number, number];     // [width, height], valid: [640,480] to [1920,1080]
    framerate: number;               // 1-60 FPS
    brightness: number;              // -1.0 to 1.0
    contrast: number;                // 0.0 to 2.0
    saturation: number;              // 0.0 to 2.0
    awb_mode: string;                // 'auto', 'fluorescent', 'incandescent', etc.
}
```

### Detection Configuration
```typescript
interface DetectionConfig {
    detection_interval: number;      // 0.01 to 5.0 seconds
    confidence_threshold: number;    // 0.0 to 1.0
    plate_confidence_threshold: number; // 0.0 to 1.0
    save_images: boolean;
    save_to_database: boolean;
}
```

### Detection Result
```typescript
interface DetectionResult {
    id: number;
    timestamp: string;               // ISO 8601 format
    detections: Detection[];
    image_path: string;
}

interface Detection {
    type: 'vehicle' | 'license_plate';
    confidence: number;              // 0.0 to 1.0
    bbox: [number, number, number, number]; // [x1, y1, x2, y2]
    license_plate?: {
        text: string;
        confidence: number;
        bbox: [number, number, number, number];
    };
}
```

---

## Testing & Development

### API Testing with curl

```bash
# Health check
curl -X GET http://localhost/health

# Camera status
curl -X GET http://localhost/camera/status

# Start camera
curl -X POST http://localhost/camera/start

# Update camera config
curl -X POST http://localhost/camera/config \
  -H "Content-Type: application/json" \
  -d '{"resolution": [1920, 1080], "framerate": 30}'

# Detection status
curl -X GET http://localhost/detection/status

# Get detection results
curl -X GET "http://localhost/detection/results?limit=10&offset=0"
```

### WebSocket Testing with JavaScript

```javascript
// Test WebSocket connection
const socket = io('http://localhost');

socket.on('connect', () => {
    console.log('Connected');
    
    // Test camera status request
    socket.emit('camera_status_request', {});
    
    // Test camera control
    socket.emit('camera_control', { command: 'start' });
});

socket.on('camera_status_update', (status) => {
    console.log('Camera status:', status);
});
```

---

## Changelog

### Version 1.3 (August 2025)
- ✅ Added comprehensive variable naming conventions
- ✅ Updated WebSocket event documentation
- ✅ Added detailed response schemas
- ✅ Improved error handling documentation
- ✅ Added rate limiting information
- ✅ Enhanced detection API endpoints
- ✅ Added system health monitoring APIs
- ✅ Improved camera configuration validation

### Version 1.2
- Basic camera and detection APIs
- WebSocket support
- Health monitoring

### Version 1.1
- Initial API implementation
- Camera control endpoints

---

**Note:** This documentation reflects the current implementation as of August 2025. For the most up-to-date information, refer to the source code in `/v1_3/src/web/blueprints/` and `variable_management.md`.