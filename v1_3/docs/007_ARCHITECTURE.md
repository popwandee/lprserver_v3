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
        'v1_3.src.components.health_monitor',
        'v1_3.src.services.camera_manager',
        'v1_3.src.services.health_service',
        # ... more modules
    ]
```

### 1.3 การใช้งาน Absolute Imports

```python
# ตัวอย่างการใช้ absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.components.camera_handler import CameraHandler
from v1_3.src.components.health_monitor import HealthMonitor
from v1_3.src.services.health_service import HealthService

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
        
        # Register health monitoring components
        try:
            from v1_3.src.components.health_monitor import HealthMonitor
            self.register_service('health_monitor', HealthMonitor, 
                                singleton=True, dependencies={'logger': 'logger'})
        except ImportError:
            self.logger.warning("HealthMonitor not available")
        
        # Register service layer components
        try:
            from v1_3.src.services.camera_manager import CameraManager, create_camera_manager
            self.register_service('camera_manager', CameraManager, 
                                singleton=True, 
                                factory=create_camera_manager,
                                dependencies={'camera_handler': 'camera_handler', 'logger': 'logger'})
        except ImportError as e:
            self.logger.warning(f"CameraManager service not available: {e}")
        
                try:
            from v1_3.src.services.health_service import HealthService, create_health_service
            self.register_service('health_service', HealthService, 
                                singleton=True,
                                factory=create_health_service,
                                dependencies={'health_monitor': 'health_monitor', 'logger': 'logger'})
        except ImportError as e:
            self.logger.warning(f"HealthService not available: {e}")
        
        # Register WebSocket Sender service
        try:
            from v1_3.src.services.websocket_sender import WebSocketSender, create_websocket_sender
            self.register_service('websocket_sender', WebSocketSender, 
                                singleton=True,
                                factory=create_websocket_sender,
                                dependencies={'database_manager': 'database_manager', 'logger': 'logger'})
        except ImportError:
            self.logger.warning("WebSocketSender not available")
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

container.register_service('health_service', HealthService,
                         dependencies={'health_monitor': 'health_monitor',
                                     'logger': 'logger'})
```

### 2.4 การใช้งานใน Components

```python
# ใน blueprint หรือ component ใดๆ ใช้ absolute imports
from v1_3.src.core.dependency_container import get_service

def some_function():
    camera_manager = get_service('camera_manager')
    detection_manager = get_service('detection_manager')
    health_service = get_service('health_service')
    
    # ใช้งาน services
    camera_manager.start()
    results = detection_manager.detect_objects('coco')
    health_status = health_service.get_system_health()
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
from v1_3.src.web.blueprints.health import health_bp, register_health_events
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
    register_health_events(socketio)
    
    # Register storage blueprint and events
    from v1_3.src.web.blueprints.storage import storage_bp, register_storage_events
    app.register_blueprint(storage_bp)
    register_storage_events(socketio)
```

### 3.4 Health Blueprint Example

```python
# v1_3/src/web/blueprints/health.py
from flask import Blueprint, render_template, jsonify, request
from flask_socketio import emit, join_room, leave_room

# Use absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')

logger = get_logger(__name__)

@health_bp.route('/')
def health_dashboard():
    """Render health monitoring dashboard."""
    return render_template('health/dashboard.html')

@health_bp.route('/system')
def get_system_health():
    """Get comprehensive system health status."""
    health_service = get_service('health_service')
    health_data = health_service.get_system_health()
    return jsonify(health_data)

@health_bp.route('/logs')
def get_health_logs():
    """Get health check logs with pagination."""
    health_service = get_service('health_service')
    logs_data = health_service.get_health_logs(
        level=level,
        limit=limit,
        page=page
    )
    return jsonify(logs_data)

@health_bp.route('/monitor/start', methods=['POST'])
def start_monitoring():
    """Start continuous health monitoring."""
    health_service = get_service('health_service')
    success = health_service.start_monitoring(interval=interval)
    return jsonify({'success': success})

@health_bp.route('/monitor/stop', methods=['POST'])
def stop_monitoring():
    """Stop continuous health monitoring."""
    health_service = get_service('health_service')
    health_service.stop_monitoring()
    return jsonify({'success': True})
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
│     └── variable_conflict_prevention_guide.md      # Guildline to prevent variable conflict
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
│   ├── health_service.py          # Health monitoring business logic
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
    │   ├── index.html             # Main dashboard with updated 2-row layout
    │   ├── camera/
    │   ├── detection/
    │   └── health/
    └── static/                    # Static Files
        ├── js/
        │   ├── dashboard.js       # Updated for new layout structure
        │   ├── camera.js
        │   ├── detection.js
        │   └── health.js
        └── css/
```

### 4.2.1 Updated Dashboard Layout Structure

The main dashboard (`index.html`) now uses a **2-row layout** for the System Information section:

**Row 1: Centered System Information**
- Single centered column (`col-md-8`)
- Left-aligned text content
- Core system information: CPU Architecture, AI Accelerator, OS & Kernel
- Clean horizontal separator

**Row 2: Three-Column Layout**
- **Column 1**: Hardware Information
  - Main Board, RAM, Disk
  - Camera details (Model, Resolution, Frame Rate, Status)
- **Column 2**: Development Information (Static)
  - Application, Framework, Architecture
  - Camera, Database, Communication, Deployment, Version Control
- **Column 3**: Component and Services (Static)
  - Flask Streaming, Camera Component, Detection Component
  - Health Monitor, WebSocket Sender, Database Manager

**Removed Elements:**
- System Status indicators (moved to dedicated health dashboard)
- Redundant camera information displays
- Duplicate status elements

**Benefits of New Layout:**
- Better visual hierarchy and organization
- Clear separation of dynamic vs static content
- Improved responsive design
- Reduced redundancy and cleaner code

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

```python
# v1_3/src/services/health_service.py
from v1_3.src.components.health_monitor import HealthMonitor
from v1_3.src.core.utils.logging_config import get_logger

