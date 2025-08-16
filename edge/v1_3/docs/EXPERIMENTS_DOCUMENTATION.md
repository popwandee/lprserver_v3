# AI Camera v1.3.2 - Experiments Component Documentation

## Overview

The Experiments component provides a comprehensive framework for conducting camera experiments and research in the AI Camera system. It enables systematic testing of different camera configurations, lens types, and environmental conditions to optimize license plate detection and OCR performance.

## Features

### Core Functionality
- **Experiment Configuration**: Create and manage experiment parameters
- **Automated Data Collection**: Capture images with metadata using rpicam-still
- **License Plate Detection**: Integrate with Hailo AI models for plate detection
- **OCR Processing**: Use EasyOCR for text recognition on cropped and full images
- **Image Quality Analysis**: Calculate sharpness and blur metrics
- **Results Analysis**: Generate comprehensive reports and visualizations
- **Real-time Monitoring**: Live experiment execution with WebSocket updates

### Experiment Types
1. **Night Mode Lens Comparison**: Compare lens performance in low-light conditions
2. **Day Mode Lens Comparison**: Compare lens performance in daylight
3. **Parameter Search**: Find optimal camera parameters
4. **Distance Testing**: Test detection accuracy at various distances

## Architecture

### Components

#### 1. Experiment Service (`v1_3/src/services/experiment_service.py`)
- **Purpose**: Core business logic for experiment execution
- **Key Methods**:
  - `run_experiment_step()`: Execute single experiment step
  - `summarize_results()`: Analyze and aggregate results
  - `get_available_experiments()`: List predefined experiments

#### 2. Experiments Blueprint (`v1_3/src/web/blueprints/experiments.py`)
- **Purpose**: Web interface and API endpoints
- **Routes**:
  - `/experiments/`: Dashboard
  - `/experiments/new`: Create new experiment
  - `/experiments/run/<id>`: Execute experiment
  - `/experiments/results/<id>`: View results
  - `/experiments/api/*`: REST API endpoints

#### 3. Templates (`v1_3/src/web/templates/experiments/`)
- **dashboard.html**: Experiment overview and management
- **new_experiment.html**: Experiment configuration form
- **run_experiment.html**: Real-time experiment execution
- **results.html**: Results analysis and visualization
- **error.html**: Error handling page

## Configuration

### Environment Variables
```bash
# Experiment Configuration
EXPERIMENT_RESULTS_DIR=/home/camuser/aicamera/experiment_results
EXPERIMENT_ENABLED=true
EXPERIMENT_AUTO_SAVE=true
EXPERIMENT_MAX_RETRIES=3
```

### Dependencies
```python
# Required packages
easyocr==1.7.0
scikit-image==0.21.0
opencv-python==4.8.1.78
numpy==1.24.3
degirum==1.0.0
```

## Usage

### 1. Creating an Experiment

1. Navigate to `/experiments/` in the web interface
2. Click "New Experiment"
3. Configure experiment parameters:
   - **Experiment Type**: Select from predefined types
   - **Camera Types**: Choose IMX708, IMX708Wide, IMX708NoIR
   - **Lens Covers**: Select Curve or Flat
   - **Distance Range**: Set start, end, and step distances
   - **Night Mode**: Enable for low-light testing
   - **Parameters**: Configure exposure, gain, lens position, etc.

### 2. Running an Experiment

1. From the experiment dashboard, click "Run Experiment"
2. Use the real-time interface to:
   - **Capture Images**: Manual or automatic capture
   - **Monitor Results**: View OCR text, confidence, sharpness
   - **Control Parameters**: Adjust camera settings
   - **Track Progress**: Monitor experiment completion

### 3. Analyzing Results

1. View experiment results at `/experiments/results/<id>`
2. Analyze:
   - **Summary Statistics**: Overall accuracy and performance
   - **Camera Comparison**: Performance by camera type
   - **Charts**: Visual analysis of trends
   - **Raw Data**: Detailed CSV export

