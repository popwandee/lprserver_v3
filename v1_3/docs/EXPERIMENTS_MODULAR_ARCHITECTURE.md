# AI Camera v1.3.2 - Experiments Modular Architecture

## Overview

The Experiments component is designed as a **truly modular** component that can be completely removed from the system without affecting core functionality. This document explains the modular architecture and how to enable/disable the experiments feature.

## Modular Design Principles

### 1. **Zero Dependencies on Core Modules**
- Experiments component does not depend on Camera, Detection, or Health modules
- Can function independently when core modules are unavailable
- Uses its own service layer without coupling to existing services

### 2. **Conditional Registration**
- Service registration is controlled by `EXPERIMENT_ENABLED` configuration
- Blueprint registration is conditional and can be disabled
- Navigation menu items are conditionally rendered

### 3. **Graceful Degradation**
- System continues to function normally when experiments are disabled
- No error messages or broken links when experiments are unavailable
- Clean separation between core and optional functionality

## Configuration Control

### Environment Variables

```bash
# Enable/Disable Experiments (default: true)
EXPERIMENT_ENABLED="true"

# Auto-save experiment results (default: true)
EXPERIMENT_AUTO_SAVE="true"

# Maximum retries for failed steps (default: 3)
EXPERIMENT_MAX_RETRIES="3"
```

### Configuration File

```python
# v1_3/src/core/config.py
EXPERIMENT_ENABLED = os.getenv('EXPERIMENT_ENABLED', 'true').lower() == 'true'
EXPERIMENT_AUTO_SAVE = os.getenv('EXPERIMENT_AUTO_SAVE', 'true').lower() == 'true'
EXPERIMENT_MAX_RETRIES = int(os.getenv('EXPERIMENT_MAX_RETRIES', '3'))
```

## Architecture Components

### 1. **Dependency Container Integration**

```python
# v1_3/src/core/dependency_container.py
# Experiment Service (Optional)
if EXPERIMENT_ENABLED:
    try:
        from v1_3.src.services.experiment_service import ExperimentService
        self.register_service('experiment_service', ExperimentService, 
                            singleton=True, dependencies={'logger': 'logger'})
        self.logger.info("Experiment Service registered (enabled in config)")
    except ImportError:
        self.logger.warning("ExperimentService not available")
else:
    self.logger.info("Experiment Service not registered (disabled in config)")
```

**Key Points:**
- Service registration is conditional on `EXPERIMENT_ENABLED`
- Only depends on logger (core infrastructure)
- Graceful handling of import errors
- Clear logging of registration status

### 2. **Blueprint Registration**

```python
# v1_3/src/web/blueprints/__init__.py
# Import experiments blueprint (optional)
experiments_bp = None
register_experiment_events = None
if EXPERIMENT_ENABLED:
    try:
        from v1_3.src.web.blueprints.experiments import experiments_bp, register_experiment_events
        logger.info("Experiments blueprint imported (enabled in config)")
    except ImportError:
        logger.warning("Experiments blueprint not available")
else:
    logger.info("Experiments blueprint not imported (disabled in config)")

# Registration
if experiments_bp and EXPERIMENT_ENABLED:
    app.register_blueprint(experiments_bp)
    logger.info("   ✅ Experiments blueprint registered (enabled)")
else:
    logger.info("   ℹ️ Experiments blueprint not registered (disabled/not available)")
```

**Key Points:**
- Import is conditional on configuration
- Blueprint registration is conditional
- WebSocket events are conditional
- Clear status logging

### 3. **Navigation Integration**

```html
<!-- v1_3/src/web/templates/base.html -->
{% if config.get('EXPERIMENT_ENABLED', true) %}
<li class="nav-item">
    <a class="nav-link {% if active_page == 'experiments' %}active{% endif %}" href="/experiments">
        <i class="fas fa-flask"></i> Experiments
    </a>
</li>
{% endif %}
```

**Key Points:**
- Menu item is conditionally rendered
- Uses configuration context
- No broken links when disabled

### 4. **Service Independence**

```python
# v1_3/src/services/experiment_service.py
class ExperimentService:
    def __init__(self, app_config: Optional[Dict[str, Any]] = None):
        # No dependencies on other services
        # Self-contained functionality
        # Uses only core infrastructure (logger, config)
```

**Key Points:**
- No imports of other services
- Self-contained business logic
- Uses only core infrastructure

## Enabling/Disabling Experiments

### Method 1: Environment Variable

