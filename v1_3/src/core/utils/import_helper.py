#!/usr/bin/env python3
"""
Import Helper for AI Camera v1.3

This module provides utilities for managing import paths and ensuring
consistent absolute imports across the application.

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)


def setup_import_paths(base_path: Optional[str] = None) -> None:
    """
    Setup import paths for absolute imports.
    
    Args:
        base_path: Base path to add to sys.path (defaults to project root)
    """
    if base_path is None:
        # Get the project root directory (aicamera/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent  # Go up from utils/core/src/v1_3
        logger.info(f"Auto-detected project root: {project_root.absolute()}")
    else:
        project_root = Path(base_path)
        logger.info(f"Using provided project root: {project_root.absolute()}")
    
    # Add project root to sys.path for absolute imports
    project_root_str = str(project_root.absolute())
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
        logger.debug(f"Added project root: {project_root_str}")
    
    # Add v1_3 directory for v1_3.* imports
    v1_3_path = str(project_root / 'v1_3')
    if v1_3_path not in sys.path:
        sys.path.insert(0, v1_3_path)
        logger.debug(f"Added v1_3 path: {v1_3_path}")
    
    # Add v1_3/src directory for src.* imports
    v1_3_src_path = str(project_root / 'v1_3' / 'src')
    if v1_3_src_path not in sys.path:
        sys.path.insert(0, v1_3_src_path)
        logger.debug(f"Added v1_3/src path: {v1_3_src_path}")
    
    # Add current working directory
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
        logger.debug(f"Added CWD: {cwd}")


def get_absolute_import_path(module_name: str) -> str:
    """
    Get absolute import path for a module.
    
    Args:
        module_name: Module name (e.g., 'core', 'components', 'services')
        
    Returns:
        Absolute import path
    """
    # Map relative module names to absolute paths
    module_mapping = {
        'core': 'v1_3.src.core',
        'components': 'v1_3.src.components', 
        'services': 'v1_3.src.services',
        'web': 'v1_3.src.web',
        'utils': 'v1_3.src.core.utils'
    }
    
    return module_mapping.get(module_name, f'v1_3.src.{module_name}')


def validate_imports() -> List[str]:
    """
    Validate that all required modules can be imported using absolute paths.
    
    Returns:
        List of import errors (empty if all imports successful)
    """
    errors = []
    required_modules = [
        'v1_3.src.core.config',
        'v1_3.src.core.dependency_container',
        'v1_3.src.core.utils.logging_config',
        'v1_3.src.components.camera_handler',
        'v1_3.src.components.detection_processor',
        'v1_3.src.components.health_monitor',
        'v1_3.src.components.database_manager',
        'v1_3.src.services.camera_manager',
        'v1_3.src.services.detection_manager',
        'v1_3.src.services.video_streaming',
        'v1_3.src.services.websocket_sender',
        'v1_3.src.web.blueprints.main',
        'v1_3.src.web.blueprints.camera',
        'v1_3.src.web.blueprints.detection',
        'v1_3.src.web.blueprints.health',
        'v1_3.src.web.blueprints.streaming',
        'v1_3.src.web.blueprints.websocket'
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