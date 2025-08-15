#!/usr/bin/env python3
"""
Edge Device Simulator for LPR Server v3

This simulator creates virtual LPR cameras that send data via:
- WebSocket (Socket.IO)
- REST API (HTTP)
- MQTT (Message Queue)

Each protocol sends the same data format to test the unified processing system.
"""

import json
import time
import uuid
import random
import logging
import argparse
import threading
from datetime import datetime
from typing import Dict, Any, List
import requests
import socketio
import paho.mqtt.client as mqtt
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class EdgeDeviceConfig:
    """Configuration for edge device simulation"""
    device_id: str
    protocol: str  # websocket, rest_api, mqtt
    interval: int  # seconds between messages
    enabled: bool = True
    location: str = "Unknown"
    camera_type: str = "LPR"

class EdgeDeviceSimulator:
    """Simulates an LPR edge device sending data via different protocols"""
    
    def __init__(self, config: EdgeDeviceConfig):
        self.config = config
        self.running = False
        self.thread = None
        
        # Protocol clients
        self.sio = None
        self.mqtt_client = None
        self.rest_session = requests.Session()
        
        # Message counters
        self.message_count = 0
        self.last_sent = None
        
        logger.info(f"Edge device {config.device_id} initialized for {config.protocol}")
    
    def start(self):
        """Start the edge device simulator"""
        if self.running:
            return
        
        self.running = True
        
        # Initialize protocol client
        if self.config.protocol == "websocket":
            self._init_websocket()
        elif self.config.protocol == "mqtt":
            self._init_mqtt()
        elif self.config.protocol == "rest_api":
            self._init_rest_api()
        
        # Start sending thread
        self.thread = threading.Thread(target=self._send_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"Edge device {self.config.device_id} started")
    
    def stop(self):
        """Stop the edge device simulator"""
        self.running = False
        
        if self.sio:
            self.sio.disconnect()
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        logger.info(f"Edge device {self.config.device_id} stopped")
    
    def _init_websocket(self):
        """Initialize WebSocket client"""
        try:
            self.sio = socketio.Client()
            
            @self.sio.event
            def connect():
                logger.info(f"WebSocket connected for {self.config.device_id}")
            
            @self.sio.event
            def disconnect():
                logger.info(f"WebSocket disconnected for {self.config.device_id}")
            
            self.sio.connect('http://localhost:5000')
            
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket for {self.config.device_id}: {e}")
    
    def _init_mqtt(self):
        """Initialize MQTT client"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_publish = self._on_mqtt_publish
            
            self.mqtt_client.connect("localhost", 1883, 60)
            self.mqtt_client.loop_start()
            
        except Exception as e:
            logger.error(f"Failed to initialize MQTT for {self.config.device_id}: {e}")
    
    def _init_rest_api(self):
        """Initialize REST API client"""
        self.rest_session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'LPR-Edge-{self.config.device_id}'
        })
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT connected for {self.config.device_id} with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        logger.info(f"MQTT disconnected for {self.config.device_id} with code {rc}")
    
    def _on_mqtt_publish(self, client, userdata, mid):
        logger.debug(f"MQTT message published for {self.config.device_id}")
    
    def _send_loop(self):
        """Main sending loop"""
        while self.running:
            try:
                # Generate and send data
                self._send_detection()
                time.sleep(self.config.interval)
                
                # Send health update every 5 cycles
                if self.message_count % 5 == 0:
                    self._send_health()
                
                # Send config update every 10 cycles
                if self.message_count % 10 == 0:
                    self._send_config()
                
                self.message_count += 1
                
            except Exception as e:
                logger.error(f"Error in send loop for {self.config.device_id}: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _send_detection(self):
        """Send detection data"""
        detection_data = self._create_detection_data()
        
        if self.config.protocol == "websocket":
            self._send_websocket_detection(detection_data)
        elif self.config.protocol == "rest_api":
            self._send_rest_detection(detection_data)
        elif self.config.protocol == "mqtt":
            self._send_mqtt_detection(detection_data)
    
    def _send_health(self):
        """Send health data"""
        health_data = self._create_health_data()
        
        if self.config.protocol == "websocket":
            self._send_websocket_health(health_data)
        elif self.config.protocol == "rest_api":
            self._send_rest_health(health_data)
        elif self.config.protocol == "mqtt":
            self._send_mqtt_health(health_data)
    
    def _send_config(self):
        """Send configuration data"""
        config_data = self._create_config_data()
        
        if self.config.protocol == "websocket":
            self._send_websocket_config(config_data)
        elif self.config.protocol == "rest_api":
            self._send_rest_config(config_data)
        elif self.config.protocol == "mqtt":
            self._send_mqtt_config(config_data)
    
    def _create_detection_data(self) -> Dict[str, Any]:
        """Create sample detection data"""
        # Generate random plate number
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        numbers = ''.join(random.choices('0123456789', k=4))
        plate_number = f"{letters}{numbers}"
        
        # Random vehicle data
        vehicle_types = ["sedan", "suv", "truck", "motorcycle", "bus"]
        colors = ["white", "black", "red", "blue", "silver", "gray"]
        brands = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Nissan"]
        
        return {
            "detection_data": {
                "vehicles_count": random.randint(1, 3),
                "plates_count": random.randint(1, 2),
                "processing_time_ms": random.randint(100, 300),
                "confidence_score": round(random.uniform(0.7, 0.99), 2),
                "detection_type": "lpr",
                "vehicles": [
                    {
                        "vehicle_index": 0,
                        "bbox": [random.randint(50, 200), random.randint(50, 200), 
                                random.randint(250, 400), random.randint(250, 400)],
                        "confidence": round(random.uniform(0.8, 0.98), 2),
                        "vehicle_class": "car",
                        "vehicle_type": random.choice(vehicle_types),
                        "color": random.choice(colors),
                        "brand": random.choice(brands),
                        "model": f"Model{random.randint(2015, 2024)}",
                        "year": random.randint(2015, 2024)
                    }
                ],
                "plates": [
                    {
                        "plate_index": 0,
                        "vehicle_id": 0,
                        "plate_number": plate_number,
                        "bbox": [random.randint(150, 180), random.randint(120, 140), 
                                random.randint(180, 220), random.randint(140, 160)],
                        "confidence": round(random.uniform(0.8, 0.95), 2),
                        "plate_type": "standard",
                        "country": "TH",
                        "province": "Bangkok",
                        "is_valid": True
                    }
                ]
            },
            "metadata": {
                "image_path": f"/storage/images/{self.config.device_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                "weather": random.choice(["clear", "cloudy", "rainy"]),
                "lighting": random.choice(["daylight", "night", "artificial"]),
                "temperature": round(random.uniform(20, 35), 1)
            }
        }
    
    def _create_health_data(self) -> Dict[str, Any]:
        """Create sample health data"""
        return {
            "health_status": random.choice(["healthy", "warning", "error"]),
            "health_details": {
                "cpu_usage": round(random.uniform(20, 80), 1),
                "memory_usage": round(random.uniform(30, 90), 1),
                "disk_usage": round(random.uniform(10, 50), 1),
                "network_status": random.choice(["connected", "disconnected", "poor"]),
                "camera_status": random.choice(["active", "inactive", "error"]),
                "last_detection": datetime.utcnow().isoformat(),
                "uptime_seconds": random.randint(3600, 86400),
                "temperature": round(random.uniform(35, 55), 1)
            },
            "alerts": []
        }
    
    def _create_config_data(self) -> Dict[str, Any]:
        """Create sample configuration data"""
        return {
            "config_type": "detection_settings",
            "config_data": {
                "detection_interval": random.randint(800, 1200),
                "confidence_threshold": round(random.uniform(0.7, 0.9), 1),
                "max_vehicles_per_frame": random.randint(3, 8),
                "image_quality": random.choice(["high", "medium", "low"]),
                "enable_recording": random.choice([True, False]),
                "recording_duration": random.randint(20, 60),
                "alert_settings": {
                    "enable_alerts": True,
                    "alert_confidence_threshold": round(random.uniform(0.8, 0.95), 2),
                    "notification_channels": ["websocket", "rest_api", "mqtt"]
                }
            }
        }
    
    def _send_websocket_detection(self, data: Dict[str, Any]):
        """Send detection via WebSocket"""
        if self.sio and self.sio.connected:
            self.sio.emit('detection', {
                'device_id': self.config.device_id,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f"WebSocket detection sent from {self.config.device_id}")
    
    def _send_websocket_health(self, data: Dict[str, Any]):
        """Send health via WebSocket"""
        if self.sio and self.sio.connected:
            self.sio.emit('health', {
                'device_id': self.config.device_id,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f"WebSocket health sent from {self.config.device_id}")
    
    def _send_websocket_config(self, data: Dict[str, Any]):
        """Send config via WebSocket"""
        if self.sio and self.sio.connected:
            self.sio.emit('config', {
                'device_id': self.config.device_id,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.info(f"WebSocket config sent from {self.config.device_id}")
    
    def _send_rest_detection(self, data: Dict[str, Any]):
        """Send detection via REST API"""
        try:
            response = self.rest_session.post(
                'http://localhost:5000/api/v1/detection',
                json={
                    'device_id': self.config.device_id,
                    'data': data,
                    'timestamp': datetime.utcnow().isoformat()
                },
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"REST detection sent from {self.config.device_id}")
            else:
                logger.warning(f"REST detection failed from {self.config.device_id}: {response.status_code}")
        except Exception as e:
            logger.error(f"REST detection error from {self.config.device_id}: {e}")
    
    def _send_rest_health(self, data: Dict[str, Any]):
        """Send health via REST API"""
        try:
            response = self.rest_session.post(
                'http://localhost:5000/api/v1/health',
                json={
                    'device_id': self.config.device_id,
                    'data': data,
                    'timestamp': datetime.utcnow().isoformat()
                },
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"REST health sent from {self.config.device_id}")
        except Exception as e:
            logger.error(f"REST health error from {self.config.device_id}: {e}")
    
    def _send_rest_config(self, data: Dict[str, Any]):
        """Send config via REST API"""
        try:
            response = self.rest_session.post(
                'http://localhost:5000/api/v1/config',
                json={
                    'device_id': self.config.device_id,
                    'data': data,
                    'timestamp': datetime.utcnow().isoformat()
                },
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"REST config sent from {self.config.device_id}")
        except Exception as e:
            logger.error(f"REST config error from {self.config.device_id}: {e}")
    
    def _send_mqtt_detection(self, data: Dict[str, Any]):
        """Send detection via MQTT"""
        if self.mqtt_client and self.mqtt_client.is_connected():
            topic = f"lprserver/cameras/{self.config.device_id}/detection"
            message = {
                'device_id': self.config.device_id,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.mqtt_client.publish(topic, json.dumps(message), qos=1)
            logger.info(f"MQTT detection sent from {self.config.device_id}")
    
    def _send_mqtt_health(self, data: Dict[str, Any]):
        """Send health via MQTT"""
        if self.mqtt_client and self.mqtt_client.is_connected():
            topic = f"lprserver/cameras/{self.config.device_id}/health"
            message = {
                'device_id': self.config.device_id,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.mqtt_client.publish(topic, json.dumps(message), qos=1, retain=True)
            logger.info(f"MQTT health sent from {self.config.device_id}")
    
    def _send_mqtt_config(self, data: Dict[str, Any]):
        """Send config via MQTT"""
        if self.mqtt_client and self.mqtt_client.is_connected():
            topic = f"lprserver/cameras/{self.config.device_id}/config"
            message = {
                'device_id': self.config.device_id,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.mqtt_client.publish(topic, json.dumps(message), qos=1, retain=True)
            logger.info(f"MQTT config sent from {self.config.device_id}")

class EdgeSimulatorManager:
    """Manages multiple edge device simulators"""
    
    def __init__(self):
        self.devices: List[EdgeDeviceSimulator] = []
        self.running = False
    
    def add_device(self, config: EdgeDeviceConfig):
        """Add a new edge device"""
        device = EdgeDeviceSimulator(config)
        self.devices.append(device)
        logger.info(f"Added edge device: {config.device_id} ({config.protocol})")
    
    def start_all(self):
        """Start all edge devices"""
        self.running = True
        for device in self.devices:
            if device.config.enabled:
                device.start()
        logger.info(f"Started {len(self.devices)} edge devices")
    
    def stop_all(self):
        """Stop all edge devices"""
        self.running = False
        for device in self.devices:
            device.stop()
        logger.info("Stopped all edge devices")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all devices"""
        return {
            "running": self.running,
            "device_count": len(self.devices),
            "devices": [
                {
                    "device_id": device.config.device_id,
                    "protocol": device.config.protocol,
                    "enabled": device.config.enabled,
                    "message_count": device.message_count,
                    "last_sent": device.last_sent
                }
                for device in self.devices
            ]
        }

