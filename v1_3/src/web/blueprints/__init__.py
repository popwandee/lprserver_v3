#!/usr/bin/env python3
"""
Enhanced Web Blueprints Module for AI Camera v1.3

This module contains all Flask blueprints for the application.
Each blueprint handles a specific area of functionality using absolute imports.

Blueprints:
- main: Main dashboard and system overview
- camera: Camera operations and management
- detection: AI detection operations
- streaming: Video streaming functionality
- health: System health monitoring
- websocket: WebSocket communication

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

from flask import Flask
from flask_socketio import SocketIO

# Import blueprints using absolute paths
from v1_3.src.web.blueprints.main import main_bp
from v1_3.src.web.blueprints.camera import camera_bp, register_camera_events
from v1_3.src.web.blueprints.health import health_bp
from v1_3.src.web.blueprints.streaming import streaming_bp
from v1_3.src.web.blueprints.detection import detection_bp, register_detection_events
from v1_3.src.web.blueprints.websocket import websocket_bp


def register_blueprints(app: Flask, socketio: SocketIO):
    """
    Register all Flask blueprints with the application.
    
    Args:
        app: Flask application instance
        socketio: Flask-SocketIO instance
    """
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(streaming_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(websocket_bp)
    
    # Register WebSocket events
    register_camera_events(socketio)
    register_detection_events(socketio)
    
    # Register other WebSocket events here
    # register_health_events(socketio)
    # register_streaming_events(socketio)
