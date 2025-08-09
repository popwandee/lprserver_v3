# AI Camera v1.3 - Context Engineering Guide

## Overview

เอกสารนี้เป็นแนวทางสำหรับการสื่อสารกับ AI เพื่อ Generate code ที่เข้ากับโครงสร้างเดิมของ AI Camera v1.3 โดยมีจุดประสงค์เพื่อป้องกันปัญหา conflict และรักษาความสอดคล้องของ Architecture

## 1. Project Context Overview

### 1.1 System Architecture
```
AI Camera v1.3 ใช้:
- Flask Framework with Blueprint Pattern
- Dependency Injection Container
- Absolute Imports System (v1_3.src.*)
- Unix Socket + Nginx Reverse Proxy
- WebSocket + HTTP API
- Systemd Service Management
```

### 1.2 Directory Structure
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

/home/camuser/aicamera/v1_3/src/
├── src/
   ├── app.py                 # Flask application entry point
   ├── wsgi.py                # WSGI entry point
   ├── core/                  # Core framework
   │   ├── dependency_container.py
   │   ├── config.py
   │   └── utils/
   │       ├── import_helper.py
   │       └── logging_config.py
   ├── components/            # Hardware/Low-level components
   │   ├── camera_handler.py
   │   ├── detection_processor.py
   │   └── database_manager.py
   ├── services/              # Business logic services
   │   ├── camera_manager.py
   │   ├── detection_manager.py
   │   └── video_streaming.py
   └── web/                   # Web interface layer
       ├── blueprints/        # Flask Blueprints
       ├── templates/         # Jinja2 templates
       └── static/            # CSS, JS, Images

```

## 2. Critical Requirements for AI Code Generation

### 2.1 MANDATORY Import Patterns
```python
# ✅ ALWAYS use absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.components.camera_handler import CameraHandler

# ❌ NEVER use relative imports
from ..core.dependency_container import get_service  # DON'T DO THIS
from core.dependency_container import get_service    # DON'T DO THIS
```

### 2.2 MANDATORY Flask Configuration
```python
# Flask app MUST be configured with these paths
app = Flask(__name__, 
           template_folder='web/templates',    # FIXED PATH
           static_folder='web/static')         # FIXED PATH
```

### 2.3 MANDATORY Dependency Injection Pattern
```python
# ✅ ALWAYS get services from DI container
camera_manager = get_service('camera_manager')
detection_manager = get_service('detection_manager')

# ❌ NEVER instantiate services directly
camera_manager = CameraManager()  # DON'T DO THIS
```

## 3. Static Files and Templates Critical Patterns

### 3.1 Template Structure Requirements
```html
<!-- MANDATORY base template extension -->
{% extends "base.html" %}

<!-- MANDATORY variables for every template -->
{% set active_page = "page_name" %}
{% set use_socketio = true %}  <!-- For pages that need WebSocket -->

<!-- MANDATORY CSS inclusion pattern -->
{% block additional_css %}
<link href="{{ url_for('static', filename='css/page_name.css') }}" rel="stylesheet">
{% endblock %}

<!-- MANDATORY JS inclusion pattern -->
{% block additional_js %}
<script src="{{ url_for('static', filename='js/page_name.js') }}"></script>
{% endblock %}
```

### 3.2 Static Files Path Requirements
```
CRITICAL: Static files MUST be in v1_3/src/web/static/
- CSS files: v1_3/src/web/static/css/
- JS files:  v1_3/src/web/static/js/
- Images:    v1_3/src/web/static/images/

NGINX serves from: /home/camuser/aicamera/v1_3/src/web/static/
```

## 4. Variable Management Standards

### 4.1 Backend Variables (Python) - snake_case
```python
# Status variables
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
```

### 4.2 Frontend Variables (JavaScript) - camelCase
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

// Element IDs - kebab-case
const elementIds = {
    cameraStatus: 'main-camera-status',
    detectionStatus: 'main-detection-status',
    systemLog: 'main-system-log'
};
```

### 4.3 API Response Format - MANDATORY Structure
```json
{
    "success": true,
    "status": {
        "initialized": true,
        "streaming": true,
        "frame_count": 1234,
        "average_fps": 29.5,
        "uptime": 3600
    },
    "timestamp": "2025-08-09T17:00:00.000Z"
}
```

## 5. WebSocket Integration Patterns

