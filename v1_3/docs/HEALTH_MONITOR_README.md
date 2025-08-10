# Health Monitor - AI Camera v1.3

## Overview

The Health Monitor is a comprehensive system monitoring component for AI Camera v1.3 that continuously monitors the health status of various system components and provides real-time diagnostics through a web interface.

## Features

### 🔍 System Health Monitoring
- **Camera Status**: Monitors camera initialization and streaming status
- **Disk Space**: Checks available disk space for image storage
- **CPU & RAM**: Monitors system resource usage and temperature
- **Detection Models**: Verifies AI model availability and loading
- **EasyOCR**: Tests OCR library initialization and functionality
- **Database**: Checks database connectivity and performance
- **Network**: Monitors external connectivity (Google DNS, WebSocket server)

### 📊 Real-time Dashboard
- **Visual Status Cards**: Color-coded status indicators for each component
- **Progress Bars**: Visual representation of resource usage
- **Health Logs**: Detailed log of all health check results
- **WebSocket Updates**: Real-time status updates without page refresh

### 🗄️ Data Persistence
- **Health Check Logging**: All health check results stored in database
- **Historical Data**: Access to past health check results
- **Filtering**: Filter logs by status level (PASS, WARNING, FAIL)

## Architecture

### Components

```
Health Monitor Architecture
├── HealthMonitor (Component)
│   ├── check_camera()
│   ├── check_disk_space()
│   ├── check_cpu_ram()
│   ├── check_model_loading()
│   ├── check_easyocr_init()
│   ├── check_database_connection()
│   └── check_network_connectivity()
├── HealthService (Service Layer)
│   ├── get_system_health()
│   ├── get_health_logs()
│   └── start_monitoring()
└── Health Blueprint (Web Interface)
    ├── /health/system
    ├── /health/logs
    └── /health/monitor/*
```

### Data Flow

1. **HealthMonitor Component** performs individual health checks
2. **DatabaseManager** stores check results in `health_checks` table
3. **HealthService** aggregates data and provides business logic
4. **Health Blueprint** exposes REST API and WebSocket endpoints
5. **Web Dashboard** displays real-time status and historical data

## Installation & Setup

### Prerequisites

```bash
# Install required packages
pip install psutil easyocr

# Ensure database is initialized
python3 v1_3/src/app.py
```

### Configuration

The health monitor uses configuration from `v1_3/src/core/config.py`:

```python
# Health monitoring interval (in seconds)
HEALTH_CHECK_INTERVAL = 3600  # 1 hour

# Image storage directory for disk space checks
IMAGE_SAVE_DIR = "/path/to/image/storage"

# AI model paths
VEHICLE_DETECTION_MODEL = "model_name"
LICENSE_PLATE_DETECTION_MODEL = "model_name"

# EasyOCR languages
EASYOCR_LANGUAGES = ['en', 'th']
```

## Usage

### Web Interface

Access the health dashboard at: `http://your-server/health`

#### Dashboard Features:
- **Run Health Check**: Manually trigger a health check
- **Start/Stop Monitoring**: Control continuous monitoring
- **Refresh Data**: Update dashboard data
- **Filter Logs**: Filter health logs by status level

#### API Endpoints:

```http
# Get system health status
GET /health/system

# Get health logs
GET /health/logs?level=PASS&limit=100

# Get health service status
GET /health/status

# Start continuous monitoring
POST /health/monitor/start
Content-Type: application/json
{
    "interval": 60
}

# Stop continuous monitoring
POST /health/monitor/stop

# Run manual health check
POST /health/check/run
```

### Programmatic Usage

```python
from v1_3.src.core.dependency_container import get_service

# Get health service
health_service = get_service('health_service')

# Get system health
health_data = health_service.get_system_health()

# Get health logs
logs_data = health_service.get_health_logs(limit=50)

# Start monitoring
health_service.start_monitoring(interval=300)  # 5 minutes
```

## Database Schema

### health_checks Table

```sql
CREATE TABLE health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    component TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Fields:
- `id`: Unique identifier
- `timestamp`: ISO format timestamp of the check
- `component`: Component being checked (Camera, Disk Space, etc.)
- `status`: Check result (PASS, WARNING, FAIL)
- `message`: Human-readable status message
- `details`: JSON string with additional details
- `created_at`: Database insertion timestamp

## Health Check Details

### Camera Health Check
- **Checks**: Initialization status, streaming status
- **Metrics**: Frame count, average FPS
- **Status**: PASS (initialized + streaming), WARNING (initialized only), FAIL (not initialized)

### Disk Space Health Check
- **Checks**: Available space in image storage directory
- **Metrics**: Total, used, free space in GB
- **Status**: PASS (≥1GB free), FAIL (<1GB free)

### CPU & RAM Health Check
- **Checks**: CPU usage, memory usage, temperature
- **Metrics**: Usage percentages, available memory
- **Status**: PASS (<90% usage), WARNING (≥90% usage)

### Detection Models Health Check
- **Checks**: AI model file availability
- **Metrics**: Required vs available models
- **Status**: PASS (all models available), FAIL (missing models)

### EasyOCR Health Check
- **Checks**: EasyOCR library import and initialization
- **Metrics**: Supported languages, version
- **Status**: PASS (initialized), FAIL (import/init error)

### Database Health Check
- **Checks**: Database connection and query execution
- **Metrics**: Connection status, database info
- **Status**: PASS (connected + queryable), FAIL (connection/query error)

### Network Health Check
- **Checks**: Google DNS (8.8.8.8), local WebSocket server
- **Metrics**: Connectivity status for each endpoint
- **Status**: PASS (both accessible), WARNING (DNS only), FAIL (no connectivity)

## WebSocket Events

### Client to Server
```javascript
// Request health status
socket.emit('health_status_request');

