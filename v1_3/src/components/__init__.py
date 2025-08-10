"""
AI Camera v1.3 Components Module

This module contains all the core components for the AI Camera system including:
- Detection processors for AI models
- Camera handlers for image capture
- Health monitoring systems
- Database managers
- Utility components

Components:
    - detection_processor: Hailo AI model detection system
    - camera_handler: Picamera2 integration and management
    - health_monitor: System health monitoring
    - database_manager: Database operations
    - improved_camera_manager: Advanced camera management

Template Components (for testing):
    - camera_manager_template: Simplified camera manager for testing
    - detection_processor_template: Simplified detection processor for testing
    - health_monitor_template: Simplified health monitor for testing
    - video_service_template: Simplified video service for testing

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detection_processor import DetectionProcessor
from camera_handler import CameraHandler
from health_monitor import HealthMonitor
from database_manager import DatabaseManager
from improved_camera_manager import ImprovedCameraManager


__all__ = [
    # Detection components
    'DetectionProcessor',
    
    # Camera components
    'CameraHandler',
    'ImprovedCameraManager',
    
    # System components
    'HealthMonitor',
    'DatabaseManager',
    
    # Template components (for testing)
    'CameraManagerTemplate',
    'DetectionProcessorTemplate',
    'HealthMonitorTemplate',
    'VideoServiceTemplate',
    'get_camera_manager',
]

__version__ = "1.3"
__author__ = "AI Camera Team"
