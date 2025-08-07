# AI Camera v1.3 Architecture Documentation

## Overview

AI Camera v1.3 ใช้ Design Patterns หลัก 2 แบบเพื่อสร้างระบบที่ Modular, Maintainable และ Testable:

1. **Dependency Injection (DI)** - สำหรับการจัดการ Dependencies ระหว่าง Components
2. **Flask Blueprints** - สำหรับการแบ่งส่วนการทำงานของ Web UI

โปรเจกต์นี้จะใช้ Design Pattern แบบ Dependency Injection เพื่อจัดการ Class ต่างๆ และใช้ Flask Blueprints สำหรับการแบ่งส่วนการทำงานของ Web UI เพื่อเพิ่ม Modularization. โดยมี /core/dependency_container.py  กำกับ module dependencies.
## 1. Dependency Injection Pattern

### แนวคิดหลัก

Dependency Injection ช่วยให้เราสามารถ:
- แยก Dependencies ออกจาก Class
- ทำให้ Testing ง่ายขึ้น
- ลดการ Coupling ระหว่าง Components
- จัดการ Lifecycle ของ Services ได้ดีขึ้น

### การใช้งานใน AI Camera v1.3

#### 1.1 Dependency Container

```python
# v1_3/src/core/dependency_container.py
class DependencyContainer:
    def __init__(self):
        self.services = {}
        self.instances = {}
        self._register_default_services()
    
    def register_service(self, name, service_type, dependencies=None):
        # ลงทะเบียน service พร้อม dependencies
        pass
    
    def get_service(self, name):
        # ดึง service instance จาก container
        pass
```

#### 1.2 Service Registration

```python
# ลงทะเบียน services พร้อม dependencies
container.register_service('camera_manager', CameraManager, 
                         dependencies={'camera_handler': 'camera_handler',
                                     'logger': 'logger'})

container.register_service('detection_manager', DetectionManager,
                         dependencies={'detection_processor': 'detection_processor',
                                     'database_manager': 'database_manager',
                                     'logger': 'logger'})
```

#### 1.3 การใช้งานใน Components

```python
# ใน blueprint หรือ component ใดๆ
from ...core.dependency_container import get_service

def some_function():
    camera_manager = get_service('camera_manager')
    detection_manager = get_service('detection_manager')
    
    # ใช้งาน services
    camera_manager.start()
    results = detection_manager.detect_objects('coco')
```

### ประโยชน์ของ Dependency Injection

1. **Testability**: สามารถ Mock Dependencies ได้ง่าย
2. **Flexibility**: เปลี่ยน Implementation ได้โดยไม่กระทบ Code อื่น
3. **Maintainability**: Code มีความชัดเจนและเข้าใจง่าย
4. **Reusability**: Components สามารถนำไปใช้ซ้ำได้

## 2. Flask Blueprints Pattern

### แนวคิดหลัก

Flask Blueprints ช่วยให้เราสามารถ:
- แบ่ง Application เป็นส่วนๆ ตามหน้าที่
- จัดการ Routes แยกกัน
- สร้าง Modular Web UI
- ง่ายต่อการ Maintain และ Scale

### โครงสร้าง Blueprints ใน AI Camera v1.3

```
v1_3/src/web/blueprints/
├── __init__.py
├── main.py          # Main dashboard และ system routes
├── camera.py        # Camera control และ configuration
├── detection.py     # AI detection และ model management
├── streaming.py     # Video streaming endpoints
├── health.py        # System health monitoring
└── websocket.py     # WebSocket communication
```

### 2.1 Main Blueprint

```python
# v1_3/src/web/blueprints/main.py
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page."""
    # ดึงข้อมูลจาก services ผ่าน DI
    camera_manager = get_service('camera_manager')
    detection_manager = get_service('detection_manager')
    
    return render_template('main/dashboard.html',
                         camera_status=camera_manager.get_status(),
                         detection_status=detection_manager.get_status())
```

