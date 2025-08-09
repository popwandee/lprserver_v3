# AI Camera v1.3 - Variable Management Standards

## Overview

เอกสารนี้กำหนดมาตรฐานการจัดการตัวแปรสำหรับการรับส่งข้อมูลระหว่าง Backend และ Frontend เพื่อลดข้อผิดพลาดและเพิ่มความสม่ำเสมอในการพัฒนา

## 1. Response Format Standards

### 1.1 Standard Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data here
    },
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 1.2 Standard Error Response
```json
{
    "success": false,
    "error": "Error description",
    "error_code": "ERROR_CODE",
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 1.3 Status Response
```json
{
    "success": true,
    "status": {
        "initialized": true,
        "streaming": true,
        "frame_count": 1234,
        "average_fps": 29.5,
        "uptime": 3600,
        "auto_start_enabled": true
    },
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

## 2. Camera Configuration Variables

### 2.1 Configuration Object Structure
```json
{
    "resolution": [1920, 1080],
    "framerate": 30,
    "brightness": 0.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "awb_mode": "auto",
    "exposure_mode": "auto",
    "iso": 100
}
```

### 2.2 Frontend Form Variables
```javascript
// Camera Configuration Form
const configForm = {
    resolution: "(1920, 1080)",  // String format for select
    framerate: 30,               // Number
    brightness: 0.0,             // Number (-1.0 to 1.0)
    contrast: 1.0,               // Number (0.0 to 2.0)
    saturation: 1.0,             // Number (0.0 to 2.0)
    awb_mode: "auto"             // String
};

// Status Display Variables
const statusDisplay = {
    cameraStatus: "online",      // "online", "offline", "warning"
    cameraStatusText: "Online",  // Display text
    frameCount: 1234,            // Number
    averageFps: 29.5,            // Number
    uptime: 3600                 // Number (seconds)
};
```

## 3. WebSocket Event Variables

### 3.1 Client to Server Events
```javascript
// Camera Control
socket.emit('camera_control', {
    command: 'start' | 'stop' | 'restart' | 'capture'
});

// Configuration Update
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

// Status Request
socket.emit('camera_status_request', {});
```

### 3.2 Server to Client Events
```javascript
// Camera Status Update
socket.on('camera_status_update', function(status) {
    // status object structure
    const status = {
        initialized: true,
        streaming: true,
        frame_count: 1234,
        average_fps: 29.5,
        uptime: 3600,
        auto_start_enabled: true,
        config: {
            resolution: [1920, 1080],
            framerate: 30,
            brightness: 0.0,
            contrast: 1.0,
            saturation: 1.0,
            awb_mode: "auto"
        }
    };
});

// Camera Control Response
socket.on('camera_control_response', function(response) {
    // response object structure
    const response = {
        command: 'start' | 'stop' | 'restart' | 'capture',
        success: true,
        message: 'Camera started successfully',
        error: null
    };
});

// Configuration Response
socket.on('camera_config_response', function(response) {
    // response object structure
    const response = {
        success: true,
        message: 'Configuration updated successfully',
        config: {
            // Updated configuration object
        },
        error: null
    };
});
```

## 4. HTTP API Variables

### 4.1 Camera Status Endpoint
```http
GET /camera/status
```

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
        "camera_handler": {
            "camera_properties": {
                "Model": "Camera Model",
                "Sensor": "Sensor Type"
            }
        }
    },
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

### 4.2 Camera Configuration Endpoint
```http
GET /camera/config
POST /camera/config
```

**POST Request Body:**
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

## 5. Variable Naming Conventions

### 5.1 Backend Variables (Python)
```python
# Camera status variables
camera_status = {
    'initialized': True,
    'streaming': True,
    'frame_count': 1234,
    'average_fps': 29.5,
    'uptime': 3600,
    'auto_start_enabled': True
}

# Configuration variables
camera_config = {
    'resolution': [1920, 1080],
    'framerate': 30,
    'brightness': 0.0,
    'contrast': 1.0,
    'saturation': 1.0,
    'awb_mode': 'auto'
}

# Response variables
response_data = {
    'success': True,
    'message': 'Operation completed',
    'data': {},
    'timestamp': datetime.now().isoformat()
}
```

