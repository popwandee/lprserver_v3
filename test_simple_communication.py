#!/usr/bin/env python3
"""
Simple Test for Unified Communication System

This script tests the basic functionality without requiring external services.
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_detection_data(edge_device_id: str, plate_number: str = None) -> Dict[str, Any]:
    """Create sample detection data"""
    if not plate_number:
        import random
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        numbers = ''.join(random.choices('0123456789', k=4))
        plate_number = f"{letters}{numbers}"
    
    return {
        "detection_data": {
            "vehicles_count": 1,
            "plates_count": 1,
            "processing_time_ms": 150,
            "confidence_score": 0.95,
            "detection_type": "lpr",
            "vehicles": [
                {
                    "vehicle_index": 0,
                    "bbox": [100, 100, 200, 200],
                    "confidence": 0.95,
                    "vehicle_class": "car",
                    "vehicle_type": "sedan",
                    "color": "white",
                    "brand": "Toyota",
                    "model": "Camry",
                    "year": 2020
                }
            ],
            "plates": [
                {
                    "plate_index": 0,
                    "vehicle_id": 0,
                    "plate_number": plate_number,
                    "bbox": [150, 120, 180, 140],
                    "confidence": 0.92,
                    "plate_type": "standard",
                    "country": "TH",
                    "province": "Bangkok",
                    "is_valid": True
                }
            ]
        },
        "metadata": {
            "image_path": f"/storage/images/{edge_device_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            "weather": "clear",
            "lighting": "daylight"
        }
    }

def test_websocket_service():
    """Test WebSocket service creation"""
    try:
        from src.services.websocket_service import WebSocketService
        
        logger.info("Testing WebSocket Service...")
        ws_service = WebSocketService()
        
        # Test initialization
        ws_service.initialize(None, None)  # Mock socketio and db_session
        
        logger.info(f"WebSocket service created successfully")
        logger.info(f"Connected status: {ws_service.connected}")
        
        # Test disconnect
        ws_service.disconnect()
        logger.info(f"After disconnect: {ws_service.connected}")
        
        return True
        
    except Exception as e:
        logger.error(f"WebSocket service test failed: {e}")
        return False

def test_data_processor():
    """Test data processor creation"""
    try:
        from src.services.data_processor import DataProcessor
        
        logger.info("Testing Data Processor...")
        
        # Use mock database config
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password'
        }
        
        data_processor = DataProcessor(db_config)
        logger.info("Data processor created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Data processor test failed: {e}")
        return False

def test_unified_message_format():
    """Test unified message format creation"""
    try:
        from src.services.unified_communication_service import UnifiedCommunicationService
        
        logger.info("Testing Unified Message Format...")
        
        # Create service without starting it
        config = {
            "websocket": {"host": "localhost", "port": 8765},
            "mqtt": {"broker_host": "localhost", "broker_port": 1883},
            "database": {"host": "localhost", "port": 5432, "database": "test", "user": "test", "password": "test"}
        }
        
        comm_service = UnifiedCommunicationService(config)
        
        # Test message creation
        detection_data = create_sample_detection_data("CAM001", "ABC1234")
        message = comm_service._create_unified_message("detection", detection_data, "CAM001")
        
        logger.info("Unified message created successfully")
        logger.info(f"Message ID: {message.get('message_id')}")
        logger.info(f"Protocol: {message.get('protocol')}")
        logger.info(f"Data Type: {message.get('data_type')}")
        logger.info(f"Edge Device: {message.get('edge_device_id')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Unified message format test failed: {e}")
        return False

def test_protocol_switching():
    """Test protocol switching logic"""
    try:
        from src.services.unified_communication_service import UnifiedCommunicationService, ProtocolType, ConnectivityLevel
        
        logger.info("Testing Protocol Switching Logic...")
        
        config = {
            "websocket": {"host": "localhost", "port": 8765},
            "mqtt": {"broker_host": "localhost", "broker_port": 1883},
            "database": {"host": "localhost", "port": 5432, "database": "test", "user": "test", "password": "test"}
        }
        
        comm_service = UnifiedCommunicationService(config)
        
        # Test connectivity assessment
        connectivity = comm_service._assess_connectivity()
        logger.info(f"Connectivity Level: {connectivity.value}")
        
        # Test protocol selection
        optimal_protocol = comm_service._select_optimal_protocol()
        logger.info(f"Optimal Protocol: {optimal_protocol.value}")
        
        # Test protocol switching
        comm_service._switch_protocol(ProtocolType.REST_API, "test_switch")
        logger.info(f"Switched to: {comm_service.current_protocol.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Protocol switching test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("LPR Server v3 - Simple Communication System Test")
    logger.info("=" * 60)
    
    tests = [
        ("WebSocket Service", test_websocket_service),
        ("Data Processor", test_data_processor),
        ("Unified Message Format", test_unified_message_format),
        ("Protocol Switching", test_protocol_switching),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n=== Testing {test_name} ===")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is working correctly.")
    else:
        logger.info("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
