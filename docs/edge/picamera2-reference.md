# Picamera2 Metadata Reference

## Overview
This document provides a comprehensive reference of all metadata extracted from Picamera2 in the AI Camera v1.3 system. The metadata is collected event-based (on initialization and configuration changes) to optimize CPU performance.

## Metadata Categories

### 1. Camera Properties (`camera_properties`)
Hardware information and capabilities of the camera sensor.

**Example:**
```json
{
  "Model": "imx708",
  "PixelArrayActiveAreas": [[0, 0, 4608, 2592]],
  "ScalerCropMaximum": [0, 0, 4608, 2592],
  "ScalerCropMinimum": [0, 0, 32, 32],
  "SensorBlackLevels": [4096, 4096, 4096, 4096],
  "SensorTestPatternModes": [],
  "AeEnable": true,
  "AfEnable": true,
  "AwbEnable": true
}
```

### 2. Sensor Modes (`available_modes`)
All available camera configurations and resolutions.

**Example:**
```json
[
  {
    "size": [4608, 2592],
    "bit_depth": 10,
    "unpacked": "BGGR10_CSI2P",
    "crop_limits": [0, 0, 4608, 2592]
  },
  {
    "size": [2304, 1296],
    "bit_depth": 10,
    "unpacked": "BGGR10_CSI2P",
    "crop_limits": [0, 0, 2304, 1296]
  }
]
```

### 3. Current Configuration (`current_config`)
Active camera settings and stream configurations.

**Example:**
```json
{
  "main": {
    "size": [1920, 1080],
    "format": "XBGR8888",
    "stride": 7680,
    "frame_size": 8294400,
    "buffer_size": 8294400,
    "controls": {
      "FrameDurationLimits": [33333, 33333],
      "ScalerCrop": [0, 0, 4608, 2592],
      "SensorExposureTime": 16666,
      "SensorAnalogueGain": 1.0
    }
  },
  "lores": {
    "size": [640, 480],
    "format": "XBGR8888",
    "stride": 2560,
    "frame_size": 1228800,
    "buffer_size": 1228800
  }
}
```

### 4. Camera Controls (`camera_controls`)
Available camera controls and their current values.

**Example:**
```json
{
  "AeEnable": true,
  "AfEnable": true,
  "AwbEnable": true,
  "FrameDurationLimits": [33333, 33333],
  "ScalerCrop": [0, 0, 4608, 2592],
  "SensorExposureTime": 16666,
  "SensorAnalogueGain": 1.0,
  "ColourGains": [1.0, 1.0],
  "ColourTemperature": 6500
}
```

### 5. Frame Metadata (`frame_metadata`)
Real-time frame information (when streaming).

**Example:**
```json
{
  "SensorTimestamp": 1234567890,
  "FrameDuration": 33333,
  "ScalerCrop": [0, 0, 4608, 2592],
  "SensorExposureTime": 16666,
  "SensorAnalogueGain": 1.0,
  "ColourGains": [1.0, 1.0],
  "ColourTemperature": 6500,
  "FocusFoM": 100,
  "AfState": "Focused"
}
```

### 6. Camera Status (`camera_status`)
Current camera operational status.

**Example:**
```json
{
  "initialized": true,
  "streaming": true,
  "recording": false
}
```

### 7. Frame Statistics (`frame_statistics`)
Internal frame processing statistics.

**Example:**
```json
{
  "frame_count": 1500,
  "average_fps": 30.2,
  "last_frame_time": 1234567890.123
}
```

### 8. Configuration Details (`configuration_details`)
Detailed camera configuration information.

**Example:**
```json
{
  "main": {
    "size": [1920, 1080],
    "format": "XBGR8888",
    "stride": 7680,
    "frame_size": 8294400,
    "buffer_size": 8294400,
    "controls": {
      "FrameDurationLimits": [33333, 33333],
      "ScalerCrop": [0, 0, 4608, 2592]
    }
  }
}
```

### 9. Stream Information (`streams`)
Stream configurations and properties.

