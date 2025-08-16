#!/usr/bin/env python3
"""
MQTT Test Client for LPR Server v3

This script provides a test client for testing MQTT communication with the LPR Server v3.
It can simulate camera devices and test various MQTT functionalities.
"""

import json
import time
import uuid
import argparse
import logging
from datetime import datetime
from typing import Dict, Any
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from mqtt_config import MQTTConfig, QOS_DETECTION, QOS_HEALTH, QOS_CONFIG, QOS_CONTROL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MQTTTestClient:
    """
    MQTT Test Client for testing LPR Server v3 MQTT communication
    
    This client can simulate:
    - Camera detection messages
    - Health status updates
    - Configuration updates
    - Control command responses
    """
    
    def __init__(self, client_id: str, camera_id: str, broker_host: str = None, 
                 broker_port: int = None, username: str = None, password: str = None):
        """
        Initialize MQTT Test Client
        
        Args:
            client_id: Unique client identifier
            camera_id: Camera ID to simulate
            broker_host: MQTT broker host
            broker_port: MQTT broker port
            username: MQTT username
            password: MQTT password
        """
        self.client_id = client_id
        self.camera_id = camera_id
        self.broker_host = broker_host or MQTTConfig.BROKER_HOST
        self.broker_port = broker_port or MQTTConfig.BROKER_PORT
        self.username = username or MQTTConfig.MQTT_USERNAME
        self.password = password or MQTTConfig.MQTT_PASSWORD
        
        # Connection state
        self.connected = False
        self.messages_sent = 0
        self.messages_received = 0
        
        # Initialize MQTT client
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
            clean_session=True
        )
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_log = self._on_log
        
        # Set authentication
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Set TLS if enabled
        if MQTTConfig.MQTT_TLS_ENABLED:
            self.client.tls_set(
                ca_certs=MQTTConfig.MQTT_CA_CERT,
                certfile=MQTTConfig.MQTT_CLIENT_CERT,
                keyfile=MQTTConfig.MQTT_CLIENT_KEY,
                tls_version=2
            )
        
        logger.info(f"MQTT Test Client initialized: {self.client_id} (Camera: {self.camera_id})")
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            logger.info(f"Connecting to MQTT broker {self.broker_host}:{self.broker_port}")
            
            result = self.client.connect(
                self.broker_host, 
                self.broker_port, 
                keepalive=MQTTConfig.MQTT_KEEPALIVE
            )
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.client.loop_start()
                logger.info("MQTT connection initiated successfully")
                return True
            else:
                logger.error(f"Failed to connect to MQTT broker: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            logger.info("Disconnecting from MQTT broker")
            self.connected = False
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def subscribe_to_control(self):
        """Subscribe to control topics"""
        control_topic = MQTTConfig.get_control_topic(self.camera_id)
        result, mid = self.client.subscribe(control_topic, QOS_CONTROL)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Subscribed to control topic: {control_topic}")
        else:
            logger.error(f"Failed to subscribe to control topic: {result}")
    
    def send_detection_message(self, plate_number: str = None, confidence: float = 0.95):
        """Send a detection message"""
        topic = MQTTConfig.get_detection_topic(self.camera_id)
        
        # Generate random plate number if not provided
        if not plate_number:
            import random
            letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
            numbers = ''.join(random.choices('0123456789', k=4))
            plate_number = f"{letters}{numbers}"
        
        message = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "camera_id": self.camera_id,
            "checkpoint_id": "CP001",
            "detection_data": {
                "vehicles_count": 1,
                "plates_count": 1,
                "processing_time_ms": 150,
                "confidence_score": confidence,
                "detection_type": "lpr",
                "vehicles": [
                    {
                        "vehicle_index": 0,
                        "bbox": [100, 100, 200, 200],
                        "confidence": confidence,
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
                        "plate_number": plate_number,
                        "bbox": [150, 120, 180, 140],
                        "confidence": confidence,
                        "plate_type": "standard",
                        "country": "TH",
                        "province": "Bangkok",
                        "is_valid": True
                    }
                ]
            },
            "metadata": {
                "image_path": f"/storage/images/{self.camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                "weather": "clear",
                "lighting": "daylight"
            }
        }
        
        payload = json.dumps(message, ensure_ascii=False)
        result, mid = self.client.publish(topic, payload, QOS_DETECTION)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.messages_sent += 1
            logger.info(f"Detection message sent: {plate_number} (confidence: {confidence})")
            return True
        else:
            logger.error(f"Failed to send detection message: {result}")
            return False
    
    def send_health_message(self, status: str = "healthy"):
        """Send a health status message"""
        topic = MQTTConfig.get_health_topic(self.camera_id)
        
        message = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "camera_id": self.camera_id,
            "health_status": status,
            "health_details": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.1,
                "network_status": "connected",
                "camera_status": "active",
                "last_detection": datetime.utcnow().isoformat(),
                "uptime_seconds": 86400,
                "temperature": 42.5
            },
            "alerts": []
        }
        
        payload = json.dumps(message, ensure_ascii=False)
        result, mid = self.client.publish(topic, payload, QOS_HEALTH, retain=True)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.messages_sent += 1
            logger.info(f"Health message sent: {status}")
            return True
        else:
            logger.error(f"Failed to send health message: {result}")
            return False
    
    def send_config_message(self, config_type: str = "detection_settings"):
        """Send a configuration message"""
        topic = MQTTConfig.get_config_topic(self.camera_id)
        
        message = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "camera_id": self.camera_id,
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
                    "notification_channels": ["mqtt", "email"]
                }
            }
        }
        
        payload = json.dumps(message, ensure_ascii=False)
        result, mid = self.client.publish(topic, payload, QOS_CONFIG, retain=True)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.messages_sent += 1
            logger.info(f"Config message sent: {config_type}")
            return True
        else:
            logger.error(f"Failed to send config message: {result}")
            return False
    
    def send_control_response(self, original_message_id: str, command: str, status: str = "executed"):
        """Send a control command response"""
        topic = f"lprserver/cameras/{self.camera_id}/control/response"
        
        message = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "original_message_id": original_message_id,
            "command": command,
            "status": status,
            "camera_id": self.camera_id,
            "result": {
                "success": status == "executed",
                "message": f"Command {command} {status}",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        payload = json.dumps(message, ensure_ascii=False)
        result, mid = self.client.publish(topic, payload, QOS_CONTROL)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.messages_sent += 1
            logger.info(f"Control response sent: {command} - {status}")
            return True
        else:
            logger.error(f"Failed to send control response: {result}")
            return False
    
    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback for successful connection"""
        if reason_code == 0:
            self.connected = True
            logger.info("Successfully connected to MQTT broker")
            
            # Subscribe to control topics
            self.subscribe_to_control()
        else:
            logger.error(f"Failed to connect to MQTT broker: {reason_code}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, reason_code, properties=None):
        """Callback for disconnection"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for received messages"""
        try:
            self.messages_received += 1
            
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.info(f"Received message on topic {topic}: {payload[:200]}...")
            
            # Parse JSON payload
            try:
                message_data = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON message: {e}")
                return
            
            # Handle control commands
            if "control" in topic:
                self._handle_control_command(message_data)
                
        except Exception as e:
            logger.error(f"Error processing received message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for successful message publish"""
        logger.debug(f"Message published successfully (MID: {mid})")
    
    def _on_log(self, client, userdata, level, buf):
        """Callback for MQTT client logs"""
        if MQTTConfig.MQTT_ENABLE_DEBUG:
            logger.debug(f"MQTT Log: {buf}")
    
    def _handle_control_command(self, message: Dict[str, Any]):
        """Handle received control command"""
        try:
            command = message.get('command')
            message_id = message.get('message_id')
            
            logger.info(f"Received control command: {command}")
            
            # Send response based on command
            if command == MQTTConfig.COMMAND_RESTART_CAMERA:
                self.send_control_response(message_id, command, "executed")
            elif command == MQTTConfig.COMMAND_STOP_CAMERA:
                self.send_control_response(message_id, command, "executed")
            elif command == MQTTConfig.COMMAND_START_CAMERA:
                self.send_control_response(message_id, command, "executed")
            elif command == MQTTConfig.COMMAND_GET_STATUS:
                self.send_control_response(message_id, command, "executed")
            elif command == MQTTConfig.COMMAND_GET_HEALTH:
                self.send_control_response(message_id, command, "executed")
            else:
                self.send_control_response(message_id, command, "unknown_command")
                
        except Exception as e:
            logger.error(f"Error handling control command: {e}")

def main():
    """Main function for MQTT test client"""
    parser = argparse.ArgumentParser(description='MQTT Test Client for LPR Server v3')
    parser.add_argument('--client-id', default=f'test_client_{uuid.uuid4().hex[:8]}', 
                       help='MQTT client ID')
    parser.add_argument('--camera-id', default='CAM001', help='Camera ID to simulate')
    parser.add_argument('--broker-host', default=MQTTConfig.BROKER_HOST, 
                       help='MQTT broker host')
    parser.add_argument('--broker-port', type=int, default=MQTTConfig.BROKER_PORT, 
                       help='MQTT broker port')
    parser.add_argument('--username', default=MQTTConfig.MQTT_USERNAME, 
                       help='MQTT username')
    parser.add_argument('--password', default=MQTTConfig.MQTT_PASSWORD, 
                       help='MQTT password')
    parser.add_argument('--mode', choices=['detection', 'health', 'config', 'interactive'], 
                       default='interactive', help='Test mode')
    parser.add_argument('--count', type=int, default=10, 
                       help='Number of messages to send')
    parser.add_argument('--interval', type=float, default=2.0, 
                       help='Interval between messages (seconds)')
    
    args = parser.parse_args()
    
    # Create test client
    client = MQTTTestClient(
        client_id=args.client_id,
        camera_id=args.camera_id,
        broker_host=args.broker_host,
        broker_port=args.broker_port,
        username=args.username,
        password=args.password
    )
    
    try:
        # Connect to broker
        if not client.connect():
            logger.error("Failed to connect to MQTT broker")
            return
        
        # Wait for connection
        time.sleep(2)
        
        if args.mode == 'detection':
            # Send detection messages
            logger.info(f"Sending {args.count} detection messages...")
            for i in range(args.count):
                plate_number = f"ABC{1000 + i}"
                client.send_detection_message(plate_number, 0.9 + (i % 10) * 0.01)
                time.sleep(args.interval)
                
        elif args.mode == 'health':
            # Send health messages
            logger.info(f"Sending {args.count} health messages...")
            for i in range(args.count):
                status = "healthy" if i % 3 != 0 else "warning"
                client.send_health_message(status)
                time.sleep(args.interval)
                
        elif args.mode == 'config':
            # Send config messages
            logger.info(f"Sending {args.count} config messages...")
            for i in range(args.count):
                config_type = f"config_type_{i % 3}"
                client.send_config_message(config_type)
                time.sleep(args.interval)
                
        elif args.mode == 'interactive':
            # Interactive mode
            logger.info("Interactive mode - Press Enter to send messages")
            logger.info("Commands: d=detection, h=health, c=config, q=quit")
            
            while True:
                try:
                    command = input("Enter command (d/h/c/q): ").strip().lower()
                    
                    if command == 'q':
                        break
                    elif command == 'd':
                        plate_number = input("Enter plate number (or press Enter for random): ").strip()
                        if not plate_number:
                            plate_number = None
                        client.send_detection_message(plate_number)
                    elif command == 'h':
                        status = input("Enter health status (healthy/warning/error): ").strip()
                        if not status:
                            status = "healthy"
                        client.send_health_message(status)
                    elif command == 'c':
                        config_type = input("Enter config type: ").strip()
                        if not config_type:
                            config_type = "detection_settings"
                        client.send_config_message(config_type)
                    else:
                        logger.info("Invalid command. Use: d=detection, h=health, c=config, q=quit")
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
        
        # Print statistics
        logger.info(f"Test completed. Messages sent: {client.messages_sent}, received: {client.messages_received}")
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
