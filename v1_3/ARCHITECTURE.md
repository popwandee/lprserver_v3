# AI Camera v1.3 Architecture Documentation

## Overview

AI Camera v1.3 ใช้ Design Patterns หลัก 3 แบบเพื่อสร้างระบบที่ Modular, Maintainable และ Testable:

1. **Dependency Injection (DI)** - สำหรับการจัดการ Dependencies ระหว่าง Components
2. **Flask Blueprints** - สำหรับการแบ่งส่วนการทำงานของ Web UI
3. **Absolute Imports** - สำหรับการจัดการ imports ที่ชัดเจนและสม่ำเสมอ

โปรเจกต์นี้จะใช้ Design Pattern แบบ Dependency Injection เพื่อจัดการ Class ต่างๆ และใช้ Flask Blueprints สำหรับการแบ่งส่วนการทำงานของ Web UI เพื่อเพิ่ม Modularization โดยมี `/core/dependency_container.py` กำกับ module dependencies และใช้ absolute imports ผ่าน `import_helper.py`

## 1. Absolute Imports Pattern

### 1.1 แนวคิดหลัก

Absolute Imports ช่วยให้เราสามารถ:
- ใช้ import paths ที่ชัดเจนและสม่ำเสมอ
- ลดปัญหา circular imports
- ทำให้ code อ่านง่ายและเข้าใจง่าย
- รองรับการ refactor และการย้ายไฟล์ได้ดี

### 1.2 Import Helper

```python
# v1_3/src/core/utils/import_helper.py
def setup_import_paths(base_path: Optional[str] = None) -> None:
    """Setup import paths for absolute imports."""
    # Add project root for v1_3.* imports
    # Add v1_3/src for src.* imports
    # Add current working directory

def validate_imports() -> List[str]:
    """Validate that all required modules can be imported using absolute paths."""
    required_modules = [
        'v1_3.src.core.config',
        'v1_3.src.core.dependency_container',
        'v1_3.src.components.camera_handler',
        'v1_3.src.services.camera_manager',
        # ... more modules
    ]
```

### 1.3 การใช้งาน Absolute Imports

```python
# ตัวอย่างการใช้ absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.components.camera_handler import CameraHandler

# Import validation on startup
import_errors = validate_imports()
if import_errors:
    logger.warning("Some imports failed:")
    for error in import_errors:
        logger.warning(f"  {error}")
```

## 2. Dependency Injection Pattern

### 2.1 แนวคิดหลัก

Dependency Injection ช่วยให้เราสามารถ:
- แยก Dependencies ออกจาก Class
- ทำให้ Testing ง่ายขึ้น
- ลดการ Coupling ระหว่าง Components
- จัดการ Lifecycle ของ Services ได้ดีขึ้น

### 2.2 Dependency Container

```python
# v1_3/src/core/dependency_container.py
class DependencyContainer:
    def __init__(self):
        self.services = {}
        self.instances = {}
        self._register_default_services()
    
    def _register_default_services(self):
        """Register default services with absolute imports."""
        # Core components
        self.register_service('logger', logging.Logger, singleton=True,
                        factory=self._create_logger)
        self.register_service('config', dict, singleton=True, 
                            factory=self._create_config)
        
        # Register components using absolute imports
        try:
            from v1_3.src.components.detection_processor import DetectionProcessor
            self.register_service('detection_processor', DetectionProcessor, 
                                singleton=True, dependencies={'logger': 'logger'})
        except ImportError:
            self.logger.warning("DetectionProcessor not available")
        
        try:
            from v1_3.src.components.camera_handler import CameraHandler
            self.register_service('camera_handler', CameraHandler, 
                                singleton=True, 
                                factory=CameraHandler.get_instance,
                                dependencies={'logger': 'logger'})
        except ImportError:
            self.logger.warning("CameraHandler not available")
        
        # Register service layer components
        try:
            from v1_3.src.services.camera_manager import CameraManager, create_camera_manager
            self.register_service('camera_manager', CameraManager, 
                                singleton=True, 
                                factory=create_camera_manager,
                                dependencies={'camera_handler': 'camera_handler', 'logger': 'logger'})
        except ImportError as e:
            self.logger.warning(f"CameraManager service not available: {e}")
```

### 2.3 Service Registration

