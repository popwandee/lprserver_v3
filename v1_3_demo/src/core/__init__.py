#!/usr/bin/env python3
"""
Core Module for AI Camera v1.3

This module contains core functionality including:
- Dependency injection container
- Configuration management
- Utility functions and helpers

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

from core.dependency_container import (
    DependencyContainer,
    get_container,
    get_service,
    register_service,
    shutdown_container
)
from core.config import *
from core.utils.import_helper import setup_import_paths, validate_imports

__all__ = [
    'DependencyContainer',
    'get_container',
    'get_service', 
    'register_service',
    'shutdown_container',
    'setup_import_paths',
    'validate_imports'
]

__version__ = "1.3"
__author__ = "AI Camera Team"