class HealthService:
    def __init__(self, health_monitor: HealthMonitor, logger):
        self.health_monitor = health_monitor
        self.logger = logger
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        return self.health_monitor.run_all_checks()
    
    def start_monitoring(self, interval: int = None) -> bool:
        """Start continuous health monitoring."""
        return self.health_monitor.start_monitoring(interval)
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self.health_monitor.stop_monitoring()
```

## 6. WebSocket Sender Architecture

### 6.1 WebSocket Sender System Overview

ระบบ WebSocket Sender ของ AI Camera v1.3 รองรับการสื่อสารแบบ Real-time และ REST API พร้อม fallback mechanism:

1. **WebSocketSender Service** - Business logic layer
2. **Socket.IO Client** - Real-time communication
3. **REST API Client** - HTTP-based communication
4. **Fallback Mechanism** - Automatic switching between protocols

### 6.2 WebSocketSender Service (Business Logic)

```python
# v1_3/src/services/websocket_sender.py
class WebSocketSender:
    """
    WebSocket Sender Service for external server communication.
    
    Features:
    - Socket.IO connection management with auto-reconnect
    - REST API fallback mechanism
    - Detection data sender thread
    - Health status sender thread  
    - Database integration for tracking sent status
    - Logging and status monitoring
    """
    
    def __init__(self, database_manager=None, logger=None):
        self.logger = logger or get_logger(__name__)
        self.database_manager = database_manager
        
        # Socket.IO connection
        self.sio = None
        self.connected = False
        self.server_url = WEBSOCKET_SERVER_URL
        self.server_type = None  # 'socketio' or 'rest'
        
        # Threading
        self.detection_thread = None
        self.health_thread = None
        self.running = False
        self.stop_event = threading.Event()
        
        # Status tracking
        self.last_detection_check = None
        self.last_health_check = None
        self.retry_count = 0
        self.total_detections_sent = 0
        self.total_health_sent = 0
    
    def _detect_server_type(self):
        """Detect if server supports Socket.IO or REST API."""
        # Try Socket.IO first, fallback to REST API
        # Convert HTTP URLs to WebSocket URLs for Socket.IO
        # Test connections and set server_type accordingly
    
    def connect(self) -> bool:
        """Connect to server (Socket.IO or REST API)."""
        # Determine server type if not already detected
        # Connect based on server type
        # Return connection status
    
    def send_data(self, data: Dict[str, Any]) -> bool:
        """Send data via Socket.IO or REST API with fallback."""
        # Try primary method first (Socket.IO or REST based on server_type)
        # Fallback to alternative method if primary fails
        # Return send status
    
    def start(self) -> bool:
        """Start WebSocket sender service threads."""
        # Initialize service
        # Start detection sender thread
        # Start health sender thread
        # Return start status
```

### 6.3 Socket.IO Communication Events

```python
# Socket.IO Events ที่รองรับ
# Client -> Server
'camera_register' - สำหรับ camera ลงทะเบียน
'lpr_data' - สำหรับส่งข้อมูล LPR detection
'health_status' - สำหรับส่งข้อมูล health check
'ping' - สำหรับทดสอบการเชื่อมต่อ

# Server -> Client
'connect' - เมื่อ client เชื่อมต่อสำเร็จ
'disconnect' - เมื่อ client ตัดการเชื่อมต่อ
'error' - เมื่อเกิดข้อผิดพลาด
'pong' - response สำหรับ ping
'lpr_response' - response สำหรับ lpr_data
'health_response' - response สำหรับ health_status
```

### 6.4 REST API Endpoints

```python
# REST API Endpoints ที่รองรับ
POST /api/cameras/register - Camera registration
POST /api/detection - LPR detection data
POST /api/health - Health check data
GET /api/test - Test connection
GET /api/statistics - Get statistics (existing)
```

### 6.5 Fallback Strategy

```python
# Priority Order:
1. Socket.IO (Primary) - Real-time communication
2. REST API (Fallback) - When Socket.IO unavailable

# Detection Logic:
- Try Socket.IO connection first
- If Socket.IO fails, fallback to REST API
- If both fail, retry after delay
```

## 7. Storage Management Architecture

### 7.1 Storage Management System Overview

ระบบ Storage Management ของ AI Camera v1.3 ประกอบด้วย 3 ชั้นหลัก:

1. **StorageMonitor Component** - Low-level storage monitoring
2. **StorageService** - Business logic layer
3. **Storage Blueprint** - Web interface layer

### 7.2 StorageMonitor Component (Low-level)

```python
# v1_3/src/components/storage_monitor.py
class StorageMonitor:
    """
    Storage Monitor Component for disk space monitoring.
    
    Features:
    - Disk usage monitoring
    - Folder size calculation
    - File status tracking (sent/unsent)
    - Prioritized cleanup (sent files first)
    - Batch file deletion
    - Configuration management
    """
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger(__name__)
        self.folder_path = STORAGE_FOLDER_PATH
        self.min_free_space_gb = STORAGE_MIN_FREE_SPACE_GB
        self.retention_days = STORAGE_RETENTION_DAYS
        self.batch_size = STORAGE_BATCH_SIZE
        self.monitor_interval = STORAGE_MONITOR_INTERVAL
        self.running = False
        self.stop_event = threading.Event()
        self.monitor_thread = None
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get comprehensive storage status."""
        # Check disk usage
        # Calculate folder statistics
        # Get file counts by status
        # Return status data
    
    def cleanup_old_files(self, priority_sent: bool = True) -> Dict[str, Any]:
        """Clean up old files with priority for sent files."""
        # Get files by status from database
        # Delete sent files first if priority_sent=True
        # Delete unsent files if still needed
        # Return cleanup statistics
```

### 7.3 StorageService (Business Logic)

```python
# v1_3/src/services/storage_service.py
class StorageService:
    """
    Storage Service for disk space management.
    
    Features:
    - Storage status aggregation
    - Cleanup orchestration
    - Alert generation
    - Configuration management
    - Monitoring control
    """
    
    def __init__(self, storage_monitor: StorageMonitor, logger=None):
        self.storage_monitor = storage_monitor
        self.logger = logger or get_logger(__name__)
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get comprehensive storage status."""
        # Get status from storage monitor
        # Add service-level information
        # Return aggregated status
    
    def start_storage_monitoring(self, interval: int = None) -> bool:
        """Start continuous storage monitoring."""
        # Start monitoring thread
        # Set monitoring interval
        # Return start status
    
    def stop_storage_monitoring(self):
        """Stop continuous storage monitoring."""
        # Stop monitoring thread
        # Clean up resources
    
    def perform_cleanup(self, priority_sent: bool = True) -> Dict[str, Any]:
        """Perform storage cleanup with priority settings."""
        # Call storage monitor cleanup
        # Log cleanup results
        # Return cleanup statistics
