#!/usr/bin/env python3
"""
Test Unified Communication System for LPR Server v3

This script demonstrates the multi-protocol communication system with:
- WebSocket (Socket.IO) as primary
- REST API as secondary
- MQTT as fallback
- Automatic protocol switching
- Centralized PostgreSQL storage
"""

import json
import time
import uuid
import logging
import argparse
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

def create_sample_health_data(edge_device_id: str, status: str = "healthy") -> Dict[str, Any]:
    """Create sample health data"""
    return {
        "health_status": status,
        "health_details": {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "network_status": "connected",
            "camera_status": "active",
            "last_detection": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": 86400,
            "temperature": 42.5
        },
        "alerts": []
    }

def create_sample_config_data(edge_device_id: str, config_type: str = "detection_settings") -> Dict[str, Any]:
    """Create sample configuration data"""
    return {
        "config_type": config_type,
        "config_data": {
            "detection_interval": 1000,
            "confidence_threshold": 0.8,
            "max_vehicles_per_frame": 5,
            "image_quality": "high",
            "enable_recording": True,
            "recording_duration": 30,
            "alert_settings": {
                "enable_alerts": True,
                "alert_confidence_threshold": 0.9,
                "notification_channels": ["websocket", "rest_api", "mqtt"]
            }
        }
    }

