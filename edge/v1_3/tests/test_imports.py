#!/usr/bin/env python3
"""
Test Imports for AI Camera v1.3

This script tests all imports to ensure they work correctly with absolute imports.

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import import helper first
try:
    from src.core.utils.import_helper import setup_import_paths, validate_imports
    setup_import_paths()
except ImportError:
    # Fallback: try direct import
    try:
        from core.utils.import_helper import setup_import_paths, validate_imports
        setup_import_paths()
    except ImportError as e:
        print(f"Failed to import import_helper: {e}")
        sys.exit(1)

def test_imports():
    """Test all imports to ensure they work correctly."""
    print("🔍 Testing AI Camera v1.3 Imports...")
    print("=" * 50)
    
    # Test core imports
    print("\n📦 Testing Core Imports:")
    try:
        from core.utils.import_helper import setup_import_paths, validate_imports
        print("  ✅ core.utils.import_helper")
        
        from core.config import FLASK_HOST, FLASK_PORT
        print("  ✅ core.config")
        
        from core.dependency_container import get_container, get_service
        print("  ✅ core.dependency_container")
        
        from core.utils.logging_config import setup_logging, get_logger
        print("  ✅ core.utils.logging_config")
        
    except ImportError as e:
        print(f"  ❌ Core import failed: {e}")
        return False
    
    # Test component imports
    print("\n🔧 Testing Component Imports:")
    try:
        from components.camera_handler import CameraHandler
        print("  ✅ components.camera_handler")
        
        from components.detection_processor import DetectionProcessor
        print("  ✅ components.detection_processor")
        
        from components.health_monitor import HealthMonitor
        print("  ✅ components.health_monitor")
        
        from components.database_manager import DatabaseManager
        print("  ✅ components.database_manager")
        
    except ImportError as e:
        print(f"  ❌ Component import failed: {e}")
        return False
    
    # Test service imports
    print("\n⚙️ Testing Service Imports:")
    try:
        from services.camera_manager import CameraManager
        print("  ✅ services.camera_manager")
        
        from services.detection_manager import DetectionManager
        print("  ✅ services.detection_manager")
        
        from services.video_streaming import VideoStreamingService
        print("  ✅ services.video_streaming")
        
        from services.websocket_sender import WebSocketSender
        print("  ✅ services.websocket_sender")
        
    except ImportError as e:
        print(f"  ❌ Service import failed: {e}")
        return False
    
    # Test web imports
    print("\n🌐 Testing Web Imports:")
    try:
        from web.blueprints.main import main_bp
        print("  ✅ web.blueprints.main")
        
        from web.blueprints.camera import camera_bp
        print("  ✅ web.blueprints.camera")
        
        from web.blueprints.detection import detection_bp
        print("  ✅ web.blueprints.detection")
        
        from web.blueprints.health import health_bp
        print("  ✅ web.blueprints.health")
        
        from web.blueprints.streaming import streaming_bp
        print("  ✅ web.blueprints.streaming")
        
        from web.blueprints.websocket import websocket_bp
        print("  ✅ web.blueprints.websocket")
        
    except ImportError as e:
        print(f"  ❌ Web import failed: {e}")
        return False
    
    # Test main application imports
    print("\n🚀 Testing Application Imports:")
    try:
        from app import create_app
        print("  ✅ app")
        
        from wsgi import application
        print("  ✅ wsgi")
        
    except ImportError as e:
        print(f"  ❌ Application import failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All imports successful!")
    return True

def test_dependency_container():
    """Test dependency container functionality."""
    print("\n🔧 Testing Dependency Container:")
    try:
        from core.dependency_container import get_container, get_service
        
        # Get container
        container = get_container()
        print("  ✅ Container created")
        
        # Test service registration
        services = container.get_registered_services()
        print(f"  ✅ Registered services: {list(services.keys())}")
        
        # Test logger service
        logger = get_service('logger')
        if logger:
            print("  ✅ Logger service retrieved")
        else:
            print("  ⚠️ Logger service not available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Dependency container test failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n⚙️ Testing Configuration:")
    try:
        from core.config import FLASK_HOST, FLASK_PORT, SECRET_KEY
        
        print(f"  ✅ Flask Host: {FLASK_HOST}")
        print(f"  ✅ Flask Port: {FLASK_PORT}")
        print(f"  ✅ Secret Key: {'*' * len(SECRET_KEY) if SECRET_KEY else 'Not set'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 AI Camera v1.3 Import Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test dependency container
        container_ok = test_dependency_container()
        
        # Test configuration
        config_ok = test_config()
        
        print("\n" + "=" * 50)
        if imports_ok and container_ok and config_ok:
            print("🎉 All tests passed! Application is ready to run.")
            return 0
        else:
            print("⚠️ Some tests failed. Please check the errors above.")
            return 1
    else:
        print("\n❌ Import tests failed. Cannot proceed with other tests.")
        return 1

if __name__ == '__main__':
    exit(main()) 