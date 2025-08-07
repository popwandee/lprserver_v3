"""
Services Module for AI Camera v1.3

This module contains service layer components that implement
business logic and coordinate between different components.

Services:
- CameraManager: Camera operations and management
- DetectionManager: AI detection operations
- VideoStreamingService: Video streaming operations
- WebSocketSender: WebSocket communication

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

from services.camera_manager import CameraManager, create_camera_manager
from services.detection_manager import DetectionManager, create_detection_manager
from services.video_streaming import VideoStreamingService, create_video_streaming_service
from services.websocket_sender import WebSocketSender, create_websocket_sender

__all__ = [
    'CameraManager',
    'DetectionManager',
    'VideoStreamingService',
    'WebSocketSender',
    'create_camera_manager',
    'create_detection_manager',
    'create_video_streaming_service',
    'create_websocket_sender',
]

__version__ = "1.3"
__author__ = "AI Camera Team"
