#!/usr/bin/env python3
"""
LPR Server v3 - Main application entry point
"""

import os
import sys
from pathlib import Path

# Add project root to Python path first
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Setup absolute imports
from core.import_helper import setup_absolute_imports
setup_absolute_imports()

# Now import app modules
from src.app import create_app, create_socketio_app

def main():
    """Main application entry point"""
    # Create Flask app with default config
    app = create_app()
    
    # Import WebSocket service to register handlers
    from src.services.websocket_service import websocket_service
    
    if __name__ == '__main__':
        # Run in development mode
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=app.config.get('DEBUG', False)
        )

if __name__ == '__main__':
    main()