```python
# ลงทะเบียน services พร้อม dependencies ใช้ absolute imports
container.register_service('camera_manager', CameraManager, 
                         dependencies={'camera_handler': 'camera_handler',
                                     'logger': 'logger'})

container.register_service('detection_manager', DetectionManager,
                         dependencies={'detection_processor': 'detection_processor',
                                     'database_manager': 'database_manager',
                                     'logger': 'logger'})
```

### 2.4 การใช้งานใน Components

```python
# ใน blueprint หรือ component ใดๆ ใช้ absolute imports
from v1_3.src.core.dependency_container import get_service

def some_function():
    camera_manager = get_service('camera_manager')
    detection_manager = get_service('detection_manager')
    
    # ใช้งาน services
    camera_manager.start()
    results = detection_manager.detect_objects('coco')
```

## 3. Flask Blueprints Pattern

### 3.1 แนวคิดหลัก

Flask Blueprints ช่วยให้เราสามารถ:
- แบ่ง Application เป็นส่วนๆ ตามหน้าที่
- จัดการ Routes แยกกัน
- สร้าง Modular Web UI
- ง่ายต่อการ Maintain และ Scale

### 3.2 โครงสร้าง Blueprints

```
v1_3/src/web/blueprints/
├── __init__.py          # Blueprint registration with absolute imports
├── main.py              # Main dashboard และ system routes
├── camera.py            # Camera control และ configuration
├── detection.py         # AI detection และ model management
├── streaming.py         # Video streaming endpoints
├── health.py            # System health monitoring
└── websocket.py         # WebSocket communication
```

### 3.3 Blueprint Registration

```python
# v1_3/src/web/blueprints/__init__.py
from flask import Flask
from flask_socketio import SocketIO

# Import blueprints using absolute paths
from v1_3.src.web.blueprints.main import main_bp
from v1_3.src.web.blueprints.camera import camera_bp, register_camera_events
from v1_3.src.web.blueprints.health import health_bp
from v1_3.src.web.blueprints.streaming import streaming_bp
from v1_3.src.web.blueprints.detection import detection_bp
from v1_3.src.web.blueprints.websocket import websocket_bp

def register_blueprints(app: Flask, socketio: SocketIO):
    """Register all Flask blueprints with the application."""
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(streaming_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(websocket_bp)
    
    # Register WebSocket events
    register_camera_events(socketio)
```

### 3.4 Camera Blueprint Example

```python
# v1_3/src/web/blueprints/camera.py
from flask import Blueprint, render_template, jsonify, request, Response
from flask_socketio import emit, join_room, leave_room

# Use absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# Create blueprint
camera_bp = Blueprint('camera', __name__, url_prefix='/camera')

logger = get_logger(__name__)

@camera_bp.route('/status')
def get_camera_status():
    """Get current camera status."""
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        status = camera_manager.get_status()
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
```

## 4. System Architecture

### 4.1 Project Structure

```
aicamera/                           # root of project
├── assets/                         # image and video for test detection inference
├── doc/                           # document for development
├── log/                           # system log
├── postprocessors/                # example of postprocess
├── resources/                     # Hailo Execute File .hef
├── systemd_service/               # systemd service files
├── tests/                         # ML, Camera, Models Detection testing scripts
├── v1_3/                          # working directory for this version
├── venv_hailo/                    # virtual environment for this project
├── gunicorn_config.py             # gunicorn configuration script
├── setup_env.sh                   # set up Hailo environment
└── requirements.txt               # dependencies 
```
### Working Directory
v1_3/
├── docs/
│     └── class_diagram.puml      # Class Diagram
│     └── component_diagram.puml      # Component Diagram
│     └── variable_conflict_prevention_guide.mk      # Guildline to prevent variable conflict
│     └── variable_mapping_diagram.puml      # variable mapping backend and frontend
├── scripts/
├── src/                #Core Components Structure
├── tmp/                # Tempolary script and Testing File
├── __init__.py
├── .evn.production    # Sensitive Environment configuration
├── ARCHITECTURE.md                  # Configuration management
├── CONTEXT_ENGINEERING.md          # Context to communicate with AI
├── README.md                       # About the version
├── requirements.txt                    # Version Dependencies
└── VARIABLE_MANAGEMENT.md      # Rules to manage variable

### 4.2 Core Components Structure

