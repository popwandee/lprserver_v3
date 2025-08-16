# AI Camera v1.3 - Variable Conflict Prevention Guide

## Overview

เอกสารนี้เป็นแนวทางสำคัญในการป้องกันปัญหา Variable Conflicts และ Naming Inconsistencies ที่เกิดขึ้นในระบบ AI Camera v1.3

**Created:** August 9, 2025  
**Last Updated:** August 9, 2025  
**Version:** 1.3

## 📋 Table of Contents

1. [Naming Convention Standards](#naming-convention-standards)
2. [Layer-Specific Variable Mapping](#layer-specific-variable-mapping)
3. [Common Conflict Scenarios](#common-conflict-scenarios)
4. [Prevention Strategies](#prevention-strategies)
5. [Testing & Validation](#testing--validation)
6. [Quick Reference](#quick-reference)

---

## 🏗️ Naming Convention Standards

### 1. Backend (Python) - `snake_case`

```python
# ✅ Correct
camera_status = {
    'initialized': True,
    'streaming': True,
    'frame_count': 1234,
    'average_fps': 29.5,
    'auto_start_enabled': True
}

detection_processor_status = {
    'models_loaded': True,
    'vehicle_model_available': True,
    'lp_detection_model_available': True
}

# ❌ Incorrect
cameraStatus = {...}  # camelCase in Python
CameraStatus = {...}  # PascalCase for variables
camera-status = {...}  # kebab-case in Python
```

### 2. Frontend (JavaScript) - `camelCase`

```javascript
// ✅ Correct
const cameraStatus = {
    initialized: true,
    streaming: true,
    frameCount: 1234,
    averageFps: 29.5,
    autoStartEnabled: true
};

const detectionProcessorStatus = {
    modelsLoaded: true,
    vehicleModelAvailable: true,
    lpDetectionModelAvailable: true
};

// ❌ Incorrect
const camera_status = {...};  // snake_case in JavaScript
const CameraStatus = {...};   // PascalCase for variables
const camera-status = {...};  // kebab-case in JavaScript
```

### 3. HTML Elements - `kebab-case`

```html
<!-- ✅ Correct -->
<span id="main-camera-model">Loading...</span>
<span id="feature-camera-resolution">Loading...</span>
<div class="status-online">Online</div>
<button id="camera-start-btn">Start</button>

<!-- ❌ Incorrect -->
<span id="mainCameraModel">Loading...</span>  <!-- camelCase -->
<span id="main_camera_model">Loading...</span>  <!-- snake_case -->
<div class="statusOnline">Online</div>  <!-- camelCase -->
```

### 4. API Endpoints - `snake_case`

```
✅ Correct:
GET /camera/status
POST /detection/start
GET /health/system

❌ Incorrect:
GET /camera/getStatus
POST /detection/startDetection
GET /health/getSystemHealth
```

### 5. WebSocket Events - `snake_case`

```javascript
// ✅ Correct
socket.emit('camera_status_request', {});
socket.on('camera_status_update', callback);
socket.emit('detection_control', {command: 'start'});

// ❌ Incorrect
socket.emit('cameraStatusRequest', {});  // camelCase
socket.on('camera-status-update', callback);  // kebab-case
```

---

## 🔄 Layer-Specific Variable Mapping

### Backend → Frontend Data Flow

```python
# Backend (Python) - snake_case
api_response = {
    "success": True,
    "status": {
        "camera_handler": {
            "current_config": {
                "main": {
                    "size": [1280, 720]
                },
                "controls": {
                    "FrameDurationLimits": [33333, 33333]
                }
            },
            "camera_properties": {
                "Model": "imx708"
            }
        }
    }
}
```

```javascript
// Frontend (JavaScript) - Access with camelCase conversion
function updateCameraStatus(status) {
    // Direct access (structure preserved)
    const resolution = status.camera_handler.current_config.main.size;
    const model = status.camera_handler.camera_properties.Model;
    const frameDuration = status.camera_handler.current_config.controls.FrameDurationLimits[0];
    
    // Convert to display format
    const resolutionText = `${resolution[0]}x${resolution[1]}`;
    const fpsText = `${Math.round(1000000 / frameDuration)} FPS`;
    
    // Update DOM elements
    document.getElementById('main-camera-resolution').textContent = resolutionText;
    document.getElementById('main-camera-fps').textContent = fpsText;
    document.getElementById('main-camera-model').textContent = model;
}
```

### HTML Element ID Mapping

```javascript
// ✅ Correct - Unique IDs for different sections
const ELEMENT_IDS = {
    // Main System Information section
    MAIN_CAMERA_MODEL: 'main-camera-model',
    MAIN_CAMERA_RESOLUTION: 'main-camera-resolution',
    MAIN_CAMERA_FPS: 'main-camera-fps',
    
    // Features section (different data, different IDs)
    FEATURE_CAMERA_MODEL: 'feature-camera-model',
    FEATURE_CAMERA_RESOLUTION: 'feature-camera-resolution',
    FEATURE_CAMERA_FPS: 'feature-camera-fps',
    
    // Status indicators
    MAIN_CAMERA_STATUS: 'main-camera-status',
    MAIN_CAMERA_DETAIL_STATUS: 'main-camera-detail-status',
    MAIN_CAMERA_FEATURE_STATUS: 'main-camera-feature-status'
};

// ❌ Wrong - Duplicate IDs cause conflicts
// Both sections using same IDs:
// 'main-camera-model' appears twice → only first gets updated
```

---

## ⚠️ Common Conflict Scenarios

### 1. Duplicate HTML Element IDs

**Problem:**
```html
<!-- System Information section -->
<span id="main-camera-model">Loading...</span>

<!-- Features section -->  
<span id="main-camera-model">Loading...</span>  <!-- ❌ Duplicate ID -->
```

**Solution:**
```html
<!-- System Information section -->
<span id="main-camera-model">Loading...</span>

<!-- Features section -->
<span id="feature-camera-model">Loading...</span>  <!-- ✅ Unique ID -->
```

### 2. Inconsistent Variable Naming Across Layers

**Problem:**
```python
# Backend
camera_status = {'frame_count': 1234}

# Frontend expects camelCase but receives snake_case
const frameCount = status.frameCount;  // ❌ undefined
```

**Solution:**
```python
# Backend - Keep snake_case
camera_status = {'frame_count': 1234}

# Frontend - Access with original structure
const frameCount = status.frame_count;  // ✅ Works
// OR convert if needed
const frameCount = status.frameCount || status.frame_count;
```

### 3. WebSocket Event Name Mismatches

**Problem:**
```javascript
// Client sends camelCase
socket.emit('cameraStatusRequest', {});

// Server expects snake_case
@socketio.on('camera_status_request')  // ❌ Mismatch
```

**Solution:**
```javascript
// Client uses snake_case
socket.emit('camera_status_request', {});  // ✅ Matches server

// Server handles snake_case
@socketio.on('camera_status_request')  // ✅ Matches client
```

### 4. CSS Class Naming Conflicts

**Problem:**
```css
/* Bootstrap uses kebab-case */
.btn-primary { ... }

/* Custom classes use camelCase */
.statusOnline { ... }  /* ❌ Inconsistent */
```

**Solution:**
```css
/* All classes use kebab-case */
.btn-primary { ... }
.status-online { ... }  /* ✅ Consistent */
```

---

## 🛡️ Prevention Strategies

### 1. Code Review Checklist

**Backend (Python):**
- [ ] All variables use `snake_case`
- [ ] API responses follow `variable_management.md` format
- [ ] WebSocket events use `snake_case` naming
- [ ] Database columns use `snake_case`
- [ ] No camelCase or kebab-case in Python code

**Frontend (JavaScript):**
- [ ] All variables use `camelCase`
- [ ] API data accessed with original structure
- [ ] WebSocket events use `snake_case` (server compatibility)
- [ ] No snake_case variables in JavaScript
- [ ] Consistent property access patterns

**HTML Templates:**
- [ ] All element IDs use `kebab-case`
- [ ] No duplicate IDs in same page
- [ ] CSS classes use `kebab-case`
- [ ] Semantic and descriptive naming
- [ ] Section prefixes for organization

### 2. Automated Validation

**ESLint Rules (JavaScript):**
```javascript
// .eslintrc.js
module.exports = {
    rules: {
        'camelcase': ['error', { properties: 'always' }],
        'id-match': ['error', '^[a-z][a-zA-Z0-9]*$', { 
            properties: true,
            onlyDeclarations: false
        }]
    }
};
```

**Python Linting (pylint/flake8):**
```python
# .pylintrc
[MESSAGES CONTROL]
enable = invalid-name

[BASIC]
variable-rgx = ^[a-z_][a-z0-9_]{2,30}$
```

**HTML Validation Script:**
```bash
#!/bin/bash
# check_duplicate_ids.sh
echo "Checking for duplicate HTML IDs..."
grep -r 'id="' v1_3/src/web/templates/ | \
  sed 's/.*id="\([^"]*\)".*/\1/' | \
  sort | uniq -d
```

### 3. Development Guidelines

**API Development:**
1. Always follow `variable_management.md` standards
2. Use consistent response structures
3. Include timestamp in all responses
4. Validate input parameter naming
5. Test with frontend integration

**Frontend Development:**
1. Use `AICameraUtils` for common operations
2. Follow camelCase for all JavaScript variables
3. Access API data with original structure
4. Create unique element IDs with prefixes
5. Test WebSocket event compatibility

**Template Development:**
1. Use semantic, descriptive element IDs
2. Apply consistent CSS class naming
3. Avoid duplicate IDs across templates
4. Use section prefixes for organization
5. Follow Bootstrap conventions

### 4. Testing Strategies

**Unit Tests:**
```python
# test_variable_naming.py
def test_api_response_format():
    response = camera_manager.get_status()
    assert 'frame_count' in response  # snake_case
    assert 'frameCount' not in response  # no camelCase
    
def test_websocket_event_names():
    events = get_registered_events()
    assert 'camera_status_request' in events
    assert 'cameraStatusRequest' not in events
```

```javascript
// test_frontend_variables.js
describe('Variable Naming', () => {
    test('should use camelCase for JavaScript variables', () => {
        const status = { frameCount: 100 };
        expect(status.frameCount).toBeDefined();
        expect(status.frame_count).toBeUndefined();
    });
    
    test('should access API data correctly', () => {
        const apiResponse = { frame_count: 100 };  // from API
        const frameCount = apiResponse.frame_count;  // direct access
        expect(frameCount).toBe(100);
    });
});
```

**Integration Tests:**
```javascript
// test_api_integration.js
describe('API Integration', () => {
    test('camera status API returns correct structure', async () => {
        const response = await fetch('/camera/status');
        const data = await response.json();
        
        expect(data.status.frame_count).toBeDefined();
        expect(data.status.camera_handler.current_config.main.size).toBeDefined();
        expect(data.status.camera_handler.camera_properties.Model).toBeDefined();
    });
});
```

---

## 🧪 Testing & Validation

### 1. Pre-deployment Checklist

**API Endpoints:**
- [ ] All endpoints return consistent response format
- [ ] Variable names follow snake_case convention
- [ ] No camelCase in API responses
- [ ] Timestamp format is ISO 8601
- [ ] Error responses include error_code

**Frontend Integration:**
- [ ] JavaScript variables use camelCase
- [ ] API data accessed correctly
- [ ] WebSocket events work bidirectionally
- [ ] No undefined variable errors
- [ ] DOM elements update correctly

**HTML Templates:**
- [ ] No duplicate element IDs
- [ ] CSS classes use kebab-case
- [ ] Element IDs are descriptive
- [ ] Bootstrap compatibility maintained
- [ ] Cross-browser compatibility tested

### 2. Validation Scripts

**Backend Validation:**
```python
#!/usr/bin/env python3
# validate_backend_naming.py

import re
import json
from v1_3.src.web.blueprints.camera import camera_bp

def validate_api_responses():
    """Validate all API responses use snake_case"""
    errors = []
    
    # Test camera status endpoint
    with camera_bp.test_client() as client:
        response = client.get('/camera/status')
        data = json.loads(response.data)
        
        if 'frameCount' in str(data):
            errors.append("Found camelCase in camera status API")
        
        if 'frame_count' not in str(data):
            errors.append("Missing snake_case variables in camera status API")
    
    return errors

if __name__ == "__main__":
    errors = validate_api_responses()
    if errors:
        print("❌ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("✅ Backend naming validation passed")
```

**Frontend Validation:**
```javascript
// validate_frontend_naming.js

function validateJavaScriptNaming() {
    const errors = [];
    
    // Check for snake_case in JavaScript (should be camelCase)
    const jsFiles = ['dashboard.js', 'camera.js', 'detection.js'];
    
    jsFiles.forEach(file => {
        const content = fs.readFileSync(`/path/to/${file}`, 'utf8');
        
        // Look for snake_case variable declarations
        const snakeCasePattern = /(?:const|let|var)\s+[a-z]+_[a-z]/g;
        const matches = content.match(snakeCasePattern);
        
        if (matches) {
            errors.push(`Found snake_case variables in ${file}: ${matches.join(', ')}`);
        }
    });
    
    return errors;
}

function validateElementIds() {
    const errors = [];
    const htmlFiles = glob.sync('v1_3/src/web/templates/**/*.html');
    const allIds = [];
    
    htmlFiles.forEach(file => {
        const content = fs.readFileSync(file, 'utf8');
        const idMatches = content.match(/id="([^"]+)"/g);
        
        if (idMatches) {
            idMatches.forEach(match => {
                const id = match.match(/id="([^"]+)"/)[1];
                
                // Check for camelCase (should be kebab-case)
                if (/[a-z][A-Z]/.test(id)) {
                    errors.push(`CamelCase ID found in ${file}: ${id}`);
                }
                
                // Check for duplicates
                if (allIds.includes(id)) {
                    errors.push(`Duplicate ID found: ${id}`);
                } else {
                    allIds.push(id);
                }
            });
        }
    });
    
    return errors;
}

// Run validations
const jsErrors = validateJavaScriptNaming();
const htmlErrors = validateElementIds();

if (jsErrors.length > 0 || htmlErrors.length > 0) {
    console.log("❌ Frontend validation failed:");
    [...jsErrors, ...htmlErrors].forEach(error => console.log(`  - ${error}`));
    process.exit(1);
} else {
    console.log("✅ Frontend naming validation passed");
}
```

### 3. Continuous Integration

**GitHub Actions Workflow:**
```yaml
# .github/workflows/variable-validation.yml
name: Variable Naming Validation

on: [push, pull_request]

jobs:
  validate-naming:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: 18
    
    - name: Install dependencies
      run: |
        pip install -r v1_3/requirements.txt
        npm install -g eslint
    
    - name: Validate backend naming
      run: python3 scripts/validate_backend_naming.py
    
    - name: Validate frontend naming
      run: node scripts/validate_frontend_naming.js
    
    - name: Check for duplicate HTML IDs
      run: ./scripts/check_duplicate_ids.sh
    
    - name: Run ESLint
      run: eslint v1_3/src/web/static/js/
```

---

## 📚 Quick Reference

### Variable Naming Quick Check

| Context | Convention | Example | ✅ / ❌ |
|---------|------------|---------|---------|
| Python Variables | snake_case | `camera_status` | ✅ |
| Python Variables | camelCase | `cameraStatus` | ❌ |
| JavaScript Variables | camelCase | `cameraStatus` | ✅ |
| JavaScript Variables | snake_case | `camera_status` | ❌ |
| HTML Element IDs | kebab-case | `main-camera-status` | ✅ |
| HTML Element IDs | camelCase | `mainCameraStatus` | ❌ |
| CSS Classes | kebab-case | `status-online` | ✅ |
| CSS Classes | camelCase | `statusOnline` | ❌ |
| API Endpoints | snake_case | `/camera/status` | ✅ |
| API Endpoints | camelCase | `/camera/getStatus` | ❌ |
| WebSocket Events | snake_case | `camera_status_update` | ✅ |
| WebSocket Events | camelCase | `cameraStatusUpdate` | ❌ |

### Common Data Paths

| Data Type | Backend Path | Frontend Access | Display Element |
|-----------|--------------|-----------------|-----------------|
| **Camera Model** | `status.camera_handler.camera_properties.Model` | `status.camera_handler.camera_properties.Model` | `main-camera-model` |
| **Resolution** | `status.camera_handler.current_config.main.size` | `status.camera_handler.current_config.main.size` | `main-camera-resolution` |
| **FPS** | `status.camera_handler.current_config.controls.FrameDurationLimits[0]` | `Math.round(1000000 / status.camera_handler.current_config.controls.FrameDurationLimits[0])` | `main-camera-fps` |
| **Camera Status** | `status.streaming` | `status.streaming` | `main-camera-status` |
| **Frame Count** | `status.frame_count` | `status.frame_count` | N/A |
| **Uptime** | `status.uptime` | `AICameraUtils.formatDuration(status.uptime)` | `main-system-uptime` |

### WebSocket Event Reference

| Event Type | Client → Server | Server → Client | Data Structure |
|------------|-----------------|-----------------|----------------|
| **Camera Status** | `camera_status_request` | `camera_status_update` | Same as API response |
| **Camera Control** | `camera_control` | `camera_control_response` | `{command, success, message}` |
| **Detection Status** | `detection_status_request` | `detection_status_update` | Same as API response |
| **Detection Control** | `detection_control` | `detection_control_response` | `{command, success, message}` |
| **System Health** | `system_health_request` | `system_health_update` | Same as API response |

### Error Prevention Checklist

**Before Code Commit:**
- [ ] Run naming validation scripts
- [ ] Check for duplicate HTML IDs
- [ ] Verify API response structure
- [ ] Test WebSocket events
- [ ] Validate CSS class names
- [ ] Check cross-browser compatibility

**Before Deployment:**
- [ ] Integration tests pass
- [ ] Frontend can access all API data
- [ ] WebSocket communication works
- [ ] No console errors
- [ ] All UI elements update correctly

---

## 🔗 Related Documents

- [`variable_management.md`](variable_management.md) - Variable standards and formats
- [`api_documentation.md`](api_documentation.md) - Complete API reference
- [`ARCHITECTURE.md`](../ARCHITECTURE.md) - System architecture overview
- [`CONTEXT_ENGINEERING.md`](../CONTEXT_ENGINEERING.md) - AI code generation guidelines

---

**Remember:** Consistency is key! When in doubt, refer to this guide and existing working examples in the codebase. Prevention is always better than debugging variable conflicts after deployment.

**Last Updated:** August 9, 2025 - After resolving camera status display issues