```

### 7.4 Storage Blueprint (Web Interface)

```python
# v1_3/src/web/blueprints/storage.py
from flask import Blueprint, render_template, jsonify, request
from flask_socketio import emit, join_room, leave_room

storage_bp = Blueprint('storage', __name__, url_prefix='/storage')

@storage_bp.route('/')
def storage_dashboard():
    """Render storage management dashboard."""
    return render_template('storage/dashboard.html')

@storage_bp.route('/status')
def get_storage_status():
    """Get storage status."""
    storage_service = get_service('storage_service')
    status_data = storage_service.get_storage_status()
    return jsonify(status_data)

@storage_bp.route('/cleanup', methods=['POST'])
def perform_cleanup():
    """Perform storage cleanup."""
    storage_service = get_service('storage_service')
    priority_sent = request.json.get('priority_sent', True)
    cleanup_data = storage_service.perform_cleanup(priority_sent)
    return jsonify(cleanup_data)

# WebSocket Events
@socketio.on('storage_status_request')
def handle_storage_status_request():
    """Handle storage status request via WebSocket."""
    storage_service = get_service('storage_service')
    status_data = storage_service.get_storage_status()
    emit('storage_status_update', status_data)
```

## 8. Auto-Startup Sequence

### 8.1 Service Initialization Order

```python
# v1_3/src/app.py - _initialize_services()
def _initialize_services(logger):
    """
    Initialize services in the correct order with auto-startup sequence.
    
    Sequence:
    1. Initialize camera manager (auto-starts camera if enabled)
    2. Initialize detection manager (auto-starts detection if enabled)
    3. Initialize health monitor (auto-starts monitoring when camera and detection are ready)
    4. Initialize WebSocket sender (auto-starts when health monitor is ready)
    5. Initialize storage service (auto-starts monitoring when WebSocket sender is ready)
    """
    
    # Step 1: Camera Manager
    camera_manager = get_service('camera_manager')
    if camera_manager and AUTO_START_CAMERA:
        camera_manager.initialize()
    
    # Step 2: Detection Manager
    detection_manager = get_service('detection_manager')
    if detection_manager and AUTO_START_DETECTION:
        detection_manager.initialize()
    
    # Step 3: Health Monitor
    health_service = get_service('health_service')
    if health_service and AUTO_START_HEALTH_MONITOR:
        health_service.initialize()
        time.sleep(HEALTH_MONITOR_STARTUP_DELAY)
        health_service.start_monitoring()
    
    # Step 4: WebSocket Sender
    websocket_sender = get_service('websocket_sender')
    if websocket_sender and AUTO_START_WEBSOCKET_SENDER:
        websocket_sender.initialize()
        time.sleep(WEBSOCKET_SENDER_STARTUP_DELAY)
        websocket_sender.start()
    
    # Step 5: Storage Service
    storage_service = get_service('storage_service')
    if storage_service and AUTO_START_STORAGE_MONITOR:
        storage_service.initialize()
        time.sleep(STORAGE_MONITOR_STARTUP_DELAY)
        storage_service.start_storage_monitoring()
