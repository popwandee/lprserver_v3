import os
import sqlite3
import logging

class DatabaseManager:
    def __init__(self, db_path="db/lpr_data.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Creates the SQLite database and initializes the required table if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lpr_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_plate TEXT NOT NULL,
                    vehicle_image_path TEXT NOT NULL,
                    license_plate_image_path TEXT NOT NULL,
                    cropped_image_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    location TEXT NOT NULL,
                    hostname TEXT NOT NULL,
                    sent_to_server INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            logging.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
        finally:
            if conn:
                conn.close()

    def save_to_database(self, license_plate, vehicle_image_path, license_plate_image_path, cropped_image_path, timestamp, location, hostname):
        """Stores license plate and image path in SQLite."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO lpr_data (license_plate, vehicle_image_path, license_plate_image_path, cropped_image_path, timestamp, location, hostname, sent_to_server) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (license_plate, vehicle_image_path, license_plate_image_path, cropped_image_path, timestamp, location, hostname, 0)
            )
            conn.commit()
            logging.info(f"✅ Saved to database: Plate {license_plate}, Image {vehicle_image_path}")
        except sqlite3.Error as e:
            logging.error(f"Error saving to database: {e}")
        finally:
            if conn:
                conn.close()

    def delete_by_id(self, record_id):
        """Delete a record by its ID."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lpr_data WHERE id = ?", (record_id,))
            conn.commit()
            logging.info(f"Deleted record with ID: {record_id}")
        except sqlite3.Error as e:
            logging.error(f"Error deleting record: {e}")
        finally:
            if conn:
                conn.close()

    def search_by_license_plate(self, license_plate):
        """Search for records by license plate."""
        conn = None
        results = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lpr_data WHERE license_plate = ?", (license_plate,))
            results = cursor.fetchall()
            logging.info(f"Found {len(results)} records for license plate: {license_plate}")
        except sqlite3.Error as e:
            logging.error(f"Error searching by license plate: {e}")
        finally:
            if conn:
                conn.close()
        return results

    def multi_criteria_search(self, license_plate=None, timestamp=None, location=None, hostname=None, sent_to_server=None):
        """Search for records using multiple criteria."""
        conn = None
        results = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = "SELECT * FROM lpr_data WHERE 1=1"
            params = []
            if license_plate:
                query += " AND license_plate = ?"
                params.append(license_plate)
            if timestamp:
                query += " AND timestamp = ?"
                params.append(timestamp)
            if location:
                query += " AND location = ?"
                params.append(location)
            if hostname:
                query += " AND hostname = ?"
                params.append(hostname)
            if sent_to_server is not None:
                query += " AND sent_to_server = ?"
                params.append(sent_to_server)
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            logging.info(f"Multi-criteria search found {len(results)} records.")
        except sqlite3.Error as e:
            logging.error(f"Error in multi-criteria search: {e}")
        finally:
            if conn:
                conn.close()
        return results

    def get_all_records(self):
        """Return all records in the database."""
        conn = None
        results = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lpr_data")
            results = cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching all records: {e}")
        finally:
            if conn:
                conn.close()
        return results

    def update_sent_to_server(self, record_id, sent=1):
        """Update the sent_to_server status for a record."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE lpr_data SET sent_to_server = ? WHERE id = ?", (sent, record_id))
            conn.commit()
            logging.info(f"Updated sent_to_server for record ID {record_id} to {sent}")
        except sqlite3.Error as e:
            logging.error(f"Error updating sent_to_server: {e}")
        finally:
            if conn:
                conn.close()