def create_sample_control_data(command: str = "get_status", parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create sample control data"""
    if parameters is None:
        parameters = {}
    
    return {
        "command": command,
        "parameters": parameters,
        "status": "pending"
    }

def test_unified_communication():
    """Test the unified communication system"""
    try:
        # Import the unified communication service
        from src.services.unified_communication_service import UnifiedCommunicationService
        
        logger.info("Starting Unified Communication System Test")
        
        # Initialize the service
        config = {
            "websocket": {
                "host": "localhost",
                "port": 8765
            },
            "mqtt": {
                "broker_host": "localhost",
                "broker_port": 1883
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "lprserver_v3",
                "user": "lpruser",
                "password": "your_password"
            }
        }
        
        # Create unified communication service
        comm_service = UnifiedCommunicationService(config)
        
        # Set up callbacks
        def on_detection_received(detection_data, edge_device_id):
            logger.info(f"Detection received from {edge_device_id}: {detection_data.get('detection_data', {}).get('plates_count', 0)} plates")
        
        def on_health_update(health_data, edge_device_id):
            logger.info(f"Health update from {edge_device_id}: {health_data.get('health_status')}")
        
        def on_config_update(config_data, edge_device_id):
            logger.info(f"Config update from {edge_device_id}: {config_data.get('config_type')}")
        
        def on_control_command(control_data, edge_device_id):
            logger.info(f"Control command for {edge_device_id}: {control_data.get('command')}")
        
        comm_service.on_detection_received = on_detection_received
        comm_service.on_health_update = on_health_update
        comm_service.on_config_update = on_config_update
        comm_service.on_control_command = on_control_command
        
        # Start the service
        if not comm_service.start():
            logger.error("Failed to start unified communication service")
            return
        
        logger.info("Unified Communication Service started successfully")
        
        # Test different scenarios
        test_scenarios = [
            {
                "name": "Urban Environment (High Connectivity)",
                "edge_devices": ["CAM001", "CAM002"],
                "protocol_preference": "websocket",
                "message_count": 10
            },
            {
                "name": "Suburban Environment (Medium Connectivity)",
                "edge_devices": ["CAM003", "CAM004"],
                "protocol_preference": "rest_api",
                "message_count": 8
            },
            {
                "name": "Rural Environment (Poor Connectivity)",
                "edge_devices": ["CAM005"],
                "protocol_preference": "mqtt",
                "message_count": 5
            }
        ]
        
        for scenario in test_scenarios:
            logger.info(f"\n=== Testing Scenario: {scenario['name']} ===")
            
            for edge_device_id in scenario["edge_devices"]:
                logger.info(f"Testing with edge device: {edge_device_id}")
                
                # Send detection messages
                for i in range(scenario["message_count"]):
                    plate_number = f"ABC{1000 + i}"
                    detection_data = create_sample_detection_data(edge_device_id, plate_number)
                    
                    success = comm_service.send_detection(detection_data, edge_device_id)
                    if success:
                        logger.info(f"Detection {i+1} sent successfully via {comm_service.current_protocol.value}")
                    else:
                        logger.warning(f"Detection {i+1} failed to send")
                    
                    time.sleep(1)  # Wait between messages
                
                # Send health update
                health_data = create_sample_health_data(edge_device_id, "healthy")
                success = comm_service.send_health(health_data, edge_device_id)
                if success:
                    logger.info(f"Health update sent successfully via {comm_service.current_protocol.value}")
                
                # Send configuration update
                config_data = create_sample_config_data(edge_device_id, "detection_settings")
                success = comm_service.send_config(config_data, edge_device_id)
                if success:
                    logger.info(f"Config update sent successfully via {comm_service.current_protocol.value}")
                
                # Send control command
                control_data = create_sample_control_data("get_status")
                success = comm_service.send_control_command("get_status", {}, edge_device_id)
                if success:
                    logger.info(f"Control command sent successfully via {comm_service.current_protocol.value}")
                
                time.sleep(2)  # Wait between devices
        
        # Test protocol switching
        logger.info("\n=== Testing Protocol Switching ===")
        
        # Simulate connectivity issues
        logger.info("Simulating connectivity issues...")
        
        # Force protocol switch by modifying health scores
        comm_service.protocol_health[comm_service.current_protocol] = 0.1
        
        # Wait for protocol switching
        time.sleep(35)  # Wait for connectivity monitor to run
        
        logger.info(f"Protocol switched to: {comm_service.current_protocol.value}")
        
        # Send test message with new protocol
        test_edge_device = "CAM_TEST"
        detection_data = create_sample_detection_data(test_edge_device, "TEST123")
        success = comm_service.send_detection(detection_data, test_edge_device)
        
        if success:
            logger.info(f"Test message sent successfully via {comm_service.current_protocol.value}")
        else:
            logger.warning("Test message failed to send")
        
        # Get health status
        health_status = comm_service.get_health_status()
        logger.info(f"\n=== Health Status ===")
        logger.info(f"Current Protocol: {health_status['current_protocol']}")
        logger.info(f"Connectivity Level: {health_status['connectivity_level']}")
        logger.info(f"Messages Sent: {health_status['metrics']['messages_sent']}")
        logger.info(f"Messages Received: {health_status['metrics']['messages_received']}")
        logger.info(f"Protocol Switches: {health_status['metrics']['protocol_switches']}")
        logger.info(f"Errors: {health_status['metrics']['errors']}")
        
        # Protocol health scores
        logger.info(f"\n=== Protocol Health Scores ===")
        for protocol, health in health_status['protocol_health'].items():
            logger.info(f"{protocol}: {health:.2f}")
        
        # Service status
        logger.info(f"\n=== Service Status ===")
        for service, status in health_status['services'].items():
            if isinstance(status, dict):
                connected = status.get('connected', status.get('enabled', False))
                health = status.get('health', 0.0)
                logger.info(f"{service}: Connected={connected}, Health={health:.2f}")
            else:
                logger.info(f"{service}: {status}")
        
        # Stop the service
        logger.info("\n=== Stopping Service ===")
        comm_service.stop()
        logger.info("Unified Communication Service stopped")
        
        logger.info("\n=== Test Completed Successfully ===")
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required services are properly implemented")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_protocol_specific():
    """Test individual protocols"""
    logger.info("Testing individual protocols...")
    
    # Test WebSocket
    try:
        from src.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        logger.info("WebSocket service created successfully")
    except Exception as e:
        logger.error(f"WebSocket service test failed: {e}")
    
    # Test MQTT
    try:
        from src.services.mqtt_service import MQTTService
        mqtt_service = MQTTService()
        logger.info("MQTT service created successfully")
    except Exception as e:
        logger.error(f"MQTT service test failed: {e}")
    
    # Test Data Processor
    try:
        from src.services.data_processor import DataProcessor
        data_processor = DataProcessor()
        logger.info("Data processor created successfully")
    except Exception as e:
        logger.error(f"Data processor test failed: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test Unified Communication System')
    parser.add_argument('--test-type', choices=['unified', 'protocols', 'all'], 
                       default='all', help='Type of test to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("LPR Server v3 - Unified Communication System Test")
    logger.info("=" * 60)
    
    if args.test_type in ['protocols', 'all']:
        test_protocol_specific()
    
    if args.test_type in ['unified', 'all']:
        test_unified_communication()
    
    logger.info("=" * 60)
    logger.info("All tests completed")

if __name__ == "__main__":
    main()