```

## 5. Health Monitoring Architecture

### 5.1 Health Monitoring System Overview

ระบบ Health Monitoring ของ AI Camera v1.3 ประกอบด้วย 3 ชั้นหลัก:

1. **HealthMonitor Component** - Low-level health checks
2. **HealthService** - Business logic layer
3. **Health Blueprint** - Web interface layer

### 5.2 HealthMonitor Component (Low-level)

```python
# v1_3/src/components/health_monitor.py
class HealthMonitor:
    """
    Health Monitor Component for system health monitoring.
    
    Monitors:
    - Camera status and streaming
    - Disk space availability
    - CPU and RAM usage
    - Detection model availability
    - EasyOCR initialization
    - Database connectivity
    - Network connectivity
    """
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger(__name__)
        self.db_manager = None
        self.camera_manager = None
        self.detection_manager = None
        self.running = False
        self.stop_event = Event()
        self.monitor_thread = None
    
    def initialize(self) -> bool:
        """Initialize Health Monitor with database connection."""
        # Initialize database manager
        # Create health_checks table
        # Get other services from DI container
    
    def check_camera(self) -> bool:
        """Check if camera is initialized and streaming."""
        # Check camera manager status
        # Validate initialization and streaming
    
    def check_disk_space(self, path: str = None, required_gb: float = 1.0) -> bool:
        """Check available disk space."""
        # Use shutil.disk_usage
        # Validate free space
    
    def check_cpu_ram(self) -> bool:
        """Check CPU and RAM usage."""
        # Use psutil for system metrics
        # Check usage thresholds
    
    def check_model_loading(self) -> bool:
        """Check if detection models are available."""
        # Check via detection service API
        # Fallback to direct degirum check
    
    def check_easyocr_init(self) -> bool:
        """Check if EasyOCR can be imported and initialized."""
        # Import easyocr
        # Initialize with supported languages
    
    def check_database_connection(self) -> bool:
        """Check database connectivity."""
        # Test database connection
        # Execute simple query
    
    def check_network_connectivity(self) -> bool:
        """Check network connectivity to external services."""
        # Test Google DNS
        # Test localhost WebSocket server
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status."""
        # Execute all checks
        # Determine overall status
        # Return detailed results
    
    def start_monitoring(self, interval: int = None) -> bool:
        """Start continuous health monitoring."""
        # Start background monitoring thread
        # Run checks at specified interval
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        # Stop monitoring thread
        # Cleanup resources
```

### 5.3 HealthService (Business Logic Layer)

```python
# v1_3/src/services/health_service.py
class HealthService:
    """
    Health Service for managing system health monitoring.
    
    Provides:
    - Health status aggregation
    - System resource monitoring
    - Health check scheduling
    - Status reporting for web interface
    - Auto-startup monitoring coordination
    """
    
    def __init__(self, health_monitor=None, logger=None):
        self.logger = logger or get_logger(__name__)
        self.health_monitor = health_monitor
        self.last_system_status = None
        self.last_check_time = None
    
    def initialize(self) -> bool:
        """Initialize Health Service with dependencies."""
        # Get health monitor from DI container
        # Initialize health monitor
        # Set up auto-start monitoring if enabled
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        # Run health checks
        # Get system resource information
        # Build component status
        # Add error details
        # Return comprehensive response
    
    def _build_component_status(self, health_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build component status from health check results."""
        # Camera status with real-time data
        # Detection status using detection module patterns
        # Database status with connection test
        # System status with resource metrics
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system resource information."""
        # CPU usage and count
        # Memory usage statistics
        # Disk usage statistics
        # System uptime
    
    def get_health_logs(self, level: str = None, limit: int = 50, page: int = 1) -> Dict[str, Any]:
        """Get health check logs from database with pagination."""
        # Get logs from health monitor
        # Apply level filtering
        # Implement pagination
        # Format response
    
    def start_monitoring(self, interval: int = None) -> bool:
        """Start continuous health monitoring."""
        # Delegate to health monitor
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        # Delegate to health monitor
    
    def _setup_auto_start_monitoring(self):
        """Set up auto-start monitoring when camera and detection are ready."""
        # Start background thread
        # Check component readiness
        # Start monitoring when ready
    
    def _should_start_monitoring(self) -> bool:
        """Check if health monitoring should start automatically."""
        # Check camera readiness
        # Check detection readiness
        # Return combined status
    
    def _is_detection_processor_ready(self, detection_status: Dict[str, Any]) -> bool:
        """Check if detection processor is ready using detection module patterns."""
        # Check processor status
        # Validate model availability
        # Return readiness status
```

### 5.4 Health Blueprint (Web Interface Layer)

```python
# v1_3/src/web/blueprints/health.py
@health_bp.route('/')
def health_dashboard():
    """Render health monitoring dashboard."""
    return render_template('health/dashboard.html')

@health_bp.route('/system')
def get_system_health():
    """Get comprehensive system health status."""
    health_service = get_service('health_service')
    health_data = health_service.get_system_health()
    return jsonify(health_data)

@health_bp.route('/logs')
def get_health_logs():
    """Get health check logs with pagination."""
    health_service = get_service('health_service')
    logs_data = health_service.get_health_logs(
        level=level,
        limit=limit,
        page=page
    )
    return jsonify(logs_data)

@health_bp.route('/monitor/start', methods=['POST'])
def start_monitoring():
    """Start continuous health monitoring."""
    health_service = get_service('health_service')
    success = health_service.start_monitoring(interval=interval)
    return jsonify({'success': success})

@health_bp.route('/monitor/stop', methods=['POST'])
def stop_monitoring():
    """Stop continuous health monitoring."""
    health_service = get_service('health_service')
    health_service.stop_monitoring()
    return jsonify({'success': True})
```

### 5.5 Health Monitoring Data Flow

```
User Request → Health Blueprint → HealthService → HealthMonitor → System Components
     ↓              ↓                ↓              ↓                ↓
Web Interface → Business Logic → Health Checks → Hardware/APIs → Status Data
     ↓              ↓                ↓              ↓                ↓
Dashboard ← JSON Response ← Aggregated Data ← Raw Checks ← Component Status
```

### 5.6 Health Status Response Structure

```json
{
    "success": true,
    "data": {
        "overall_status": "healthy|unhealthy|critical|unknown",
        "components": {
            "camera": {
                "status": "healthy|unhealthy|critical|unknown",
                "initialized": true,
                "streaming": true,
                "frame_count": 1234,
                "average_fps": 29.5,
                "uptime": 3600,
                "auto_start_enabled": true,
                "last_check": "2025-08-10T11:30:00.000Z"
            },
            "detection": {
                "status": "healthy|unhealthy|critical|unknown",
                "models_loaded": true,
                "easyocr_available": true,
                "detection_active": true,
                "service_running": true,
                "thread_alive": true,
                "auto_start": true,
                "last_check": "2025-08-10T11:30:00.000Z"
            },
            "database": {
                "status": "healthy|unhealthy|critical|unknown",
                "connected": true,
                "database_path": "/path/to/database.db",
                "last_check": "2025-08-10T11:30:00.000Z"
            },
            "system": {
                "status": "healthy|unhealthy|critical|unknown",
                "last_check": "2025-08-10T11:30:00.000Z"
            }
        },
        "system": {
            "cpu_usage": 25.5,
            "cpu_count": 4,
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
        "error_details": {
            "component_name": {
                "status": "unhealthy",
                "issues": ["Issue description"]
            }
        },
        "last_check": "2025-08-10T11:30:00.000Z"
    },
    "timestamp": "2025-08-10T11:30:00.000Z"
}
```

## 6. WebSocket Integration

### 6.1 Blueprint WebSocket Events

```python
# v1_3/src/web/blueprints/health.py
def register_health_events(socketio):
    @socketio.on('health_status_request')
    def handle_health_status_request():
        health_service = get_service('health_service')
        health_data = health_service.get_system_health()
        emit('health_status_update', health_data)
    
    @socketio.on('health_logs_request')
    def handle_health_logs_request(data):
        health_service = get_service('health_service')
        logs_data = health_service.get_health_logs(
            level=data.get('level'),
            limit=data.get('limit', 50),
            page=data.get('page', 1)
        )
        emit('health_logs_update', logs_data)
    
    @socketio.on('health_monitor_start')
    def handle_health_monitor_start(data):
        health_service = get_service('health_service')
        success = health_service.start_monitoring(interval=data.get('interval'))
        emit('health_monitor_response', {
            'success': success,
            'message': 'Health monitoring started successfully' if success else 'Failed to start monitoring'
        })
    
    @socketio.on('health_monitor_stop')
    def handle_health_monitor_stop():
        health_service = get_service('health_service')
        health_service.stop_monitoring()
        emit('health_monitor_response', {
            'success': True,
            'message': 'Health monitoring stopped successfully'
        })
    
    @socketio.on('health_check_run')
    def handle_health_check_run():
        health_service = get_service('health_service')
        health_data = health_service.get_system_health()
        emit('health_check_response', health_data)
    
    @socketio.on('join_health_room')
    def handle_join_health_room():
        join_room('health_monitoring')
        emit('health_room_joined', {
            'success': True,
            'message': 'Joined health monitoring room'
        })
    
    @socketio.on('leave_health_room')
    def handle_leave_health_room():
        leave_room('health_monitoring')
        emit('health_room_left', {
            'success': True,
            'message': 'Left health monitoring room'
        })
```

### 6.2 การลงทะเบียน WebSocket Events

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

## 7. การใช้งานในทางปฏิบัติ

### 7.1 การเพิ่ม Component ใหม่

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

### 7.2 การ Testing

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

```python
# test_health_service.py
def test_health_service():
    # Mock dependencies
    mock_health_monitor = Mock()
    mock_logger = Mock()
    
    # Create service with mocked dependencies
    health_service = HealthService(mock_health_monitor, mock_logger)
    
    # Test functionality
    health_service.get_system_health()
    mock_health_monitor.run_all_checks.assert_called_once()
```

## 8. ประโยชน์ของ Architecture นี้

### 8.1 Modularity
- แต่ละ Component มีหน้าที่ชัดเจน
- สามารถพัฒนาและทดสอบแยกกันได้
- ง่ายต่อการเพิ่มหรือลบฟีเจอร์
- **Absolute imports ทำให้ dependencies ชัดเจน**

### 8.2 Maintainability
- Code มีโครงสร้างชัดเจน
- Dependencies ถูกจัดการอย่างเป็นระบบ
- ง่ายต่อการ Debug และ Troubleshoot
- **Import paths ชัดเจนและเข้าใจง่าย**

### 8.3 Scalability
- สามารถเพิ่ม Components ใหม่ได้ง่าย
- Blueprints ช่วยจัดการ Routes ได้ดี
- DI ช่วยจัดการ Dependencies ได้อย่างมีประสิทธิภาพ
- **Absolute imports รองรับการขยายระบบได้ดี**

### 8.4 Testability
- Components สามารถ Mock ได้ง่าย
- Unit Testing ทำได้สะดวก
- Integration Testing มีโครงสร้างชัดเจน
- **Import validation ช่วยตรวจสอบ dependencies**

### 8.5 Health Monitoring Benefits
- **Comprehensive Monitoring**: ครอบคลุมทุก component หลัก
- **Real-time Status**: สถานะแบบ real-time ผ่าน WebSocket
- **Auto-startup Coordination**: ประสานงานกับ auto-startup sequence
- **Detailed Logging**: บันทึก logs อย่างละเอียดในฐานข้อมูล
- **Error Prevention**: ป้องกันข้อผิดพลาดด้วย validation patterns

## 9. Best Practices

1. **ใช้ Absolute Imports** สำหรับทุก module
2. **ใช้ DI Container** สำหรับการจัดการ Dependencies ทั้งหมด
3. **แยก Business Logic** ไปไว้ใน Service Layer
4. **ใช้ Blueprints** สำหรับการจัดการ Routes ตามหน้าที่
5. **เขียน Documentation** สำหรับแต่ละ Component
6. **ทำ Unit Testing** สำหรับทุก Component
7. **ใช้ Logging** อย่างเหมาะสม
8. **จัดการ Error** อย่างเป็นระบบ
9. **Validate Imports** ในการ startup
10. **Health Monitoring Integration** สำหรับทุก component ใหม่

## 10. Migration Guide

### 10.1 การแปลงจาก Relative Imports เป็น Absolute Imports

```bash
# รัน migration script
cd v1_3
python scripts/migrate_absolute_imports.py
```

### 10.2 การตรวจสอบ Imports

```python
# ตรวจสอบ imports ใน startup
from v1_3.src.core.utils.import_helper import validate_imports

import_errors = validate_imports()
if import_errors:
    for error in import_errors:
        print(f"Import error: {error}")
```

### 10.3 การเพิ่ม Module ใหม่

```python
# 1. สร้างไฟล์ใหม่
# 2. ใช้ absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# 3. ลงทะเบียนใน DI container
# 4. อัพเดท import validation
```

## 11. Auto-Startup Sequence Architecture

### 11.1 Auto-Startup Configuration
```python
# v1_3/src/core/config.py
AUTO_START_CAMERA = True
AUTO_START_STREAMING = True  
AUTO_START_DETECTION = True
AUTO_START_HEALTH_MONITOR = True  # Auto start health monitoring when detection starts
STARTUP_DELAY = 5.0  # seconds
HEALTH_MONITOR_STARTUP_DELAY = 10.0  # Delay before starting health monitoring
```

### 11.2 Service Initialization Order
```python
# v1_3/src/app.py
def _initialize_services(logger):
    """Initialize services in proper order for auto-startup."""
    # 1. Camera Manager (handles camera + streaming auto-start)
    camera_manager = get_service('camera_manager')
    if camera_manager:
        camera_manager.initialize()  # Auto-starts camera/streaming if configured
        
    # 2. Detection Manager (handles detection auto-start)
    detection_manager = get_service('detection_manager')
    if detection_manager:
        detection_manager.initialize()  # Auto-starts detection if configured
        
    # 3. Health Monitor and Service (auto-starts monitoring when camera and detection are ready)
    health_monitor = get_service('health_monitor')
    health_service = get_service('health_service')
    if health_monitor and health_service:
        health_monitor.initialize()
        health_service.initialize()  # Auto-starts monitoring when components are ready
```

### 11.3 Camera Manager Auto-Startup
```python
# v1_3/src/services/camera_manager.py
def initialize(self):
    """Initialize camera manager with auto-start support."""
    if self.auto_start_enabled:
        self._auto_start_camera()
        
def _auto_start_camera(self):
    """Auto-start camera and streaming if configured."""
    # Start camera
    if self.start_camera():
        # Start streaming if configured
        if self.auto_streaming_enabled:
            self.start_streaming()
```

### 11.4 Detection Manager Auto-Startup
```python
# v1_3/src/services/detection_manager.py
def initialize(self):
    """Initialize detection manager with auto-start support."""
    if self.auto_start_enabled:
        self._auto_start_detection()
        
def _auto_start_detection(self):
    """Auto-start detection after camera is ready."""
    time.sleep(STARTUP_DELAY)  # Wait for camera to be ready
    camera_manager = get_service('camera_manager')
    if self._is_camera_ready(camera_manager):
        self.start_detection()
```

### 11.5 Health Monitor Auto-Startup
```python
# v1_3/src/services/health_service.py
def initialize(self):
    """Initialize health service with auto-start support."""
    # Initialize health monitor component
    if self.health_monitor.initialize():
        # Set up auto-start monitoring if enabled
        if AUTO_START_HEALTH_MONITOR:
            self._setup_auto_start_monitoring()
            
def _setup_auto_start_monitoring(self):
    """Set up auto-start monitoring when camera and detection are ready."""
    def auto_start_monitor():
        # Wait initial delay
        time.sleep(HEALTH_MONITOR_STARTUP_DELAY)
        
        # Check if components are ready
        while not self._should_start_monitoring():
            time.sleep(30)  # Check every 30 seconds
            
        # Start monitoring when ready
        self.start_monitoring(interval=60)
    
    # Start monitoring thread
    threading.Thread(target=auto_start_monitor, daemon=True).start()
```

## 12. Frame Capture Data Flow Architecture

### 12.1 Frame Data Structure
```python
# Camera Handler returns dict format
frame_data = {
    'frame': np.ndarray,     # Actual image data
    'metadata': dict,        # Frame metadata
    'timestamp': float       # Capture timestamp
}

# Camera Manager extracts numpy array
frame = frame_data['frame']  # Extract for detection processing
```

### 12.2 Frame Validation Pipeline
```python
# v1_3/src/components/detection_processor.py
def validate_and_enhance_frame(self, frame):
    """Validate frame data with type checking."""
    # Handle dict input (extract frame)
    if isinstance(frame, dict):
        if 'frame' in frame:
            frame = frame['frame']
        else:
            return None
    
    # Validate numpy array
    if not isinstance(frame, np.ndarray):
        return None
        
    if frame.size == 0:
        return None
```

### 12.3 Detection Pipeline Data Flow
```
Camera Handler.capture_frame()
    ↓ (returns dict with 'frame' key)
Camera Manager.capture_frame()
    ↓ (extracts numpy array from dict)
Detection Manager.process_frame_from_camera()
    ↓ (receives numpy array)
Detection Processor.validate_and_enhance_frame()
    ↓ (validates and processes numpy array)
AI Model Processing
    ↓ (detection results)
Result Storage & WebSocket Broadcast
```

## 13. Error Prevention Patterns

### 13.1 Attribute Access Safety
```python
# Safe camera status checking
def _is_camera_ready(self, camera_manager):
    """Safely check if camera is ready for detection."""
    if not camera_manager:
        return False
    
    status = camera_manager.get_status()
    return (status.get('initialized', False) and 
            status.get('streaming', False))
```

### 13.2 Service Configuration Safety
```python
# Safe attribute access for auto-start settings
def get_status(self):
    """Get detection manager status safely."""
    return {
        'active': self.active,
        'auto_start': self.auto_start_enabled,  # Use correct attribute name
        'detection_count': self.detection_count
    }
```

### 13.4 Frame Error Prevention Patterns
```python
# Frame validation error codes
FRAME_ERROR_CODES = {
    'INVALID_TYPE': 'Expected numpy.ndarray, got dict',
    'EMPTY_FRAME': 'Frame size is 0',
    'MISSING_FRAME_KEY': 'Dict missing frame key',
    'VALIDATION_FAILED': 'Frame validation failed'
}

# Frame error response format
def create_frame_error_response(error_type: str, details: dict) -> dict:
    return {
        'success': False,
        'error': FRAME_ERROR_CODES.get(error_type, 'Frame validation failed'),
        'error_type': error_type,
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
```

## 14. Health Monitoring Integration Patterns

### 14.1 Component Health Check Integration
```python
# Every component should provide health check methods
class NewComponent:
    def get_health_status(self) -> Dict[str, Any]:
        """Get component health status for health monitoring."""
        return {
            'status': 'healthy' if self.initialized else 'unhealthy',
            'initialized': self.initialized,
            'last_check': datetime.now().isoformat(),
            'details': {
                'component_specific_metric': self.some_metric
            }
        }
```

### 14.2 Service Health Check Integration
```python
# Every service should integrate with health monitoring
class NewService:
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status for health monitoring."""
        component_status = self.component.get_health_status() if self.component else {}
        return {
            'status': 'healthy' if self.active else 'unhealthy',
            'service_running': self.active,
            'component_status': component_status,
            'last_check': datetime.now().isoformat()
        }