### 2.2 Camera Blueprint

```python
# v1_3/src/web/blueprints/camera.py
camera_bp = Blueprint('camera', __name__, url_prefix='/camera')

@camera_bp.route('/status', methods=['GET'])
def get_camera_status():
    """Get current camera status."""
    camera_manager = get_service('camera_manager')
    status = camera_manager.get_status()
    
    return jsonify({
        'success': True,
        'status': status
    })

@camera_bp.route('/config', methods=['POST'])
def update_camera_config():
    """Update camera configuration."""
    data = request.get_json()
    camera_manager = get_service('camera_manager')
    updated_config = camera_manager.update_configuration(data)
    
    return jsonify({
        'success': True,
        'config': updated_config
    })
```

### 2.3 Detection Blueprint

```python
# v1_3/src/web/blueprints/detection.py
detection_bp = Blueprint('detection', __name__, url_prefix='/detection')

@detection_bp.route('/models', methods=['GET'])
def get_available_models():
    """Get list of available AI models."""
    detection_manager = get_service('detection_manager')
    models = detection_manager.get_available_models()
    
    return jsonify({
        'success': True,
        'models': models
    })

@detection_bp.route('/detect', methods=['POST'])
def run_detection():
    """Run detection on an image or camera frame."""
    data = request.get_json()
    detection_manager = get_service('detection_manager')
    results = detection_manager.detect_objects(**data)
    
    return jsonify({
        'success': True,
        'results': results
    })
```

### 2.4 การลงทะเบียน Blueprints

```python
# v1_3/src/app.py
def register_blueprints(app):
    """Register all Flask blueprints."""
    app.register_blueprint(main_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(streaming_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(websocket_bp)
```

## 3. Component Architecture

### Common Dependencies
aicamera/  # root of project
aicamera/assets # image and video for test detection inference
aicamera/doc       # document for development
aicamera/log        # system log
aicamera/postprocessors # example of postprocess
aicamera/resources  # Hailo Execute File .hef
aicamera/systemd_service/aicamera_v1.3.service  # systemd service
aicamera/tests      # Machine Learning , Camera, Models Detection testing script file
aicamera/v1_3       # working directory for this version
aicamera/venv_hailo # virtual environment for this project, activate by "source venv_setup.sh"
aicamera/gunicorn_config.py # gunicorn configuration script
aicamera/setup_env.sh   # set up Hailo environment, Get HailoRT the Device Architecture, Activate TAPPAS virtual environment
aicamera/requirements.txt   # dependencies
aicamera/v1_3/requirements.txt # dependencies for this version
aicamera/v1_3/.env.production   # sensitive configuration parameter

### 3.1 Core Components

```
v1_3/src/
├── core/
│   ├── __init__.py
│   ├── dependency_container.py    # DI Container    
│   ├── config.py              # Configuration
│   └── utils/                 # Utilities
├── components/                    # Low-level components (Hardware/External APIs)
│   ├── __init__.py
│   ├── detection_processor.py     # AI Detection by Hailo AI models
│   ├── camera_handler.py          # Camera Interface, Picamera2 wrapper
│   ├── health_monitor.py          # System Health monitoring
│   └── database_manager.py        # Database Operations
├── services/                      # High-level business logic
│   ├── camera_manager.py          # Camera Management ,Camera business logic
│   ├── detection_manager.py       # Detection Management, Detection workflow
│   ├── video_streaming.py         # Video Streaming, service
│   └── websocket_sender.py        # WebSocket Communication
└── web/                           # Web interface layer
    ├── blueprints/                # Flask Blueprints
    ├── templates/                 # HTML Templates
    └── static/                    # Static Files
```
## 🔄 **Dependency Flow**

```
Web Blueprints → Services → Components → Hardware/External APIs
     ↓              ↓           ↓              ↓
  User Input → Business Logic → Low-level → Picamera2/AI Models

ใช้ absolute imports ใน dependency_container.py
```