### 5.2 Frontend Variables (JavaScript)
```javascript
// Status variables
const cameraStatus = {
    initialized: true,
    streaming: true,
    frameCount: 1234,
    averageFps: 29.5,
    uptime: 3600,
    autoStartEnabled: true
};

// Configuration variables
const cameraConfig = {
    resolution: [1920, 1080],
    framerate: 30,
    brightness: 0.0,
    contrast: 1.0,
    saturation: 1.0,
    awbMode: 'auto'
};

// UI state variables
const uiState = {
    cameraStatusText: 'Online',
    cameraStatusClass: 'status-online',
    isStreaming: true,
    isConfiguring: false
};
```

## 6. Data Type Standards

### 6.1 Camera Configuration Types
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| resolution | Array[Number] | [width, height] | Camera resolution |
| framerate | Number | 1-60 | Frames per second |
| brightness | Number | -1.0 to 1.0 | Brightness adjustment |
| contrast | Number | 0.0 to 2.0 | Contrast adjustment |
| saturation | Number | 0.0 to 2.0 | Saturation adjustment |
| awb_mode | String | "auto", "fluorescent", etc. | White balance mode |

### 6.2 Status Types
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| initialized | Boolean | true/false | Camera initialization status |
| streaming | Boolean | true/false | Camera streaming status |
| frame_count | Number | 0+ | Total frames captured |
| average_fps | Number | 0+ | Average frames per second |
| uptime | Number | 0+ | System uptime in seconds |
| auto_start_enabled | Boolean | true/false | Auto-start feature status |

## 7. Error Handling Standards

### 7.1 Error Codes
```python
ERROR_CODES = {
    'CAMERA_NOT_INITIALIZED': 'Camera not initialized',
    'CAMERA_NOT_STREAMING': 'Camera not streaming',
    'CONFIGURATION_FAILED': 'Configuration update failed',
    'SERVICE_UNAVAILABLE': 'Service not available',
    'INVALID_PARAMETER': 'Invalid parameter provided',
    'OPERATION_FAILED': 'Operation failed'
}
```

### 7.2 Error Response Format
```json
{
    "success": false,
    "error": "Camera not initialized",
    "error_code": "CAMERA_NOT_INITIALIZED",
    "timestamp": "2025-08-08T15:30:00.000Z"
}
```

## 8. Validation Rules

### 8.1 Frontend Validation
```javascript
// Configuration validation
function validateConfig(config) {
    const errors = [];
    
    if (config.framerate < 1 || config.framerate > 60) {
        errors.push('Framerate must be between 1 and 60');
    }
    
    if (config.brightness < -1.0 || config.brightness > 1.0) {
        errors.push('Brightness must be between -1.0 and 1.0');
    }
    
    if (config.contrast < 0.0 || config.contrast > 2.0) {
        errors.push('Contrast must be between 0.0 and 2.0');
    }
    
    return errors;
}
```

### 8.2 Backend Validation
```python
def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate camera configuration parameters."""
    errors = []
    
    if 'framerate' in config:
        if not (1 <= config['framerate'] <= 60):
            errors.append('Framerate must be between 1 and 60')
    
    if 'brightness' in config:
        if not (-1.0 <= config['brightness'] <= 1.0):
            errors.append('Brightness must be between -1.0 and 1.0')
    
    if 'contrast' in config:
        if not (0.0 <= config['contrast'] <= 2.0):
            errors.append('Contrast must be between 0.0 and 2.0')
    
    return errors
```

## 9. Testing Standards

### 9.1 Variable Testing
```python
def test_camera_config_variables():
    """Test camera configuration variable formats."""
    test_config = {
        'resolution': [1920, 1080],
        'framerate': 30,
        'brightness': 0.0,
        'contrast': 1.0,
        'saturation': 1.0,
        'awb_mode': 'auto'
    }
    
    # Test data types
    assert isinstance(test_config['resolution'], list)
    assert isinstance(test_config['framerate'], int)
    assert isinstance(test_config['brightness'], float)
    
    # Test value ranges
    assert 1 <= test_config['framerate'] <= 60
    assert -1.0 <= test_config['brightness'] <= 1.0
    assert 0.0 <= test_config['contrast'] <= 2.0
```

## 10. Documentation Maintenance

### 10.1 Change Log
- 2025-08-08: Initial variable management standards
- 2025-08-08: Added WebSocket event variables
- 2025-08-08: Added validation rules

### 10.2 Review Process
1. All variable changes must be documented
2. Frontend and backend teams must review changes
3. Update UML diagrams when architecture changes
4. Test all variable interactions before deployment

---

**Note:** เอกสารนี้ควรได้รับการอัพเดตเมื่อมีการเปลี่ยนแปลงโครงสร้างหรือตัวแปรใหม่ เพื่อรักษามาตรฐานการพัฒนาร่วมกัน
