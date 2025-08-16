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

### 1.4 Health Monitor Response
```json
{
    "success": true,
    "data": {
        "overall_status": "healthy",
        "components": {
            "camera": {
                "status": "healthy",
                "initialized": true,
                "streaming": true,
                "auto_start_enabled": true,
                "last_check": "2025-08-10T11:30:00.000Z"
            },
            "detection": {
                "status": "healthy",
                "models_loaded": true,
                "easyocr_available": true,
                "auto_start": true,
                "last_check": "2025-08-10T11:30:00.000Z"
            },
            "database": {
                "status": "healthy",
                "connected": true,
                "last_check": "2025-08-10T11:30:00.000Z"
            },
            "system": {
                "status": "healthy",
                "cpu_usage": 25.5,
                "memory_usage": {
                    "used": 6.2,
                    "total": 15.84,
                    "percentage": 39.1
                },
                "disk_usage": {
                    "used": 20.64,
                    "total": 57.44,
                    "percentage": 35.9
                },
                "uptime": 86400,
                "last_check": "2025-08-10T11:30:00.000Z"
            }
        },
        "system": {
            "cpu_count": 4,
            "cpu_usage": 25.5,
            "memory_usage": {
                "used": 6.2,
                "total": 15.84,
                "percentage": 39.1
            },
            "disk_usage": {
                "used": 20.64,
                "total": 57.44,
                "percentage": 35.9
            },
            "uptime": 86400
        },
        "last_check": "2025-08-10T11:30:00.000Z"
    },
    "timestamp": "2025-08-10T11:30:00.000Z"
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

// Health Monitor Status Variables
const healthStatus = {
    overallStatus: "healthy",    // "healthy", "unhealthy", "critical", "unknown"
    componentStatus: {
        camera: "healthy",       // "healthy", "unhealthy", "critical", "unknown"
        detection: "healthy",    // "healthy", "unhealthy", "critical", "unknown"
        database: "healthy",     // "healthy", "unhealthy", "critical", "unknown"
        system: "healthy"        // "healthy", "unhealthy", "critical", "unknown"
    },
    systemResources: {
        cpuUsage: 25.5,          // Number (percentage)
        memoryUsage: 45.2,       // Number (percentage)
        diskUsage: 35.8,         // Number (percentage)
        uptime: 86400            // Number (seconds)
    }
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

### 6.3 Health Monitor Status Types
| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| overall_status | String | "healthy", "unhealthy", "critical", "unknown" | Overall system health status |
| component_status | Object | Component-specific status | Individual component health status |
| camera.status | String | "healthy", "unhealthy", "critical", "unknown" | Camera component status |
| detection.status | String | "healthy", "unhealthy", "critical", "unknown" | Detection component status |
| database.status | String | "healthy", "unhealthy", "critical", "unknown" | Database component status |
| system.status | String | "healthy", "unhealthy", "critical", "unknown" | System component status |
| cpu_usage | Number | 0-100 | CPU usage percentage |
| memory_usage | Object | Usage statistics | Memory usage information |
| disk_usage | Object | Usage statistics | Disk usage information |

## 7. Error Handling Standards

### 7.1 Error Codes
```python
ERROR_CODES = {
    'CAMERA_NOT_INITIALIZED': 'Camera not initialized',
    'CAMERA_NOT_STREAMING': 'Camera not streaming',
    'CONFIGURATION_FAILED': 'Configuration update failed',
    'SERVICE_UNAVAILABLE': 'Service not available',
    'INVALID_PARAMETER': 'Invalid parameter provided',
    'OPERATION_FAILED': 'Operation failed',
    'HEALTH_CHECK_FAILED': 'Health check failed',
    'COMPONENT_UNHEALTHY': 'Component is unhealthy',
    'SYSTEM_CRITICAL': 'System is in critical state',
    'FRAME_VALIDATION_ERROR': 'Frame validation failed'
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

## 10. Frame Data Variables

### 10.1 Frame Data Structure (Camera Handler Output)
```json
{
    "frame": "numpy.ndarray",
    "metadata": {
        "width": 1920,
        "height": 1080,
        "channels": 3,
        "format": "BGR",
        "timestamp": 1691234567.123
    },
    "capture_info": {
        "exposure_time": 33333,
        "analog_gain": 1.0,
        "digital_gain": 1.0
    }
}
```

### 10.2 Frame Processing Variables (Detection Pipeline)
```python
# Backend frame processing variables
frame_validation = {
    'is_valid': True,
    'frame_type': 'numpy.ndarray',
    'frame_shape': [1080, 1920, 3],
    'frame_size': 6220800,
    'validation_errors': []
}

# Detection processing variables
detection_input = {
    'original_frame': 'numpy.ndarray',
    'enhanced_frame': 'numpy.ndarray', 
    'preprocessing_applied': ['resize', 'normalize'],
    'model_input_shape': [640, 640, 3]
}
```

### 10.3 Auto-Startup Configuration Variables
```python
# Backend configuration variables
auto_startup_config = {
    'auto_start_camera': True,
    'auto_start_streaming': True,
    'auto_start_detection': True,
    'startup_delay': 5.0,
    'startup_sequence': ['camera', 'streaming', 'detection']
}

# Service status variables
service_status = {
    'camera_manager': {
        'initialized': True,
        'auto_start_enabled': True,
        'auto_streaming_enabled': True
    },
    'detection_manager': {
        'initialized': True,
        'auto_start_enabled': True,
        'active': False
    }
}
```

### 10.4 Frontend Auto-Startup Variables
```javascript
// Auto-startup status display
const autoStartupStatus = {
    cameraAutoStart: true,
    streamingAutoStart: true,
    detectionAutoStart: true,
    startupDelay: 5.0,
    currentPhase: 'camera_starting'  // 'camera_starting', 'streaming_starting', 'detection_starting', 'completed'
};

// Service initialization tracking
const serviceInitialization = {
    cameraManager: {
        initialized: false,
        autoStartEnabled: true,
        status: 'initializing'  // 'initializing', 'ready', 'error'
    },
    detectionManager: {
        initialized: false,
        autoStartEnabled: true,
        status: 'waiting'  // 'waiting', 'initializing', 'ready', 'error'
    }
};
```

## 11. Error Prevention Variables

### 11.1 Attribute Safety Variables
```python
# Backend safe attribute access
safe_attributes = {
    'camera_manager': {
        'required': ['initialized', 'streaming'],
        'optional': ['auto_start_enabled', 'auto_streaming_enabled']
    },
    'detection_manager': {
        'required': ['active', 'initialized'],
        'optional': ['auto_start_enabled', 'detection_count']
    }
}

# Error tracking variables
attribute_errors = {
    'missing_attributes': [],
    'type_errors': [],
    'access_errors': []
}
```

### 11.2 Frame Validation Error Variables
```python
# Frame validation error tracking
frame_errors = {
    'invalid_type': 'Expected numpy.ndarray, got dict',
    'empty_frame': 'Frame size is 0',
    'missing_frame_key': 'Dict missing frame key',
    'validation_failed': 'Frame validation failed'
}

# Error response format
frame_error_response = {
    'success': False,
    'error': 'Frame validation failed',
    'error_type': 'FRAME_VALIDATION_ERROR',
    'details': {
        'expected_type': 'numpy.ndarray',
        'received_type': 'dict',
        'frame_size': 0
    },
    'timestamp': '2025-08-09T22:00:00.000Z'
}
```

### 11.3 Frontend Error Display Variables
```javascript
// Error state management
const errorStates = {
    frameValidation: {
        hasError: false,
        errorType: null,  // 'invalid_type', 'empty_frame', 'missing_key'
        errorMessage: '',
        lastOccurred: null
    },
    attributeAccess: {
        hasError: false,
        missingAttribute: '',
        serviceName: '',
        errorMessage: ''
    },
    autoStartup: {
        hasError: false,
        failedPhase: '',  // 'camera', 'streaming', 'detection'
        errorMessage: '',
        retryAttempts: 0
    }
};
```

## 12. Detection Pipeline Variables

### 12.1 Detection Results Variables
```python
# Backend detection results
detection_results = {
    'vehicle_detections': [
        {
            'bbox': [x1, y1, x2, y2],
            'confidence': 0.95,
            'class_id': 2,
            'class_name': 'car'
        }
    ],
    'license_plate_detections': [
        {
            'bbox': [x1, y1, x2, y2],
            'confidence': 0.87,
            'plate_text': 'ABC-123',
            'ocr_confidence': 0.92
        }
    ],
    'processing_time': 0.045,
    'frame_timestamp': '2025-08-09T22:00:00.123Z',
    'model_versions': {
        'vehicle_model': 'yolov5s_vehicle_v1',
        'plate_model': 'yolov5s_plate_v1',
        'ocr_model': 'easyocr_v1'
    }
}
```

### 12.2 Frontend Detection Display Variables
```javascript
// Detection visualization variables
const detectionDisplay = {
    vehicleDetections: [
        {
            bbox: [100, 150, 300, 400],
            confidence: 95,
            className: 'car',
            displayColor: '#00ff00'
        }
    ],
    licensePlateDetections: [
        {
            bbox: [120, 180, 200, 220],
            confidence: 87,
            plateText: 'ABC-123',
            ocrConfidence: 92,
            displayColor: '#ff0000'
        }
    ],
    processingStats: {
        processingTime: 45,  // milliseconds
        averageFps: 22.1,
        totalDetections: 156,
        lastUpdate: '2025-08-09T22:00:00.123Z'
    }
};
```

## 13. Documentation Maintenance

### 13.1 Change Log
- 2025-08-08: Initial variable management standards
- 2025-08-08: Added WebSocket event variables
- 2025-08-08: Added validation rules
- 2025-08-09: Added frame data structure variables
- 2025-08-09: Added auto-startup configuration variables
- 2025-08-09: Added error prevention variables
- 2025-08-09: Added detection pipeline variables
- 2025-08-10: Added health monitor status variables and error codes
- 2025-08-10: Updated dashboard layout to 2-row structure with improved variable organization

### 13.2 Review Process
1. All variable changes must be documented
2. Frontend and backend teams must review changes
3. Update UML diagrams when architecture changes
4. Test all variable interactions before deployment
5. Validate frame data structures after camera changes
6. Test auto-startup sequence after service modifications
7. Validate health monitor status values and error codes
8. Test health check response formats and data structures

### 13.3 Frame Data Testing Requirements
```python
# Required frame data tests
frame_tests = [
    'test_camera_handler_returns_dict',
    'test_camera_manager_extracts_numpy_array',
    'test_detection_processor_validates_frame_type',
    'test_frame_validation_handles_dict_input',
    'test_frame_validation_rejects_invalid_types'
]

# Required health monitor tests
health_tests = [
    'test_health_status_values',
    'test_component_status_structure',
    'test_system_resource_format',
    'test_error_code_consistency',
    'test_response_format_compliance'
]
```

## 14. Updated Dashboard Layout Variables

### 14.1 New Layout Structure Variables

**Row 1: Centered System Information**
```html
<!-- System Information Section (Centered) -->
<div class="row justify-content-center mb-4">
    <div class="col-md-8">
        <h6 class="text-center">System Information</h6>
        <ul class="list-unstyled text-start">
            <li><strong>CPU Architecture:</strong> <span id="system-info-cpu">Loading...</span></li>
            <li><strong>AI Accelerator:</strong> <span id="system-info-ai-accelerator">Loading...</span></li>
            <li><strong>OS & Kernel:</strong> <span id="system-info-os">Loading...</span></li>
        </ul>
    </div>
</div>
```

**Row 2: Three-Column Layout**
```html
<!-- Hardware Information (Column 1) -->
<div class="col-md-4">
    <h6>Hardware Information</h6>
    <ul class="list-unstyled">
        <li><strong>Main Board:</strong> Raspberry Pi 5</li>
        <li><strong>RAM:</strong> <span id="system-info-ram">Loading...</span></li>
        <li><strong>Disk:</strong> <span id="system-info-disk">Loading...</span></li>
        <li><strong>Camera Model:</strong> <span id="feature-camera-model">Loading...</span></li>
        <li><strong>Resolution:</strong> <span id="feature-camera-resolution">Loading...</span></li>
        <li><strong>Frame Rate:</strong> <span id="feature-camera-fps">Loading...</span></li>
        <li><strong>Status:</strong> <span id="feature-camera-status">Loading...</span></li>
    </ul>
</div>

<!-- Development Information (Column 2) -->
<div class="col-md-4">
    <h6>Development Information</h6>
    <ul class="list-unstyled">
        <li><strong>Application:</strong> AI Camera v1.3</li>
        <li><strong>Framework:</strong> Flask + Blueprints</li>
        <li><strong>Architecture:</strong> Dependency Injection + Services</li>
        <li><strong>Camera:</strong> Picamera2 + Hailo AI</li>
        <li><strong>Database:</strong> SQLite + SQLAlchemy</li>
        <li><strong>Communication:</strong> WebSocket + REST API</li>
        <li><strong>Deployment:</strong> Gunicorn + Nginx</li>
        <li><strong>Version Control:</strong> Git</li>
    </ul>
</div>

<!-- Component and Services (Column 3) -->
<div class="col-md-4">
    <h6>Component and Services</h6>
    <ul class="list-unstyled">
        <li><strong>Flask Streaming</strong></li>
        <li><strong>Camera Component</strong></li>
        <li><strong>Detection Component</strong></li>
        <li><strong>Health Monitor</strong></li>
        <li><strong>WebSocket Sender</strong></li>
        <li><strong>Database Manager</strong></li>
    </ul>
</div>
```

### 14.2 Updated Element ID Variables

**New System Information Elements:**
```javascript
// System Information Elements (Row 1)
const systemInfoElements = {
    cpu: document.getElementById('system-info-cpu'),
    aiAccelerator: document.getElementById('system-info-ai-accelerator'),
    os: document.getElementById('system-info-os')
};

// Hardware Information Elements (Row 2, Column 1)
const hardwareElements = {
    ram: document.getElementById('system-info-ram'),
    disk: document.getElementById('system-info-disk'),
    cameraModel: document.getElementById('feature-camera-model'),
    cameraResolution: document.getElementById('feature-camera-resolution'),
    cameraFps: document.getElementById('feature-camera-fps'),
    cameraStatus: document.getElementById('feature-camera-status')
};
```

**Removed Elements (No longer used):**
```javascript
// Removed Element IDs
const removedElements = [
    'main-camera-model',
    'main-camera-resolution', 
    'main-camera-fps',
    'main-camera-detail-status',
    'main-database-detail-status',
    'main-system-uptime',
    'main-camera-status',
    'main-detection-status',
    'main-database-status',
    'main-system-status'
];
```

### 14.3 JavaScript Update Functions

**Updated System Information Update Function:**
```javascript
function updateSystemInfo(healthData) {
    // Update CPU Architecture
    if (healthData.system && healthData.system.cpu_info) {
        const cpuElement = document.getElementById('system-info-cpu');
        if (cpuElement) {
            const cpuInfo = healthData.system.cpu_info;
            cpuElement.textContent = `${cpuInfo.model} ${cpuInfo.architecture}`;
        }
    }
    
    // Update AI Accelerator
    if (healthData.system && healthData.system.ai_accelerator_info) {
        const aiElement = document.getElementById('system-info-ai-accelerator');
        if (aiElement) {
            const aiInfo = healthData.system.ai_accelerator_info;
            aiElement.textContent = `Device Architecture: ${aiInfo.device_architecture}, Firmware: ${aiInfo.firmware_version}`;
        }
    }
    
    // Update OS Information
    if (healthData.system && healthData.system.os_info) {
        const osElement = document.getElementById('system-info-os');
        if (osElement) {
            const osInfo = healthData.system.os_info;
            osElement.textContent = `${osInfo.distribution} ${osInfo.distribution_version} (Kernel ${osInfo.kernel_version})`;
        }
    }
    
    // Update RAM and Disk
    if (healthData.system) {
        const ramElement = document.getElementById('system-info-ram');
        const diskElement = document.getElementById('system-info-disk');
        
        if (ramElement && healthData.system.memory_usage) {
            ramElement.textContent = `${healthData.system.memory_usage.total.toFixed(2)} GB`;
        }
        
        if (diskElement && healthData.system.disk_usage) {
            diskElement.textContent = `${healthData.system.disk_usage.total.toFixed(2)} GB`;
        }
    }
}
```

### 14.4 Layout Responsiveness Variables

**Bootstrap Grid Classes:**
```css
/* Row 1: Centered layout */
.row-1-classes = {
    container: 'row justify-content-center mb-4',
    content: 'col-md-8',
    title: 'text-center',
    content: 'text-start'
};

/* Row 2: Three-column layout */
.row-2-classes = {
    container: 'row',
    column1: 'col-md-4',  // Hardware Information
    column2: 'col-md-4',  // Development Information  
    column3: 'col-md-4'   // Component and Services
};

/* Responsive breakpoints */
.responsive-breakpoints = {
    mobile: 'col-12',     // Stack vertically on mobile
    tablet: 'col-md-6',   // Two columns on tablet
    desktop: 'col-md-4'   // Three columns on desktop
};
```

### 14.5 Layout Benefits and Improvements

**Visual Hierarchy Improvements:**
- **Row 1**: Core system information prominently displayed and centered
- **Row 2**: Detailed information organized in logical categories
- **Clear Separation**: Dynamic vs static content clearly separated
- **Better UX**: Improved readability and information organization

**Code Organization Benefits:**
- **Reduced Redundancy**: Eliminated duplicate status indicators
- **Cleaner JavaScript**: Removed unused variable declarations
- **Better Maintainability**: Clearer element ID naming convention
- **Improved Responsiveness**: Better mobile and tablet experience

## 15. WebSocket Sender Offline Mode Variables

### 15.1 Offline Mode Status Variables

**Backend Status Variables (snake_case):**
```python
# WebSocket Sender Status with Offline Mode
websocket_sender_status = {
    'enabled': True,
    'running': True,
    'connected': False,  # False in offline mode
    'server_url': None,  # None indicates offline mode
    'offline_mode': True,  # New field for offline mode
    'aicamera_id': '1',
    'checkpoint_id': '1',
    'retry_count': 0,
    'total_detections_sent': 0,
    'total_health_sent': 0,
    'last_detection_check': '2025-08-10T11:30:00.000Z',
    'last_health_check': '2025-08-10T11:30:00.000Z',
    'detection_thread_alive': True,
    'health_thread_alive': True
}
```

**Frontend Status Variables (camelCase):**
```javascript
// WebSocket Sender Status with Offline Mode
const websocketSenderStatus = {
    enabled: true,
    running: true,
    connected: false,  // False in offline mode
    serverUrl: null,   // null indicates offline mode
    offlineMode: true, // New field for offline mode
    aicameraId: '1',
    checkpointId: '1',
    retryCount: 0,
    totalDetectionsSent: 0,
    totalHealthSent: 0,
    lastDetectionCheck: '2025-08-10T11:30:00.000Z',
    lastHealthCheck: '2025-08-10T11:30:00.000Z',
    detectionThreadAlive: true,
    healthThreadAlive: true
};
```

### 15.2 Offline Mode Log Variables

**Backend Log Variables (snake_case):**
```python
# Offline Mode Log Entry
offline_log_entry = {
    'timestamp': '2025-08-10T11:30:00.000Z',
    'action': 'send_detection',
    'status': 'offline',  # New status for offline mode
    'message': 'Processing 5 detection records locally (offline mode)',
    'data_type': 'detection_results',
    'record_count': 5,
    'aicamera_id': '1',
    'checkpoint_id': '1'
}

# Connection Log Entry
connection_log_entry = {
    'timestamp': '2025-08-10T11:30:00.000Z',
    'action': 'connect',
    'status': 'success',  # or 'failed'
    'message': 'Connected to ws://100.95.46.128:8765',
    'aicamera_id': '1',
    'checkpoint_id': '1'
}
```

**Frontend Log Display Variables (camelCase):**
```javascript
// Offline Mode Log Display
const offlineLogDisplay = {
    timestamp: '2025-08-10T11:30:00.000Z',
    action: 'send_detection',
    status: 'offline',  // New status for offline mode
    message: 'Processing 5 detection records locally (offline mode)',
    dataType: 'detection_results',
    recordCount: 5,
    aicameraId: '1',
    checkpointId: '1'
};

// Connection Log Display
const connectionLogDisplay = {
    timestamp: '2025-08-10T11:30:00.000Z',
    action: 'connect',
    status: 'success',  // or 'failed'
    message: 'Connected to ws://100.95.46.128:8765',
    aicameraId: '1',
    checkpointId: '1'
};
```

### 15.3 Dashboard Status Display Variables

**Offline Mode Status Display:**
```javascript
// Offline Mode Status Display Variables
const offlineStatusDisplay = {
    // Server Connection Status
    serverConnection: {
        connected: false,
        connectionText: 'Offline Mode',
        statusClass: 'status-offline'
    },
    
    // Data Sending Status
    dataSending: {
        active: true,  // true if threads are alive
        dataText: 'Active (Local)',
        statusClass: 'status-active'
    },
    
    // Last Sync Time
    lastSync: {
        time: '2025-08-10T11:30:00.000Z',
        displayText: '2025-08-10 11:30:00'
    }
};
```

## 16. WebSocket Communication Variables

### 16.1 WebSocket Event Variables

**Socket.IO Event Names:**
```javascript
// Client -> Server Events
const SOCKETIO_CLIENT_EVENTS = {
    CAMERA_REGISTER: 'camera_register',
    LPR_DATA: 'lpr_data',
    HEALTH_STATUS: 'health_status',
    PING: 'ping'
};

// Server -> Client Events
const SOCKETIO_SERVER_EVENTS = {
    CONNECT: 'connect',
    DISCONNECT: 'disconnect',
    ERROR: 'error',
    PONG: 'pong',
    LPR_RESPONSE: 'lpr_response',
    HEALTH_RESPONSE: 'health_response'
};
```

**REST API Endpoints:**
```javascript
const REST_API_ENDPOINTS = {
    CAMERA_REGISTER: '/api/cameras/register',
    DETECTION: '/api/detection',
    HEALTH: '/api/health',
    TEST: '/api/test',
    STATISTICS: '/api/statistics'
};
```

### 16.2 WebSocket Data Format Variables

**Camera Registration Data:**
```javascript
const cameraRegistrationData = {
    camera_id: '1',
    checkpoint_id: '1',
    timestamp: '2024-12-19T10:00:00Z'
};
```

**LPR Detection Data:**
```javascript
const lprDetectionData = {
    type: 'detection_result',
    camera_id: '1',
    checkpoint_id: '1',
    timestamp: '2024-12-19T10:00:00Z',
    vehicles_count: 1,
    plates_count: 1,
    ocr_results: ['ABC1234'],
    vehicle_detections: [...],
    plate_detections: [...],
    processing_time_ms: 150,
    annotated_image: 'base64_encoded_image_data',
    cropped_plates: ['base64_plate1', 'base64_plate2']
};
```

**Health Status Data:**
```javascript
const healthStatusData = {
    type: 'health_check',
    camera_id: '1',
    checkpoint_id: '1',
    timestamp: '2024-12-19T10:00:00Z',
    component: 'camera',
    status: 'healthy',
    message: 'Camera working normally',
    details: {
        cpu_usage: 45.2,
        memory_usage: 67.8,
        disk_usage: 23.1
    }
};
```

### 16.3 WebSocket Status Variables

**Connection Status:**
```javascript
const websocketStatus = {
    connected: true,
    server_type: 'socketio',  // 'socketio' or 'rest'
    server_url: 'ws://100.95.46.128:8765',
    retry_count: 0,
    last_connection: '2024-12-19T10:00:00Z',
    fallback_mode: false
};
```

**Data Transmission Status:**
```javascript
const dataTransmissionStatus = {
    total_detections_sent: 1234,
    total_health_sent: 567,
    last_detection_sent: '2024-12-19T10:00:00Z',
    last_health_sent: '2024-12-19T10:00:00Z',
    detection_thread_alive: true,
    health_thread_alive: true
};
```

## 17. Storage Management Variables

### 17.1 Storage Status Variables

**Disk Usage Variables:**
```javascript
const diskUsageVariables = {
    total_space_gb: 57.44,
    used_space_gb: 20.64,
    free_space_gb: 36.80,
    usage_percentage: 35.9,
    status: 'healthy'  // 'healthy', 'warning', 'critical'
};
```

**Folder Statistics Variables:**
```javascript
const folderStatisticsVariables = {
    total_files: 1234,
    total_size_gb: 15.6,
    sent_files: 890,
    unsent_files: 344,
    oldest_file: '2024-12-12T10:00:00Z',
    newest_file: '2024-12-19T10:00:00Z'
};
```

### 17.2 Storage Configuration Variables

**Storage Settings:**
```javascript
const storageConfigurationVariables = {
    min_free_space_gb: 10.0,
    retention_days: 7,
    batch_size: 100,
    monitor_interval: 300,  // seconds
    folder_path: '/home/camuser/aicamera/captured_images',
    auto_cleanup_enabled: true
};
```

**Cleanup Settings:**
```javascript
const cleanupSettingsVariables = {
    priority_sent: true,  // Delete sent files first
    batch_processing: true,
    dry_run: false,
    max_files_per_batch: 100
};
```

### 17.3 Storage Action Variables

**Cleanup Results:**
```javascript
const cleanupResultsVariables = {
    files_deleted: 45,
    space_freed_gb: 2.3,
    sent_files_deleted: 30,
    unsent_files_deleted: 15,
    errors: 0,
    duration_ms: 1500
};
```

**Monitoring Status:**
```javascript
const monitoringStatusVariables = {
    monitoring_active: true,
    last_check: '2024-12-19T10:00:00Z',
    next_check: '2024-12-19T10:05:00Z',
    checks_performed: 1234,
    cleanups_performed: 45
};
```

### 17.4 Storage WebSocket Events

**Storage WebSocket Event Names:**
```javascript
const STORAGE_WEBSOCKET_EVENTS = {
    // Client -> Server
    STORAGE_STATUS_REQUEST: 'storage_status_request',
    STORAGE_CLEANUP_REQUEST: 'storage_cleanup_request',
    STORAGE_CONFIG_UPDATE: 'storage_config_update',
    
    // Server -> Client
    STORAGE_STATUS_UPDATE: 'storage_status_update',
    STORAGE_CLEANUP_RESULT: 'storage_cleanup_result',
    STORAGE_CONFIG_UPDATED: 'storage_config_updated'
};
```

**Storage Status Response:**
```javascript
const storageStatusResponse = {
    success: true,
    data: {
        disk_usage: diskUsageVariables,
        folder_stats: folderStatisticsVariables,
        configuration: storageConfigurationVariables,
        monitoring: monitoringStatusVariables
    },
    timestamp: '2024-12-19T10:00:00Z'
};
```

// Online Mode Status Display Variables
const onlineStatusDisplay = {
    // Server Connection Status
    serverConnection: {
        connected: true,
        connectionText: 'Connected',
        statusClass: 'status-online'
    },
    
    // Data Sending Status
    dataSending: {
        active: true,
        dataText: 'Active',
        statusClass: 'status-active'
    },
    
    // Last Sync Time
    lastSync: {
        time: '2025-08-10T11:30:00.000Z',
        displayText: '2025-08-10 11:30:00'
    }
};
```

### 15.4 Environment Configuration Variables

**Environment Variables (.env.production):**
```bash
# WebSocket Server Configuration
WEBSOCKET_SERVER_URL="ws://lprserver:port"
AICAMERA_ID="1"
CHECKPOINT_ID="1"

# Database Configuration
DB_PATH="db/lpr_data.db"

# Security Configuration
SECRET_KEY="f4cf43e2322bcca04b16f201cad8b281ce1360d85e0170e0"
```

**Configuration Loading Variables:**
```python
# Config Loading Process Variables
config_loading = {
    'env_file_path': '/home/camuser/aicamera/v1_3/.env.production',
    'env_file_exists': True,
    'loaded_variables': {
        'WEBSOCKET_SERVER_URL': 'ws://lprserver:port',
        'AICAMERA_ID': '1',
        'CHECKPOINT_ID': '1',
        'SECRET_KEY': 'f4cf43e2322bcca04b16f201cad8b281ce1360d85e0170e0',
        'DB_PATH': 'db/lpr_data.db'
    },
    'missing_variables': [],
    'validation_status': 'success'
}
```

### 15.5 Import Helper Variables

**Import Path Variables:**
```python
# Import Helper Path Variables
import_paths = {
    'project_root': '/home/camuser/aicamera',
    'v1_3_path': '/home/camuser/aicamera/v1_3',
    'v1_3_src_path': '/home/camuser/aicamera/v1_3/src',
    'current_working_directory': '/home/camuser/aicamera/v1_3'
}

# Import Validation Variables
import_validation = {
    'required_modules': [
        'v1_3.src.core.config',
        'v1_3.src.core.dependency_container',
        'v1_3.src.components.camera_handler',
        'v1_3.src.components.health_monitor',
        'v1_3.src.services.camera_manager',
        'v1_3.src.services.health_service',
        'v1_3.src.services.websocket_sender'
    ],
    'validation_errors': [],
    'validation_status': 'success'
}
```

### 15.6 Application Startup Variables

**Startup Sequence Variables:**
```python
# Application Startup Variables
startup_sequence = {
    'step_1_load_env': {
        'status': 'completed',
        'env_file_loaded': True,
        'variables_loaded': 5
    },
    'step_2_setup_imports': {
        'status': 'completed',
        'import_paths_setup': True,
        'validation_passed': True
    },
    'step_3_create_app': {
        'status': 'completed',
        'flask_app_created': True,
        'template_folder': '/home/camuser/aicamera/v1_3/src/web/templates',
        'static_folder': '/home/camuser/aicamera/v1_3/src/web/static'
    },
    'step_4_initialize_services': {
        'status': 'completed',
        'camera_manager': 'initialized',
        'detection_manager': 'initialized',
        'health_service': 'initialized',
        'websocket_sender': 'initialized_offline_mode'
    }
}
```

---

**Note:** เอกสารนี้ควรได้รับการอัพเดตเมื่อมีการเปลี่ยนแปลงโครงสร้างหรือตัวแปรใหม่ เพื่อรักษามาตรฐานการพัฒนาร่วมกัน รวมถึงการเปลี่ยนแปลงในโครงสร้างข้อมูล frame, auto-startup sequence, health monitor status values, dashboard layout structure, WebSocket sender offline mode, และ configuration management system
