#!/usr/bin/env python3
"""
Core Utilities for AI Camera v1.3

This package contains utility modules for the core functionality.

Modules:
- logging_config: Logging configuration and setup
- camera_config: Camera configuration utilities
- import_helper: Import path management and validation

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

from core.utils.logging_config import setup_logging, get_logger
from core.utils.camera_config import CameraConfiguration
from core.utils.import_helper import setup_import_paths, validate_imports, safe_import

__all__ = [
    'setup_logging',
    'get_logger', 
    'CameraConfiguration',
    'setup_import_paths',
    'validate_imports',
    'safe_import'
]

__version__ = "1.3"
__author__ = "AI Camera Team"