```

### 14.3 Health Check Registration
```python
# Register health checks in health monitor
def register_health_checks(self):
    """Register all health checks."""
    self.health_checks = {
        'camera': self.check_camera,
        'disk_space': self.check_disk_space,
        'cpu_ram': self.check_cpu_ram,
        'models': self.check_model_loading,
        'easyocr': self.check_easyocr_init,
        'database': self.check_database_connection,
        'network': self.check_network_connectivity,
        'new_component': self.check_new_component  # Add new component checks
    }
```

## 15. Updated Variable Management and Layout

### 15.1 Dashboard Layout Evolution

The dashboard layout has evolved from a single-row system to a **2-row responsive layout**:

**Previous Layout Issues:**
- Mixed dynamic and static content in single row
- Redundant status indicators
- Poor visual hierarchy
- Inconsistent element naming

**Current Layout Benefits:**
- **Row 1**: Centered core system information (CPU, AI Accelerator, OS)
- **Row 2**: Three-column organization (Hardware, Development, Components)
- Clear separation of dynamic vs static content
- Improved responsive design
- Better user experience

### 15.2 Variable Naming Convention Updates

**Updated Element IDs:**
- `system-info-cpu` - CPU Architecture information
- `system-info-ai-accelerator` - AI Accelerator details
- `system-info-os` - Operating System information
- `system-info-ram` - RAM usage
- `system-info-disk` - Disk usage
- `feature-camera-*` - Camera-related information

**Removed Element IDs:**
- `main-camera-model`, `main-camera-resolution`, `main-camera-fps`
- `main-camera-detail-status`, `main-database-detail-status`
- `main-system-uptime`, `main-camera-status`, `main-detection-status`
- `main-database-status`, `main-system-status`

**JavaScript Variable Updates:**
- Updated `dashboard.js` to reflect new element structure
- Removed unused variable declarations
- Added new system information update functions
- Improved error handling for missing elements

### 15.3 Layout Responsiveness

**Bootstrap Grid System:**
- Row 1: `justify-content-center` for centering
- Row 2: `col-md-4` for equal three-column layout
- Responsive breakpoints for mobile devices
- Consistent spacing with `mb-4` and `my-3`

## 16. WebSocket Sender Offline Mode Architecture

### 16.1 Offline Mode Overview

WebSocket Sender ใน AI Camera v1.3 รองรับ **Offline Mode** เพื่อให้ระบบทำงานได้แม้ไม่สามารถเชื่อมต่อ server ได้:

**Key Features:**
- **Graceful Degradation**: ทำงานใน local mode เมื่อไม่มี server URL
- **Data Persistence**: บันทึกข้อมูลในฐานข้อมูล local
- **Auto Recovery**: ส่งข้อมูลที่ค้างไว้เมื่อเชื่อมต่อได้
- **Smart Reconnection**: Retry connection อัตโนมัติ

### 16.2 Offline Mode Implementation

```python
# WebSocket Sender Offline Mode Logic
class WebSocketSender:
    def initialize(self) -> bool:
        if not self.server_url:
            self.logger.warning("WEBSOCKET_SERVER_URL not configured - service will run in offline mode")
            self.server_url = None  # Set to None to indicate offline mode
            return True  # Allow initialization in offline mode
    
    def _send_detection_data(self) -> int:
        # Check if in offline mode
        if not self.server_url:
            # In offline mode, just log that we're processing locally
            self.database_manager.log_websocket_action(
                action='send_detection',
                status='offline',
                message=f'Processing {len(unsent_detections)} detection records locally (offline mode)',
                data_type='detection_results',
                record_count=len(unsent_detections)
            )
            return len(unsent_detections)  # Return count as "processed"
        
        # Normal online mode - send to server
        # ... existing sending logic