## Data Collection

### CSV Structure
The experiment service logs data to `experiment_log.csv` with the following columns:

| Column | Description |
|--------|-------------|
| Timestamp | Experiment timestamp |
| ExperimentID | Unique experiment identifier |
| ExperimentType | Type of experiment |
| CameraType | Camera model used |
| LensCover | Lens cover type |
| Distance(m) | Distance in meters |
| LicenseTextCropped | OCR text from cropped image |
| LicenseTextFull | OCR text from full image |
| ConfidenceCrop | OCR confidence (cropped) |
| ConfidenceFull | OCR confidence (full) |
| SharpnessLaplacian | Image sharpness metric |
| BlurGaussian | Image blur metric |
| ExposureTime | Camera exposure time |
| AnalogueGain | Camera analog gain |
| DigitalGain | Camera digital gain |
| LensPosition | Lens focus position |
| FocusFoM | Focus figure of merit |
| AfState | Autofocus state |
| SensorTemperature | Sensor temperature |
| FrameDuration | Frame duration |
| Lux | Light level |
| ImagePath | Path to captured image |
| MetadataPath | Path to metadata file |

### Image Storage
- **Location**: `experiment_results/` directory
- **Naming**: `{timestamp}_{camera_type}_{lens_cover}_{distance}m.jpg`
- **Metadata**: JSON files with camera parameters

## API Reference

### REST Endpoints

#### GET `/experiments/api/experiments`
Get available experiment types.

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "night_mode_lens_comparison",
      "name": "Night Mode Lens Comparison",
      "description": "Compare lens performance in night mode",
      "parameters": {
        "camera_types": ["IMX708", "IMX708Wide", "IMX708NoIR"],
        "lens_covers": ["Curve", "Flat"],
        "distances": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "night_mode": true
      }
    }
  ],
  "timestamp": "2025-08-10T12:00:00.000Z"
}
```

#### POST `/experiments/api/run_step/<experiment_id>`
Execute a single experiment step.

**Request**:
```json
{
  "current_distance": 5,
  "current_camera_type": "IMX708",
  "current_lens_cover": "Curve",
  "is_night_mode": true,
  "exposure_time_us": 499989,
  "analog_gain": 16.0,
  "lens_position": 0.07,
  "sharpness": 2.0,
  "noise_reduction_mode": 0
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "timestamp": "20250810_120000",
    "image_path": "experiment_results/20250810_120000_IMX708_Curve_5m.jpg",
    "license_text_cropped": "กก 6014 อุบลราชธานี",
    "confidence_cropped": 0.95,
    "sharpness_laplacian": 245.67,
    "blur_gaussian": 12.34,
    "metadata": {
      "ExposureTime": 499989,
      "AnalogueGain": 16.0,
      "LensPosition": 0.07
    }
  },
  "timestamp": "2025-08-10T12:00:00.000Z"
}
```

#### GET `/experiments/api/summary/<experiment_id>`
Get experiment summary statistics.

**Response**:
```json
{
  "success": true,
  "data": {
    "experiment_id": "uuid",
    "total_records": 100,
    "summary_by_camera_type": {
      "IMX708": {
        "accuracy_rate": 0.85,
        "avg_sharpness": 234.56,
        "avg_confidence_cropped": 0.92,
        "correct_ocr_count": 85,
        "total_ocr_attempts": 100
      }
    },
    "overall_stats": {
      "accuracy_rate": 0.82,
      "avg_sharpness": 245.67,
      "avg_confidence_cropped": 0.89,
      "correct_ocr_count": 82,
      "total_ocr_attempts": 100
    }
  },
  "timestamp": "2025-08-10T12:00:00.000Z"
}
```

### WebSocket Events

#### Client to Server
- `join_experiment`: Join experiment room for updates
- `leave_experiment`: Leave experiment room
- `experiment_step_complete`: Notify step completion

#### Server to Client
- `step_result`: Broadcast step results
- `experiment_error`: Broadcast experiment errors

## Integration

### Dependency Injection
The experiment service is registered in the dependency container:

```python
# v1_3/src/core/dependency_container.py
from v1_3.src.services.experiment_service import ExperimentService
self.register_service('experiment_service', ExperimentService, 
                     singleton=True, dependencies={'logger': 'logger'})
