#!/usr/bin/env python3
"""
Detection Blueprint for AI Camera v1.3

This is a stub blueprint that will be implemented later.
"""

from flask import Blueprint
from flask_socketio import emit
import logging

detection_bp = Blueprint('detection', __name__, url_prefix='/detection')
logger = logging.getLogger(__name__)


def register_detection_events(socketio):
    """Register WebSocket events for detection functionality."""
    
    @socketio.on('detection_status_request')
    def handle_detection_status_request():
        """Handle detection status request from client."""
        emit('detection_status_update', {
            'status': 'stub',
            'message': 'Detection not implemented yet'
        })