### 5.1 Template WebSocket Setup
```html
<!-- MANDATORY: Set use_socketio = true for WebSocket pages -->
{% set use_socketio = true %}
```

### 5.2 JavaScript WebSocket Patterns
```javascript
// ✅ CORRECT: Use WebSocketManager from base.js
WebSocketManager.init();
WebSocketManager.socket.on('camera_status_update', (status) => {
    this.updateCameraStatus(status);
});

// ✅ CORRECT: Use AICameraUtils for common functions
AICameraUtils.addLogMessage('main-system-log', 'Message', 'info');
AICameraUtils.updateStatusIndicator('main-camera-status', true, 'Online');
```

## 6. Blueprint Creation Patterns

### 6.1 Blueprint File Structure
```python
# MANDATORY blueprint structure
from flask import Blueprint, render_template, jsonify, request
from flask_socketio import emit, join_room, leave_room

# MANDATORY absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# MANDATORY blueprint creation pattern
blueprint_name_bp = Blueprint('blueprint_name', __name__, url_prefix='/blueprint_name')
logger = get_logger(__name__)

@blueprint_name_bp.route('/')
def blueprint_dashboard():
    return render_template('blueprint_name/dashboard.html')

@blueprint_name_bp.route('/status')
def get_blueprint_status():
    try:
        service = get_service('service_name')
        if not service:
            return jsonify({'error': 'Service not available'}), 500
        
        status = service.get_status()
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# MANDATORY WebSocket event registration
def register_blueprint_events(socketio):
    @socketio.on('blueprint_status_request')
    def handle_status_request():
        service = get_service('service_name')
        status = service.get_status()
        emit('blueprint_status_update', status)
```

### 6.2 Blueprint Registration Pattern
```python
# In v1_3/src/web/blueprints/__init__.py
from v1_3.src.web.blueprints.new_blueprint import new_blueprint_bp, register_new_blueprint_events

def register_blueprints(app: Flask, socketio: SocketIO):
    app.register_blueprint(new_blueprint_bp)
    register_new_blueprint_events(socketio)
```

## 7. Service and Component Creation Patterns

### 7.1 Component Creation Pattern
```python
# File: v1_3/src/components/new_component.py
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

class NewComponent:
    def __init__(self, logger=None):
        self.logger = logger or get_logger(__name__)
        self.initialized = False
    
    def initialize(self):
        try:
            # Initialization logic
            self.initialized = True
            self.logger.info("NewComponent initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize NewComponent: {e}")
            return False
    
    def get_status(self):
        return {
            'initialized': self.initialized,
            'component_name': 'NewComponent'
        }
```

### 7.2 Service Creation Pattern
```python
# File: v1_3/src/services/new_service.py
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

class NewService:
    def __init__(self, component=None, logger=None):
        self.component = component
        self.logger = logger or get_logger(__name__)
    
    def start(self):
        if not self.component:
            self.component = get_service('new_component')
        
        if self.component and self.component.initialize():
            self.logger.info("NewService started successfully")
            return True
        return False
    
    def get_status(self):
        component_status = self.component.get_status() if self.component else {}
        return {
            'service_running': self.component.initialized if self.component else False,
            'component_status': component_status
        }

def create_new_service(component=None, logger=None):
    return NewService(component, logger)
```

### 7.3 DI Container Registration Pattern
```python
# In v1_3/src/core/dependency_container.py - _register_default_services method
try:
    from v1_3.src.components.new_component import NewComponent
    self.register_service('new_component', NewComponent, 
                         singleton=True, 
                         dependencies={'logger': 'logger'})
except ImportError:
    self.logger.warning("NewComponent not available")

try:
    from v1_3.src.services.new_service import NewService, create_new_service
    self.register_service('new_service', NewService,
                         singleton=True,
                         factory=create_new_service,
                         dependencies={'component': 'new_component', 'logger': 'logger'})
except ImportError as e:
    self.logger.warning(f"NewService not available: {e}")
```

## 8. JavaScript Patterns and Standards

