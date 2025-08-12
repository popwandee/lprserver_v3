#!/usr/bin/env python3
"""
WebSocket Server for LPR data reception
Runs on port 8765 as specified
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_socketio_app
from config import Config

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main WebSocket server entry point"""
    try:
        # Create SocketIO app
        socketio, app = create_socketio_app()
        
        # Import WebSocket service to register handlers
        from src.services.websocket_service import websocket_service
        
        logger.info("Starting LPR WebSocket Server on port 8765")
        
        # Run SocketIO server
        socketio.run(
            app,
            host='0.0.0.0',
            port=8765,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        logger.error(f"Error starting WebSocket server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
