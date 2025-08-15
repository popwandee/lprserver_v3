# MQTT Development Guide for LPR Server v3

## 🚀 MQTT Communication Protocol Implementation

### 📋 **Overview**

MQTT (Message Queuing Telemetry Transport) is a lightweight, publish-subscribe messaging protocol designed for IoT and machine-to-machine (M2M) communication. This guide outlines the implementation of MQTT communication protocol for LPR Server v3 with best practices.

### 🎯 **Objectives**

- **Reliable Communication**: Ensure reliable data transmission between Edge Cameras and LPR Server
- **Scalability**: Support multiple cameras and high-frequency data transmission
- **Security**: Implement secure MQTT communication with authentication and encryption
- **Performance**: Optimize for low latency and high throughput
- **Monitoring**: Real-time monitoring and health checks

## 🏗️ **Architecture Design**

### **MQTT Broker Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Edge Camera   │    │   Edge Camera   │    │   Edge Camera   │
│      (CAM001)   │    │      (CAM002)   │    │      (CAM003)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      MQTT Broker          │
                    │   (Mosquitto/Eclipse)     │
                    │   Port: 1883 (TLS: 8883)  │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     LPR Server v3         │
                    │   (MQTT Subscriber)       │
                    │   Port: 5000 (Web)        │
                    └───────────────────────────┘
```

### **Topic Structure**
```
lprserver/
├── cameras/
│   ├── {camera_id}/
│   │   ├── detection/     # Detection data
│   │   ├── health/        # Health status
│   │   ├── config/        # Configuration
│   │   └── control/       # Control commands
├── checkpoints/
│   ├── {checkpoint_id}/
│   │   ├── status/        # Checkpoint status
│   │   └── analytics/     # Analytics data
├── system/
│   ├── alerts/            # System alerts
│   ├── logs/              # System logs
│   └── monitoring/        # System monitoring
└── blacklist/
    ├── updates/           # Blacklist updates
    └── notifications/     # Blacklist notifications
```

## 📡 **MQTT Topics Specification**

### **Detection Topics**
```python
# Detection data from cameras
TOPIC_DETECTION = "lprserver/cameras/{camera_id}/detection"
TOPIC_DETECTION_ACK = "lprserver/cameras/{camera_id}/detection/ack"

# Example:
# lprserver/cameras/CAM001/detection
# lprserver/cameras/CAM001/detection/ack
```

### **Health Monitoring Topics**
```python
# Camera health status
TOPIC_HEALTH = "lprserver/cameras/{camera_id}/health"
TOPIC_HEALTH_REQUEST = "lprserver/cameras/{camera_id}/health/request"

# System health
TOPIC_SYSTEM_HEALTH = "lprserver/system/health"
TOPIC_SYSTEM_STATUS = "lprserver/system/status"
```

### **Configuration Topics**
```python
# Camera configuration
TOPIC_CONFIG = "lprserver/cameras/{camera_id}/config"
TOPIC_CONFIG_UPDATE = "lprserver/cameras/{camera_id}/config/update"
TOPIC_CONFIG_REQUEST = "lprserver/cameras/{camera_id}/config/request"
```

### **Control Topics**
```python
# Camera control commands
TOPIC_CONTROL = "lprserver/cameras/{camera_id}/control"
TOPIC_CONTROL_RESPONSE = "lprserver/cameras/{camera_id}/control/response"