### 8.1 JavaScript File Structure
```javascript
/**
 * AI Camera v1.3 - [Component Name] JavaScript
 * [Brief description of functionality]
 */

// [Component Name] state management
const ComponentManager = {
    socket: null,
    statusUpdateInterval: null,
    
    /**
     * Initialize component
     */
    init: function() {
        this.initializeWebSocket();
        this.setupEventHandlers();
        this.setupStatusUpdates();
        console.log('ComponentManager initialized');
    },

    /**
     * Initialize WebSocket connection
     */
    initializeWebSocket: function() {
        if (typeof io === 'undefined') {
            console.warn('Socket.IO not available');
            return;
        }
        
        this.socket = io('/component_namespace');  // or io() for default
        this.setupSocketHandlers();
    },

    /**
     * Setup WebSocket event handlers
     */
    setupSocketHandlers: function() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            console.log('Connected to component service');
            AICameraUtils.addLogMessage('log-container', 'Connected to service', 'success');
        });

        this.socket.on('component_status_update', (status) => {
            this.updateComponentStatus(status);
        });
    },

    /**
     * Update component status display
     */
    updateComponentStatus: function(status) {
        // Status update logic using AICameraUtils
        AICameraUtils.updateStatusIndicator('component-status', status.active, 
            status.active ? 'Active' : 'Inactive');
    },

    /**
     * Cleanup when leaving page
     */
    cleanup: function() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    ComponentManager.init();
    
    window.addEventListener('beforeunload', function() {
        ComponentManager.cleanup();
    });
    
    console.log('Component JavaScript loaded');
});
```

### 8.2 Common JavaScript Utilities Usage
```javascript
// ✅ ALWAYS use AICameraUtils for common functions
AICameraUtils.addLogMessage('log-container-id', 'Message text', 'info|success|warning|error');
AICameraUtils.updateStatusIndicator('status-element-id', isOnline, 'Status Text');
AICameraUtils.showToast('Message', 'info|success|warning|error');
AICameraUtils.apiRequest('/api/endpoint', {method: 'POST', body: JSON.stringify(data)});

// ✅ ALWAYS use WebSocketManager for WebSocket connections
WebSocketManager.init('/namespace');
WebSocketManager.emit('event_name', data);
```

## 9. Error Handling and Logging Standards

### 9.1 Python Error Handling
```python
# MANDATORY error handling pattern
try:
    service = get_service('service_name')
    if not service:
        return jsonify({'error': 'Service not available'}), 500
    
    result = service.perform_operation()
    return jsonify({
        'success': True,
        'data': result,
        'timestamp': datetime.now().isoformat()
    })
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return jsonify({
        'success': False,
        'error': str(e),
        'timestamp': datetime.now().isoformat()
    }), 500
```

### 9.2 JavaScript Error Handling
```javascript
// MANDATORY API call error handling
AICameraUtils.apiRequest('/api/endpoint')
    .then(data => {
        if (data && data.success) {
            // Handle success
            this.updateStatus(data.status);
        } else {
            console.warn('Invalid response:', data);
        }
    })
    .catch(error => {
        console.error('API call failed:', error);
        AICameraUtils.addLogMessage('log-container', 'Failed to get data: ' + error.message, 'error');
        // Set fallback/default values
        this.updateStatus({default: 'values'});
    });
```

## 10. Database and Configuration Patterns

### 10.1 Configuration Access Pattern
```python
# ✅ CORRECT: Get config from DI container
config = get_service('config')
setting_value = config.get('SETTING_NAME', default_value)

# ✅ CORRECT: Direct import for constants
from v1_3.src.core.config import DEFAULT_RESOLUTION, DEFAULT_FRAMERATE
```

### 10.2 Database Operations Pattern
```python
# ✅ CORRECT: Get database manager from DI container
db_manager = get_service('database_manager')
if db_manager:
    result = db_manager.execute_query(query, params)
    return result
```

## 11. Testing Patterns

### 11.1 Component Testing
```python
# File: tests/test_new_component.py
import unittest
from unittest.mock import Mock, patch
from v1_3.src.components.new_component import NewComponent

class TestNewComponent(unittest.TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.component = NewComponent(logger=self.mock_logger)
    
    def test_initialization(self):
        result = self.component.initialize()
        self.assertTrue(result)
        self.assertTrue(self.component.initialized)
```

### 11.2 Service Testing with DI
```python
# File: tests/test_new_service.py
import unittest
from unittest.mock import Mock
from v1_3.src.services.new_service import NewService

class TestNewService(unittest.TestCase):
    def setUp(self):
        self.mock_component = Mock()
        self.mock_logger = Mock()
        self.service = NewService(self.mock_component, self.mock_logger)
    
    def test_service_start(self):
        self.mock_component.initialize.return_value = True
        result = self.service.start()
        self.assertTrue(result)
        self.mock_component.initialize.assert_called_once()
```