```
v1_3/src/
├── core/
│   ├── __init__.py
│   ├── dependency_container.py    # DI Container with absolute imports
│   ├── config.py                  # Configuration management
│   └── utils/                     # Core utilities
│       ├── __init__.py
│       ├── import_helper.py       # Absolute import management
│       └── logging_config.py      # Logging configuration
├── components/                    # Low-level components (Hardware/External APIs)
│   ├── __init__.py
│   ├── detection_processor.py     # AI Detection by Hailo AI models
│   ├── camera_handler.py          # Camera Interface, Picamera2 wrapper
│   ├── health_monitor.py          # System Health monitoring
│   └── database_manager.py        # Database Operations
├── services/                      # High-level business logic
│   ├── __init__.py
│   ├── camera_manager.py          # Camera Management, Camera business logic
│   ├── detection_manager.py       # Detection Management, Detection workflow
│   ├── video_streaming.py         # Video Streaming service
│   └── websocket_sender.py        # WebSocket Communication
└── web/                           # Web interface layer
    ├── __init__.py
    ├── blueprints/                # Flask Blueprints with absolute imports
    │   ├── __init__.py
    │   ├── main.py
    │   ├── camera.py
    │   ├── detection.py
    │   ├── streaming.py
    │   ├── health.py
    │   └── websocket.py
    ├── templates/                 # HTML Templates
    └── static/                    # Static Files
```

### 4.3 Dependency Flow

```
Web Blueprints → Services → Components → Hardware/External APIs
     ↓              ↓           ↓              ↓
  User Input → Business Logic → Low-level → Picamera2/AI Models

ใช้ absolute imports ในทุก layer:
- v1_3.src.web.blueprints.*
- v1_3.src.services.*
- v1_3.src.components.*
- v1_3.src.core.*
```

### 4.4 Service Layer

Services เป็นชั้นกลางที่จัดการ Business Logic ใช้ absolute imports:

```python
# v1_3/src/services/camera_manager.py
from v1_3.src.components.camera_handler import CameraHandler
from v1_3.src.core.utils.logging_config import get_logger

class CameraManager:
    def __init__(self, camera_handler: CameraHandler, logger):
        self.camera_handler = camera_handler
        self.logger = logger
    
    def start(self):
        """Start camera."""
        return self.camera_handler.initialize_camera()
    
    def stop(self):
        """Stop camera."""
        return self.camera_handler.close_camera()
    
    def get_status(self):
        """Get camera status."""
        return self.camera_handler.get_status()
```

## 5. WebSocket Integration

### 5.1 Blueprint WebSocket Events

```python
# v1_3/src/web/blueprints/camera.py
def register_camera_events(socketio):
    @socketio.on('camera_status_request')
    def handle_camera_status_request():
        camera_manager = get_service('camera_manager')
        status = camera_manager.get_status()
        emit('camera_status_update', status)
    
    @socketio.on('camera_control')
    def handle_camera_control(data):
        command = data.get('command')
        camera_manager = get_service('camera_manager')
        
        if command == 'start':
            success = camera_manager.start()
        elif command == 'stop':
            success = camera_manager.stop()
        
        emit('camera_control_response', {
            'command': command,
            'success': success
        })
```

### 5.2 การลงทะเบียน WebSocket Events

```python
# v1_3/src/app.py
def register_websocket_handlers(socketio):
    from v1_3.src.web.blueprints.camera import register_camera_events
    from v1_3.src.web.blueprints.detection import register_detection_events
    from v1_3.src.web.blueprints.streaming import register_streaming_events
    from v1_3.src.web.blueprints.health import register_health_events
    from v1_3.src.web.blueprints.websocket import register_websocket_events
    from v1_3.src.web.blueprints.main import register_main_events
    
    register_camera_events(socketio)
    register_detection_events(socketio)
    register_streaming_events(socketio)
    register_health_events(socketio)
    register_websocket_events(socketio)
    register_main_events(socketio)
```

## 6. การใช้งานในทางปฏิบัติ

### 6.1 การเพิ่ม Component ใหม่

1. **สร้าง Component Class ใช้ absolute imports**:
```python
# v1_3/src/components/new_component.py
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

class NewComponent:
    def __init__(self, logger):
        self.logger = logger
    
    def process(self, data):
        # Your logic here
        pass
```

2. **ลงทะเบียนใน DI Container ใช้ absolute imports**:
```python
# v1_3/src/core/dependency_container.py
def _register_default_services(self):
    try:
        from v1_3.src.components.new_component import NewComponent
        self.register_service('new_component', NewComponent,
                             dependencies={'logger': 'logger'})
    except ImportError:
        self.logger.warning("NewComponent not available")
```

