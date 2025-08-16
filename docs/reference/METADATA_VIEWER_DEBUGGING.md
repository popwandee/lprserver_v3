# Metadata Viewer Debugging Guide

## Issue: 500 Internal Server Error

If you're getting a 500 error when accessing `/camera/metadata`, follow these debugging steps:

## Step 1: Check Service Availability

Test if the camera manager service is available:

```bash
# Test the camera service endpoint
curl http://localhost:5000/camera/test

# Expected response if working:
{
  "success": true,
  "message": "Camera manager service is available",
  "service_type": "CameraManager",
  "timestamp": "2025-01-XX..."
}

# If you get an error, the service is not properly registered
```

## Step 2: Check Application Logs

Look for error messages in the application logs:

```bash
# Check the application logs for errors
tail -f /path/to/your/app.log

# Look for these specific error messages:
# - "Camera manager not available in metadata viewer"
# - "Service not registered in metadata viewer"
# - "Error in camera metadata viewer"
```

## Step 3: Verify Dependency Injection

Check if the dependency injection container is properly initialized:

```python
# In Python console or debug script
from v1_3.src.core.dependency_container import get_service, get_container

# Check if container is initialized
container = get_container()
print(f"Container: {container}")

# Check registered services
services = container.get_registered_services()
print(f"Registered services: {list(services.keys())}")

# Try to get camera manager
try:
    camera_manager = get_service('camera_manager')
    print(f"Camera manager: {camera_manager}")
except Exception as e:
    print(f"Error getting camera manager: {e}")
```

## Step 4: Check Camera Manager Initialization

Verify that the camera manager was properly initialized:

```python
# Check camera manager status
camera_manager = get_service('camera_manager')
if camera_manager:
    status = camera_manager.get_status()
    print(f"Camera status: {status}")
else:
    print("Camera manager not available")
```

## Step 5: Common Issues and Solutions

### Issue 1: Service Not Registered
**Error**: `KeyError: 'camera_manager'`

**Solution**: 
- Check if the application was started properly
- Verify that the dependency injection container is initialized
- Restart the application

### Issue 2: Camera Handler Not Available
**Error**: `Camera handler not available`

**Solution**:
- Check if the camera hardware is connected
- Verify camera permissions
- Check if camera modules are loaded

### Issue 3: Import Errors
**Error**: `ImportError` or `ModuleNotFoundError`

**Solution**:
- Check Python path and imports
- Verify all required packages are installed
- Check file permissions

## Step 6: Manual Testing

Test the metadata viewer step by step:

1. **Test basic route**:
   ```bash
   curl http://localhost:5000/camera/metadata
   ```

2. **Test camera status**:
   ```bash
   curl http://localhost:5000/camera/status
   ```

3. **Test camera dashboard**:
   ```bash
   curl http://localhost:5000/camera/
   ```

## Step 7: Alternative Access Methods

If the metadata viewer still doesn't work, you can access metadata through:

1. **API endpoint**: `GET /camera/status`
2. **WebSocket**: Listen for `camera_status_update` events
3. **Direct service call**: Use the camera manager service directly

## Step 8: Fallback Debugging

If all else fails, add debug logging:

```python
# Add to the metadata viewer route
import traceback

@camera_bp.route('/metadata')
def camera_metadata_viewer():
    try:
        logger.info("Starting metadata viewer...")
        
        # Test dependency injection
        logger.info("Testing dependency injection...")
        camera_manager = get_service('camera_manager')
        logger.info(f"Camera manager: {camera_manager}")
        
        if not camera_manager:
            logger.error("Camera manager is None")
            return render_template('camera/metadata_viewer.html',
                                 camera_status={'error': 'Camera manager is None'},
                                 title="Camera Metadata Viewer")
        
        # Test status retrieval
        logger.info("Getting camera status...")
        camera_status = camera_manager.get_status()
        logger.info(f"Camera status keys: {list(camera_status.keys())}")
        
        return render_template('camera/metadata_viewer.html',
                             camera_status=camera_status,
                             title="Camera Metadata Viewer")
    except Exception as e:
        logger.error(f"Error in metadata viewer: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return render_template('camera/metadata_viewer.html',
                             camera_status={'error': str(e)},
                             title="Camera Metadata Viewer")
```

## Step 9: Check System Requirements

Ensure your system meets the requirements:

1. **Hardware**: Camera module connected
2. **Software**: Picamera2 installed and working
3. **Permissions**: Camera access permissions
4. **Dependencies**: All Python packages installed

## Step 10: Reset and Restart

If nothing else works:

1. **Stop the application**
2. **Clear any cached data**
3. **Restart the application**
4. **Check logs for initialization errors**

## Quick Fix Commands

```bash
# Restart the application
sudo systemctl restart your-app-service

# Check camera hardware
ls /dev/video*
ls /dev/media*

# Check camera modules
lsmod | grep camera

# Test camera manually
python3 -c "from picamera2 import Picamera2; print('Camera available')"
```

## Contact Support

If you're still experiencing issues:

1. **Collect logs**: Application logs, system logs
2. **System info**: OS version, Python version, hardware info
3. **Error details**: Exact error messages and stack traces
4. **Steps to reproduce**: Detailed steps that cause the error

This debugging guide should help identify and resolve the 500 error with the metadata viewer.
