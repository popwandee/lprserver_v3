"""
MQTT Service for LPR Server v3

This module provides MQTT communication functionality for the LPR Server v3,
including connection management, message handling, and error recovery.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Callable, Optional, List
from threading import Lock, Thread
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from mqtt_config import MQTTConfig, QOS_DETECTION, QOS_HEALTH, QOS_CONFIG, QOS_CONTROL

# Configure logging
logger = logging.getLogger(__name__)

class MQTTService:
    """
    MQTT Service for handling communication with MQTT broker
    
    This class provides a robust MQTT client implementation with:
    - Automatic reconnection
    - Message queuing
    - Error handling
    - Health monitoring
    - Message validation
    """
    
    def __init__(self, broker_host: str = None, broker_port: int = None, 
                 username: str = None, password: str = None):
        """
        Initialize MQTT Service
        
        Args:
            broker_host: MQTT broker host (defaults to config)
            broker_port: MQTT broker port (defaults to config)
            username: MQTT username (defaults to config)
            password: MQTT password (defaults to config)
        """
        # Use provided parameters or defaults from config
        self.broker_host = broker_host or MQTTConfig.BROKER_HOST
        self.broker_port = broker_port or MQTTConfig.BROKER_PORT
        self.username = username or MQTTConfig.MQTT_USERNAME
        self.password = password or MQTTConfig.MQTT_PASSWORD
        self.client_id = MQTTConfig.MQTT_CLIENT_ID
        
        # Connection state
        self.connected = False
        self.connection_attempts = 0
        self.last_connection_attempt = 0
        
        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self.message_queue: List[Dict[str, Any]] = []
        self.queue_lock = Lock()
        
        # Metrics
        self.messages_sent = 0
        self.messages_received = 0
        self.messages_failed = 0
        self.last_message_time = None
        
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
        self.client.on_subscribe = self._on_subscribe
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
                tls_version=2  # TLSv1.2
            )
        
        # Set connection parameters
        self.client.keepalive = MQTTConfig.MQTT_KEEPALIVE
        self.client.max_inflight_messages = MQTTConfig.MQTT_MAX_INFLIGHT
        self.client.max_queued_messages = MQTTConfig.MQTT_MAX_QUEUED_MESSAGES
        
        # Start connection monitoring thread
        self.monitor_thread = Thread(target=self._connection_monitor, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"MQTT Service initialized for broker {self.broker_host}:{self.broker_port}")
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker with retry logic
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MQTT broker {self.broker_host}:{self.broker_port}")
            
            # Connect to broker
            result = self.client.connect(
                self.broker_host, 
                self.broker_port, 
                keepalive=MQTTConfig.MQTT_KEEPALIVE
            )
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                # Start the network loop
                self.client.loop_start()
                self.connection_attempts = 0
                logger.info("MQTT connection initiated successfully")
                return True
            else:
                logger.error(f"Failed to connect to MQTT broker: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            self.connection_attempts += 1
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
    
    def subscribe(self, topic: str, qos: int = 1, callback: Callable = None) -> bool:
        """
        Subscribe to MQTT topic
        
        Args:
            topic: MQTT topic to subscribe to
            qos: Quality of Service level (0, 1, or 2)
            callback: Optional callback function for message handling
            
        Returns:
            bool: True if subscription successful, False otherwise
        """
        try:
            if not self.connected:
                logger.warning("Cannot subscribe: not connected to MQTT broker")
                return False
            
            # Subscribe to topic
            result, mid = self.client.subscribe(topic, qos)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Subscribed to topic: {topic} (QoS: {qos})")
                
                # Register callback if provided
                if callback:
                    self.message_handlers[topic] = callback
                
                return True
            else:
                logger.error(f"Failed to subscribe to topic {topic}: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error subscribing to topic {topic}: {e}")
            return False
    
    def publish(self, topic: str, message: Dict[str, Any], qos: int = 1, 
                retain: bool = False) -> bool:
        """
        Publish message to MQTT topic
        
        Args:
            topic: MQTT topic to publish to
            message: Message data to publish
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether to retain the message
            
        Returns:
            bool: True if publish successful, False otherwise
        """
        try:
            # Add message metadata
            if isinstance(message, dict):
                if 'message_id' not in message:
                    message['message_id'] = str(uuid.uuid4())
                if 'timestamp' not in message:
                    message['timestamp'] = datetime.utcnow().isoformat()
            
            # Convert message to JSON
            payload = json.dumps(message, ensure_ascii=False)
            
            if not self.connected:
                # Queue message for later delivery
                with self.queue_lock:
                    self.message_queue.append({
                        'topic': topic,
                        'payload': payload,
                        'qos': qos,
                        'retain': retain,
                        'timestamp': time.time()
                    })
                logger.debug(f"Message queued for topic {topic} (not connected)")
                return True
            
            # Publish message
            result, mid = self.client.publish(topic, payload, qos, retain)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.messages_sent += 1
                self.last_message_time = time.time()
                logger.debug(f"Message published to topic {topic} (QoS: {qos})")
                return True
            else:
                self.messages_failed += 1
                logger.error(f"Failed to publish message to topic {topic}: {result}")
                return False
                
        except Exception as e:
            self.messages_failed += 1
            logger.error(f"Error publishing message to topic {topic}: {e}")
            return False
    
    def register_handler(self, topic: str, handler: Callable):
        """
        Register message handler for specific topic
        
        Args:
            topic: MQTT topic pattern
            handler: Callback function to handle messages
        """
        self.message_handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get MQTT service health status
        
        Returns:
            Dict containing health status information
        """
        return {
            "status": "healthy" if self.connected else "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "connection_status": "connected" if self.connected else "disconnected",
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "client_id": self.client_id,
            "connection_attempts": self.connection_attempts,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "messages_failed": self.messages_failed,
            "queue_size": len(self.message_queue),
            "last_message_time": self.last_message_time,
            "uptime_seconds": time.time() - self.last_connection_attempt if self.last_connection_attempt else 0
        }
    
    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback for successful connection"""
        if reason_code == 0:
            self.connected = True
            self.connection_attempts = 0
            self.last_connection_attempt = time.time()
            logger.info("Successfully connected to MQTT broker")
            
            # Process queued messages
            self._process_queued_messages()
            
            # Subscribe to default topics
            self._subscribe_to_default_topics()
        else:
            logger.error(f"Failed to connect to MQTT broker: {reason_code}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, reason_code, properties=None):
        """Callback for disconnection"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")
        
        # Attempt reconnection if not intentional disconnect
        if reason_code != 0:
            self._schedule_reconnect()
    
    def _on_message(self, client, userdata, msg):
        """Callback for received messages"""
        try:
            self.messages_received += 1
            self.last_message_time = time.time()
            
            # Parse message
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"Received message on topic {topic}: {payload[:100]}...")
            
            # Parse JSON payload
            try:
                message_data = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON message: {e}")
                return
            
            # Find and call appropriate handler
            handler_found = False
            for handler_topic, handler in self.message_handlers.items():
                if self._topic_matches(handler_topic, topic):
                    try:
                        handler(topic, message_data)
                        handler_found = True
                        break
                    except Exception as e:
                        logger.error(f"Error in message handler for topic {topic}: {e}")
            
            if not handler_found:
                logger.warning(f"No handler found for topic: {topic}")
                
        except Exception as e:
            logger.error(f"Error processing received message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for successful message publish"""
        logger.debug(f"Message published successfully (MID: {mid})")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Callback for successful subscription"""
        logger.debug(f"Successfully subscribed (MID: {mid}, QoS: {granted_qos})")
    
    def _on_log(self, client, userdata, level, buf):
        """Callback for MQTT client logs"""
        if MQTTConfig.MQTT_ENABLE_DEBUG:
            logger.debug(f"MQTT Log: {buf}")
    
    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """
        Check if topic matches pattern (supports wildcards)
        
        Args:
            pattern: Topic pattern with wildcards
            topic: Actual topic
            
        Returns:
            bool: True if topic matches pattern
        """
        # Simple wildcard matching
        if pattern == topic:
            return True
        
        # Handle single-level wildcard (+)
        if '+' in pattern:
            pattern_parts = pattern.split('/')
            topic_parts = topic.split('/')
            
            if len(pattern_parts) != len(topic_parts):
                return False
            
            for i, pattern_part in enumerate(pattern_parts):
                if pattern_part != '+' and pattern_part != topic_parts[i]:
                    return False
            return True
        
        # Handle multi-level wildcard (#)
        if pattern.endswith('/#'):
            base_pattern = pattern[:-2]
            return topic.startswith(base_pattern)
        
        return False
    
    def _subscribe_to_default_topics(self):
        """Subscribe to default topics"""
        default_subscriptions = [
            (MQTTConfig.TOPIC_CAMERA_DETECTION, QOS_DETECTION),
            (MQTTConfig.TOPIC_CAMERA_HEALTH, QOS_HEALTH),
            (MQTTConfig.TOPIC_CAMERA_CONFIG, QOS_CONFIG),
            (MQTTConfig.TOPIC_CAMERA_CONTROL, QOS_CONTROL),
            (MQTTConfig.TOPIC_SYSTEM_HEALTH, QOS_SYSTEM),
            (MQTTConfig.TOPIC_BLACKLIST_UPDATE, QOS_BLACKLIST),
        ]
        
        for topic, qos in default_subscriptions:
            self.subscribe(topic, qos)
    
    def _process_queued_messages(self):
        """Process queued messages after reconnection"""
        with self.queue_lock:
            if not self.message_queue:
                return
            
            logger.info(f"Processing {len(self.message_queue)} queued messages")
            
            # Process messages in order
            for msg_data in self.message_queue:
                try:
                    result, mid = self.client.publish(
                        msg_data['topic'],
                        msg_data['payload'],
                        msg_data['qos'],
                        msg_data['retain']
                    )
                    
                    if result == mqtt.MQTT_ERR_SUCCESS:
                        self.messages_sent += 1
                        logger.debug(f"Queued message published to {msg_data['topic']}")
                    else:
                        logger.error(f"Failed to publish queued message to {msg_data['topic']}")
                        
                except Exception as e:
                    logger.error(f"Error publishing queued message: {e}")
            
            # Clear queue
            self.message_queue.clear()
    
    def _schedule_reconnect(self):
        """Schedule reconnection attempt"""
        if self.connection_attempts < MQTTConfig.MQTT_MAX_RECONNECT_ATTEMPTS:
            delay = MQTTConfig.MQTT_RECONNECT_DELAY * (2 ** self.connection_attempts)
            logger.info(f"Scheduling reconnection attempt {self.connection_attempts + 1} in {delay} seconds")
            
            # Schedule reconnection
            def delayed_reconnect():
                time.sleep(delay)
                self.connect()
            
            reconnect_thread = Thread(target=delayed_reconnect, daemon=True)
            reconnect_thread.start()
        else:
            logger.error("Maximum reconnection attempts reached")
    
    def _connection_monitor(self):
        """Monitor connection health and trigger reconnection if needed"""
        while True:
            try:
                if not self.connected and time.time() - self.last_connection_attempt > MQTTConfig.MQTT_RECONNECT_DELAY:
                    logger.info("Connection monitor: attempting reconnection")
                    self.connect()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in connection monitor: {e}")
                time.sleep(30)  # Wait longer on error

# ============================================================================
# MESSAGE HANDLERS
# ============================================================================

class DetectionMessageHandler:
    """Handler for detection messages"""
    
    def __init__(self, mqtt_service: MQTTService):
        self.mqtt_service = mqtt_service
    
    def handle_detection(self, topic: str, message: Dict[str, Any]):
        """Handle detection message"""
        try:
            camera_id = message.get('camera_id')
            detection_data = message.get('detection_data', {})
            
            logger.info(f"Processing detection from camera {camera_id}")
            
            # Process detection data
            # TODO: Implement detection processing logic
            
            # Send acknowledgment
            ack_topic = f"lprserver/cameras/{camera_id}/detection/ack"
            ack_message = {
                "message_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "original_message_id": message.get('message_id'),
                "status": "processed",
                "camera_id": camera_id
            }
            
            self.mqtt_service.publish(ack_topic, ack_message, QOS_DETECTION)
            
        except Exception as e:
            logger.error(f"Error handling detection message: {e}")

class HealthMessageHandler:
    """Handler for health messages"""
    
    def __init__(self, mqtt_service: MQTTService):
        self.mqtt_service = mqtt_service
    
    def handle_health(self, topic: str, message: Dict[str, Any]):
        """Handle health message"""
        try:
            camera_id = message.get('camera_id')
            health_status = message.get('health_status')
            health_details = message.get('health_details', {})
            
            logger.info(f"Health update from camera {camera_id}: {health_status}")
            
            # Process health data
            # TODO: Implement health processing logic
            
        except Exception as e:
            logger.error(f"Error handling health message: {e}")

class ConfigMessageHandler:
    """Handler for configuration messages"""
    
    def __init__(self, mqtt_service: MQTTService):
        self.mqtt_service = mqtt_service
    
    def handle_config(self, topic: str, message: Dict[str, Any]):
        """Handle configuration message"""
        try:
            camera_id = message.get('camera_id')
            config_type = message.get('config_type')
            config_data = message.get('config_data', {})
            
            logger.info(f"Config update from camera {camera_id}: {config_type}")
            
            # Process configuration data
            # TODO: Implement configuration processing logic
            
        except Exception as e:
            logger.error(f"Error handling config message: {e}")

class ControlMessageHandler:
    """Handler for control messages"""
    
    def __init__(self, mqtt_service: MQTTService):
        self.mqtt_service = mqtt_service
    
    def handle_control(self, topic: str, message: Dict[str, Any]):
        """Handle control message"""
        try:
            camera_id = message.get('camera_id')
            command = message.get('command')
            parameters = message.get('parameters', {})
            
            logger.info(f"Control command for camera {camera_id}: {command}")
            
            # Process control command
            # TODO: Implement control processing logic
            
            # Send response
            response_topic = f"lprserver/cameras/{camera_id}/control/response"
            response_message = {
                "message_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "original_message_id": message.get('message_id'),
                "command": command,
                "status": "executed",
                "camera_id": camera_id
            }
            
            self.mqtt_service.publish(response_topic, response_message, QOS_CONTROL)
            
        except Exception as e:
            logger.error(f"Error handling control message: {e}")

# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_mqtt_service() -> MQTTService:
    """
    Create and configure MQTT service with default handlers
    
    Returns:
        MQTTService: Configured MQTT service instance
    """
    # Create MQTT service
    mqtt_service = MQTTService()
    
    # Create message handlers
    detection_handler = DetectionMessageHandler(mqtt_service)
    health_handler = HealthMessageHandler(mqtt_service)
    config_handler = ConfigMessageHandler(mqtt_service)
    control_handler = ControlMessageHandler(mqtt_service)
    
    # Register handlers
    mqtt_service.register_handler(MQTTConfig.TOPIC_CAMERA_DETECTION, detection_handler.handle_detection)
    mqtt_service.register_handler(MQTTConfig.TOPIC_CAMERA_HEALTH, health_handler.handle_health)
    mqtt_service.register_handler(MQTTConfig.TOPIC_CAMERA_CONFIG, config_handler.handle_config)
    mqtt_service.register_handler(MQTTConfig.TOPIC_CAMERA_CONTROL, control_handler.handle_control)
    
    return mqtt_service
