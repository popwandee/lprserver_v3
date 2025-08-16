# AI Camera v1.3 Scripts Directory

This directory contains all utility scripts and test files for the AI Camera v1.3 system.

## Quick Start

To run tests and utilities, use the unified test runner:

```bash
cd /home/camuser/aicamera/v1_3/scripts
./test_runner.sh
```

## Script Categories

### 1. Test Runner
- **`test_runner.sh`** - Unified test runner with interactive menu

### 2. System Integration Tests
- **`test_auto_startup_sequence.py`** - Auto-startup sequence testing
- **`test_production_startup.py`** - Production startup testing
- **`test_frame_capture.py`** - Frame capture testing
- **`test_imports.py`** - Import validation testing

### 3. Component Tests
- **`test_detection_models.py`** - Detection models testing
- **`test_attribute_fixes.py`** - Attribute fixes testing
- **`test_status_indicator.py`** - Status indicator testing

### 4. Health Monitoring Tests
- **`test_health_monitor.py`** - Health monitor testing
- **`test_detection_health_integration.py`** - Detection-health integration
- **`test_health_detection_integration.py`** - Health-detection integration

### 5. WebSocket Tests
- **`test_websocket_client.py`** - WebSocket client testing
- **`test_websocket_server.py`** - WebSocket server testing

### 6. Database Tests
- **`test_progress_pagination.py`** - Database pagination testing
- **`insert_sample_detection_data.py`** - Insert sample data

### 7. Production Tests
- **`test_metrics_size.py`** - Metrics size testing

### 8. Utility Scripts
- **`migrate_absolute_imports.py`** - Migrate to absolute imports
- **`log_rotation.sh`** - Log rotation utility

## Usage Examples

### Running Individual Tests

```bash
# Run import validation
python3 test_imports.py

# Run health monitor test
python3 test_health_monitor.py

# Run log rotation
./log_rotation.sh
```

### Running Test Categories

```bash
# Run all system integration tests
./test_runner.sh
# Select option 1

# Run all health monitoring tests
./test_runner.sh
# Select option 3

# Run all tests
./test_runner.sh
# Select option 9
```

### Database Operations

```bash
# Insert sample detection data
python3 insert_sample_detection_data.py

# Test database pagination
python3 test_progress_pagination.py
```

### System Maintenance

```bash
# Rotate log files
./log_rotation.sh

# Migrate to absolute imports
python3 migrate_absolute_imports.py
```

## Test Runner Features

The `test_runner.sh` script provides:

1. **Interactive Menu**: Easy selection of test categories and individual tests
2. **Virtual Environment Management**: Automatic activation of venv_hailo
3. **Color-coded Output**: Clear visual feedback with colored output
4. **Test Results Summary**: Detailed reporting of passed/failed tests
5. **Error Handling**: Graceful handling of test failures
6. **Batch Testing**: Option to run all tests sequentially

## Test Categories

### System Integration Tests
Tests that verify the overall system integration and startup sequences.

### Component Tests
Tests for individual components like detection models and status indicators.

### Health Monitoring Tests
Tests for the health monitoring system and its integration with other components.

### WebSocket Tests
Tests for WebSocket communication functionality.

### Database Tests
Tests for database operations and data management.

### Production Tests
Tests specifically designed for production environment validation.

### Utility Scripts
Maintenance and utility scripts for system management.

## Environment Requirements

- Python 3.11+
- Virtual environment: `venv_hailo`
- Required packages: See `../requirements.txt`
- Hailo AI accelerator (for detection tests)
- Camera module (for camera tests)

## Troubleshooting

### Virtual Environment Issues
```bash
# Activate virtual environment manually
source ../venv_hailo/bin/activate

# Then run tests
python3 test_imports.py
```

### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh

# Check file permissions
ls -la
```

### Import Errors
```bash
# Run import validation first
python3 test_imports.py

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"
```

### Test Failures
1. Check virtual environment is activated
2. Verify all dependencies are installed
3. Check system requirements (camera, Hailo accelerator)
4. Review test output for specific error messages

## Adding New Tests

To add a new test:

1. Create the test file in this directory
2. Follow naming convention: `test_*.py`
3. Add to appropriate category in `test_runner.sh`
4. Update this README with test description

## Log Management

The `log_rotation.sh` script:
- Rotates log files when they exceed 100MB
- Keeps up to 5 backup files
- Cleans up files older than 30 days
- Can be run manually or via cron

## Cron Setup

To set up automatic log rotation:

```bash
# Edit crontab
crontab -e

# Add daily log rotation at 2 AM
0 2 * * * /home/camuser/aicamera/v1_3/scripts/log_rotation.sh
```

## Support

For issues with tests or scripts:
1. Check the test output for error messages
2. Verify system requirements are met
3. Review the main project documentation
4. Check logs in `../logs/` directory
