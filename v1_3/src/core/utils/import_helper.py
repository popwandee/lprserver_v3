#!/usr/bin/env python3
"""
Import Helper for AI Camera v1.3

This module provides utilities for managing import paths and ensuring
consistent imports across the application.

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def setup_import_paths(base_path: Optional[str] = None) -> None:
    """
    Setup import paths for the application.
    
    Args:
        base_path: Base path to add to sys.path (defaults to src directory)
    """
    if base_path is None:
        # Get the src directory path
        current_file = Path(__file__)
        src_path = current_file.parent.parent.parent  # Go up from utils/core/src
    else:
        src_path = Path(base_path)
    
    src_path_str = str(src_path.absolute())
    
    # Add to sys.path if not already present
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
        logger.debug(f"Added {src_path_str} to Python path")
        print(f"Added {src_path_str} to Python path")
    # Also add parent directory for relative imports
    parent_path = str(src_path.parent)
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)
        logger.debug(f"Added {parent_path} to Python path")
        print(f"Added {parent_path} to Python path")
    # Add current working directory
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
        logger.debug(f"Added {cwd} to Python path")
        print(f"Added {cwd} to Python path")
     # Add v1_3 directory for absolute imports
    v1_3_path = str(Path(cwd) / 'v1_3')
    if v1_3_path not in sys.path:
        sys.path.insert(0, v1_3_path)
        logger.debug(f"Added {v1_3_path} to Python path")
        print(f"Added {v1_3_path} to Python path")
    
    # Add v1_3/src directory for absolute imports
    v1_3_src_path = str(Path(cwd) / 'v1_3' / 'src')
    if v1_3_src_path not in sys.path:
        sys.path.insert(0, v1_3_src_path)
        logger.debug(f"Added {v1_3_src_path} to Python path")
        print(f"Added {v1_3_src_path} to Python path")
    # Add project root for absolute imports
    project_root = str(Path(cwd))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.debug(f"Added {project_root} to Python path")
        print(f"Added {project_root} to Python path")
        
def get_module_path(module_name: str) -> Optional[str]:
    """
    Get the absolute path for a module.
    
    Args:
        module_name: Name of the module (e.g., 'core', 'components', 'services')
        
    Returns:
        Absolute path to the module or None if not found
    """
    try:
        import importlib
        module = importlib.import_module(module_name)
        return os.path.dirname(module.__file__)
    except ImportError:
        return None


def validate_imports() -> List[str]:
    """
    Validate that all required modules can be imported.
    
    Returns:
        List of import errors (empty if all imports successful)
    """
    errors = []
    required_modules = [
        'core.config',
        'core.dependency_container',
        'core.utils.logging_config',
        'components.camera_handler',
        'components.detection_processor',
        'components.health_monitor',
        'components.database_manager',
        'services.camera_manager',
        'services.detection_manager',
        'services.video_streaming',
        'services.websocket_sender',
        'web.blueprints.main',
        'web.blueprints.camera',
        'web.blueprints.detection'
    ]
    
    for module_name in required_modules:
        try:
            __import__(module_name)
            logger.debug(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            error_msg = f"✗ Failed to import {module_name}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    return errors


def safe_import(module_name: str, default=None):
    """
    Safely import a module with fallback.
    
    Args:
        module_name: Name of the module to import
        default: Default value to return if import fails
        
    Returns:
        Imported module or default value
    """
    try:
        return __import__(module_name, fromlist=['*'])
    except ImportError as e:
        logger.warning(f"Failed to import {module_name}: {e}")
        return default


# Auto-setup import paths when this module is imported
setup_import_paths() 