```

### 16.3 Reconnection and Pending Data Handling

```python
async def connect(self) -> bool:
    """Connect to WebSocket server with pending data handling."""
    try:
        # ... connection logic ...
        
        if self.connected:
            # Try to send any pending data after successful connection
            await self._send_pending_data()
        
        return True
    except Exception as e:
        # ... error handling ...

async def _send_pending_data(self):
    """Send any pending data after successful connection."""
    try:
        if not self.connected or not self.server_url:
            return
        
        self.logger.info("Sending pending data after reconnection...")
        
        # Send pending detection data
        detection_count = self._send_detection_data()
        if detection_count > 0:
            self.logger.info(f"Sent {detection_count} pending detection records")
        
        # Send pending health data
        health_count = self._send_health_data()
        if health_count > 0:
            self.logger.info(f"Sent {health_count} pending health records")
            
    except Exception as e:
        self.logger.error(f"Error sending pending data: {e}")
```

### 16.4 Status Display Integration

**Dashboard Status Indicators:**

```javascript
// Offline Mode Status Display
updateServerConnectionDisplay: function(status) {
    let connected = false;
    let connectionText = 'Disconnected';
    let dataActive = false;
    let dataText = 'Inactive';

    if (status) {
        // Check if in offline mode
        if (status.offline_mode) {
            connected = false;
            connectionText = 'Offline Mode';
            dataActive = status.running && (status.detection_thread_alive || status.health_thread_alive);
            dataText = dataActive ? 'Active (Local)' : 'Inactive';
        } else {
            // Normal online mode
            if (status.connected) {
                connected = true;
                connectionText = 'Connected';
            }
            if (status.running && (status.detection_thread_alive || status.health_thread_alive)) {
                dataActive = true;
                dataText = 'Active';
            }
        }
    }

    // Update UI elements
    AICameraUtils.updateStatusIndicator('main-server-connection-status', connected, connectionText);
    AICameraUtils.updateStatusIndicator('main-data-sending-status', dataActive, dataText);
}
```

### 16.5 Configuration Management

**Environment Configuration:**
```bash
# v1_3/.env.production
WEBSOCKET_SERVER_URL="ws://100.95.46.128:8765"
AICAMERA_ID="1"
CHECKPOINT_ID="1"
```

**Config Loading Process:**
```python
# v1_3/src/core/config.py
def load_env_file():
    """Load environment variables from .env.production file."""
    env_file = Path(__file__).parent.parent.parent / '.env.production'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key.strip()] = value