## 12. Common Pitfalls and Solutions

### 12.1 Import Issues
```python
# ❌ PROBLEM: ModuleNotFoundError: No module named 'v1_3'
# ✅ SOLUTION: Always run from project root and use absolute imports

# ❌ PROBLEM: Circular imports
# ✅ SOLUTION: Use dependency injection, avoid direct imports between services
```

### 12.2 Static Files 404
```nginx
# ✅ SOLUTION: Ensure nginx static path is correct
location /static/ {
    alias /home/camuser/aicamera/v1_3/src/web/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 12.3 WebSocket Not Working
```html
<!-- ✅ SOLUTION: Always set use_socketio = true -->
{% set use_socketio = true %}
```

### 12.4 JavaScript Errors
```javascript
// ❌ PROBLEM: TypeError: Cannot read property of undefined
// ✅ SOLUTION: Always check element existence
const element = document.getElementById('element-id');
if (element) {
    element.textContent = 'New value';
}
```

## 13. AI Code Generation Prompts

### 13.1 For New Components
```
Create a new component for AI Camera v1.3:
- Component name: [ComponentName]
- Functionality: [Description]
- Requirements:
  * Use absolute imports (v1_3.src.*)
  * Follow dependency injection pattern
  * Include error handling and logging
  * Register in DI container
  * Create corresponding service if needed
```

### 13.2 For New Blueprints
```
Create a new Flask blueprint for AI Camera v1.3:
- Blueprint name: [blueprint_name]
- URL prefix: /[blueprint_name]
- Features: [List features]
- Requirements:
  * Use absolute imports
  * Include WebSocket support if needed
  * Follow variable naming standards
  * Create corresponding template
  * Register in blueprint __init__.py
```

### 13.3 For Frontend Features
```
Create frontend JavaScript for AI Camera v1.3:
- Feature: [FeatureName]
- Template: [template_name]
- Requirements:
  * Use AICameraUtils and WebSocketManager
  * Follow camelCase for variables
  * Use kebab-case for element IDs
  * Include error handling
  * Set use_socketio = true if needed
```

## 14. Deployment and Maintenance

### 14.1 Service Restart Procedure
```bash
# After code changes
sudo systemctl stop aicamera_v1.3.service
sudo rm -f /tmp/aicamera.sock  # Remove old socket
sudo systemctl start aicamera_v1.3.service
sudo systemctl status aicamera_v1.3.service
```

### 14.2 Import Validation
```python
# Always run after adding new modules
python3 -c "from v1_3.src.core.utils.import_helper import validate_imports; print('Import validation:', validate_imports())"
```

### 14.3 Static Files Update
```bash
# After updating CSS/JS files
sudo systemctl reload nginx
# Check browser cache - may need hard refresh
```

## 15. Version Control and Documentation

### 15.1 Code Comments Standards
```python
# MANDATORY: Document all new functions/classes
def new_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dict containing result data
    
    Raises:
        ValueError: If parameters are invalid
    """
```

### 15.2 Change Documentation
```markdown
# Always update relevant documentation files:
- ARCHITECTURE.md: For structural changes
- README.md: For feature changes
- variable_management.md: For API changes
- CONTEXT_ENGINEERING.md: For new patterns
```

---

## Summary for AI Assistants

When generating code for AI Camera v1.3:

1. **ALWAYS use absolute imports**: `from v1_3.src.* import ...`
2. **ALWAYS use dependency injection**: `get_service('service_name')`
3. **ALWAYS follow variable naming**: snake_case (Python), camelCase (JS), kebab-case (HTML IDs)
4. **ALWAYS include error handling**: try/catch blocks with logging
5. **ALWAYS set `use_socketio = true`** for WebSocket-enabled templates
6. **ALWAYS use static path**: `v1_3/src/web/static/`
7. **ALWAYS register new services** in DI container
8. **ALWAYS register new blueprints** in `__init__.py`
9. **ALWAYS use AICameraUtils** for common frontend functions
10. **ALWAYS validate imports** after changes

This document ensures consistency and prevents conflicts in AI Camera v1.3 development.
