#!/usr/bin/env python3
"""
Database Manager Component for AI Camera v1.3

This component provides database operations for storing detection results
and managing application data using SQLite database.

Features:
- SQLite database connection management
- Detection results storage and retrieval
- Database schema creation and maintenance
- Query execution and error handling

Author: AI Camera Team
Version: 1.3
Date: August 2025

"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.core.config import DATABASE_PATH

logger = get_logger(__name__)


class DatabaseManager:
    """
    Database Manager Component for managing application data storage.
    
    This component handles:
    - Database connection and initialization
    - Detection results storage and retrieval
    - Database schema management
    - Data serialization and cleanup
    """
    
    def __init__(self, logger=None):
        """
        Initialize Database Manager.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or get_logger(__name__)
        self.database_path = DATABASE_PATH
        self.connection = None
        
        self.logger.info("DatabaseManager initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the database connection and create tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Create database directory if it doesn't exist
            if self.database_path:
                Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Create tables
            self._create_tables()
            
            self.logger.info(f"Database initialized successfully: {self.database_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            return False
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Detection results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detection_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    vehicles_count INTEGER DEFAULT 0,
                    plates_count INTEGER DEFAULT 0,
                    ocr_results TEXT,
                    annotated_image_path TEXT,
                    cropped_plates_paths TEXT,
                    vehicle_detections TEXT,
                    plate_detections TEXT,
                    processing_time_ms REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # System events table for logging
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            self.logger.info("Database tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating database tables: {e}")
            raise
    
    def insert_detection_result(self, detection_data: Dict[str, Any]) -> Optional[int]:
        """
        Insert detection result into database.
        
        Args:
            detection_data: Dictionary containing detection results
            
        Returns:
            Optional[int]: ID of inserted record, None if failed
        """
        try:
            if not self.connection:
                self.logger.error("Database connection not available")
                return None
            
            cursor = self.connection.cursor()
            
            # Serialize complex data to JSON
            ocr_results_json = json.dumps(detection_data.get('ocr_results', []))
            cropped_paths_json = json.dumps(detection_data.get('cropped_plates_paths', []))
            vehicle_detections_json = json.dumps(detection_data.get('vehicle_detections', []))
            plate_detections_json = json.dumps(detection_data.get('plate_detections', []))
            
            cursor.execute("""
                INSERT INTO detection_results (
                    timestamp, vehicles_count, plates_count, ocr_results,
                    annotated_image_path, cropped_plates_paths,
                    vehicle_detections, plate_detections, processing_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_data.get('timestamp'),
                detection_data.get('vehicles_count', 0),
                detection_data.get('plates_count', 0),
                ocr_results_json,
                detection_data.get('annotated_image_path', ''),
                cropped_paths_json,
                vehicle_detections_json,
                plate_detections_json,
                detection_data.get('processing_time_ms', 0.0)
            ))
            
            self.connection.commit()
            record_id = cursor.lastrowid
            
            self.logger.debug(f"Detection result inserted with ID: {record_id}")
            return record_id
            
        except Exception as e:
            self.logger.error(f"Error inserting detection result: {e}")
            return None
    
    def get_recent_detections(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent detection results from database.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: List of detection records
        """
        try:
            if not self.connection:
                self.logger.error("Database connection not available")
                return []
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM detection_results
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                result = {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'vehicles_count': row['vehicles_count'],
                    'plates_count': row['plates_count'],
                    'annotated_image_path': row['annotated_image_path'],
                    'processing_time_ms': row['processing_time_ms'],
                    'created_at': row['created_at']
                }
                
                # Deserialize JSON fields
                try:
                    result['ocr_results'] = json.loads(row['ocr_results'] or '[]')
                    result['cropped_plates_paths'] = json.loads(row['cropped_plates_paths'] or '[]')
                    result['vehicle_detections'] = json.loads(row['vehicle_detections'] or '[]')
                    result['plate_detections'] = json.loads(row['plate_detections'] or '[]')
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Error deserializing JSON for record {row['id']}: {e}")
                    result['ocr_results'] = []
                    result['cropped_plates_paths'] = []
                    result['vehicle_detections'] = []
                    result['plate_detections'] = []
                
                results.append(result)
            
            self.logger.debug(f"Retrieved {len(results)} recent detection records")
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting recent detections: {e}")
            return []
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """
        Get detection statistics from database.
        
        Returns:
            Dict[str, Any]: Statistics summary
        """
        try:
            if not self.connection:
                return {}
            
            cursor = self.connection.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) as total_detections FROM detection_results")
            total_detections = cursor.fetchone()['total_detections']
            
            cursor.execute("SELECT SUM(vehicles_count) as total_vehicles FROM detection_results")
            total_vehicles = cursor.fetchone()['total_vehicles'] or 0
            
            cursor.execute("SELECT SUM(plates_count) as total_plates FROM detection_results")
            total_plates = cursor.fetchone()['total_plates'] or 0
            
            cursor.execute("SELECT AVG(processing_time_ms) as avg_processing_time FROM detection_results")
            avg_processing_time = cursor.fetchone()['avg_processing_time'] or 0
            
            # Get recent activity
            cursor.execute("""
                SELECT timestamp FROM detection_results 
                ORDER BY created_at DESC LIMIT 1
            """)
            last_result = cursor.fetchone()
            last_detection = last_result['timestamp'] if last_result else None
            
            return {
                'total_detections': total_detections,
                'total_vehicles': total_vehicles,
                'total_plates': total_plates,
                'avg_processing_time_ms': round(avg_processing_time, 2),
                'last_detection': last_detection
            }
            
        except Exception as e:
            self.logger.error(f"Error getting detection statistics: {e}")
            return {}
    
    def log_system_event(self, event_type: str, event_data: Any = None):
        """
        Log system event to database.
        
        Args:
            event_type: Type of event (e.g., 'detection_start', 'model_load', etc.)
            event_data: Additional event data
        """
        try:
            if not self.connection:
                return
            
            cursor = self.connection.cursor()
            event_data_json = json.dumps(event_data) if event_data else None
            
            cursor.execute("""
                INSERT INTO system_events (event_type, event_data)
                VALUES (?, ?)
            """, (event_type, event_data_json))
            
            self.connection.commit()
            self.logger.debug(f"System event logged: {event_type}")
            
        except Exception as e:
            self.logger.warning(f"Error logging system event: {e}")
    
    def cleanup_old_records(self, days_to_keep: int = 30):
        """
        Clean up old records from database.
        
        Args:
            days_to_keep: Number of days to keep records
        """
        try:
            if not self.connection:
                return
            
            cursor = self.connection.cursor()
            
            # Clean up old detection results
            cursor.execute("""
                DELETE FROM detection_results 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days_to_keep))
            
            # Clean up old system events
            cursor.execute("""
                DELETE FROM system_events 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days_to_keep))
            
            self.connection.commit()
            self.logger.info(f"Cleaned up old records older than {days_to_keep} days")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old records: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get database manager status.
        
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            connected = self.connection is not None
            
            # Get database file size if connected
            db_size = 0
            record_count = 0
            
            if connected and Path(self.database_path).exists():
                db_size = Path(self.database_path).stat().st_size
                
                # Get record count
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM detection_results")
                record_count = cursor.fetchone()['count']
            
            return {
                'connected': connected,
                'database_path': self.database_path,
                'database_size_bytes': db_size,
                'detection_records_count': record_count,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting database status: {e}")
            return {
                'connected': False,
                'error': str(e),
                'last_update': datetime.now().isoformat()
            }
    
    def cleanup(self):
        """Clean up database connection and resources."""
        try:
            self.logger.info("Cleaning up DatabaseManager...")
            
            if self.connection:
                self.connection.close()
                self.connection = None
            
            self.logger.info("DatabaseManager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during DatabaseManager cleanup: {e}")