# Load environment variables
load_env_file()

# WebSocket server configuration
WEBSOCKET_SERVER_URL = os.getenv("WEBSOCKET_SERVER_URL")
```

## 17. Import Helper and Configuration Architecture

### 17.1 Import Helper System

**Purpose:** จัดการ import paths และ absolute imports ให้ถูกต้อง

```python
# v1_3/src/core/utils/import_helper.py
def setup_import_paths(base_path: Optional[str] = None) -> None:
    """Setup import paths for absolute imports."""
    if base_path is None:
        # Get the project root directory (aicamera/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent  # Go up from utils/core/src/v1_3
        logger.info(f"Auto-detected project root: {project_root.absolute()}")
    else:
        project_root = Path(base_path)
    
    # Add project root to sys.path for absolute imports
    project_root_str = str(project_root.absolute())
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    # Add v1_3 directory for v1_3.* imports
    v1_3_path = str(project_root / 'v1_3')
    if v1_3_path not in sys.path:
        sys.path.insert(0, v1_3_path)
    
    # Add v1_3/src directory for src.* imports
    v1_3_src_path = str(project_root / 'v1_3' / 'src')
    if v1_3_src_path not in sys.path:
        sys.path.insert(0, v1_3_src_path)
```

### 17.2 Application Startup Process

**Startup Sequence:**
```python
# v1_3/src/app.py
def create_app():
    """Create and configure Flask application using absolute imports."""
    # 1. Load environment variables
    load_env_file()
    
    # 2. Setup import paths
    from v1_3.src.core.utils.import_helper import setup_import_paths, validate_imports
    setup_import_paths()
    
    # 3. Validate imports
    import_errors = validate_imports()
    if import_errors:
        logger.warning("Some imports failed:")
        for error in import_errors:
            logger.warning(f"  {error}")
    
    # 4. Create Flask app with correct paths
    current_dir = Path(__file__).parent
    template_dir = current_dir / 'web' / 'templates'
    static_dir = current_dir / 'web' / 'static'
    
    app = Flask(__name__, 
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    
    # 5. Load configuration
    app.config.from_object('v1_3.src.core.config')
    
    # 6. Initialize dependency container
    container = get_container()
    
    # 7. Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # 8. Register blueprints
    register_blueprints(app, socketio)
    
    # 9. Initialize services with auto-startup sequence
    _initialize_services(logger)
    
    return app, socketio
```

### 17.3 WSGI Entry Point

```python
# v1_3/src/wsgi.py
#!/usr/bin/env python3
"""
WSGI Entry Point for AI Camera v1.3

This module provides the WSGI application entry point for deployment.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup import paths
from v1_3.src.core.utils.import_helper import setup_import_paths
setup_import_paths()

# Import and create application
from v1_3.src.app import create_app

app, socketio = create_app()

if __name__ == "__main__":
    app.run()
```

### 17.4 Configuration Best Practices

**1. Environment Variables:**
- ใช้ `.env.production` สำหรับ production settings
- ใช้ `os.getenv()` ใน config.py
- ไม่ hardcode sensitive values

**2. Import Management:**
- ใช้ absolute imports: `from v1_3.src.core.* import *`
- เรียก `setup_import_paths()` ก่อน import modules
- ใช้ `validate_imports()` เพื่อตรวจสอบ

**3. Path Management:**
- ใช้ `Path(__file__).parent` สำหรับ relative paths
- ตรวจสอบ file existence ก่อนใช้งาน
- ใช้ absolute paths สำหรับ deployment

## 18. สรุป

AI Camera v1.3 ใช้ Dependency Injection, Flask Blueprints และ **Absolute Imports** เพื่อสร้างระบบที่:
- **Modular**: แบ่งส่วนการทำงานชัดเจน
- **Maintainable**: ง่ายต่อการบำรุงรักษา
- **Testable**: ทดสอบได้ง่าย
- **Scalable**: ขยายได้ง่าย
- **Clear**: Import paths ชัดเจนและเข้าใจง่าย
- **Auto-Startup**: รองรับการเริ่มงานอัตโนมัติแบบ sequential (camera → detection → health monitor)
- **Frame-Safe**: ป้องกัน frame data type errors
- **Attribute-Safe**: ป้องกัน attribute access errors
- **Health-Monitored**: ระบบ health monitoring ที่ครอบคลุมและอัตโนมัติ
- **Layout-Optimized**: 2-row responsive layout with improved UX
- **Variable-Clean**: Streamlined element IDs and JavaScript variables
- **Offline-Capable**: WebSocket Sender รองรับ offline mode และ auto-recovery
- **Config-Managed**: จัดการ configuration ผ่าน environment variables และ import helper
- **WebSocket-Ready**: รองรับ Socket.IO และ REST API พร้อม fallback mechanism
- **Storage-Managed**: ระบบจัดการพื้นที่จัดเก็บอัตโนมัติพร้อม prioritized cleanup

Architecture นี้ทำให้ระบบมีความยืดหยุ่นและสามารถพัฒนาเพิ่มเติมได้อย่างมีประสิทธิภาพ พร้อมกับความชัดเจนในการจัดการ dependencies และ imports รวมถึงการจัดการ startup sequence, error prevention, comprehensive health monitoring system, optimized user interface layout และ robust offline mode support

