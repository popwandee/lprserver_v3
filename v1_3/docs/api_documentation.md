# AI Camera v1.3 - API Documentation

## Overview

เอกสาร API สำหรับ AI Camera v1.3 ระบบการจัดการกล้องอัจฉริยะ

## Base URL

```
http://localhost:5000
```

## Authentication
ปัจจุบันระบบไม่ต้องการ authentication

## Response Format
ทุก API response จะมี format มาตรฐาน:

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {},
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

## Endpoints

### 1. Main Dashboard
**GET** `/`

**Description:** หน้า dashboard หลัก

**Response:**
```json
{
    "success": true,
    "title": "AI Camera v1.3 Dashboard"
}
```

### 2. Camera Status
**GET** `/camera/status`

**Description:** รับสถานะกล้องปัจจุบัน

**Response:**
```json
{
    "success": true,
    "status": {
        "initialized": true,
        "streaming": true,
        "frame_count": 1234,
        "average_fps": 29.5,
        "uptime": 3600,
        "auto_start_enabled": true,
        "config": {
            "resolution": [1920, 1080],
            "framerate": 30,
            "brightness": 0.0,
            "contrast": 1.0,
            "saturation": 1.0,
            "awb_mode": "auto"
        }
    },
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 3. Start Camera
**POST** `/camera/start`

**Description:** เริ่มการทำงานกล้อง

**Response:**
```json
{
    "success": true,
    "message": "Camera started successfully",
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 4. Stop Camera
**POST** `/camera/stop`

**Description:** หยุดการทำงานกล้อง

**Response:**
```json
{
    "success": true,
    "message": "Camera stopped successfully",
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 5. Restart Camera
**POST** `/camera/restart`

**Description:** รีสตาร์ทกล้อง

**Response:**
```json
{
    "success": true,
    "message": "Camera restarted successfully",
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 6. Camera Configuration
**GET** `/camera/config`

**Description:** รับการตั้งค่ากล้องปัจจุบัน

**Response:**
```json
{
    "success": true,
    "config": {
        "resolution": [1920, 1080],
        "framerate": 30,
        "brightness": 0.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "awb_mode": "auto"
    },
    "settings": {
        "available_resolutions": [[1920, 1080], [1280, 720], [640, 480]],
        "available_framerates": [15, 30, 60],
        "available_awb_modes": ["auto", "fluorescent", "incandescent"]
    },
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

**POST** `/camera/config`

**Description:** อัพเดตการตั้งค่ากล้อง

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
    "config": {
        "resolution": [1920, 1080],
        "framerate": 30,
        "brightness": 0.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "awb_mode": "auto"
    },
    "message": "Configuration updated successfully",
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 7. Capture Image
**POST** `/camera/capture`

**Description:** ถ่ายภาพ

**Response:**
```json
{
    "success": true,
    "message": "Image captured successfully",
    "image_path": "/path/to/image.jpg",
    "size": [1920, 1080],
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 8. Video Stream
**GET** `/camera/video_feed`

**Description:** สตรีมวิดีโอแบบ MJPEG

**Response:** Multipart MJPEG stream

### 9. Low Resolution Video Stream
**GET** `/camera/video_feed_lores`

**Description:** สตรีมวิดีโอความละเอียดต่ำ

**Response:** Multipart MJPEG stream

### 10. ML Frame
**GET** `/camera/ml_frame`

**Description:** รับเฟรมสำหรับ AI processing

**Response:**
```json
{
    "success": true,
    "frame": "base64_encoded_image",
    "metadata": {
        "timestamp": 1628434200.123,
        "format": "RGB888",
        "size": [1920, 1080]
    },
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 11. Camera Health
**GET** `/camera/health`

**Description:** ตรวจสอบสุขภาพกล้อง

**Response:**
```json
{
    "success": true,
    "health": {
        "status": "healthy",
        "camera_initialized": true,
        "streaming_active": true,
        "auto_start_enabled": true,
        "uptime": 3600,
        "frame_count": 1234,
        "average_fps": 29.5,
        "timestamp": "2025-08-08T15:30:00.000Z"
    },
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 12. Debug Information
**GET** `/camera/debug`

**Description:** ข้อมูล debug สำหรับการแก้ไขปัญหา

**Response:**
```json
{
    "success": true,
    "debug": {
        "camera_status": {
            "initialized": true,
            "streaming": true
        },
        "frame_capture_success": true,
        "frame_shape": [1080, 1920, 3],
        "frame_error": null,
        "camera_initialized": true,
        "camera_streaming": true,
        "timestamp": "2025-08-08T15:30:00.000Z"
    }
}
```

## WebSocket Events

### Connection
```javascript
const socket = io('/camera');
```

### Client to Server Events

#### Camera Status Request
```javascript
socket.emit('camera_status_request');
```

#### Camera Control
```javascript
socket.emit('camera_control', {
    command: 'start' | 'stop' | 'restart' | 'capture'
});
```

#### Configuration Update
```javascript
socket.emit('camera_config_update', {
    config: {
        resolution: [1920, 1080],
        framerate: 30,
        brightness: 0.0,
        contrast: 1.0,
        saturation: 1.0,
        awb_mode: "auto"
    }
});
```

### Server to Client Events

#### Camera Status Update
```javascript
socket.on('camera_status_update', function(status) {
    // status object
});
```

#### Camera Control Response
```javascript
socket.on('camera_control_response', function(response) {
    // response object
});
```

#### Configuration Response
```javascript
socket.on('camera_config_response', function(response) {
    // response object
});
```

## Error Codes

| Code | Description |
|------|-------------|
| CAMERA_NOT_INITIALIZED | กล้องยังไม่ได้เริ่มต้น |
| CAMERA_NOT_STREAMING | กล้องไม่ได้สตรีม |
| CONFIGURATION_FAILED | การตั้งค่าไม่สำเร็จ |
| SERVICE_UNAVAILABLE | บริการไม่พร้อมใช้งาน |
| INVALID_PARAMETER | พารามิเตอร์ไม่ถูกต้อง |
| OPERATION_FAILED | การดำเนินการไม่สำเร็จ |

## Rate Limiting

ปัจจุบันไม่มี rate limiting

## CORS

CORS เปิดใช้งานสำหรับ development

## Security Considerations

1. ระบบควรเพิ่ม authentication ในอนาคต
2. ควรจำกัดการเข้าถึง API จาก IP ที่อนุญาต
3. ควรเข้ารหัสข้อมูลที่สำคัญ

---

**Version:** 1.3  
**Last Updated:** 2025-08-08
```

## 5. แนวทางการบริหารจัดการตัวแปร

### 5.1 สร้าง Type Definitions (TypeScript-like)

```typescript:v1_3/docs/type_definitions.ts
// Type definitions for AI Camera v1.3
// This file serves as a reference for variable types

// Camera Configuration Types
interface CameraConfig {
    resolution: [number, number];
    framerate: number;
    brightness: number;
    contrast: number;
    saturation: number;
    awb_mode: string;
    exposure_mode?: string;
    iso?: number;
}

// Camera Status Types
interface CameraStatus {
    initialized: boolean;
    streaming: boolean;
    frame_count: number;
    average_fps: number;
    uptime: number;
    auto_start_enabled: boolean;
    config?: CameraConfig;
    camera_handler?: {
        camera_properties: {
            Model: string;
            Sensor: string;
        };
    };
}

// API Response Types
interface ApiResponse<T = any> {
    success: boolean;
    message?: string;
    error?: string;
    error_code?: string;
    data?: T;
    timestamp: string;
}

// WebSocket Event Types
interface WebSocketEvent {
    event: string;
    data: any;
    timestamp: string;
}

// Camera Control Commands
type CameraCommand = 'start' | 'stop' | 'restart' | 'capture';

// White Balance Modes
type AwbMode = 'auto' | 'fluorescent' | 'incandescent' | 'tungsten' | 'horizon' | 'daylight' | 'cloudy' | 'shade';

// Status Indicators
type StatusIndicator = 'online' | 'offline' | 'warning';
```

### 5.2 สร้าง Validation Schema

```python:v1_3/src/core/validation.py
#!/usr/bin/env python3
"""
Validation schemas for AI Camera v1.3

This module provides validation schemas for all data structures
used in the application to ensure consistency and reduce errors.
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CameraConfigSchema:
    """Schema for camera configuration validation."""
    
    @staticmethod
    def validate_resolution(resolution: List[int]) -> bool:
        """Validate resolution format."""
        if not isinstance(resolution, list) or len(resolution) != 2:
            return False
        width, height = resolution
        return (isinstance(width, int) and isinstance(height, int) and
                width > 0 and height > 0)
    
    @staticmethod
    def validate_framerate(framerate: int) -> bool:
        """Validate framerate range."""
        return isinstance(framerate, int) and 1 <= framerate <= 60
    
    @staticmethod
    def validate_brightness(brightness: float) -> bool:
        """Validate brightness range."""
        return isinstance(brightness, (int, float)) and -1.0 <= brightness <= 1.0
    
    @staticmethod
    def validate_contrast(contrast: float) -> bool:
        """Validate contrast range."""
        return isinstance(contrast, (int, float)) and 0.0 <= contrast <= 2.0
    
    @staticmethod
    def validate_saturation(saturation: float) -> bool:
        """Validate saturation range."""
        return isinstance(saturation, (int, float)) and 0.0 <= saturation <= 2.0
    
    @staticmethod
    def validate_awb_mode(awb_mode: str) -> bool:
        """Validate white balance mode."""
        valid_modes = ['auto', 'fluorescent', 'incandescent', 'tungsten', 
                      'horizon', 'daylight', 'cloudy', 'shade']
        return isinstance(awb_mode, str) and awb_mode in valid_modes
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete camera configuration."""
        errors = []
        
        if 'resolution' in config:
            if not cls.validate_resolution(config['resolution']):
                errors.append('Invalid resolution format')
        
        if 'framerate' in config:
            if not cls.validate_framerate(config['framerate']):
                errors.append('Framerate must be between 1 and 60')
        
        if 'brightness' in config:
            if not cls.validate_brightness(config['brightness']):
                errors.append('Brightness must be between -1.0 and 1.0')
        
        if 'contrast' in config:
            if not cls.validate_contrast(config['contrast']):
                errors.append('Contrast must be between 0.0 and 2.0')
        
        if 'saturation' in config:
            if not cls.validate_saturation(config['saturation']):
                errors.append('Saturation must be between 0.0 and 2.0')
        
        if 'awb_mode' in config:
            if not cls.validate_awb_mode(config['awb_mode']):
                errors.append('Invalid white balance mode')
        
        return len(errors) == 0, errors


@dataclass
class ApiResponseSchema:
    """Schema for API response validation."""
    
    @staticmethod
    def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Create standardized success response."""
        from datetime import datetime
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_error_response(error: str, error_code: str = None) -> Dict[str, Any]:
        """Create standardized error response."""
        from datetime import datetime
        response = {
            "success": False,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        if error_code:
            response["error_code"] = error_code
        return response
    
    @staticmethod
    def validate_response(response: Dict[str, Any]) -> bool:
        """Validate API response format."""
        required_fields = ['success', 'timestamp']
        return all(field in response for field in required_fields)


@dataclass
class WebSocketEventSchema:
    """Schema for WebSocket event validation."""
    
    @staticmethod
    def validate_camera_control(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate camera control event data."""
        errors = []
        
        if 'command' not in data:
            errors.append('Command is required')
        elif data['command'] not in ['start', 'stop', 'restart', 'capture']:
            errors.append('Invalid command')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_config_update(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration update event data."""
        errors = []
        
        if 'config' not in data:
            errors.append('Config is required')
        else:
            is_valid, config_errors = CameraConfigSchema.validate_config(data['config'])
            if not is_valid:
                errors.extend(config_errors)
        
        return len(errors) == 0, errors


# Global validation functions
def validate_camera_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Global function to validate camera configuration."""
    return CameraConfigSchema.validate_config(config)


def create_api_response(success: bool, data: Any = None, message: str = None, 
                       error: str = None, error_code: str = None) -> Dict[str, Any]:
    """Global function to create standardized API response."""
    if success:
        return ApiResponseSchema.create_success_response(data, message)
    else:
        return ApiResponseSchema.create_error_response(error, error_code)


def validate_websocket_event(event_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Global function to validate WebSocket events."""
    if event_type == 'camera_control':
        return WebSocketEventSchema.validate_camera_control(data)
    elif event_type == 'camera_config_update':
        return WebSocketEventSchema.validate_config_update(data)
    else:
        return False, [f'Unknown event type: {event_type}']
```

## สรุปแนวทางการบริหารจัดการตัวแปร

### 1. **มาตรฐานการตั้งชื่อ**
- Backend: snake_case (Python)
- Frontend: camelCase (JavaScript)
- Constants: UPPER_SNAKE_CASE

### 2. **Type Safety**
- ใช้ TypeScript definitions เป็น reference
- Validation schemas สำหรับทุก data structure
- Consistent data types ระหว่าง frontend/backend

### 3. **Documentation**
- UML diagrams สำหรับ architecture
- API documentation ที่ครบถ้วน
- Variable management standards

### 4. **Testing**
- Unit tests สำหรับ validation
- Integration tests สำหรับ API responses
- Frontend tests สำหรับ data handling

### 5. **Version Control**
- Semantic versioning
- Change logs สำหรับทุก breaking changes
- Backward compatibility เมื่อเป็นไปได้

การจัดการตัวแปรแบบนี้จะช่วยลดข้อผิดพลาดและเพิ่มความสม่ำเสมอในการพัฒนาร่วมกัน