```bash
# Disable experiments
export EXPERIMENT_ENABLED=false

# Enable experiments (default)
export EXPERIMENT_ENABLED=true
```

### Method 2: Environment File

```bash
# Edit .env.production
EXPERIMENT_ENABLED="false"
```

### Method 3: Runtime Configuration

```python
# In your application code
import os
os.environ['EXPERIMENT_ENABLED'] = 'false'
```

## Verification of Modularity

### 1. **Service Independence Test**

```python
# Test that experiments work without core services
def test_experiment_independence():
    # Disable core services
    os.environ['AUTO_START_CAMERA'] = 'false'
    os.environ['AUTO_START_DETECTION'] = 'false'
    
    # Enable experiments
    os.environ['EXPERIMENT_ENABLED'] = 'true'
    
    # Experiments should still work
    experiment_service = ExperimentService()
    assert experiment_service is not None
```

### 2. **System Functionality Test**

```python
# Test that system works without experiments
def test_system_without_experiments():
    # Disable experiments
    os.environ['EXPERIMENT_ENABLED'] = 'false'
    
    # Core functionality should still work
    camera_service = get_service('camera_manager')
    detection_service = get_service('detection_manager')
    
    assert camera_service is not None
    assert detection_service is not None
```

### 3. **Blueprint Availability Test**

```python
# Test blueprint registration
def test_blueprint_registration():
    # With experiments enabled
    os.environ['EXPERIMENT_ENABLED'] = 'true'
    app = create_app()
    assert 'experiments' in [bp.name for bp in app.blueprints.values()]
    
    # With experiments disabled
    os.environ['EXPERIMENT_ENABLED'] = 'false'
    app = create_app()
    assert 'experiments' not in [bp.name for bp in app.blueprints.values()]
```

## Benefits of Modular Design

### 1. **Deployment Flexibility**
- Can deploy with or without experiments
- Reduces system complexity when not needed
- Allows for different deployment configurations

### 2. **Development Isolation**
- Experiments can be developed independently
- No risk of breaking core functionality
- Easier testing and debugging

### 3. **Resource Management**
- Can disable experiments to save resources
- Reduces memory and CPU usage when not needed
- Cleaner system architecture

### 4. **Maintenance**
- Easier to maintain and update
- Clear separation of concerns
- Reduced coupling between components

## Troubleshooting

### Common Issues

#### 1. **Experiments Not Available**
```bash
# Check configuration
echo $EXPERIMENT_ENABLED

# Check logs for registration status
grep "Experiment" logs/app.log
```

#### 2. **Import Errors**
```bash
# Check if experiment files exist
ls -la v1_3/src/services/experiment_service.py
ls -la v1_3/src/web/blueprints/experiments.py
```

#### 3. **Navigation Issues**
```html
<!-- Check if menu item is rendered -->
<!-- View page source and look for experiments menu -->
```

### Debug Commands

```bash
# Check experiment service status
python3 -c "
from v1_3.src.core.dependency_container import get_service
try:
    service = get_service('experiment_service')
    print('Experiment service available')
except:
    print('Experiment service not available')
"

# Check blueprint registration
python3 -c "
from v1_3.src.app import create_app
app = create_app()
print('Registered blueprints:', [bp.name for bp in app.blueprints.values()])
"
```

## Migration Guide

### From v1.3.1 to v1.3.2

1. **No Breaking Changes**: Core functionality remains unchanged
2. **Optional Feature**: Experiments are disabled by default
3. **Configuration**: Add experiment configuration to `.env.production`
4. **Dependencies**: Install additional requirements if using experiments

### Enabling Experiments in Existing Installation

```bash
# 1. Update configuration
echo 'EXPERIMENT_ENABLED="true"' >> .env.production

# 2. Install dependencies
pip install scikit-image==0.21.0

# 3. Restart application
sudo systemctl restart aicamera_v1.3

# 4. Verify
curl http://localhost/experiments/
```

## Conclusion

The Experiments component demonstrates true modular architecture by:

1. **Zero Dependencies**: No coupling to core modules
2. **Conditional Registration**: Can be completely disabled
3. **Graceful Degradation**: System works normally without it
4. **Clean Separation**: Clear boundaries between core and optional features

This design ensures that the AI Camera system remains robust and maintainable while providing the flexibility to add or remove experimental features as needed.

---

**Author**: AI Camera Team  
**Version**: 1.3.2  
**Date**: August 10, 2025
