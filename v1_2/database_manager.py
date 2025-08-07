import sqlite3
import logging
from datetime import datetime
import threading
import uuid
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None # Singleton instance
    _lock = threading.Lock() # Thread safety for singleton

    def __new__(cls, db_lock=None):
        """
        Ensures only one instance of DatabaseManager exists (Singleton pattern).
        Thread-safe implementation.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance.conn = None
                    cls._instance.cursor = None
                    cls._instance.db_lock = db_lock
                    cls._instance.connect()
                    cls._instance._init_db()
        return cls._instance

    def _init_db(self, db_lock=None):
        """
        Initializes the database connection and creates tables if they don't exist.
        """
        if self.conn is None:
            self.connect()

    def connect(self):
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                self.cursor = self.conn.cursor()
                self._create_tables()
                logging.info("Database connection successful.")
            except sqlite3.Error as e:
                logging.error(f"Error connecting to database: {e}")

    def _create_tables(self):
        """
        Creates the necessary tables in the database.
        - camera_metadata: Stores information about each captured frame.
        - detection_results: Stores details of each vehicle/license plate detection.
        """
        if not self.conn:
            logger.error("Cannot create tables: Database connection not established.")
            return

        try:
            # Table for camera metadata (per frame)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS camera_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frame_id TEXT UNIQUE NOT NULL, -- UUID for linking detections
                    timestamp TEXT NOT NULL,
                    exposure_time REAL,
                    analog_gain REAL,
                    digital_gain REAL,
                    lux REAL,
                    colour_temperature REAL,
                    lens_position REAL,
                    focus_state INTEGER,
                    image_filename TEXT,           -- Original image filename
                    processed_image_filename TEXT  -- Image with bounding boxes
                )
            ''')

            # Table for detection results (can have multiple per frame_id)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS detection_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frame_id TEXT NOT NULL,
                    license_plate_text TEXT,
                    lp_confidence REAL,
                    lp_box_x INTEGER,
                    lp_box_y INTEGER,
                    lp_box_w INTEGER,
                    lp_box_h INTEGER,
                    lp_image_filename TEXT, -- Cropped license plate image filename
                    sent_to_server INTEGER DEFAULT 0, -- 0 for not sent, 1 for sent
                    sent_timestamp TEXT,              -- When it was sent
                    FOREIGN KEY (frame_id) REFERENCES camera_metadata (frame_id)
                )
            ''')

            # Table for health check results
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,       -- 'PASS' or 'FAIL'
                    message TEXT,               -- Detailed message (e.g., error info)
                    sent_to_server INTEGER DEFAULT 0,
                    sent_timestamp TEXT
                )
            ''')
            self.conn.commit()
            logger.info("Database tables checked/created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")

    def insert_camera_metadata(self, timestamp, frame_id, exposure_time, analog_gain,
                               digital_gain, lux, colour_temperature, lens_position,
                               focus_state, image_filename, processed_image_filename):
        """
        Inserts camera metadata for a captured frame into the database.
        """
        if not self.conn:
            logger.error("Cannot insert camera metadata: Database connection not established.")
            return

        try:
            self.cursor.execute('''
                INSERT INTO camera_metadata (
                    timestamp, frame_id, exposure_time, analog_gain, digital_gain,
                    lux, colour_temperature, lens_position, focus_state,
                    image_filename, processed_image_filename
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(), frame_id, exposure_time, analog_gain,
                digital_gain, lux, colour_temperature, lens_position,
                focus_state, image_filename, processed_image_filename
            ))
            self.conn.commit()
            logger.debug(f"Inserted metadata for frame_id: {frame_id}")
        except sqlite3.Error as e:
            logger.error(f"Error inserting camera metadata for frame_id {frame_id}: {e}")

    def insert_detection_result(self, detection_data):
        """
        Inserts a detection result (license plate) into the database.
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot insert detection result: Database connection not established.")
                return

            try:
                self.cursor.execute('''
                    INSERT INTO detection_results (
                        frame_id, license_plate_text, lp_confidence,
                        lp_box_x, lp_box_y, lp_box_w, lp_box_h, lp_image_filename
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    detection_data["frame_id"], detection_data["license_plate_text"], detection_data["lp_confidence"],
                    detection_data["lp_box_x"], detection_data["lp_box_y"], detection_data["lp_box_w"],
                    detection_data["lp_box_h"], detection_data["lp_image_filename"]
                ))
                self.conn.commit()
                lp_text = detection_data["license_plate_text"]
                logger.debug(f"Inserted detection result , LP: {lp_text}")
            except sqlite3.Error as e:
                logger.error(f"Error inserting detection result for {lp_text}: {e}")

    def get_unsent_detections(self):
        """
        Retrieves detection results that have not yet been sent to the server.
        Returns a list of dictionaries.
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot get unsent detections: Database connection not established.")
                return []

            try:
                self.cursor.execute('''
                    SELECT
                        dr.id, dr.frame_id, dr.license_plate_text, dr.lp_confidence,
                        dr.lp_box_x, dr.lp_box_y, dr.lp_box_w, dr.lp_box_h, dr.lp_image_filename,
                        cm.timestamp AS frame_timestamp,
                        cm.exposure_time, cm.analog_gain, cm.digital_gain, cm.lux,
                        cm.colour_temperature, cm.lens_position, cm.focus_state,
                        cm.image_filename AS original_image_filename,
                        cm.processed_image_filename
                    FROM detection_results dr
                    JOIN camera_metadata cm ON dr.frame_id = cm.frame_id
                    WHERE dr.sent_to_server = 0
                    ORDER BY dr.id ASC
                ''')
                rows = self.cursor.fetchall()
                
                # Convert rows to a list of dictionaries for easier handling
                columns = [description[0] for description in self.cursor.description]
                unsent_detections = [dict(zip(columns, row)) for row in rows]
                
                logger.debug(f"Retrieved {len(unsent_detections)} unsent detections.")
                return unsent_detections
            except sqlite3.Error as e:
                logger.error(f"Error retrieving unsent detections: {e}")
                return []

    def update_detection_sent_status(self, detection_id):
        """
        Updates the 'sent_to_server' status of a detection result to 1 (sent).
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot update sent status: Database connection not established.")
                return

            try:
                now = datetime.now().isoformat()
                self.cursor.execute('''
                    UPDATE detection_results
                    SET sent_to_server = 1, sent_timestamp = ?
                    WHERE id = ?
                ''', (now, detection_id))
                self.conn.commit()
                logger.debug(f"Updated sent status for detection_id: {detection_id}")
            except sqlite3.Error as e:
                logger.error(f"Error updating sent status for detection_id {detection_id}: {e}")
    
    def insert_health_check_result(self, timestamp, component, status, message):
        """
        Inserts a health check result into the database.
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot insert health check result: Database connection not established.")
                return

            try:
                self.cursor.execute('''
                    INSERT INTO health_checks (timestamp, component, status, message)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp.isoformat(), component, status, message))
                self.conn.commit()
                logger.debug(f"Inserted health check for {component} with status: {status}")
            except sqlite3.Error as e:
                logger.error(f"Error inserting health check result for {component}: {e}")

    def insert_detection_result(self, license_plate, vehicle_image_path, license_plate_image_path, 
                               cropped_image_path, timestamp, location="", hostname="", confidence=0.0):
        """
        Inserts a detection result into the database.
        Simplified version for the detection thread.
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot insert detection result: Database connection not established.")
                return

            try:
                # Generate a unique frame ID
                frame_id = str(uuid.uuid4())
                
                # Insert camera metadata first
                self.cursor.execute('''
                    INSERT INTO camera_metadata (
                        timestamp, frame_id, exposure_time, analog_gain, digital_gain,
                        lux, colour_temperature, lens_position, focus_state,
                        image_filename, processed_image_filename
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp, frame_id, 0, 0, 0, 0, 0, 0, 0,
                    vehicle_image_path, license_plate_image_path
                ))
                
                # Insert detection result
                self.cursor.execute('''
                    INSERT INTO detection_results (
                        frame_id, license_plate_text, lp_confidence,
                        lp_box_x, lp_box_y, lp_box_w, lp_box_h, lp_image_filename
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    frame_id, license_plate, confidence, 0, 0, 0, 0, cropped_image_path
                ))
                
                self.conn.commit()
                logger.info(f"Inserted detection result: {license_plate}")
                
            except sqlite3.Error as e:
                logger.error(f"Error inserting detection result: {e}")

    def insert_vehicle_detection(self, vehicle_image_path, license_plate_image_path, timestamp, location="", hostname=""):
        """
        Inserts a vehicle detection (without license plate) into the database.
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot insert vehicle detection: Database connection not established.")
                return

            try:
                # Generate a unique frame ID
                frame_id = str(uuid.uuid4())
                
                # Insert camera metadata first
                self.cursor.execute('''
                    INSERT INTO camera_metadata (
                        timestamp, frame_id, exposure_time, analog_gain, digital_gain,
                        lux, colour_temperature, lens_position, focus_state,
                        image_filename, processed_image_filename
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp, frame_id, 0, 0, 0, 0, 0, 0, 0,
                    vehicle_image_path, license_plate_image_path
                ))
                
                # Insert detection result with empty license plate
                self.cursor.execute('''
                    INSERT INTO detection_results (
                        frame_id, license_plate_text, lp_confidence,
                        lp_box_x, lp_box_y, lp_box_w, lp_box_h, lp_image_filename
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    frame_id, "VEHICLE_ONLY", 0.0, 0, 0, 0, 0, ""
                ))
                
                self.conn.commit()
                logger.info(f"Inserted vehicle detection (no license plate)")
                
            except sqlite3.Error as e:
                logger.error(f"Error inserting vehicle detection: {e}")

    def get_latest_health_checks(self, limit=10):
        """
        Retrieves the latest health check results.
        Returns a list of dictionaries.
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot get health checks: Database connection not established.")
                return []
            
            try:
                self.cursor.execute('''
                    SELECT id, timestamp, component, status, message
                    FROM health_checks
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                rows = self.cursor.fetchall()
                columns = [description[0] for description in self.cursor.description]
                health_checks = [dict(zip(columns, row)) for row in rows]
                return health_checks
            except sqlite3.Error as e:
                logger.error(f"Error retrieving latest health checks: {e}")
                return []

    def get_unsent_health_checks(self):
        """
        Retrieves health check results that have not yet been sent to the server.
        Returns a list of dictionaries.
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot get unsent health checks: Database connection not established.")
                return []

            try:
                self.cursor.execute('''
                    SELECT id, timestamp, component, status, message
                    FROM health_checks
                    WHERE sent_to_server = 0
                    ORDER BY id ASC
                ''')
                rows = self.cursor.fetchall()
                columns = [description[0] for description in self.cursor.description]
                unsent_checks = [dict(zip(columns, row)) for row in rows]
                logger.debug(f"Retrieved {len(unsent_checks)} unsent health checks.")
                return unsent_checks
            except sqlite3.Error as e:
                logger.error(f"Error retrieving unsent health checks: {e}")
                return []

    def update_health_check_sent_status(self, check_id):
        """
        Updates the 'sent_to_server' status of a health check result to 1 (sent).
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot update health check sent status: Database connection not established.")
                return

            try:
                now = datetime.now().isoformat()
                self.cursor.execute('''
                    UPDATE health_checks
                    SET sent_to_server = 1, sent_timestamp = ?
                    WHERE id = ?
                ''', (now, check_id))
                self.conn.commit()
                logger.debug(f"Updated sent status for health_check_id: {check_id}")
            except sqlite3.Error as e:
                logger.error(f"Error updating health check sent status for id {check_id}: {e}")
    def get_detection_data_paginated(self, page=1, per_page=10, sort_by='timestamp', sort_order='desc', 
                                   search='', date_from='', date_to=''):
        """
        Get detection data with pagination, sorting, and filtering
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot get detection data: Database connection not established.")
                return {'results': [], 'total': 0, 'total_pages': 0}
            
            try:
                # Build WHERE clause for filtering
                where_conditions = []
                params = []
                
                if search:
                    where_conditions.append("(dr.license_plate_text LIKE ? OR cm.image_filename LIKE ?)")
                    params.extend([f'%{search}%', f'%{search}%'])
                
                if date_from:
                    where_conditions.append("cm.timestamp >= ?")
                    params.append(date_from)
                
                if date_to:
                    where_conditions.append("cm.timestamp <= ?")
                    params.append(date_to)
                
                where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                
                # Validate sort_by to prevent SQL injection
                allowed_sort_fields = ['timestamp', 'license_plate_text', 'lp_confidence', 'exposure_time', 'analog_gain']
                if sort_by not in allowed_sort_fields:
                    sort_by = 'timestamp'
                
                # Get total count
                count_query = f'''
                    SELECT COUNT(*) FROM detection_results dr
                    JOIN camera_metadata cm ON dr.frame_id = cm.frame_id
                    {where_clause}
                '''
                self.cursor.execute(count_query, params)
                total = self.cursor.fetchone()[0]
                
                # Calculate pagination
                total_pages = (total + per_page - 1) // per_page
                offset = (page - 1) * per_page
                
                # Get paginated data
                query = f'''
                    SELECT 
                        dr.id,
                        dr.license_plate_text,
                        dr.lp_confidence,
                        dr.lp_image_filename,
                        cm.timestamp,
                        cm.exposure_time,
                        cm.analog_gain,
                        cm.lux,
                        cm.image_filename,
                        cm.processed_image_filename
                    FROM detection_results dr
                    JOIN camera_metadata cm ON dr.frame_id = cm.frame_id
                    {where_clause}
                    ORDER BY cm.{sort_by} {sort_order.upper()}
                    LIMIT ? OFFSET ?
                '''
                
                self.cursor.execute(query, params + [per_page, offset])
                rows = self.cursor.fetchall()
                
                # Convert to list of dictionaries
                columns = ['id', 'license_plate_text', 'lp_confidence', 'lp_image_filename', 
                          'timestamp', 'exposure_time', 'analog_gain', 'lux', 
                          'image_filename', 'processed_image_filename']
                results = [dict(zip(columns, row)) for row in rows]
                
                return {
                    'results': results,
                    'total': total,
                    'total_pages': total_pages
                }
                
            except sqlite3.Error as e:
                logger.error(f"Error getting detection data: {e}")
                return {'results': [], 'total': 0, 'total_pages': 0}

    def get_detection_statistics(self):
        """
        Get detection statistics
        """
        with self.db_lock:
            if not self.conn:
                logger.error("Cannot get detection stats: Database connection not established.")
                return {}
            
            try:
                # Total detections
                self.cursor.execute("SELECT COUNT(*) FROM detection_results")
                total_detections = self.cursor.fetchone()[0]
                
                # Today's detections
                today = datetime.now().strftime('%Y-%m-%d')
                self.cursor.execute("""
                    SELECT COUNT(*) FROM detection_results dr
                    JOIN camera_metadata cm ON dr.frame_id = cm.frame_id
                    WHERE DATE(cm.timestamp) = ?
                """, (today,))
                today_detections = self.cursor.fetchone()[0]
                
                # Average confidence
                self.cursor.execute("SELECT AVG(lp_confidence) FROM detection_results WHERE lp_confidence > 0")
                avg_confidence = self.cursor.fetchone()[0] or 0
                
                # Most common license plates
                self.cursor.execute("""
                    SELECT license_plate_text, COUNT(*) as count
                    FROM detection_results
                    WHERE license_plate_text IS NOT NULL AND license_plate_text != ''
                    GROUP BY license_plate_text
                    ORDER BY count DESC
                    LIMIT 5
                """)
                top_plates = self.cursor.fetchall()
                
                return {
                    'total_detections': total_detections,
                    'today_detections': today_detections,
                    'avg_confidence': round(avg_confidence, 2),
                    'top_plates': [{'plate': plate, 'count': count} for plate, count in top_plates]
                }
                
            except sqlite3.Error as e:
                logger.error(f"Error getting detection statistics: {e}")
                return {}

    def get_health_data_paginated(self, page=1, per_page=20, component='', status_filter=''):
        """Get health data with pagination and filtering"""
        try:
            with self.db_lock:
                # Build WHERE clause for filtering
                where_conditions = []
                params = []
                
                if component:
                    where_conditions.append("component LIKE ?")
                    params.append(f"%{component}%")
                
                if status_filter:
                    where_conditions.append("status = ?")
                    params.append(status_filter)
                
                where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                
                # Get total count
                count_query = f"SELECT COUNT(*) FROM health_checks{where_clause}"
                self.cursor.execute(count_query, params)
                total = self.cursor.fetchone()[0]
                
                # Calculate pagination
                offset = (page - 1) * per_page
                total_pages = (total + per_page - 1) // per_page
                
                # Get paginated data
                data_query = f"""
                    SELECT id, timestamp, component, status, message 
                    FROM health_checks{where_clause}
                    ORDER BY timestamp DESC 
                    LIMIT ? OFFSET ?
                """
                self.cursor.execute(data_query, params + [per_page, offset])
                
                results = []
                for row in self.cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'timestamp': row[1],
                        'component': row[2],
                        'status': row[3],
                        'message': row[4]
                    })
                
                return {
                    'results': results,
                    'total': total,
                    'total_pages': total_pages
                }
        except Exception as e:
            logger.error(f"Error getting health data: {e}")
            return {
                'results': [],
                'total': 0,
                'total_pages': 0
            }

    def get_detection_by_id(self, detection_id):
        """Get detection result by ID"""
        try:
            with self.db_lock:
                self.cursor.execute("""
                    SELECT * FROM detection_results 
                    WHERE id = ?
                """, (detection_id,))
                
                result = self.cursor.fetchone()
                if result:
                    # Convert to dictionary
                    columns = [description[0] for description in self.cursor.description]
                    detection = dict(zip(columns, result))
                    return detection
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting detection by ID: {e}")
            return None

    def close_connection(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Database connection closed.")