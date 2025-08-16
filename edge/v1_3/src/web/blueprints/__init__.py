#!/usr/bin/env python3
"""
Enhanced Web Blueprints Module for AI Camera v1.3

This module contains all Flask blueprints for the application.
Each blueprint handles a specific area of functionality using absolute imports.

Modular Architecture:
- Core Blueprints: main, camera, detection, health, streaming (always available)
- Optional Blueprints: websocket_sender, storage (can be disabled)

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

from flask import Flask
from flask_socketio import SocketIO
from v1_3.src.core.config import WEBSOCKET_SENDER_ENABLED, STORAGE_MONITOR_ENABLED, EXPERIMENT_ENABLED
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

# Import core blueprints using absolute paths (always available)
from v1_3.src.web.blueprints.main import main_bp, register_main_events
from v1_3.src.web.blueprints.camera import camera_bp, register_camera_events
from v1_3.src.web.blueprints.health import health_bp, register_health_events
from v1_3.src.web.blueprints.streaming import streaming_bp, register_streaming_events
from v1_3.src.web.blueprints.detection import detection_bp, register_detection_events
from v1_3.src.web.blueprints.detection_results import detection_results_bp

# Import experiments blueprint (optional)
experiments_bp = None
register_experiment_events = None
if EXPERIMENT_ENABLED:
    try:
        from v1_3.src.web.blueprints.experiments import experiments_bp, register_experiment_events
        logger.info("Experiments blueprint imported (enabled in config)")
    except ImportError:
        logger.warning("Experiments blueprint not available")
else:
    logger.info("Experiments blueprint not imported (disabled in config)")

# Import optional blueprints (may not be available)
websocket_sender_bp = None
register_websocket_sender_events = None
storage_bp = None
register_storage_events = None

# Conditionally import optional blueprints
if WEBSOCKET_SENDER_ENABLED:
    try:
        from v1_3.src.web.blueprints.websocket_sender import websocket_sender_bp, register_websocket_sender_events
        logger.info("WebSocket Sender blueprint imported (enabled in config)")
    except ImportError:
        logger.warning("WebSocket Sender blueprint not available")
else:
    logger.info("WebSocket Sender blueprint not imported (disabled in config)")

if STORAGE_MONITOR_ENABLED:
    try:
        from v1_3.src.web.blueprints.storage import storage_bp, register_storage_events
        logger.info("Storage blueprint imported (enabled in config)")
    except ImportError:
        logger.warning("Storage blueprint not available")
else:
    logger.info("Storage blueprint not imported (disabled in config)")

# Import websocket blueprint (core communication)
try:
    from v1_3.src.web.blueprints.websocket import websocket_bp, register_websocket_events
except ImportError:
    logger.warning("WebSocket blueprint not available")
    websocket_bp = None
    register_websocket_events = None


def register_blueprints(app: Flask, socketio: SocketIO):
    """
    Register all Flask blueprints with the application using modular architecture.
    
    Core blueprints are always registered.
    Optional blueprints are registered only if enabled and available.
    
    Args:
        app: Flask application instance
        socketio: Flask-SocketIO instance
    """
    logger.info("🔧 Registering blueprints with modular architecture...")
    
    # === CORE BLUEPRINTS (Always Registered) ===
    logger.info("📋 Registering core blueprints...")
    
    # Core blueprints - essential functionality
    app.register_blueprint(main_bp)
    logger.info("   ✅ Main blueprint registered")
    
    app.register_blueprint(camera_bp)
    logger.info("   ✅ Camera blueprint registered")
    
    app.register_blueprint(health_bp)
    logger.info("   ✅ Health blueprint registered")
    
    app.register_blueprint(streaming_bp)
    logger.info("   ✅ Streaming blueprint registered")
    
    app.register_blueprint(detection_bp)
    logger.info("   ✅ Detection blueprint registered")
    
    app.register_blueprint(detection_results_bp)
    logger.info("   ✅ Detection Results blueprint registered")
    
    # Register experiments blueprint if available and enabled
    if experiments_bp and EXPERIMENT_ENABLED:
        app.register_blueprint(experiments_bp)
        logger.info("   ✅ Experiments blueprint registered (enabled)")
    else:
        logger.info("   ℹ️ Experiments blueprint not registered (disabled/not available)")
    
    # WebSocket blueprint (core communication)
    if websocket_bp:
        app.register_blueprint(websocket_bp)
        logger.info("   ✅ WebSocket blueprint registered")
    else:
        logger.warning("   ⚠️ WebSocket blueprint not available")
    
    # === OPTIONAL BLUEPRINTS (Conditionally Registered) ===
    logger.info("🔌 Registering optional blueprints...")
    
    # WebSocket Sender blueprint (optional)
    if websocket_sender_bp and WEBSOCKET_SENDER_ENABLED:
        app.register_blueprint(websocket_sender_bp)
        logger.info("   ✅ WebSocket Sender blueprint registered (enabled)")
    else:
        logger.info("   ℹ️ WebSocket Sender blueprint not registered (disabled/not available)")
    
    # Storage blueprint (optional)
    if storage_bp and STORAGE_MONITOR_ENABLED:
        app.register_blueprint(storage_bp)
        logger.info("   ✅ Storage blueprint registered (enabled)")
    else:
        logger.info("   ℹ️ Storage blueprint not registered (disabled/not available)")
    
    # === REGISTER WEBSOCKET EVENTS ===
    logger.info("📡 Registering WebSocket events...")
    
    # Core WebSocket events
    register_main_events(socketio)
    logger.info("   ✅ Main events registered")
    
    register_camera_events(socketio)
    logger.info("   ✅ Camera events registered")
    
    register_detection_events(socketio)
    logger.info("   ✅ Detection events registered")
    
    register_health_events(socketio)
    logger.info("   ✅ Health events registered")
    
    register_streaming_events(socketio)
    logger.info("   ✅ Streaming events registered")
    
    # Register experiment events if available and enabled
    if register_experiment_events and EXPERIMENT_ENABLED:
        register_experiment_events(socketio)
        logger.info("   ✅ Experiment events registered (enabled)")
    else:
        logger.info("   ℹ️ Experiment events not registered (disabled/not available)")
    
    # Optional WebSocket events
    if register_websocket_events:
        register_websocket_events(socketio)
        logger.info("   ✅ WebSocket events registered")
    
    if register_websocket_sender_events and WEBSOCKET_SENDER_ENABLED:
        register_websocket_sender_events(socketio)
        logger.info("   ✅ WebSocket Sender events registered (enabled)")
    else:
        logger.info("   ℹ️ WebSocket Sender events not registered (disabled/not available)")
    
    if register_storage_events and STORAGE_MONITOR_ENABLED:
        register_storage_events(socketio)
        logger.info("   ✅ Storage events registered (enabled)")
    else:
        logger.info("   ℹ️ Storage events not registered (disabled/not available)")
    
    logger.info("🎉 Blueprint registration completed successfully!")


def get_available_blueprints():
    """
    Get list of available blueprints for debugging and monitoring.
    
    Returns:
        Dict containing core and optional blueprints status
    """
    return {
        'core_blueprints': {
            'main': True,
            'camera': True,
            'health': True,
            'streaming': True,
            'detection': True,
            'detection_results': True,
            'websocket': websocket_bp is not None
        },
        'optional_blueprints': {
            'websocket_sender': {
                'enabled': WEBSOCKET_SENDER_ENABLED,
                'available': websocket_sender_bp is not None,
                'registered': WEBSOCKET_SENDER_ENABLED and websocket_sender_bp is not None
            },
            'storage': {
                'enabled': STORAGE_MONITOR_ENABLED,
                'available': storage_bp is not None,
                'registered': STORAGE_MONITOR_ENABLED and storage_bp is not None
            }
        }
    }