3. **สร้าง Blueprint ใช้ absolute imports** (ถ้าจำเป็น):
```python
# v1_3/src/web/blueprints/new_feature.py
from flask import Blueprint, jsonify
from v1_3.src.core.dependency_container import get_service

new_feature_bp = Blueprint('new_feature', __name__, url_prefix='/new-feature')

@new_feature_bp.route('/action', methods=['POST'])
def perform_action():
    component = get_service('new_component')
    result = component.process(data)
    return jsonify({'result': result})
```

4. **ลงทะเบียน Blueprint ใช้ absolute imports**:
```python
# v1_3/src/web/blueprints/__init__.py
from v1_3.src.web.blueprints.new_feature import new_feature_bp

def register_blueprints(app: Flask, socketio: SocketIO):
    app.register_blueprint(new_feature_bp)
```

### 6.2 การ Testing

```python
# test_example.py
def test_camera_manager():
    # Mock dependencies
    mock_camera_handler = Mock()
    mock_logger = Mock()
    
    # Create service with mocked dependencies
    camera_manager = CameraManager(mock_camera_handler, mock_logger)
    
    # Test functionality
    camera_manager.start()
    mock_camera_handler.initialize_camera.assert_called_once()
```

## 7. ประโยชน์ของ Architecture นี้

### 7.1 Modularity
- แต่ละ Component มีหน้าที่ชัดเจน
- สามารถพัฒนาและทดสอบแยกกันได้
- ง่ายต่อการเพิ่มหรือลบฟีเจอร์
- **Absolute imports ทำให้ dependencies ชัดเจน**

### 7.2 Maintainability
- Code มีโครงสร้างชัดเจน
- Dependencies ถูกจัดการอย่างเป็นระบบ
- ง่ายต่อการ Debug และ Troubleshoot
- **Import paths ชัดเจนและเข้าใจง่าย**

### 7.3 Scalability
- สามารถเพิ่ม Components ใหม่ได้ง่าย
- Blueprints ช่วยจัดการ Routes ได้ดี
- DI ช่วยจัดการ Dependencies ได้อย่างมีประสิทธิภาพ
- **Absolute imports รองรับการขยายระบบได้ดี**

### 7.4 Testability
- Components สามารถ Mock ได้ง่าย
- Unit Testing ทำได้สะดวก
- Integration Testing มีโครงสร้างชัดเจน
- **Import validation ช่วยตรวจสอบ dependencies**

## 8. Best Practices

1. **ใช้ Absolute Imports** สำหรับทุก module
2. **ใช้ DI Container** สำหรับการจัดการ Dependencies ทั้งหมด
3. **แยก Business Logic** ไปไว้ใน Service Layer
4. **ใช้ Blueprints** สำหรับการจัดการ Routes ตามหน้าที่
5. **เขียน Documentation** สำหรับแต่ละ Component
6. **ทำ Unit Testing** สำหรับทุก Component
7. **ใช้ Logging** อย่างเหมาะสม
8. **จัดการ Error** อย่างเป็นระบบ
9. **Validate Imports** ในการ startup

## 9. Migration Guide

### 9.1 การแปลงจาก Relative Imports เป็น Absolute Imports

```bash
# รัน migration script
cd v1_3
python scripts/migrate_absolute_imports.py
```

### 9.2 การตรวจสอบ Imports

```python
# ตรวจสอบ imports ใน startup
from v1_3.src.core.utils.import_helper import validate_imports

import_errors = validate_imports()
if import_errors:
    for error in import_errors:
        print(f"Import error: {error}")
```

### 9.3 การเพิ่ม Module ใหม่

```python
# 1. สร้างไฟล์ใหม่
# 2. ใช้ absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# 3. ลงทะเบียนใน DI container
# 4. อัพเดท import validation
```

## 10. สรุป

AI Camera v1.3 ใช้ Dependency Injection, Flask Blueprints และ **Absolute Imports** เพื่อสร้างระบบที่:
- **Modular**: แบ่งส่วนการทำงานชัดเจน
- **Maintainable**: ง่ายต่อการบำรุงรักษา
- **Testable**: ทดสอบได้ง่าย
- **Scalable**: ขยายได้ง่าย
- **Clear**: Import paths ชัดเจนและเข้าใจง่าย

Architecture นี้ทำให้ระบบมีความยืดหยุ่นและสามารถพัฒนาเพิ่มเติมได้อย่างมีประสิทธิภาพ พร้อมกับความชัดเจนในการจัดการ dependencies และ imports