**Example:**
```json
{
  "main": {
    "size": [1920, 1080],
    "format": "XBGR8888",
    "stride": 7680,
    "frame_size": 8294400
  },
  "lores": {
    "size": [640, 480],
    "format": "XBGR8888",
    "stride": 2560,
    "frame_size": 1228800
  }
}
```

### 10. Camera Config (`camera_config`)
Device-specific configuration details.

**Example:**
```json
{
  "sensor": {
    "model": "imx708",
    "resolution": [4608, 2592],
    "bit_depth": 10
  },
  "isp": {
    "enabled": true,
    "format": "XBGR8888"
  }
}
```

### 11. Metadata Timestamp (`metadata_timestamp`)
When the metadata was collected.

**Example:**
```json
{
  "metadata_timestamp": 1234567890.123
}
```

## Metadata Collection Events

### Initialization Event
Metadata is collected when the camera is first initialized:
- Camera properties
- Sensor modes
- Initial configuration
- Camera controls
- Camera status

### Configuration Change Event
Metadata is updated when camera configuration changes:
- Current configuration
- Camera controls
- Configuration details
- Stream information
- Frame metadata (if streaming)

### Manual Refresh
Metadata can be manually refreshed via:
- API endpoint: `GET /api/camera/status`
- WebSocket event: `camera_status_request`
- UI refresh button in metadata viewer

## Performance Optimization

### Event-Based Updates
- **No periodic polling**: Eliminates background threads
- **CPU efficient**: Updates only when needed
- **Reduced overhead**: Minimal impact on camera performance
- **Responsive**: Immediate updates on configuration changes

### Memory Management
- **JSON serializable**: All metadata converted to web-safe format
- **Structured storage**: Organized by category for easy access
- **Timestamp tracking**: Know when metadata was last updated
- **Error handling**: Graceful degradation when metadata unavailable

## Usage Examples

### API Access
```bash
# Get camera status with metadata
curl http://localhost:5000/api/camera/status

# Response includes comprehensive metadata
{
  "initialized": true,
  "streaming": true,
  "metadata": {
    "camera_properties": {...},
    "available_modes": [...],
    "current_config": {...},
    "camera_controls": {...},
    "frame_metadata": {...},
    "camera_status": {...},
    "frame_statistics": {...},
    "configuration_details": {...},
    "streams": {...},
    "camera_config": {...},
    "metadata_timestamp": 1234567890.123
  }
}
```

### WebSocket Events
```javascript
// Listen for metadata updates
socket.on('camera_status_update', (status) => {
  if (status.metadata) {
    console.log('Camera metadata updated:', status.metadata);
    // Update UI with new metadata
  }
});

// Request metadata update
socket.emit('camera_status_request');
```

### Metadata Viewer
Access the comprehensive metadata viewer at:
```
/camera/metadata
```

Features:
- Organized display of all metadata categories
- Export functionality for debugging
- Real-time updates via WebSocket
- Responsive design for mobile devices

## Debugging and Troubleshooting

### Common Metadata Issues
1. **Missing frame metadata**: Camera not streaming
2. **Empty camera properties**: Camera not initialized
3. **No sensor modes**: Camera hardware issue
4. **Stale metadata**: Check timestamp for freshness

### Debug Commands
```python
# Force metadata update
camera_manager._update_metadata()

# Check metadata freshness
metadata = camera_manager.last_metadata
timestamp = metadata.get('metadata_timestamp', 0)
age = time.time() - timestamp
print(f"Metadata age: {age} seconds")

# Export metadata for analysis
import json
with open('camera_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
```

## Integration Points

### Dashboard Display
- Resolution and frame rate from metadata
- Sensor model information
- Camera status indicators
- Fallback to configuration data

### Health Monitoring
- Camera initialization status
- Streaming status
- Hardware capabilities
- Configuration validation

### Configuration Management
- Available sensor modes
- Current settings
- Control limits
- Format compatibility

This comprehensive metadata system provides complete visibility into the camera's state and capabilities while maintaining optimal performance through event-based updates.
