"""
MQTT Configuration for LPR Server v3

This module contains all MQTT-related configuration settings, topic definitions,
and constants for the LPR Server v3 MQTT communication protocol.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MQTTConfig:
    """MQTT Configuration class with all settings and constants"""
    
    # ============================================================================
    # BROKER CONFIGURATION
    # ============================================================================
    
    # Broker connection settings
    BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'localhost')
    BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', 1883))
    BROKER_TLS_PORT = int(os.environ.get('MQTT_BROKER_TLS_PORT', 8883))
    
    # Authentication
    MQTT_USERNAME = os.environ.get('MQTT_USERNAME', 'lpruser')
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', 'secure_password')
    MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', 'lprserver_v3')
    
    # Security settings
    MQTT_TLS_ENABLED = os.environ.get('MQTT_TLS_ENABLED', 'false').lower() == 'true'
    MQTT_CA_CERT = os.environ.get('MQTT_CA_CERT', '/etc/mqtt/ca.crt')
    MQTT_CLIENT_CERT = os.environ.get('MQTT_CLIENT_CERT', '/etc/mqtt/client.crt')
    MQTT_CLIENT_KEY = os.environ.get('MQTT_CLIENT_KEY', '/etc/mqtt/client.key')
    
    # Connection settings
    MQTT_KEEPALIVE = int(os.environ.get('MQTT_KEEPALIVE', 60))
    MQTT_RECONNECT_DELAY = int(os.environ.get('MQTT_RECONNECT_DELAY', 5))
    MQTT_MAX_RECONNECT_ATTEMPTS = int(os.environ.get('MQTT_MAX_RECONNECT_ATTEMPTS', 10))
    MQTT_CONNECTION_TIMEOUT = int(os.environ.get('MQTT_CONNECTION_TIMEOUT', 30))
    
    # ============================================================================
    # TOPIC DEFINITIONS
    # ============================================================================
    
    # Base topic prefix
    TOPIC_PREFIX = "lprserver"
    
    # Camera topics
    TOPIC_CAMERA_DETECTION = f"{TOPIC_PREFIX}/cameras/+/detection"
    TOPIC_CAMERA_DETECTION_ACK = f"{TOPIC_PREFIX}/cameras/+/detection/ack"
    TOPIC_CAMERA_HEALTH = f"{TOPIC_PREFIX}/cameras/+/health"
    TOPIC_CAMERA_HEALTH_REQUEST = f"{TOPIC_PREFIX}/cameras/+/health/request"
    TOPIC_CAMERA_CONFIG = f"{TOPIC_PREFIX}/cameras/+/config"
    TOPIC_CAMERA_CONFIG_UPDATE = f"{TOPIC_PREFIX}/cameras/+/config/update"
    TOPIC_CAMERA_CONFIG_REQUEST = f"{TOPIC_PREFIX}/cameras/+/config/request"
    TOPIC_CAMERA_CONTROL = f"{TOPIC_PREFIX}/cameras/+/control"
    TOPIC_CAMERA_CONTROL_RESPONSE = f"{TOPIC_PREFIX}/cameras/+/control/response"
    
    # Checkpoint topics
    TOPIC_CHECKPOINT_STATUS = f"{TOPIC_PREFIX}/checkpoints/+/status"
    TOPIC_CHECKPOINT_ANALYTICS = f"{TOPIC_PREFIX}/checkpoints/+/analytics"
    
    # System topics
    TOPIC_SYSTEM_HEALTH = f"{TOPIC_PREFIX}/system/health"
    TOPIC_SYSTEM_STATUS = f"{TOPIC_PREFIX}/system/status"
    TOPIC_SYSTEM_ALERTS = f"{TOPIC_PREFIX}/system/alerts"
    TOPIC_SYSTEM_LOGS = f"{TOPIC_PREFIX}/system/logs"
    TOPIC_SYSTEM_MONITORING = f"{TOPIC_PREFIX}/system/monitoring"
    TOPIC_SYSTEM_CONTROL = f"{TOPIC_PREFIX}/system/control"
    
    # Blacklist topics
    TOPIC_BLACKLIST_UPDATE = f"{TOPIC_PREFIX}/blacklist/updates"
    TOPIC_BLACKLIST_NOTIFICATION = f"{TOPIC_PREFIX}/blacklist/notifications"
    TOPIC_BLACKLIST_REQUEST = f"{TOPIC_PREFIX}/blacklist/request"
    
    # ============================================================================
    # QUALITY OF SERVICE (QOS) LEVELS
    # ============================================================================
    
    # QoS Levels for different message types
    QOS_DETECTION = 1      # At least once delivery for detection data
    QOS_HEALTH = 0         # At most once delivery for health updates
    QOS_CONFIG = 2         # Exactly once delivery for configuration
    QOS_CONTROL = 2        # Exactly once delivery for control commands
    QOS_BLACKLIST = 1      # At least once delivery for blacklist updates
    QOS_SYSTEM = 1         # At least once delivery for system messages
    QOS_ANALYTICS = 0      # At most once delivery for analytics data
    
    # ============================================================================
    # MESSAGE RETENTION SETTINGS
    # ============================================================================
    
    # Message retention settings
    RETAIN_DETECTION = False    # Don't retain detection messages
    RETAIN_HEALTH = True        # Retain latest health status
    RETAIN_CONFIG = True        # Retain configuration
    RETAIN_CONTROL = False      # Don't retain control messages
    RETAIN_BLACKLIST = True     # Retain blacklist updates
    RETAIN_SYSTEM = False       # Don't retain system messages
    
    # ============================================================================
    # ERROR HANDLING AND LOGGING
    # ============================================================================
    
    # Error handling
    MQTT_LOG_LEVEL = os.environ.get('MQTT_LOG_LEVEL', 'INFO')
    MQTT_ENABLE_DEBUG = os.environ.get('MQTT_ENABLE_DEBUG', 'false').lower() == 'true'
    MQTT_ERROR_RETRY_ATTEMPTS = int(os.environ.get('MQTT_ERROR_RETRY_ATTEMPTS', 3))
    MQTT_ERROR_RETRY_DELAY = int(os.environ.get('MQTT_ERROR_RETRY_DELAY', 10))
    
    # ============================================================================
    # PERFORMANCE SETTINGS
    # ============================================================================
    
    # Performance settings
    MQTT_MAX_INFLIGHT = int(os.environ.get('MQTT_MAX_INFLIGHT', 20))
    MQTT_MAX_QUEUED_MESSAGES = int(os.environ.get('MQTT_MAX_QUEUED_MESSAGES', 100))
    MQTT_MESSAGE_TIMEOUT = int(os.environ.get('MQTT_MESSAGE_TIMEOUT', 30))
    
    # ============================================================================
    # MESSAGE FORMATS AND SCHEMAS
    # ============================================================================
    
    @staticmethod
    def get_detection_topic(camera_id: str) -> str:
        """Get detection topic for specific camera"""
        return f"lprserver/cameras/{camera_id}/detection"
    
    @staticmethod
    def get_health_topic(camera_id: str) -> str:
        """Get health topic for specific camera"""
        return f"lprserver/cameras/{camera_id}/health"
    
    @staticmethod
    def get_config_topic(camera_id: str) -> str:
        """Get config topic for specific camera"""
        return f"lprserver/cameras/{camera_id}/config"
    
    @staticmethod
    def get_control_topic(camera_id: str) -> str:
        """Get control topic for specific camera"""
        return f"lprserver/cameras/{camera_id}/control"
    
    @staticmethod
    def get_checkpoint_topic(checkpoint_id: str) -> str:
        """Get checkpoint topic for specific checkpoint"""
        return f"lprserver/checkpoints/{checkpoint_id}/status"
    
    # ============================================================================
    # MESSAGE SCHEMAS
    # ============================================================================
    
    @staticmethod
    def get_detection_schema() -> Dict[str, Any]:
        """Get detection message schema"""
        return {
            "type": "object",
            "required": ["message_id", "timestamp", "camera_id", "detection_data"],
            "properties": {
                "message_id": {"type": "string", "format": "uuid"},
                "timestamp": {"type": "string", "format": "date-time"},
                "camera_id": {"type": "string"},
                "checkpoint_id": {"type": "string"},
                "detection_data": {
                    "type": "object",
                    "properties": {
                        "vehicles_count": {"type": "integer"},
                        "plates_count": {"type": "integer"},
                        "processing_time_ms": {"type": "integer"},
                        "confidence_score": {"type": "number"},
                        "detection_type": {"type": "string"},
                        "vehicles": {"type": "array"},
                        "plates": {"type": "array"}
                    }
                },
                "metadata": {"type": "object"}
            }
        }
    
    @staticmethod
    def get_health_schema() -> Dict[str, Any]:
        """Get health message schema"""
        return {
            "type": "object",
            "required": ["message_id", "timestamp", "camera_id", "health_status"],
            "properties": {
                "message_id": {"type": "string", "format": "uuid"},
                "timestamp": {"type": "string", "format": "date-time"},
                "camera_id": {"type": "string"},
                "health_status": {"type": "string", "enum": ["healthy", "warning", "error"]},
                "health_details": {"type": "object"},
                "alerts": {"type": "array"}
            }
        }
    
    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """Get configuration message schema"""
        return {
            "type": "object",
            "required": ["message_id", "timestamp", "camera_id", "config_type", "config_data"],
            "properties": {
                "message_id": {"type": "string", "format": "uuid"},
                "timestamp": {"type": "string", "format": "date-time"},
                "camera_id": {"type": "string"},
                "config_type": {"type": "string"},
                "config_data": {"type": "object"}
            }
        }
    
    @staticmethod
    def get_control_schema() -> Dict[str, Any]:
        """Get control message schema"""
        return {
            "type": "object",
            "required": ["message_id", "timestamp", "camera_id", "command"],
            "properties": {
                "message_id": {"type": "string", "format": "uuid"},
                "timestamp": {"type": "string", "format": "date-time"},
                "camera_id": {"type": "string"},
                "command": {"type": "string"},
                "parameters": {"type": "object"},
                "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"]}
            }
        }
    
    # ============================================================================
    # COMMAND DEFINITIONS
    # ============================================================================
    
    # Camera control commands
    COMMAND_RESTART_CAMERA = "restart_camera"
    COMMAND_STOP_CAMERA = "stop_camera"
    COMMAND_START_CAMERA = "start_camera"
    COMMAND_UPDATE_CONFIG = "update_config"
    COMMAND_GET_STATUS = "get_status"
    COMMAND_GET_HEALTH = "get_health"
    COMMAND_CALIBRATE = "calibrate"
    COMMAND_TEST_CONNECTION = "test_connection"
    
    # System control commands
    COMMAND_SYSTEM_RESTART = "system_restart"
    COMMAND_SYSTEM_SHUTDOWN = "system_shutdown"
    COMMAND_SYSTEM_UPDATE = "system_update"
    COMMAND_BACKUP_DATA = "backup_data"
    COMMAND_CLEANUP_LOGS = "cleanup_logs"
    
    # ============================================================================
    # STATUS DEFINITIONS
    # ============================================================================
    
    # Health status values
    HEALTH_STATUS_HEALTHY = "healthy"
    HEALTH_STATUS_WARNING = "warning"
    HEALTH_STATUS_ERROR = "error"
    HEALTH_STATUS_OFFLINE = "offline"
    
    # Camera status values
    CAMERA_STATUS_ACTIVE = "active"
    CAMERA_STATUS_INACTIVE = "inactive"
    CAMERA_STATUS_MAINTENANCE = "maintenance"
    CAMERA_STATUS_ERROR = "error"
    
    # Priority levels
    PRIORITY_LOW = "low"
    PRIORITY_NORMAL = "normal"
    PRIORITY_HIGH = "high"
    PRIORITY_CRITICAL = "critical"
    
    # ============================================================================
    # MONITORING AND METRICS
    # ============================================================================
    
    # Metrics collection intervals (seconds)
    METRICS_COLLECTION_INTERVAL = int(os.environ.get('METRICS_COLLECTION_INTERVAL', 60))
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 30))
    
    # Performance thresholds
    MAX_LATENCY_MS = int(os.environ.get('MAX_LATENCY_MS', 1000))
    MAX_MESSAGE_RATE = int(os.environ.get('MAX_MESSAGE_RATE', 100))
    MAX_ERROR_RATE = float(os.environ.get('MAX_ERROR_RATE', 0.05))  # 5%
    
    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================
    
    @staticmethod
    def validate_camera_id(camera_id: str) -> bool:
        """Validate camera ID format"""
        if not camera_id:
            return False
        # Camera ID should be alphanumeric with optional underscore
        return bool(camera_id.replace('_', '').isalnum())
    
    @staticmethod
    def validate_checkpoint_id(checkpoint_id: str) -> bool:
        """Validate checkpoint ID format"""
        if not checkpoint_id:
            return False
        # Checkpoint ID should be alphanumeric with optional underscore
        return bool(checkpoint_id.replace('_', '').isalnum())
    
    @staticmethod
    def validate_topic(topic: str) -> bool:
        """Validate MQTT topic format"""
        if not topic:
            return False
        # Topic should not contain invalid characters
        invalid_chars = ['+', '#', '\0']
        return not any(char in topic for char in invalid_chars)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    @staticmethod
    def get_broker_url() -> str:
        """Get broker URL based on TLS configuration"""
        if MQTTConfig.MQTT_TLS_ENABLED:
            return f"ssl://{MQTTConfig.BROKER_HOST}:{MQTTConfig.BROKER_TLS_PORT}"
        else:
            return f"tcp://{MQTTConfig.BROKER_HOST}:{MQTTConfig.BROKER_PORT}"
    
    @staticmethod
    def get_connection_config() -> Dict[str, Any]:
        """Get connection configuration dictionary"""
        config = {
            'host': MQTTConfig.BROKER_HOST,
            'port': MQTTConfig.BROKER_TLS_PORT if MQTTConfig.MQTT_TLS_ENABLED else MQTTConfig.BROKER_PORT,
            'username': MQTTConfig.MQTT_USERNAME,
            'password': MQTTConfig.MQTT_PASSWORD,
            'client_id': MQTTConfig.MQTT_CLIENT_ID,
            'keepalive': MQTTConfig.MQTT_KEEPALIVE,
            'max_inflight_messages': MQTTConfig.MQTT_MAX_INFLIGHT,
            'max_queued_messages': MQTTConfig.MQTT_MAX_QUEUED_MESSAGES
        }
        
        if MQTTConfig.MQTT_TLS_ENABLED:
            config.update({
                'ca_certs': MQTTConfig.MQTT_CA_CERT,
                'certfile': MQTTConfig.MQTT_CLIENT_CERT,
                'keyfile': MQTTConfig.MQTT_CLIENT_KEY,
                'tls_version': 'tlsv1.2'
            })
        
        return config

# ============================================================================
# CONSTANTS FOR EASY ACCESS
# ============================================================================

# QoS Levels
QOS_DETECTION = MQTTConfig.QOS_DETECTION
QOS_HEALTH = MQTTConfig.QOS_HEALTH
QOS_CONFIG = MQTTConfig.QOS_CONFIG
QOS_CONTROL = MQTTConfig.QOS_CONTROL
QOS_BLACKLIST = MQTTConfig.QOS_BLACKLIST
QOS_SYSTEM = MQTTConfig.QOS_SYSTEM
QOS_ANALYTICS = MQTTConfig.QOS_ANALYTICS

# Topics
TOPIC_PREFIX = MQTTConfig.TOPIC_PREFIX
TOPIC_CAMERA_DETECTION = MQTTConfig.TOPIC_CAMERA_DETECTION
TOPIC_CAMERA_HEALTH = MQTTConfig.TOPIC_CAMERA_HEALTH
TOPIC_CAMERA_CONFIG = MQTTConfig.TOPIC_CAMERA_CONFIG
TOPIC_CAMERA_CONTROL = MQTTConfig.TOPIC_CAMERA_CONTROL
TOPIC_SYSTEM_HEALTH = MQTTConfig.TOPIC_SYSTEM_HEALTH
TOPIC_BLACKLIST_UPDATE = MQTTConfig.TOPIC_BLACKLIST_UPDATE

# Commands
COMMAND_RESTART_CAMERA = MQTTConfig.COMMAND_RESTART_CAMERA
COMMAND_STOP_CAMERA = MQTTConfig.COMMAND_STOP_CAMERA
COMMAND_START_CAMERA = MQTTConfig.COMMAND_START_CAMERA
COMMAND_UPDATE_CONFIG = MQTTConfig.COMMAND_UPDATE_CONFIG

# Status values
HEALTH_STATUS_HEALTHY = MQTTConfig.HEALTH_STATUS_HEALTHY
HEALTH_STATUS_WARNING = MQTTConfig.HEALTH_STATUS_WARNING
HEALTH_STATUS_ERROR = MQTTConfig.HEALTH_STATUS_ERROR
CAMERA_STATUS_ACTIVE = MQTTConfig.CAMERA_STATUS_ACTIVE
CAMERA_STATUS_INACTIVE = MQTTConfig.CAMERA_STATUS_INACTIVE
