"""
Data Processor for LPR Server v3

This module handles centralized data processing and storage to PostgreSQL
for all communication protocols (WebSocket, REST API, MQTT).
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Configure logging
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Centralized data processor for all protocols
    
    This class handles:
    - Data validation and normalization
    - PostgreSQL storage
    - Analytics updates
    - Notification triggers
    - Business logic processing
    """
    
    def __init__(self, db_config: Dict[str, Any] = None):
        """
        Initialize the data processor
        
        Args:
            db_config: PostgreSQL database configuration
        """
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'lprserver_v3',
            'user': 'lpruser',
            'password': 'your_password'
        }
        
        self.db_connection = None
        self.analytics_engine = None
        self.notification_service = None
        
        # Initialize database connection
        self._init_database()
        
        logger.info("Data Processor initialized")
    
    def _init_database(self):
        """Initialize PostgreSQL database connection"""
        try:
            self.db_connection = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.db_connection = None
    
    def process_incoming_data(self, data: Dict[str, Any], protocol: str):
        """
        Process incoming data from any protocol
        
        Args:
            data: Unified message data
            protocol: Source protocol (websocket, rest_api, mqtt)
        """
        try:
            # 1. Validate data structure
            if not self._validate_data(data):
                logger.warning(f"Invalid data structure from {protocol}")
                return
            
            # 2. Extract common fields
            message_id = data.get("message_id")
            timestamp = data.get("timestamp")
            edge_device_id = data.get("edge_device_id")
            data_type = data.get("data_type")
            payload = data.get("payload")
            metadata = data.get("metadata", {})
            
            # 3. Apply business logic based on data type
            if data_type == "detection":
                self._process_detection(payload, edge_device_id, timestamp, metadata, protocol)
            elif data_type == "health":
                self._process_health(payload, edge_device_id, timestamp, metadata, protocol)
            elif data_type == "config":
                self._process_config(payload, edge_device_id, timestamp, metadata, protocol)
            elif data_type == "control":
                self._process_control(payload, edge_device_id, timestamp, metadata, protocol)
            
            # 4. Store to PostgreSQL
            self._store_to_database(data)
            
            # 5. Update analytics
            self._update_analytics(data)
            
            # 6. Trigger notifications if needed
            self._trigger_notifications(data)
            
            logger.debug(f"Processed {data_type} data from {edge_device_id} via {protocol}")
            
        except Exception as e:
            logger.error(f"Error processing incoming data: {e}")
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate data structure
        
        Args:
            data: Data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["message_id", "timestamp", "edge_device_id", "data_type", "payload"]
        
        # Check required fields
        if not all(field in data for field in required_fields):
            return False
        
        # Validate data types
        data_type = data.get("data_type")
        if data_type not in ["detection", "health", "config", "control"]:
            return False
        
        # Validate payload structure based on data type
        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            return False
        
        return True
    
    def _process_detection(self, payload: Dict[str, Any], edge_device_id: str, 
                          timestamp: str, metadata: Dict[str, Any], protocol: str):
        """
        Process detection data
        
        Args:
            payload: Detection payload
            edge_device_id: Edge device ID
            timestamp: Detection timestamp
            metadata: Message metadata
            protocol: Source protocol
        """
        try:
            # Extract detection information
            detection_data = payload.get("detection_data", {})
            vehicles = detection_data.get("vehicles", [])
            plates = detection_data.get("plates", [])
            
            # Process each vehicle detection
            for vehicle in vehicles:
                self._store_vehicle_detection(vehicle, edge_device_id, timestamp, metadata, protocol)
            
            # Process each plate detection
            for plate in plates:
                self._store_plate_detection(plate, edge_device_id, timestamp, metadata, protocol)
            
            # Check for blacklist matches
            self._check_blacklist_matches(plates, edge_device_id, timestamp)
            
            # Update detection statistics
            self._update_detection_stats(edge_device_id, len(vehicles), len(plates))
            
        except Exception as e:
            logger.error(f"Error processing detection data: {e}")
    
    def _process_health(self, payload: Dict[str, Any], edge_device_id: str, 
                       timestamp: str, metadata: Dict[str, Any], protocol: str):
        """
        Process health data
        
        Args:
            payload: Health payload
            edge_device_id: Edge device ID
            timestamp: Health timestamp
            metadata: Message metadata
            protocol: Source protocol
        """
        try:
            health_status = payload.get("health_status")
            health_details = payload.get("health_details", {})
            alerts = payload.get("alerts", [])
            
            # Store health log
            self._store_health_log(edge_device_id, health_status, health_details, timestamp, protocol)
            
            # Process alerts
            for alert in alerts:
                self._process_alert(alert, edge_device_id, timestamp)
            
            # Update device health status
            self._update_device_health(edge_device_id, health_status, health_details)
            
        except Exception as e:
            logger.error(f"Error processing health data: {e}")
    
    def _process_config(self, payload: Dict[str, Any], edge_device_id: str, 
                       timestamp: str, metadata: Dict[str, Any], protocol: str):
        """
        Process configuration data
        
        Args:
            payload: Configuration payload
            edge_device_id: Edge device ID
            timestamp: Configuration timestamp
            metadata: Message metadata
            protocol: Source protocol
        """
        try:
            config_type = payload.get("config_type")
            config_data = payload.get("config_data", {})
            
            # Store configuration update
            self._store_config_update(edge_device_id, config_type, config_data, timestamp, protocol)
            
            # Apply configuration changes
            self._apply_configuration(edge_device_id, config_type, config_data)
            
        except Exception as e:
            logger.error(f"Error processing config data: {e}")
    
    def _process_control(self, payload: Dict[str, Any], edge_device_id: str, 
                        timestamp: str, metadata: Dict[str, Any], protocol: str):
        """
        Process control data
        
        Args:
            payload: Control payload
            edge_device_id: Edge device ID
            timestamp: Control timestamp
            metadata: Message metadata
            protocol: Source protocol
        """
        try:
            command = payload.get("command")
            parameters = payload.get("parameters", {})
            status = payload.get("status", "executed")
            
            # Store control command
            self._store_control_command(edge_device_id, command, parameters, status, timestamp, protocol)
            
            # Execute control logic
            self._execute_control_command(edge_device_id, command, parameters)
            
        except Exception as e:
            logger.error(f"Error processing control data: {e}")
    
    def _store_to_database(self, data: Dict[str, Any]):
        """
        Store data to PostgreSQL database
        
        Args:
            data: Data to store
        """
        try:
            if not self.db_connection:
                logger.warning("No database connection available")
                return
            
            # Store in unified message log
            self._store_message_log(data)
            
            # Store in protocol-specific tables
            data_type = data.get("data_type")
            if data_type == "detection":
                self._store_detection_data(data)
            elif data_type == "health":
                self._store_health_data(data)
            elif data_type == "config":
                self._store_config_data(data)
            elif data_type == "control":
                self._store_control_data(data)
            
        except Exception as e:
            logger.error(f"Error storing data to database: {e}")
    
    def _store_message_log(self, data: Dict[str, Any]):
        """Store message in unified log table"""
        try:
            cursor = self.db_connection.cursor()
            
            query = """
                INSERT INTO system_logs (
                    message_id, timestamp, protocol, edge_device_id, 
                    data_type, payload, metadata, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                data.get("message_id"),
                data.get("timestamp"),
                data.get("protocol"),
                data.get("edge_device_id"),
                data.get("data_type"),
                json.dumps(data.get("payload")),
                json.dumps(data.get("metadata", {})),
                datetime.utcnow()
            ))
            
            self.db_connection.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error storing message log: {e}")
            self.db_connection.rollback()
    
    def _store_detection_data(self, data: Dict[str, Any]):
        """Store detection data in database"""
        try:
            cursor = self.db_connection.cursor()
            
            # Insert detection record
            detection_query = """
                INSERT INTO detections (
                    detection_id, camera_id, checkpoint_id, timestamp,
                    vehicles_count, plates_count, processing_time_ms,
                    confidence_score, detection_type, metadata, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            payload = data.get("payload", {})
            detection_data = payload.get("detection_data", {})
            
            cursor.execute(detection_query, (
                data.get("message_id"),
                data.get("edge_device_id"),
                payload.get("checkpoint_id"),
                data.get("timestamp"),
                detection_data.get("vehicles_count", 0),
                detection_data.get("plates_count", 0),
                detection_data.get("processing_time_ms"),
                detection_data.get("confidence_score"),
                detection_data.get("detection_type", "lpr"),
                json.dumps(data.get("metadata", {})),
                datetime.utcnow()
            ))
            
            detection_id = cursor.fetchone()[0]
            
            # Insert vehicle records
            vehicles = detection_data.get("vehicles", [])
            for vehicle in vehicles:
                vehicle_query = """
                    INSERT INTO vehicles (
                        detection_id, vehicle_index, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                        confidence, vehicle_class, vehicle_type, color, brand, model, year, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                bbox = vehicle.get("bbox", [0, 0, 0, 0])
                cursor.execute(vehicle_query, (
                    detection_id,
                    vehicle.get("vehicle_index", 0),
                    bbox[0] if len(bbox) > 0 else 0,
                    bbox[1] if len(bbox) > 1 else 0,
                    bbox[2] if len(bbox) > 2 else 0,
                    bbox[3] if len(bbox) > 3 else 0,
                    vehicle.get("confidence"),
                    vehicle.get("vehicle_class"),
                    vehicle.get("vehicle_type"),
                    vehicle.get("color"),
                    vehicle.get("brand"),
                    vehicle.get("model"),
                    vehicle.get("year"),
                    json.dumps(vehicle.get("metadata", {}))
                ))
                
                vehicle_id = cursor.fetchone()[0]
                
                # Insert plate records for this vehicle
                plates = detection_data.get("plates", [])
                for plate in plates:
                    if plate.get("vehicle_id") == vehicle.get("vehicle_index"):
                        plate_query = """
                            INSERT INTO plates (
                                detection_id, vehicle_id, plate_index, plate_number,
                                bbox_x1, bbox_y1, bbox_x2, bbox_y2, confidence,
                                plate_type, country, province, is_valid, metadata
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        plate_bbox = plate.get("bbox", [0, 0, 0, 0])
                        cursor.execute(plate_query, (
                            detection_id,
                            vehicle_id,
                            plate.get("plate_index", 0),
                            plate.get("plate_number"),
                            plate_bbox[0] if len(plate_bbox) > 0 else 0,
                            plate_bbox[1] if len(plate_bbox) > 1 else 0,
                            plate_bbox[2] if len(plate_bbox) > 2 else 0,
                            plate_bbox[3] if len(plate_bbox) > 3 else 0,
                            plate.get("confidence"),
                            plate.get("plate_type"),
                            plate.get("country", "TH"),
                            plate.get("province"),
                            plate.get("is_valid", True),
                            json.dumps(plate.get("metadata", {}))
                        ))
            
            self.db_connection.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error storing detection data: {e}")
            self.db_connection.rollback()
    
    def _store_health_data(self, data: Dict[str, Any]):
        """Store health data in database"""
        try:
            cursor = self.db_connection.cursor()
            
            payload = data.get("payload", {})
            
            query = """
                INSERT INTO health_logs (
                    camera_id, checkpoint_id, health_status, health_details,
                    alerts, timestamp, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                data.get("edge_device_id"),
                payload.get("checkpoint_id"),
                payload.get("health_status"),
                json.dumps(payload.get("health_details", {})),
                json.dumps(payload.get("alerts", [])),
                data.get("timestamp"),
                datetime.utcnow()
            ))
            
            self.db_connection.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error storing health data: {e}")
            self.db_connection.rollback()
    
    def _store_config_data(self, data: Dict[str, Any]):
        """Store configuration data in database"""
        try:
            cursor = self.db_connection.cursor()
            
            payload = data.get("payload", {})
            
            query = """
                INSERT INTO analytics (
                    camera_id, checkpoint_id, config_type, config_data,
                    timestamp, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                data.get("edge_device_id"),
                payload.get("checkpoint_id"),
                payload.get("config_type"),
                json.dumps(payload.get("config_data", {})),
                data.get("timestamp"),
                datetime.utcnow()
            ))
            
            self.db_connection.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error storing config data: {e}")
            self.db_connection.rollback()
    
    def _store_control_data(self, data: Dict[str, Any]):
        """Store control data in database"""
        try:
            cursor = self.db_connection.cursor()
            
            payload = data.get("payload", {})
            
            query = """
                INSERT INTO system_logs (
                    message_id, timestamp, protocol, edge_device_id,
                    data_type, payload, metadata, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                data.get("message_id"),
                data.get("timestamp"),
                data.get("protocol"),
                data.get("edge_device_id"),
                "control_command",
                json.dumps(payload),
                json.dumps(data.get("metadata", {})),
                datetime.utcnow()
            ))
            
            self.db_connection.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error storing control data: {e}")
            self.db_connection.rollback()
    
    def _check_blacklist_matches(self, plates: List[Dict[str, Any]], edge_device_id: str, timestamp: str):
        """Check for blacklist matches and trigger alerts"""
        try:
            if not plates:
                return
            
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
            
            for plate in plates:
                plate_number = plate.get("plate_number")
                if not plate_number:
                    continue
                
                # Check blacklist
                query = """
                    SELECT * FROM blacklist 
                    WHERE plate_number = %s AND is_active = true
                """
                cursor.execute(query, (plate_number,))
                blacklist_entry = cursor.fetchone()
                
                if blacklist_entry:
                    # Trigger alert
                    self._trigger_blacklist_alert(plate, blacklist_entry, edge_device_id, timestamp)
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error checking blacklist matches: {e}")
    
    def _trigger_blacklist_alert(self, plate: Dict[str, Any], blacklist_entry: Dict[str, Any], 
                                edge_device_id: str, timestamp: str):
        """Trigger blacklist alert"""
        try:
            alert_data = {
                "type": "blacklist_match",
                "plate_number": plate.get("plate_number"),
                "confidence": plate.get("confidence"),
                "edge_device_id": edge_device_id,
                "timestamp": timestamp,
                "blacklist_reason": blacklist_entry.get("reason"),
                "alert_level": blacklist_entry.get("alert_level", "high")
            }
            
            # Store alert
            cursor = self.db_connection.cursor()
            query = """
                INSERT INTO system_logs (
                    message_id, timestamp, protocol, edge_device_id,
                    data_type, payload, metadata, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                str(uuid.uuid4()),
                timestamp,
                "system",
                edge_device_id,
                "blacklist_alert",
                json.dumps(alert_data),
                json.dumps({"source": "data_processor"}),
                datetime.utcnow()
            ))
            
            self.db_connection.commit()
            cursor.close()
            
            logger.warning(f"Blacklist alert triggered for {plate.get('plate_number')}")
            
        except Exception as e:
            logger.error(f"Error triggering blacklist alert: {e}")
    
    def _update_analytics(self, data: Dict[str, Any]):
        """Update analytics and metrics"""
        try:
            # This would update real-time analytics
            # For now, we'll just log the update
            logger.debug(f"Analytics updated for {data.get('data_type')} from {data.get('edge_device_id')}")
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def _trigger_notifications(self, data: Dict[str, Any]):
        """Trigger notifications based on data"""
        try:
            data_type = data.get("data_type")
            
            if data_type == "detection":
                # Check for high-confidence detections
                payload = data.get("payload", {})
                detection_data = payload.get("detection_data", {})
                confidence = detection_data.get("confidence_score", 0)
                
                if confidence > 0.95:
                    self._send_high_confidence_notification(data)
            
            elif data_type == "health":
                # Check for health alerts
                payload = data.get("payload", {})
                health_status = payload.get("health_status")
                
                if health_status in ["warning", "error"]:
                    self._send_health_alert_notification(data)
            
        except Exception as e:
            logger.error(f"Error triggering notifications: {e}")
    
    def _send_high_confidence_notification(self, data: Dict[str, Any]):
        """Send notification for high-confidence detection"""
        logger.info(f"High confidence detection notification: {data.get('edge_device_id')}")
    
    def _send_health_alert_notification(self, data: Dict[str, Any]):
        """Send notification for health alert"""
        logger.info(f"Health alert notification: {data.get('edge_device_id')}")
    
    def close(self):
        """Close database connection"""
        try:
            if self.db_connection:
                self.db_connection.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the data processor"""
        return {
            "status": "healthy" if self.db_connection else "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connected": self.db_connection is not None,
            "analytics_enabled": self.analytics_engine is not None,
            "notifications_enabled": self.notification_service is not None
        }
