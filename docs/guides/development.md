# AI Camera Edge System - Development Guide

**Version:** 1.0.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Category:** Development  
**Status:** Active

## Table of Contents

1. [Overview](#overview)
2. [Development Environment](#development-environment)
3. [Code Standards](#code-standards)
4. [Testing](#testing)
5. [Debugging](#debugging)
6. [Performance Optimization](#performance-optimization)
7. [Best Practices](#best-practices)

## Overview

Development guide สำหรับ AI Camera Edge System ครอบคลุมการตั้งค่า environment การเขียนโค้ด การทดสอบ และการ optimize ประสิทธิภาพ

### Development Workflow
1. **Setup Environment** - ตั้งค่า development environment
2. **Code Development** - เขียนโค้ดตาม standards
3. **Testing** - ทดสอบ functionality และ performance
4. **Code Review** - review โค้ดก่อน merge
5. **Deployment** - deploy ไปยัง target environment

## Development Environment

### Prerequisites

#### Required Software
- **Python 3.10+**
- **Git**
- **VS Code** หรือ **PyCharm**
- **Docker** (optional)
- **Postman** หรือ **curl** สำหรับ API testing

#### Required Accounts
- **GitHub** account
- **Tailscale** account
- **Hailo** developer account

### Environment Setup

#### 1. Clone Repository
```bash
# Clone the repository
git clone https://github.com/your-org/aicamera.git
cd aicamera

# Setup git hooks
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### 2. Python Environment
```bash
# Create virtual environment
python3 -m venv venv_hailo

# Activate virtual environment
source venv_hailo/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### 3. IDE Configuration

##### VS Code Configuration
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv_hailo/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

##### PyCharm Configuration
1. **Project Interpreter:** เลือก `venv_hailo/bin/python`
2. **Code Style:** ใช้ Black formatter
3. **Linting:** เปิดใช้งาน Pylint
4. **Testing:** ตั้งค่า pytest

#### 4. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Configuration Files

#### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

#### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Code Standards

### Python Code Style

#### PEP 8 Compliance
- **Line Length:** 88 characters (Black default)
- **Indentation:** 4 spaces
- **Naming:** snake_case for variables and functions
- **Classes:** PascalCase
- **Constants:** UPPER_CASE

#### Code Formatting
```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check code style with flake8
flake8 .
```

#### Example Code Structure
```python
"""
AI Camera Edge System - Camera Module

This module handles camera operations and image processing.
"""

import logging
from typing import Optional, Tuple
from dataclasses import dataclass

import cv2
import numpy as np
from picamera2 import Picamera2


@dataclass
class CameraConfig:
    """Configuration for camera operations."""
    
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    device: str = "/dev/video0"


class CameraManager:
    """Manages camera operations and image capture."""
    
    def __init__(self, config: CameraConfig) -> None:
        """Initialize camera manager.
        
        Args:
            config: Camera configuration
            
        Raises:
            RuntimeError: If camera initialization fails
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._picam2: Optional[Picamera2] = None
        
    def initialize(self) -> bool:
        """Initialize camera device.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self._picam2 = Picamera2()
            self._picam2.configure(
                self._picam2.create_preview_configuration(
                    main={"size": self.config.resolution}
                )
            )
            self._picam2.start()
            self.logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from camera.
        
        Returns:
            Captured frame as numpy array, or None if failed
        """
        if not self._picam2:
            self.logger.error("Camera not initialized")
            return None
            
        try:
            frame = self._picam2.capture_array()
            return frame
            
        except Exception as e:
            self.logger.error(f"Frame capture failed: {e}")
            return None
    
    def cleanup(self) -> None:
        """Clean up camera resources."""
        if self._picam2:
            self._picam2.stop()
            self._picam2.close()
            self.logger.info("Camera cleanup completed")
```

### Documentation Standards

#### Docstring Format
ใช้ Google-style docstrings:

```python
def process_image(image: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Process image with AI model.
    
    Args:
        image: Input image as numpy array
        threshold: Confidence threshold for detection
        
    Returns:
        Processed image with detections
        
    Raises:
        ValueError: If image is invalid
        RuntimeError: If AI model fails
        
    Example:
        >>> image = cv2.imread('test.jpg')
        >>> result = process_image(image, threshold=0.7)
    """
    pass
```

#### Module Documentation
```python
"""
AI Camera Edge System - Image Processing Module

This module provides image processing capabilities using Hailo AI accelerator.

Classes:
    ImageProcessor: Main image processing class
    DetectionResult: Result of object detection
    
Functions:
    preprocess_image: Prepare image for AI processing
    postprocess_results: Convert AI output to usable format
    
Example:
    >>> processor = ImageProcessor()
    >>> result = processor.detect_objects(image)
    >>> print(f"Found {len(result.detections)} objects")
"""
```

### Error Handling

#### Exception Handling
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def safe_operation(func):
    """Decorator for safe operation execution."""
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            return None
    
    return wrapper


class AIProcessor:
    """AI processing with proper error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_frame(self, frame: np.ndarray) -> Optional[dict]:
        """Process frame with error handling."""
        try:
            # Validate input
            if frame is None or frame.size == 0:
                raise ValueError("Invalid frame input")
            
            # Process frame
            result = self._run_inference(frame)
            
            # Validate output
            if result is None:
                raise RuntimeError("Inference returned no result")
            
            return result
            
        except ValueError as e:
            self.logger.warning(f"Input validation failed: {e}")
            return None
            
        except RuntimeError as e:
            self.logger.error(f"Processing failed: {e}")
            return None
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
```

## Testing

### Testing Strategy

#### Test Types
1. **Unit Tests** - ทดสอบ individual functions
2. **Integration Tests** - ทดสอบ component interaction
3. **Performance Tests** - ทดสอบ performance และ latency
4. **End-to-End Tests** - ทดสอบ complete workflow

#### Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── test_camera.py
│   ├── test_ai_processor.py
│   └── test_network.py
├── integration/             # Integration tests
│   ├── test_camera_ai.py
│   └── test_network_communication.py
├── performance/             # Performance tests
│   ├── test_inference_speed.py
│   └── test_memory_usage.py
├── e2e/                     # End-to-end tests
│   └── test_complete_workflow.py
└── conftest.py              # Pytest configuration
```

### Unit Testing

#### Example Unit Test
```python
"""Unit tests for camera module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from v1_3.src.camera import CameraManager, CameraConfig


class TestCameraManager:
    """Test cases for CameraManager class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = CameraConfig(resolution=(640, 480), fps=30)
        self.camera_manager = CameraManager(self.config)
    
    def test_camera_config_initialization(self):
        """Test camera configuration initialization."""
        assert self.camera_manager.config.resolution == (640, 480)
        assert self.camera_manager.config.fps == 30
        assert self.camera_manager.config.device == "/dev/video0"
    
    @patch('v1_3.src.camera.Picamera2')
    def test_camera_initialization_success(self, mock_picamera2):
        """Test successful camera initialization."""
        mock_camera = Mock()
        mock_picamera2.return_value = mock_camera
        
        result = self.camera_manager.initialize()
        
        assert result is True
        mock_camera.configure.assert_called_once()
        mock_camera.start.assert_called_once()
    
    @patch('v1_3.src.camera.Picamera2')
    def test_camera_initialization_failure(self, mock_picamera2):
        """Test camera initialization failure."""
        mock_picamera2.side_effect = Exception("Camera not found")
        
        result = self.camera_manager.initialize()
        
        assert result is False
    
    def test_capture_frame_without_initialization(self):
        """Test frame capture without initialization."""
        result = self.camera_manager.capture_frame()
        assert result is None
```

### Integration Testing

#### Example Integration Test
```python
"""Integration tests for camera and AI processing."""

import pytest
import numpy as np
from unittest.mock import patch

from v1_3.src.camera import CameraManager
from v1_3.src.ai_processor import AIProcessor


class TestCameraAIIntegration:
    """Integration tests for camera and AI processing."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.camera_manager = CameraManager()
        self.ai_processor = AIProcessor()
    
    @patch('v1_3.src.camera.Picamera2')
    def test_camera_to_ai_workflow(self, mock_picamera2):
        """Test complete camera to AI processing workflow."""
        # Mock camera
        mock_camera = Mock()
        mock_camera.capture_array.return_value = np.random.rand(480, 640, 3)
        mock_picamera2.return_value = mock_camera
        
        # Initialize camera
        assert self.camera_manager.initialize()
        
        # Capture frame
        frame = self.camera_manager.capture_frame()
        assert frame is not None
        assert frame.shape == (480, 640, 3)
        
        # Process with AI
        result = self.ai_processor.process_frame(frame)
        assert result is not None
        assert 'detections' in result
```

### Performance Testing

#### Example Performance Test
```python
"""Performance tests for AI processing."""

import time
import pytest
import numpy as np

from v1_3.src.ai_processor import AIProcessor


class TestAIPerformance:
    """Performance tests for AI processing."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.ai_processor = AIProcessor()
        self.test_image = np.random.rand(1080, 1920, 3)
    
    def test_inference_latency(self):
        """Test AI inference latency."""
        latencies = []
        
        for _ in range(10):
            start_time = time.time()
            result = self.ai_processor.process_frame(self.test_image)
            end_time = time.time()
            
            assert result is not None
            latencies.append(end_time - start_time)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Performance requirements
        assert avg_latency < 0.1  # Average < 100ms
        assert max_latency < 0.2  # Max < 200ms
    
    def test_memory_usage(self):
        """Test memory usage during processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process multiple frames
        for _ in range(100):
            result = self.ai_processor.process_frame(self.test_image)
            assert result is not None
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100 * 1024 * 1024  # < 100MB
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=v1_3
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    e2e: End-to-end tests
    slow: Slow running tests
```

#### conftest.py
```python
"""Pytest configuration and fixtures."""

import pytest
import numpy as np
from unittest.mock import Mock


@pytest.fixture
def sample_image():
    """Provide a sample image for testing."""
    return np.random.rand(480, 640, 3).astype(np.uint8)


@pytest.fixture
def mock_camera():
    """Provide a mock camera for testing."""
    camera = Mock()
    camera.capture_array.return_value = np.random.rand(480, 640, 3)
    return camera


@pytest.fixture
def mock_ai_model():
    """Provide a mock AI model for testing."""
    model = Mock()
    model.predict.return_value = {
        'detections': [
            {'bbox': [100, 100, 200, 200], 'confidence': 0.9, 'class': 'person'}
        ]
    }
    return model
```

## Debugging

### Debugging Tools

#### Logging Configuration
```python
import logging
import logging.handlers
import os

def setup_debug_logging():
    """Setup debug logging configuration."""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/debug.log',
                maxBytes=10*1024*1024,
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('v1_3.src.camera').setLevel(logging.DEBUG)
    logging.getLogger('v1_3.src.ai_processor').setLevel(logging.DEBUG)
```

#### Debug Decorators
```python
import functools
import time
import logging

logger = logging.getLogger(__name__)


def debug_timing(func):
    """Decorator to log function execution time."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.debug(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    
    return wrapper


def debug_args(func):
    """Decorator to log function arguments."""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned {result}")
        return result
    
    return wrapper
```

### Debugging Techniques

#### Interactive Debugging
```python
import pdb
import logging

logger = logging.getLogger(__name__)


def debug_function():
    """Example function with debugging."""
    try:
        # Some complex operation
        result = complex_operation()
        
        # Set breakpoint for debugging
        pdb.set_trace()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in debug_function: {e}")
        raise
```

#### Memory Debugging
```python
import tracemalloc
import psutil
import os

def debug_memory_usage():
    """Debug memory usage."""
    process = psutil.Process(os.getpid())
    
    # Start memory tracking
    tracemalloc.start()
    
    # Your code here
    result = some_operation()
    
    # Get memory snapshot
    current, peak = tracemalloc.get_traced_memory()
    
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    
    # Get top memory allocations
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("Top 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()
```

## Performance Optimization

### Profiling

#### CPU Profiling
```python
import cProfile
import pstats
import io

def profile_function(func, *args, **kwargs):
    """Profile a function's CPU usage."""
    pr = cProfile.Profile()
    pr.enable()
    
    result = func(*args, **kwargs)
    
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print(s.getvalue())
    return result
```

#### Memory Profiling
```python
import tracemalloc

def profile_memory(func, *args, **kwargs):
    """Profile a function's memory usage."""
    tracemalloc.start()
    
    result = func(*args, **kwargs)
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
    return result
```

### Optimization Techniques

#### Code Optimization
```python
# Use list comprehensions instead of loops
# Before
result = []
for i in range(1000):
    if i % 2 == 0:
        result.append(i * 2)

# After
result = [i * 2 for i in range(1000) if i % 2 == 0]

# Use generators for large datasets
def process_large_dataset(data):
    """Process large dataset using generator."""
    for item in data:
        yield process_item(item)

# Use numpy for numerical operations
import numpy as np

# Before
result = []
for i in range(1000):
    result.append(i * 2 + 1)

# After
result = np.arange(1000) * 2 + 1
```

#### Caching
```python
import functools
from typing import Dict, Any

class Cache:
    """Simple cache implementation."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def get(self, key: str) -> Any:
        """Get value from cache."""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value
    
    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()


# Use functools.lru_cache for function caching
@functools.lru_cache(maxsize=128)
def expensive_operation(x: int) -> int:
    """Expensive operation with caching."""
    # Simulate expensive computation
    import time
    time.sleep(0.1)
    return x * x
```

## Best Practices

### Code Organization

#### Project Structure
```
v1_3/
├── src/
│   ├── __init__.py
│   ├── camera.py          # Camera operations
│   ├── ai_processor.py    # AI processing
│   ├── network.py         # Network communication
│   ├── utils.py           # Utility functions
│   └── config.py          # Configuration management
├── tests/                 # Test files
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

#### Module Organization
```python
"""
Module docstring
"""

# Standard library imports
import os
import sys
from typing import Optional, List

# Third-party imports
import numpy as np
import cv2

# Local imports
from .utils import helper_function
from .config import Config

# Constants
DEFAULT_CONFIG_PATH = "config.yaml"

# Classes
class MainClass:
    """Main class docstring."""
    pass

# Functions
def main_function():
    """Main function docstring."""
    pass

# Main execution
if __name__ == "__main__":
    main_function()
```

### Error Handling

#### Comprehensive Error Handling
```python
import logging
from typing import Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing operation."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class RobustProcessor:
    """Processor with comprehensive error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_with_retry(self, data: dict, max_retries: int = 3) -> ProcessingResult:
        """Process data with retry mechanism."""
        for attempt in range(max_retries):
            try:
                result = self._process_data(data)
                return ProcessingResult(success=True, data=result)
                
            except ValueError as e:
                self.logger.warning(f"Validation error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return ProcessingResult(success=False, error=str(e))
                    
            except RuntimeError as e:
                self.logger.error(f"Processing error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return ProcessingResult(success=False, error=str(e))
                    
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return ProcessingResult(success=False, error=str(e))
        
        return ProcessingResult(success=False, error="Max retries exceeded")
```

### Security

#### Input Validation
```python
import re
from typing import Union, List

def validate_image_path(path: str) -> bool:
    """Validate image file path."""
    if not path or not isinstance(path, str):
        return False
    
    # Check for path traversal
    if '..' in path or path.startswith('/'):
        return False
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    if not any(path.lower().endswith(ext) for ext in allowed_extensions):
        return False
    
    return True


def validate_config(config: dict) -> bool:
    """Validate configuration dictionary."""
    required_keys = ['camera', 'ai_model', 'network']
    
    for key in required_keys:
        if key not in config:
            return False
    
    # Validate camera config
    camera_config = config.get('camera', {})
    if not isinstance(camera_config.get('resolution'), (list, tuple)):
        return False
    
    return True
```

## References

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)

---

**Note:** เอกสารนี้จะได้รับการอัปเดตเมื่อมีการเปลี่ยนแปลงใน development practices หรือ tools