def create_test_scenario() -> EdgeSimulatorManager:
    """Create a test scenario with multiple edge devices"""
    manager = EdgeSimulatorManager()
    
    # Urban environment - WebSocket
    manager.add_device(EdgeDeviceConfig(
        device_id="CAM001",
        protocol="websocket",
        interval=3,
        location="Bangkok Downtown",
        camera_type="LPR"
    ))
    
    manager.add_device(EdgeDeviceConfig(
        device_id="CAM002",
        protocol="websocket",
        interval=4,
        location="Bangkok Airport",
        camera_type="LPR"
    ))
    
    # Suburban environment - REST API
    manager.add_device(EdgeDeviceConfig(
        device_id="CAM003",
        protocol="rest_api",
        interval=5,
        location="Bangkok Suburbs",
        camera_type="LPR"
    ))
    
    manager.add_device(EdgeDeviceConfig(
        device_id="CAM004",
        protocol="rest_api",
        interval=6,
        location="Bangkok Industrial",
        camera_type="LPR"
    ))
    
    # Rural environment - MQTT
    manager.add_device(EdgeDeviceConfig(
        device_id="CAM005",
        protocol="mqtt",
        interval=8,
        location="Bangkok Rural",
        camera_type="LPR"
    ))
    
    return manager

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Edge Device Simulator')
    parser.add_argument('--duration', type=int, default=300, 
                       help='Simulation duration in seconds (default: 300)')
    parser.add_argument('--devices', type=int, default=5,
                       help='Number of devices to simulate (default: 5)')
    parser.add_argument('--protocol', choices=['websocket', 'rest_api', 'mqtt', 'all'],
                       default='all', help='Protocol to use (default: all)')
    parser.add_argument('--interval', type=int, default=5,
                       help='Message interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    logger.info("Starting Edge Device Simulator")
    logger.info(f"Duration: {args.duration}s, Devices: {args.devices}, Protocol: {args.protocol}")
    
    # Create simulator manager
    manager = EdgeSimulatorManager()
    
    # Add devices based on arguments
    if args.protocol == "all":
        protocols = ["websocket", "rest_api", "mqtt"]
    else:
        protocols = [args.protocol]
    
    for i in range(args.devices):
        device_id = f"CAM{str(i+1).zfill(3)}"
        protocol = protocols[i % len(protocols)]
        
        manager.add_device(EdgeDeviceConfig(
            device_id=device_id,
            protocol=protocol,
            interval=args.interval,
            location=f"Location {i+1}",
            camera_type="LPR"
        ))
    
    try:
        # Start all devices
        manager.start_all()
        
        # Run for specified duration
        logger.info(f"Running simulation for {args.duration} seconds...")
        time.sleep(args.duration)
        
        # Get final status
        status = manager.get_status()
        logger.info(f"Simulation completed. Total messages: {sum(d['message_count'] for d in status['devices'])}")
        
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    finally:
        # Stop all devices
        manager.stop_all()
        logger.info("Simulation ended")

if __name__ == "__main__":
    main()
