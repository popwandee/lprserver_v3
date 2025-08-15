"""
Unified Communication Service for LPR Server v3

This service provides a unified interface for handling communication across multiple protocols:
- WebSocket (Socket.IO) - Primary for real-time communication
- REST API - Secondary for reliable communication
- MQTT - Fallback for IoT devices with limited connectivity
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from threading import Lock, Thread
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class ProtocolType(Enum):
    """Supported communication protocols"""
    WEBSOCKET = "websocket"
    REST_API = "rest_api"
    MQTT = "mqtt"

class ConnectivityLevel(Enum):
    """Connectivity quality levels"""
    EXCELLENT = "excellent"  # > 80% score
    GOOD = "good"           # 50-80% score
    POOR = "poor"           # < 50% score
    OFFLINE = "offline"     # No connectivity

class UnifiedCommunicationService:
    """
    Unified Communication Service that manages multiple protocols
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the unified communication service"""
        self.config = config or {}
        
        # Protocol services
        self.websocket_service = None
        self.mqtt_service = None
        self.rest_api_enabled = True
        
        # Communication state
        self.current_protocol = ProtocolType.WEBSOCKET
        self.connectivity_level = ConnectivityLevel.EXCELLENT
        
        # Protocol health scores (0.0 to 1.0)
        self.protocol_health = {
            ProtocolType.WEBSOCKET: 1.0,
            ProtocolType.REST_API: 1.0,
            ProtocolType.MQTT: 1.0
        }
        
        # Performance metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "protocol_switches": 0,
            "errors": 0,
            "last_activity": None
        }
        
        # Data processing
        self.message_queue = []
        self.queue_lock = Lock()
        
        # Callbacks
        self.on_detection_received = None
        self.on_health_update = None
        self.on_config_update = None
        self.on_control_command = None
        
        # Threading
        self.monitor_thread = None
        self.running = False
        
        logger.info("Unified Communication Service initialized")
    
    def start(self):
        """Start the unified communication service"""
        try:
            logger.info("Starting Unified Communication Service")
            self.running = True
            
            # Initialize protocol services
            self._initialize_services()
            
            # Start connectivity monitoring
            self.monitor_thread = Thread(target=self._connectivity_monitor, daemon=True)
            self.monitor_thread.start()
            
            logger.info("Unified Communication Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Unified Communication Service: {e}")
            return False
    
    def stop(self):
        """Stop the unified communication service"""
        try:
            logger.info("Stopping Unified Communication Service")
            self.running = False
            
            # Stop protocol services
            if self.websocket_service:
                self.websocket_service.disconnect()
            if self.mqtt_service:
                self.mqtt_service.disconnect()
            
            logger.info("Unified Communication Service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Unified Communication Service: {e}")
    
    def _initialize_services(self):
        """Initialize all protocol services"""
        try:
            # Initialize WebSocket service
            from .websocket_service import WebSocketService
            self.websocket_service = WebSocketService()
            self.websocket_service.on_detection_received = self._handle_detection
            self.websocket_service.on_health_update = self._handle_health
            self.websocket_service.on_config_update = self._handle_config
            self.websocket_service.on_control_command = self._handle_control
            
            # Initialize MQTT service
            from .mqtt_service import MQTTService
            self.mqtt_service = MQTTService()
            
            logger.info("Protocol services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize protocol services: {e}")
            raise
    
    def send_detection(self, detection_data: Dict[str, Any], edge_device_id: str) -> bool:
        """Send detection data using the best available protocol"""
        try:
            message = self._create_unified_message("detection", detection_data, edge_device_id)
            success = self._send_via_protocol(message, self.current_protocol)
            
            if success:
                self.metrics["messages_sent"] += 1
                self.metrics["last_activity"] = time.time()
            else:
                success = self._try_fallback_protocols(message)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending detection: {e}")
            self.metrics["errors"] += 1
            return False
    
    def send_health(self, health_data: Dict[str, Any], edge_device_id: str) -> bool:
        """
        Send health data using the best available protocol
        
        Args:
            health_data: Health data to send
            edge_device_id: ID of the edge device
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message = self._create_unified_message(
                data_type="health",
                payload=health_data,
                edge_device_id=edge_device_id
            )
            
            success = self._send_via_protocol(message, self.current_protocol)
            
            if success:
                self.metrics["messages_sent"] += 1
                self.metrics["last_activity"] = time.time()
            else:
                success = self._try_fallback_protocols(message)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending health data: {e}")
            self.metrics["errors"] += 1
            return False
    
    def send_config(self, config_data: Dict[str, Any], edge_device_id: str) -> bool:
        """
        Send configuration data using the best available protocol
        
        Args:
            config_data: Configuration data to send
            edge_device_id: ID of the edge device
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message = self._create_unified_message(
                data_type="config",
                payload=config_data,
                edge_device_id=edge_device_id
            )
            
            success = self._send_via_protocol(message, self.current_protocol)
            
            if success:
                self.metrics["messages_sent"] += 1
                self.metrics["last_activity"] = time.time()
            else:
                success = self._try_fallback_protocols(message)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending config data: {e}")
            self.metrics["errors"] += 1
            return False
    
    def send_control_command(self, command: str, parameters: Dict[str, Any], 
                           edge_device_id: str) -> bool:
        """
        Send control command using the best available protocol
        
        Args:
            command: Control command to send
            parameters: Command parameters
            edge_device_id: ID of the edge device
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            control_data = {
                "command": command,
                "parameters": parameters,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            message = self._create_unified_message(
                data_type="control",
                payload=control_data,
                edge_device_id=edge_device_id
            )
            
            success = self._send_via_protocol(message, self.current_protocol)
            
            if success:
                self.metrics["messages_sent"] += 1
                self.metrics["last_activity"] = time.time()
            else:
                success = self._try_fallback_protocols(message)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending control command: {e}")
            self.metrics["errors"] += 1
            return False
    
    def _create_unified_message(self, data_type: str, payload: Dict[str, Any], 
                               edge_device_id: str) -> Dict[str, Any]:
        """Create a unified message format for all protocols"""
        return {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "protocol": self.current_protocol.value,
            "edge_device_id": edge_device_id,
            "data_type": data_type,
            "payload": payload,
            "metadata": {
                "protocol_version": "1.0",
                "compression": False,
                "encryption": True,
                "connectivity_level": self.connectivity_level.value,
                "protocol_health": self.protocol_health[self.current_protocol]
            }
        }
    
    def _send_via_protocol(self, message: Dict[str, Any], protocol: ProtocolType) -> bool:
        """Send message via specific protocol"""
        try:
            if protocol == ProtocolType.WEBSOCKET:
                return self._send_via_websocket(message)
            elif protocol == ProtocolType.REST_API:
                return self._send_via_rest_api(message)
            elif protocol == ProtocolType.MQTT:
                return self._send_via_mqtt(message)
            else:
                logger.error(f"Unknown protocol: {protocol}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending via {protocol.value}: {e}")
            return False
    
    def _send_via_websocket(self, message: Dict[str, Any]) -> bool:
        """Send message via WebSocket"""
        try:
            if self.websocket_service and self.websocket_service.connected:
                data_type = message["data_type"]
                payload = message["payload"]
                edge_device_id = message["edge_device_id"]
                
                if data_type == "detection":
                    return self.websocket_service.send_detection(payload, edge_device_id)
                elif data_type == "health":
                    return self.websocket_service.send_health(payload, edge_device_id)
                elif data_type == "config":
                    return self.websocket_service.send_config(payload, edge_device_id)
                elif data_type == "control":
                    return self.websocket_service.send_control(payload, edge_device_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending via WebSocket: {e}")
            return False
    
    def _send_via_rest_api(self, message: Dict[str, Any]) -> bool:
        """Send message via REST API"""
        try:
            # Simulate REST API call
            logger.debug(f"REST API send: {message['data_type']} for {message['edge_device_id']}")
            return True  # Simulated success
            
        except Exception as e:
            logger.error(f"Error sending via REST API: {e}")
            return False
    
    def _send_via_mqtt(self, message: Dict[str, Any]) -> bool:
        """Send message via MQTT"""
        try:
            if self.mqtt_service and self.mqtt_service.connected:
                from mqtt_config import MQTTConfig
                data_type = message["data_type"]
                edge_device_id = message["edge_device_id"]
                
                if data_type == "detection":
                    topic = MQTTConfig.get_detection_topic(edge_device_id)
                    return self.mqtt_service.publish(topic, message, MQTTConfig.QOS_DETECTION)
                elif data_type == "health":
                    topic = MQTTConfig.get_health_topic(edge_device_id)
                    return self.mqtt_service.publish(topic, message, MQTTConfig.QOS_HEALTH, retain=True)
                elif data_type == "config":
                    topic = MQTTConfig.get_config_topic(edge_device_id)
                    return self.mqtt_service.publish(topic, message, MQTTConfig.QOS_CONFIG, retain=True)
                elif data_type == "control":
                    topic = MQTTConfig.get_control_topic(edge_device_id)
                    return self.mqtt_service.publish(topic, message, MQTTConfig.QOS_CONTROL)
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending via MQTT: {e}")
            return False
    
    def _try_fallback_protocols(self, message: Dict[str, Any]) -> bool:
        """Try sending message via fallback protocols"""
        fallback_order = [ProtocolType.REST_API, ProtocolType.MQTT]
        
        for protocol in fallback_order:
            if protocol != self.current_protocol:
                logger.info(f"Trying fallback protocol: {protocol.value}")
                if self._send_via_protocol(message, protocol):
                    self._switch_protocol(protocol, "fallback_success")
                    return True
        
        return False
    
    def _switch_protocol(self, new_protocol: ProtocolType, reason: str):
        """Switch to a different protocol"""
        if new_protocol != self.current_protocol:
            old_protocol = self.current_protocol
            self.current_protocol = new_protocol
            self.metrics["protocol_switches"] += 1
            
            logger.info(f"Protocol switched from {old_protocol.value} to {new_protocol.value} ({reason})")
    
    def _assess_connectivity(self) -> ConnectivityLevel:
        """Assess current connectivity level"""
        try:
            scores = []
            
            if self.websocket_service:
                ws_score = self.protocol_health[ProtocolType.WEBSOCKET]
                if self.websocket_service.connected:
                    scores.append(ws_score)
                else:
                    scores.append(0.0)
            
            rest_score = self.protocol_health[ProtocolType.REST_API]
            scores.append(rest_score)
            
            if self.mqtt_service:
                mqtt_score = self.protocol_health[ProtocolType.MQTT]
                if self.mqtt_service.connected:
                    scores.append(mqtt_score)
                else:
                    scores.append(0.0)
            
            if scores:
                avg_score = sum(scores) / len(scores)
                
                if avg_score >= 0.8:
                    return ConnectivityLevel.EXCELLENT
                elif avg_score >= 0.5:
                    return ConnectivityLevel.GOOD
                elif avg_score >= 0.2:
                    return ConnectivityLevel.POOR
                else:
                    return ConnectivityLevel.OFFLINE
            else:
                return ConnectivityLevel.OFFLINE
                
        except Exception as e:
            logger.error(f"Error assessing connectivity: {e}")
            return ConnectivityLevel.OFFLINE
    
    def _select_optimal_protocol(self) -> ProtocolType:
        """Select the optimal protocol based on current conditions"""
        connectivity = self._assess_connectivity()
        
        if connectivity == ConnectivityLevel.EXCELLENT:
            if self.protocol_health[ProtocolType.WEBSOCKET] >= 0.8:
                return ProtocolType.WEBSOCKET
            elif self.protocol_health[ProtocolType.REST_API] >= 0.8:
                return ProtocolType.REST_API
            else:
                return ProtocolType.MQTT
                
        elif connectivity == ConnectivityLevel.GOOD:
            if self.protocol_health[ProtocolType.REST_API] >= 0.6:
                return ProtocolType.REST_API
            elif self.protocol_health[ProtocolType.WEBSOCKET] >= 0.7:
                return ProtocolType.WEBSOCKET
            else:
                return ProtocolType.MQTT
                
        elif connectivity == ConnectivityLevel.POOR:
            if self.protocol_health[ProtocolType.MQTT] >= 0.5:
                return ProtocolType.MQTT
            elif self.protocol_health[ProtocolType.REST_API] >= 0.6:
                return ProtocolType.REST_API
            else:
                return ProtocolType.WEBSOCKET
                
        else:  # OFFLINE
            return ProtocolType.MQTT
    
    def _connectivity_monitor(self):
        """Monitor connectivity and adjust protocol selection"""
        while self.running:
            try:
                # Update connectivity level
                self.connectivity_level = self._assess_connectivity()
                
                # Select optimal protocol
                optimal_protocol = self._select_optimal_protocol()
                
                # Switch if necessary
                if optimal_protocol != self.current_protocol:
                    self._switch_protocol(optimal_protocol, "connectivity_optimization")
                
                # Update protocol health scores
                self._update_protocol_health()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in connectivity monitor: {e}")
                time.sleep(60)
    
    def _update_protocol_health(self):
        """Update health scores for all protocols"""
        try:
            if self.websocket_service:
                if self.websocket_service.connected:
                    self.protocol_health[ProtocolType.WEBSOCKET] = min(1.0, 
                        self.protocol_health[ProtocolType.WEBSOCKET] + 0.1)
                else:
                    self.protocol_health[ProtocolType.WEBSOCKET] = max(0.0, 
                        self.protocol_health[ProtocolType.WEBSOCKET] - 0.1)
            
            if self.mqtt_service:
                if self.mqtt_service.connected:
                    self.protocol_health[ProtocolType.MQTT] = min(1.0, 
                        self.protocol_health[ProtocolType.MQTT] + 0.1)
                else:
                    self.protocol_health[ProtocolType.MQTT] = max(0.0, 
                        self.protocol_health[ProtocolType.MQTT] - 0.1)
            
            self.protocol_health[ProtocolType.REST_API] = 0.9  # Simulated good health
            
        except Exception as e:
            logger.error(f"Error updating protocol health: {e}")
    
    def _start_data_processing(self):
        """Start the data processing pipeline"""
        try:
            # Initialize data processor
            from .data_processor import DataProcessor
            self.data_processor = DataProcessor()
            
            # Start processing thread
            processing_thread = Thread(target=self._process_queued_data, daemon=True)
            processing_thread.start()
            
            logger.info("Data processing pipeline started")
            
        except Exception as e:
            logger.error(f"Error starting data processing: {e}")
    
    def _process_queued_data(self):
        """Process queued data"""
        while self.running:
            try:
                with self.queue_lock:
                    if self.message_queue:
                        message = self.message_queue.pop(0)
                        self._process_message(message)
                
                time.sleep(0.1)  # Process every 100ms
                
            except Exception as e:
                logger.error(f"Error processing queued data: {e}")
                time.sleep(1)
    
    def _process_message(self, message: Dict[str, Any]):
        """Process a single message"""
        try:
            if self.data_processor:
                from .data_processor import DataProcessor
                self.data_processor.process_incoming_data(message, message.get("protocol"))
            
            self.metrics["messages_received"] += 1
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _handle_detection(self, detection_data: Dict[str, Any], edge_device_id: str):
        """Handle detection data from any protocol"""
        try:
            message = self._create_unified_message("detection", detection_data, edge_device_id)
            
            with self.queue_lock:
                self.message_queue.append(message)
            
            if self.on_detection_received:
                self.on_detection_received(detection_data, edge_device_id)
            
        except Exception as e:
            logger.error(f"Error handling detection: {e}")
    
    def _handle_health(self, health_data: Dict[str, Any], edge_device_id: str):
        """Handle health data from any protocol"""
        try:
            message = self._create_unified_message("health", health_data, edge_device_id)
            
            with self.queue_lock:
                self.message_queue.append(message)
            
            if self.on_health_update:
                self.on_health_update(health_data, edge_device_id)
            
        except Exception as e:
            logger.error(f"Error handling health data: {e}")
    
    def _handle_config(self, config_data: Dict[str, Any], edge_device_id: str):
        """Handle configuration data from any protocol"""
        try:
            message = self._create_unified_message("config", config_data, edge_device_id)
            
            with self.queue_lock:
                self.message_queue.append(message)
            
            if self.on_config_update:
                self.on_config_update(config_data, edge_device_id)
            
        except Exception as e:
            logger.error(f"Error handling config data: {e}")
    
    def _handle_control(self, control_data: Dict[str, Any], edge_device_id: str):
        """Handle control commands from any protocol"""
        try:
            message = self._create_unified_message("control", control_data, edge_device_id)
            
            with self.queue_lock:
                self.message_queue.append(message)
            
            if self.on_control_command:
                self.on_control_command(control_data, edge_device_id)
            
        except Exception as e:
            logger.error(f"Error handling control command: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of the communication service"""
        return {
            "status": "healthy" if self.running else "stopped",
            "timestamp": datetime.utcnow().isoformat(),
            "current_protocol": self.current_protocol.value,
            "connectivity_level": self.connectivity_level.value,
            "protocol_health": {
                protocol.value: health 
                for protocol, health in self.protocol_health.items()
            },
            "metrics": self.metrics.copy(),
            "queue_size": len(self.message_queue),
            "services": {
                "websocket": {
                    "connected": self.websocket_service.connected if self.websocket_service else False,
                    "health": self.protocol_health[ProtocolType.WEBSOCKET]
                },
                "mqtt": {
                    "connected": self.mqtt_service.connected if self.mqtt_service else False,
                    "health": self.protocol_health[ProtocolType.MQTT]
                },
                "rest_api": {
                    "enabled": self.rest_api_enabled,
                    "health": self.protocol_health[ProtocolType.REST_API]
                }
            }
        }