### 3.2 Service Layer

Services เป็นชั้นกลางที่จัดการ Business Logic:

```python
# v1_3/src/services/camera_manager.py
class CameraManager:
    def __init__(self, camera_handler, logger):
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

## 4. WebSocket Integration

### 4.1 Blueprint WebSocket Events

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

### 4.2 การลงทะเบียน WebSocket Events

```python
# v1_3/src/app.py
def register_websocket_handlers(socketio):
    register_camera_events(socketio)
    register_detection_events(socketio)
    register_streaming_events(socketio)
    register_health_events(socketio)
    register_websocket_events(socketio)
    register_main_events(socketio)
```

## 5. การใช้งานในทางปฏิบัติ

### 5.1 การเพิ่ม Component ใหม่

1. **สร้าง Component Class**:
```python
# v1_3/src/components/new_component.py
class NewComponent:
    def __init__(self, logger):
        self.logger = logger
    
    def do_something(self):
        return "Something done"
```

2. **ลงทะเบียนใน DI Container**:
```python
# v1_3/src/core/dependency_container.py
def _register_default_services(self):
    self.register_service('new_component', NewComponent,
                         dependencies={'logger': 'logger'})
```

3. **สร้าง Blueprint** (ถ้าจำเป็น):
```python
# v1_3/src/web/blueprints/new_feature.py
new_feature_bp = Blueprint('new_feature', __name__, url_prefix='/new-feature')

@new_feature_bp.route('/action', methods=['POST'])
def perform_action():
    component = get_service('new_component')
    result = component.do_something()
    return jsonify({'result': result})
```

4. **ลงทะเบียน Blueprint**:
```python
# v1_3/src/app.py
def register_blueprints(app):
    app.register_blueprint(new_feature_bp)
```

### 5.2 การ Testing

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

## 6. ประโยชน์ของ Architecture นี้

### 6.1 Modularity
- แต่ละ Component มีหน้าที่ชัดเจน
- สามารถพัฒนาและทดสอบแยกกันได้
- ง่ายต่อการเพิ่มหรือลบฟีเจอร์

### 6.2 Maintainability
- Code มีโครงสร้างชัดเจน
- Dependencies ถูกจัดการอย่างเป็นระบบ
- ง่ายต่อการ Debug และ Troubleshoot

### 6.3 Scalability
- สามารถเพิ่ม Components ใหม่ได้ง่าย
- Blueprints ช่วยจัดการ Routes ได้ดี
- DI ช่วยจัดการ Dependencies ได้อย่างมีประสิทธิภาพ

### 6.4 Testability
- Components สามารถ Mock ได้ง่าย
- Unit Testing ทำได้สะดวก
- Integration Testing มีโครงสร้างชัดเจน

## 7. Best Practices

1. **ใช้ DI Container** สำหรับการจัดการ Dependencies ทั้งหมด
2. **แยก Business Logic** ไปไว้ใน Service Layer
3. **ใช้ Blueprints** สำหรับการจัดการ Routes ตามหน้าที่
4. **เขียน Documentation** สำหรับแต่ละ Component
5. **ทำ Unit Testing** สำหรับทุก Component
6. **ใช้ Logging** อย่างเหมาะสม
7. **จัดการ Error** อย่างเป็นระบบ

## 8. สรุป

AI Camera v1.3 ใช้ Dependency Injection และ Flask Blueprints เพื่อสร้างระบบที่:
- **Modular**: แบ่งส่วนการทำงานชัดเจน
- **Maintainable**: ง่ายต่อการบำรุงรักษา
- **Testable**: ทดสอบได้ง่าย
- **Scalable**: ขยายได้ง่าย

Architecture นี้ทำให้ระบบมีความยืดหยุ่นและสามารถพัฒนาเพิ่มเติมได้อย่างมีประสิทธิภาพ

