"""
Import Helper for Absolute Imports

This module provides utilities for managing absolute imports across the LPR Server project.
It ensures consistent import paths and helps prevent circular import issues.
"""

import os
import sys
from pathlib import Path

def setup_absolute_imports():
    """
    Setup absolute imports by adding project root to Python path.
    This should be called at the beginning of any module that needs absolute imports.
    """
    # Get the project root directory (parent of src)
    project_root = Path(__file__).parent.parent.parent
    src_path = project_root / "src"
    
    # Add src directory to Python path if not already there
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    return project_root, src_path

def validate_imports():
    """
    Validate that all required modules can be imported.
    This is useful for startup validation and testing.
    """
    required_modules = [
        'core.models.lpr_record',
        'core.models.camera',
        'core.models.blacklist_plate',
        'core.models.health_check',
        'services.websocket_service',
        'services.blacklist_service',
        'web.blueprints.main',
        'web.blueprints.api',
        'constants'
    ]
    
    failed_imports = []
    
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            failed_imports.append((module_name, str(e)))
    
    return failed_imports

# Setup imports when this module is imported
PROJECT_ROOT, SRC_PATH = setup_absolute_imports()
