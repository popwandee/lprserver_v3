"""
Web Module for AI Camera v1.3

This module contains web-related components including:
- Flask blueprints
- WebSocket handlers
- Template utilities
- Web interface components

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

from web.blueprints import (
    main_bp,
    camera_bp,
    detection_bp,
    streaming_bp,
    health_bp,
    websocket_bp
)

__all__ = [
    'main_bp',
    'camera_bp',
    'detection_bp',
    'streaming_bp',
    'health_bp',
    'websocket_bp'
]

__version__ = "1.3"
__author__ = "AI Camera Team"