# System control
TOPIC_SYSTEM_CONTROL = "lprserver/system/control"
```

### **Blacklist Topics**
```python
# Blacklist management
TOPIC_BLACKLIST_UPDATE = "lprserver/blacklist/updates"
TOPIC_BLACKLIST_NOTIFICATION = "lprserver/blacklist/notifications"
TOPIC_BLACKLIST_REQUEST = "lprserver/blacklist/request"
```

## 📊 **Message Format Specification**

### **Detection Message Format**
```json
{
  "message_id": "uuid-string",
  "timestamp": "2024-01-15T10:30:00Z",
  "camera_id": "CAM001",
  "checkpoint_id": "CP001",
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
        "plate_number": "ABC1234",
        "bbox": [150, 120, 180, 140],
        "confidence": 0.92,
        "plate_type": "standard",
        "country": "TH",
        "province": "Bangkok",
        "is_valid": true
      }
    ]
  },
  "metadata": {
    "image_path": "/storage/images/CAM001_20240115_103000.jpg",
    "weather": "clear",
    "lighting": "daylight"
  }
}
```

### **Health Message Format**
```json
{
  "message_id": "uuid-string",
  "timestamp": "2024-01-15T10:30:00Z",
  "camera_id": "CAM001",
  "health_status": "healthy",
  "health_details": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1,
    "network_status": "connected",
    "camera_status": "active",
    "last_detection": "2024-01-15T10:29:45Z",
    "uptime_seconds": 86400,
    "temperature": 42.5
  },
  "alerts": [
    {
      "level": "warning",
      "message": "High CPU usage detected",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### **Configuration Message Format**
```json
{
  "message_id": "uuid-string",
  "timestamp": "2024-01-15T10:30:00Z",
  "camera_id": "CAM001",
  "config_type": "detection_settings",
  "config_data": {
    "detection_interval": 1000,
    "confidence_threshold": 0.8,
    "max_vehicles_per_frame": 5,
    "image_quality": "high",
    "enable_recording": true,
    "recording_duration": 30,
    "alert_settings": {
      "enable_alerts": true,
      "alert_confidence_threshold": 0.9,
      "notification_channels": ["mqtt", "email"]
    }
  }
}
```

### **Control Message Format**
```json
{
  "message_id": "uuid-string",
  "timestamp": "2024-01-15T10:30:00Z",
  "camera_id": "CAM001",
  "command": "restart_camera",
  "parameters": {
    "delay_seconds": 5,
    "reason": "scheduled_maintenance"
  },
  "priority": "normal"
}
```

## 🔧 **Implementation Best Practices**

### **1. Quality of Service (QoS) Levels**
```python
# QoS Levels for different message types
QOS_DETECTION = 1      # At least once delivery for detection data
QOS_HEALTH = 0         # At most once delivery for health updates
QOS_CONFIG = 2         # Exactly once delivery for configuration
QOS_CONTROL = 2        # Exactly once delivery for control commands
QOS_BLACKLIST = 1      # At least once delivery for blacklist updates
```

### **2. Message Retention and Cleanup**
```python
# Message retention settings
RETAIN_DETECTION = False    # Don't retain detection messages
RETAIN_HEALTH = True        # Retain latest health status
RETAIN_CONFIG = True        # Retain configuration
RETAIN_CONTROL = False      # Don't retain control messages
```

### **3. Security Implementation**
```python
# Security settings
MQTT_TLS_ENABLED = True
MQTT_TLS_PORT = 8883
MQTT_USERNAME = "lpruser"
MQTT_PASSWORD = "secure_password"
MQTT_CLIENT_ID = "lprserver_v3"

# Certificate paths
MQTT_CA_CERT = "/etc/mqtt/ca.crt"
MQTT_CLIENT_CERT = "/etc/mqtt/client.crt"
MQTT_CLIENT_KEY = "/etc/mqtt/client.key"
```

### **4. Connection Management**
```python
# Connection settings
MQTT_KEEPALIVE = 60
MQTT_RECONNECT_DELAY = 5
MQTT_MAX_RECONNECT_ATTEMPTS = 10
MQTT_CONNECTION_TIMEOUT = 30
```

### **5. Error Handling and Logging**
```python
# Error handling
MQTT_LOG_LEVEL = "INFO"
MQTT_ENABLE_DEBUG = False
MQTT_ERROR_RETRY_ATTEMPTS = 3
MQTT_ERROR_RETRY_DELAY = 10
```

## 📝 **Code Implementation Structure**

### **MQTT Service Class**
```python
class MQTTService:
    def __init__(self, broker_host, broker_port, username, password):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        self.message_handlers = {}
        
    def connect(self):
        """Establish MQTT connection with retry logic"""
        pass
        
    def disconnect(self):
        """Disconnect from MQTT broker"""
        pass
        
    def subscribe(self, topic, qos=1, callback=None):
        """Subscribe to MQTT topic"""
        pass
        
    def publish(self, topic, message, qos=1, retain=False):
        """Publish message to MQTT topic"""
        pass
        
    def on_connect(self, client, userdata, flags, rc):
        """Connection callback"""
        pass
        
    def on_message(self, client, userdata, msg):
        """Message received callback"""
        pass
        
    def on_disconnect(self, client, userdata, rc):
        """Disconnection callback"""
        pass
```

### **Message Handlers**
```python
class DetectionMessageHandler:
    def handle_detection(self, message):
        """Handle detection messages"""
        pass
        
class HealthMessageHandler:
    def handle_health(self, message):
        """Handle health messages"""
        pass
        
class ConfigMessageHandler:
    def handle_config(self, message):
        """Handle configuration messages"""
        pass
        
class ControlMessageHandler:
    def handle_control(self, message):
        """Handle control messages"""
        pass
```

## 🔒 **Security Best Practices**

### **1. Authentication**
- Use username/password authentication
- Implement certificate-based authentication for production
- Regular password rotation
- Use strong, unique passwords

### **2. Encryption**
- Enable TLS/SSL encryption
- Use TLS 1.2 or higher
- Validate server certificates
- Implement certificate pinning

### **3. Access Control**
- Implement topic-based access control
- Use wildcard subscriptions carefully
- Monitor and log access attempts
- Implement rate limiting

### **4. Network Security**
- Use VPN for remote connections
- Implement firewall rules
- Monitor network traffic
- Regular security audits

## 📊 **Monitoring and Metrics**

### **Key Metrics to Monitor**
```python
# Connection metrics
mqtt_connections_total = 0
mqtt_connections_active = 0
mqtt_connections_failed = 0

# Message metrics
mqtt_messages_sent = 0
mqtt_messages_received = 0
mqtt_messages_failed = 0

# Performance metrics
mqtt_latency_ms = 0
mqtt_throughput_msg_per_sec = 0
mqtt_queue_size = 0

# Error metrics
mqtt_errors_total = 0
mqtt_errors_by_type = {}
```

### **Health Checks**
```python
def check_mqtt_health():
    """Check MQTT service health"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "connection_status": "connected",
        "last_message_received": None,
        "message_rate": 0,
        "error_rate": 0,
        "latency_ms": 0
    }
    return health_status
```

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
def test_mqtt_connection():
    """Test MQTT connection establishment"""
    pass
    
def test_message_publishing():
    """Test message publishing"""
    pass
    
def test_message_subscription():
    """Test message subscription"""
    pass
    
def test_error_handling():
    """Test error handling scenarios"""
    pass
```

### **Integration Tests**
```python
def test_camera_detection_flow():
    """Test complete camera detection flow"""
    pass
    
def test_health_monitoring_flow():
    """Test health monitoring flow"""
    pass
    
def test_configuration_flow():
    """Test configuration management flow"""
    pass
```

### **Performance Tests**
```python
def test_message_throughput():
    """Test message throughput under load"""
    pass
    
def test_concurrent_connections():
    """Test multiple concurrent connections"""
    pass
    
def test_latency_measurement():
    """Test message latency"""
    pass
```

## 📚 **Dependencies and Requirements**

### **Python Dependencies**
```txt
paho-mqtt==1.6.1
asyncio-mqtt==0.11.1
pydantic==2.0.0
python-dotenv==1.0.0
```

### **System Requirements**
- MQTT Broker (Mosquitto, Eclipse HiveMQ, AWS IoT)
- Python 3.8+
- Network connectivity
- SSL certificates (for production)

## 🚀 **Deployment Guide**

### **1. MQTT Broker Setup**
```bash
# Install Mosquitto MQTT Broker
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Configure Mosquitto
sudo nano /etc/mosquitto/mosquitto.conf

# Start Mosquitto service
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

### **2. Security Configuration**
```bash
# Generate SSL certificates
openssl req -new -x509 -days 365 -extensions v3_ca -keyout ca.key -out ca.crt

# Configure TLS in Mosquitto
sudo nano /etc/mosquitto/mosquitto.conf
```

### **3. Application Deployment**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp env.example .env
nano .env

# Start MQTT service
python mqtt_service.py
```

## 📋 **Next Steps**

1. **Implement MQTT Service Class**
2. **Create Message Handlers**
3. **Set up MQTT Broker**
4. **Implement Security Features**
5. **Add Monitoring and Logging**
6. **Create Test Suite**
7. **Performance Optimization**
8. **Documentation Updates**

---

**Note**: This guide provides a comprehensive framework for implementing MQTT communication in LPR Server v3. Follow the best practices outlined to ensure reliable, secure, and scalable MQTT communication.