// Request health logs
socket.emit('health_logs_request', {level: 'PASS', limit: 100});

// Start monitoring
socket.emit('health_monitor_start', {interval: 60});

// Stop monitoring
socket.emit('health_monitor_stop');

// Run health check
socket.emit('health_check_run');

// Join health monitoring room
socket.emit('join_health_room');

// Leave health monitoring room
socket.emit('leave_health_room');
```

### Server to Client
```javascript
// Health status update
socket.on('health_status_update', (data) => {
    // data contains comprehensive health information
});

// Health logs update
socket.on('health_logs_update', (data) => {
    // data contains filtered log entries
});

// Monitor response
socket.on('health_monitor_response', (data) => {
    // data contains operation result
});

// Health check response
socket.on('health_check_response', (data) => {
    // data contains check results
});
```

## Testing

### Run Health Monitor Tests

```bash
# Run comprehensive test suite
python3 v1_3/test_health_monitor.py
```

### Test Individual Components

```python
# Test health monitor component
from v1_3.src.components.health_monitor import HealthMonitor

health_monitor = HealthMonitor()
health_monitor.initialize()

# Run individual checks
disk_ok = health_monitor.check_disk_space()
cpu_ok = health_monitor.check_cpu_ram()

# Run comprehensive check
result = health_monitor.run_all_checks()
```

## Troubleshooting

### Common Issues

1. **Health Monitor Not Initializing**
   - Check database connection
   - Verify required packages are installed
   - Check log files for errors

2. **Health Checks Failing**
   - Verify component dependencies
   - Check file permissions for model paths
   - Ensure network connectivity

3. **Web Dashboard Not Loading**
   - Check Flask application is running
   - Verify blueprint registration
   - Check browser console for JavaScript errors

4. **WebSocket Connection Issues**
   - Verify Socket.IO is properly configured
   - Check firewall settings
   - Ensure WebSocket events are registered

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.getLogger('v1_3.src.components.health_monitor').setLevel(logging.DEBUG)
```

### Performance Monitoring

Monitor health check performance:

```python
import time

start_time = time.time()
result = health_monitor.run_all_checks()
duration = time.time() - start_time

print(f"Health check completed in {duration:.2f} seconds")
```

## API Response Examples

### System Health Response

```json
{
    "success": true,
    "health": {
        "overall_status": "healthy",
        "components": {
            "camera": {
                "status": "healthy",
                "initialized": true,
                "streaming": true,
                "last_check": "2025-08-09T18:36:57.390144"
            },
            "detection": {
                "status": "healthy",
                "models_loaded": true,
                "easyocr_available": true,
                "last_check": "2025-08-09T18:36:57.390144"
            }
        },
        "system": {
            "cpu_usage": 15.5,
            "memory_usage": {
                "used": 2.1,
                "total": 8.0,
                "percentage": 26.3
            },
            "disk_usage": {
                "used": 50.2,
                "total": 200.0,
                "percentage": 25.1
            },
            "uptime": 86400.5
        },
        "last_check": "2025-08-09T18:36:57.390144"
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

### Health Logs Response

```json
{
    "success": true,
    "data": {
        "logs": [
            {
                "timestamp": "2025-08-09T18:36:57.390144",
                "level": "PASS",
                "module": "Camera",
                "message": "Camera initialized and streaming",
                "details": "{\"initialized\": true, \"streaming\": true}"
            }
        ],
        "total_count": 1500,
        "level_filter": "PASS",
        "limit": 100
    },
    "timestamp": "2025-08-09T18:36:57.390144"
}
```

## Contributing

When adding new health checks:

1. **Add check method** to `HealthMonitor` class
2. **Update `run_all_checks()`** to include new check
3. **Add database logging** using `_log_result()`
4. **Update service layer** to handle new component
5. **Add UI components** to dashboard template
6. **Write tests** for new functionality

## License

This health monitor is part of AI Camera v1.3 and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Run the test suite to verify functionality
4. Check the API documentation for endpoint details