```

### Blueprint Registration
The experiments blueprint is conditionally registered:

```python
# v1_3/src/web/blueprints/__init__.py
if experiments_bp:
    app.register_blueprint(experiments_bp)
    logger.info("   ✅ Experiments blueprint registered")
```

### Navigation Integration
The experiments menu item is added to the main navigation:

```html
<!-- v1_3/src/web/templates/base.html -->
<li class="nav-item">
    <a class="nav-link {% if active_page == 'experiments' %}active{% endif %}" href="/experiments">
        <i class="fas fa-flask"></i> Experiments
    </a>
</li>
```

## Best Practices

### Experiment Design
1. **Systematic Testing**: Test one variable at a time
2. **Control Conditions**: Maintain consistent baseline parameters
3. **Replication**: Run multiple trials for statistical significance
4. **Documentation**: Record environmental conditions and setup

### Performance Optimization
1. **Batch Processing**: Use auto-run for large parameter sweeps
2. **Resource Management**: Monitor disk space and memory usage
3. **Error Handling**: Implement retry logic for failed captures
4. **Data Validation**: Verify image quality before processing

### Data Analysis
1. **Statistical Analysis**: Calculate confidence intervals
2. **Trend Analysis**: Identify performance patterns
3. **Comparative Analysis**: Compare different configurations
4. **Visualization**: Use charts for intuitive understanding

## Troubleshooting

### Common Issues

#### 1. Camera Capture Failures
- **Symptom**: rpicam-still command fails
- **Solution**: Check camera permissions and hardware connections
- **Debug**: Review system logs and camera status

#### 2. OCR Performance Issues
- **Symptom**: Low confidence scores
- **Solution**: Adjust camera parameters (exposure, gain, focus)
- **Debug**: Check image quality and lighting conditions

#### 3. Memory/Storage Issues
- **Symptom**: System becomes unresponsive
- **Solution**: Implement automatic cleanup and storage monitoring
- **Debug**: Monitor disk usage and memory consumption

#### 4. WebSocket Connection Issues
- **Symptom**: Real-time updates not working
- **Solution**: Check network connectivity and firewall settings
- **Debug**: Review WebSocket logs and connection status

### Debug Mode
Enable debug logging for detailed troubleshooting:

```python
# In experiment service
logger.setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Machine learning-based performance prediction
2. **Automated Optimization**: AI-driven parameter tuning
3. **Multi-camera Support**: Simultaneous testing of multiple cameras
4. **Cloud Integration**: Remote experiment management and data storage
5. **Real-time Collaboration**: Multi-user experiment sessions

### Performance Improvements
1. **Parallel Processing**: Concurrent experiment execution
2. **Caching**: Optimize repeated parameter combinations
3. **Compression**: Efficient image and data storage
4. **Streaming**: Real-time video analysis

## Version History

### v1.3.2 (Current)
- Initial implementation of experiments component
- Basic experiment configuration and execution
- Real-time monitoring and results analysis
- WebSocket integration for live updates

### Planned v1.3.3
- Advanced analytics and machine learning integration
- Automated parameter optimization
- Enhanced visualization and reporting
- Multi-camera support

## Support

For technical support and questions about the experiments component:

1. **Documentation**: Review this documentation thoroughly
2. **Logs**: Check system logs for error details
3. **Configuration**: Verify environment variables and settings
4. **Hardware**: Ensure camera and AI accelerator are properly connected
5. **Community**: Consult the AI Camera development team

---

**Author**: AI Camera Team  
**Version**: 1.3.2  
**Date**: August 10, 2025
