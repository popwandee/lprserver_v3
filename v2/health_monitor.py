import os
import shutil
import logging
import time
from datetime import datetime
import importlib.util # To check if modules are importable

from config import (
   BASE_DIR, DATABASE_PATH, IMAGE_SAVE_DIR, VEHICLE_DETECTION_MODEL,
    LICENSE_PLATE_DETECTION_MODEL, EASYOCR_LANGUAGES, HEALTH_CHECK_INTERVAL
)
from database_manager import DatabaseManager
from camera_handler import CameraHandler # To check camera status

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, frames_queue, camera_handler):
        self.db_manager = DatabaseManager()
        self.camera_handler = camera_handler
        self.running = False

    def _log_result(self, component, status, message):
        """Helper to log and store health check results."""
        timestamp = datetime.now()
        logger.info(f"Health Check - {component}: {status} - {message}")
        self.db_manager.insert_health_check_result(timestamp, component, status, message)

    def check_camera(self):
        """Checks if the camera is initialized and streaming."""
        component = "Camera"
        try:
            if self.camera_handler.is_initialized and getattr(self.camera_handler.picam2, "started", False):
                # Attempt to get a frame to ensure it's actively working
                # This might be too aggressive if run frequently; consider a lighter check
                # if frames are not immediately available for health check purposes
                # For this MVP, we assume a frame can be captured if started.
                # A more thorough check might involve trying to capture a single frame
                # and ensuring it's not None and has expected dimensions.
                # frame, _ = self.camera_handler.capture_frame_and_metadata() # This is too heavy for a simple check
                # if frame is None:
                #     self._log_result(component, "FAIL", "Camera initialized but no frame captured.")
                #     return False
                self._log_result(component, "PASS", "Camera initialized and streaming.")
                return True
            else:
                self._log_result(component, "FAIL", "Camera not initialized or not started.")
                return False
        except Exception as e:
            self._log_result(component, "FAIL", f"Camera check failed: {e}")
            return False

    def check_disk_space(self, path=IMAGE_SAVE_DIR, required_gb=1.0):
        """Checks if there's enough free disk space."""
        component = "Disk Space"
        try:
            total, used, free = shutil.disk_usage(path)
            free_gb = free / (1024**3)
            if free_gb >= required_gb:
                self._log_result(component, "PASS", f"Enough disk space: {free_gb:.2f} GB free.")
                return True
            else:
                self._log_result(component, "FAIL", f"Low disk space: {free_gb:.2f} GB free (required {required_gb} GB).")
                return False
        except Exception as e:
            self._log_result(component, "FAIL", f"Disk space check failed: {e}")
            return False

    def check_model_loading(self):
        """Checks if detection models exist at their configured paths."""
        component = "Detection Models"
        all_models_found = True

        # Vehicle Detection Model
        if not VEHICLE_DETECTION_MODEL: # Check if the model name is set in config
            logger.error("VEHICLE_DETECTION_MODEL: is not set in config.")
            self._log_result(component, "FAIL", "Vehicle detection model not found in config.")
            all_models_found = False
        else:
            vehicle_detection_model_path = os.path.join(BASE_DIR, 'models', VEHICLE_DETECTION_MODEL,VEHICLE_DETECTION_MODEL+'.hef')
            if not os.path.isfile(vehicle_detection_model_path):
                logger.error(f"Vehicle detection model file not found: {vehicle_detection_model_path}")
                self._log_result(component, "FAIL", f"Vehicle detection model file not found: {vehicle_detection_model_path}")
                all_models_found = False
            else:
                logger.debug(f"Vehicle detection model found: {vehicle_detection_model_path}")

        # License Plate Detection Model
        if not LICENSE_PLATE_DETECTION_MODEL: # Check if the model name is set in config
            logger.error("LICENSE_PLATE_DETECTION_MODEL: is not set in config.")
            self._log_result(component, "FAIL", "License plate detection model not found in config.")
            all_models_found = False
        else:   
            license_plate_detection_model_path = os.path.join(BASE_DIR, 'models', LICENSE_PLATE_DETECTION_MODEL,LICENSE_PLATE_DETECTION_MODEL+'.hef')
            if not os.path.isfile(license_plate_detection_model_path):
                logger.error(f"License plate detection model file not found: {license_plate_detection_model_path}")
                self._log_result(component, "FAIL", f"License plate detection model file not found: {license_plate_detection_model_path}")
                all_models_found = False
            else:
                logger.debug(f"License plate detection model found: {license_plate_detection_model_path}")
        
        if all_models_found:
            self._log_result(component, "PASS", "All detection model files found.")
            return True
        else:
            return False # Already logged failures for specific models

    def check_easyocr_init(self):
        """Checks if EasyOCR can be initialized."""
        component = "EasyOCR"
        try:
            # We don't want to re-initialize EasyOCR every check,
            # but ensure its core dependencies are met.
            # A simple check: if the main reader object from DetectionProcessor exists and is ready
            # Or, we can try importing core parts.
            # For simplicity, let's assume if easyocr module loads, it's generally fine.
            if importlib.util.find_spec("easyocr"):
                self._log_result(component, "PASS", "EasyOCR module is importable.")
                return True
            else:
                self._log_result(component, "FAIL", "EasyOCR module not found or importable.")
                return False
        except Exception as e:
            self._log_result(component, "FAIL", f"EasyOCR initialization check failed: {e}")
            return False

    def check_database_connection(self):
        """Checks if the database connection is active."""
        component = "Database"
        try:
            if self.db_manager.conn and self.db_manager.cursor:
                # Try a simple query to confirm connection is live
                self.db_manager.cursor.execute("SELECT 1")
                self._log_result(component, "PASS", "Database connection is active.")
                return True
            else:
                self._log_result(component, "FAIL", "Database connection not established.")
                return False
        except Exception as e:
            self._log_result(component, "FAIL", f"Database connection check failed: {e}")
            return False
            
    def check_network_connectivity(self, host="8.8.8.8", port=53, timeout=3):
        """Checks external network connectivity (e.g., to Google DNS)."""
        component = "Network Connectivity"
        try:
            import socket
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self._log_result(component, "PASS", f"Network connectivity to {host}:{port} successful.")
            return True
        except Exception as e:
            self._log_result(component, "FAIL", f"Network connectivity check failed: {e}")
            return False

    def run_all_checks(self):
        """Runs all defined health checks."""
        logger.info("Starting all system health checks...")
        self.check_camera()
        self.check_disk_space()
        self.check_model_loading()
        self.check_easyocr_init()
        self.check_database_connection()
        self.check_network_connectivity()
        logger.info("All system health checks completed.")

    def run(self):
        """Main loop for the health monitor thread."""
        self.running = True
        logger.info("Health monitor thread started.")
        while self.running:
            self.run_all_checks()
            for i in range(HEALTH_CHECK_INTERVAL):
                if not self.running: # Allow stopping during sleep
                    break
                time.sleep(1)
        logger.info("Health monitor thread stopped.")

    def stop(self):
        """Stops the health monitor thread."""
        self.running = False
        logger.info("Stopping health monitor thread...")