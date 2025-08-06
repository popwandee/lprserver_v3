#!/usr/bin/env python3
"""
Simple Health Monitor for AI Camera v2
Enhanced version with comprehensive system monitoring
"""

import os
import shutil
import logging
import time
import psutil
import socket
import importlib.util
from datetime import datetime
from threading import Thread, Event

from config import (
    BASE_DIR, DATABASE_PATH, IMAGE_SAVE_DIR, VEHICLE_DETECTION_MODEL,
    LICENSE_PLATE_DETECTION_MODEL, EASYOCR_LANGUAGES, HEALTH_CHECK_INTERVAL
)
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, camera_manager):
        self.db_manager = DatabaseManager()
        self.camera_manager = camera_manager
        self.running = False
        self.stop_event = Event()
        self.monitor_thread = None

    def _log_result(self, component, status, message):
        """Helper to log and store health check results."""
        timestamp = datetime.now()
        logger.info(f"Health Check - {component}: {status} - {message}")
        self.db_manager.insert_health_check_result(timestamp, component, status, message)

    def check_camera(self):
        """Checks if the camera is initialized and streaming."""
        component = "Camera"
        try:
            if self.camera_manager.is_initialized:
                if self.camera_manager.streaming:
                    self._log_result(component, "PASS", "Camera initialized and streaming.")
                    return True
                else:
                    self._log_result(component, "WARNING", "Camera initialized but not streaming.")
                    return False
            else:
                self._log_result(component, "FAIL", "Camera not initialized.")
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
            total_gb = total / (1024**3)
            used_percent = (used / total) * 100
            
            if free_gb >= required_gb:
                self._log_result(component, "PASS", 
                    f"Disk space OK: {free_gb:.2f} GB free ({used_percent:.1f}% used, {total_gb:.1f} GB total).")
                return True
            else:
                self._log_result(component, "FAIL", 
                    f"Low disk space: {free_gb:.2f} GB free (required {required_gb} GB).")
                return False
        except Exception as e:
            self._log_result(component, "FAIL", f"Disk space check failed: {e}")
            return False

    def check_cpu_ram(self):
        """Checks CPU and RAM status."""
        component = "CPU & RAM"
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # RAM usage
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            ram_gb = memory.total / (1024**3)
            ram_available_gb = memory.available / (1024**3)
            
            # CPU temperature (if available)
            try:
                cpu_temp = psutil.sensors_temperatures()
                if cpu_temp and 'cpu_thermal' in cpu_temp:
                    temp = cpu_temp['cpu_thermal'][0].current
                    temp_info = f", CPU temp: {temp:.1f}°C"
                else:
                    temp_info = ""
            except:
                temp_info = ""
            
            # Check if system is healthy
            if cpu_percent < 90 and ram_percent < 90:
                self._log_result(component, "PASS", 
                    f"CPU: {cpu_percent:.1f}% ({cpu_count} cores), RAM: {ram_percent:.1f}% "
                    f"({ram_available_gb:.1f} GB available of {ram_gb:.1f} GB){temp_info}.")
                return True
            else:
                self._log_result(component, "WARNING", 
                    f"High usage - CPU: {cpu_percent:.1f}%, RAM: {ram_percent:.1f}%{temp_info}.")
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"CPU/RAM check failed: {e}")
            return False

    def check_detection_models(self):
        """Checks if detection models exist at their configured paths."""
        component = "Detection Models"
        try:
            all_models_found = True
            missing_models = []
            
            # Check if models directory exists
            models_dir = os.path.join(BASE_DIR, 'resources')
            if not os.path.exists(models_dir):
                self._log_result(component, "FAIL", f"Models directory not found: {models_dir}")
                return False
            
            # Vehicle Detection Model
            if VEHICLE_DETECTION_MODEL:
                vehicle_model_path = os.path.join(models_dir, VEHICLE_DETECTION_MODEL)
                if not os.path.exists(vehicle_model_path):
                    missing_models.append(f"Vehicle: {VEHICLE_DETECTION_MODEL}")
                    all_models_found = False
                else:
                    logger.info(f"Vehicle detection model found: {vehicle_model_path}")
            
            # License Plate Detection Model
            if LICENSE_PLATE_DETECTION_MODEL:
                lp_model_path = os.path.join(models_dir, LICENSE_PLATE_DETECTION_MODEL)
                if not os.path.exists(lp_model_path):
                    missing_models.append(f"License Plate: {LICENSE_PLATE_DETECTION_MODEL}")
                    all_models_found = False
                else:
                    logger.info(f"License plate detection model found: {lp_model_path}")
            
            if all_models_found:
                self._log_result(component, "PASS", "All detection model directories found.")
                return True
            else:
                self._log_result(component, "FAIL", f"Missing models: {', '.join(missing_models)}")
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"Detection models check failed: {e}")
            return False

    def check_easyocr(self):
        """Checks if EasyOCR can be imported and initialized."""
        component = "EasyOCR"
        try:
            # Check if easyocr module can be imported
            if importlib.util.find_spec("easyocr"):
                # Try to create a simple reader to test initialization
                import easyocr
                try:
                    # Test with minimal languages to avoid heavy initialization
                    reader = easyocr.Reader(['en'], gpu=False)
                    self._log_result(component, "PASS", "EasyOCR module imported and initialized successfully.")
                    return True
                except Exception as init_error:
                    self._log_result(component, "WARNING", f"EasyOCR importable but initialization failed: {init_error}")
                    return False
            else:
                self._log_result(component, "FAIL", "EasyOCR module not found or not importable.")
                return False
        except Exception as e:
            self._log_result(component, "FAIL", f"EasyOCR check failed: {e}")
            return False

    def check_database(self):
        """Checks if the database connection is active."""
        component = "Database"
        try:
            if self.db_manager.conn and self.db_manager.cursor:
                # Try a simple query to confirm connection is live
                self.db_manager.cursor.execute("SELECT 1")
                result = self.db_manager.cursor.fetchone()
                if result:
                    self._log_result(component, "PASS", "Database connection is active and responsive.")
                    return True
                else:
                    self._log_result(component, "FAIL", "Database query returned no result.")
                    return False
            else:
                self._log_result(component, "FAIL", "Database connection not established.")
                return False
        except Exception as e:
            self._log_result(component, "FAIL", f"Database connection check failed: {e}")
            return False

    def check_network_connectivity(self):
        """Checks external network connectivity."""
        component = "Network Connectivity"
        try:
            # Test Google DNS
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            
            # Test websocket server if configured
            try:
                from config import WEBSOCKET_SERVER_URL
                if WEBSOCKET_SERVER_URL:
                    # Extract host and port from websocket URL
                    if WEBSOCKET_SERVER_URL.startswith("ws://"):
                        host_port = WEBSOCKET_SERVER_URL[5:]  # Remove "ws://"
                    elif WEBSOCKET_SERVER_URL.startswith("wss://"):
                        host_port = WEBSOCKET_SERVER_URL[6:]  # Remove "wss://"
                    else:
                        host_port = WEBSOCKET_SERVER_URL
                    
                    if ":" in host_port:
                        host, port_str = host_port.split(":")
                        port = int(port_str)
                    else:
                        host = host_port
                        port = 8765  # Default websocket port
                    
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                    self._log_result(component, "PASS", 
                        f"Network connectivity OK - Google DNS and WebSocket server ({host}:{port}) reachable.")
                else:
                    self._log_result(component, "PASS", "Network connectivity OK - Google DNS reachable.")
            except Exception as ws_error:
                self._log_result(component, "WARNING", 
                    f"Google DNS reachable but WebSocket server connection failed: {ws_error}")
            
            return True
            
        except Exception as e:
            self._log_result(component, "FAIL", f"Network connectivity check failed: {e}")
            return False

    def run_all_checks(self):
        """Runs all defined health checks."""
        logger.info("Starting comprehensive system health checks...")
        
        # Run each check individually to prevent one failure from stopping others
        results = {}
        
        try:
            results['camera'] = self.check_camera()
        except Exception as e:
            logger.error(f"Camera check failed: {e}")
            results['camera'] = False
            
        try:
            results['disk_space'] = self.check_disk_space()
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            results['disk_space'] = False
            
        try:
            results['cpu_ram'] = self.check_cpu_ram()
        except Exception as e:
            logger.error(f"CPU/RAM check failed: {e}")
            results['cpu_ram'] = False
            
        try:
            results['detection_models'] = self.check_detection_models()
        except Exception as e:
            logger.error(f"Detection models check failed: {e}")
            results['detection_models'] = False
            
        try:
            results['easyocr'] = self.check_easyocr()
        except Exception as e:
            logger.error(f"EasyOCR check failed: {e}")
            results['easyocr'] = False
            
        try:
            results['database'] = self.check_database()
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            results['database'] = False
            
        try:
            results['network'] = self.check_network_connectivity()
        except Exception as e:
            logger.error(f"Network connectivity check failed: {e}")
            results['network'] = False
        
        # Summary
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        logger.info(f"Health check summary: {passed}/{total} components passed.")
        
        return results

    def get_latest_health_checks(self, limit=10):
        """Get the latest health check results from database."""
        try:
            return self.db_manager.get_latest_health_checks(limit)
        except Exception as e:
            logger.error(f"Error getting latest health checks: {e}")
            return []

    def start_monitoring(self):
        """Start the health monitoring thread."""
        if not self.running:
            self.running = True
            self.stop_event.clear()
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            # Wait a moment to ensure thread starts
            time.sleep(0.1)
            
            if self.monitor_thread.is_alive():
                logger.info("Health monitoring started successfully.")
            else:
                logger.error("Health monitoring thread failed to start.")
                self.running = False
        else:
            logger.info("Health monitoring already running.")

    def stop_monitoring(self):
        """Stop the health monitoring thread."""
        if self.running:
            self.running = False
            self.stop_event.set()
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            logger.info("Health monitoring stopped.")
        else:
            logger.info("Health monitoring already stopped.")

    def is_monitoring(self):
        """Check if health monitoring is currently running."""
        return self.running and self.monitor_thread and self.monitor_thread.is_alive()

    def _monitor_loop(self):
        """Main monitoring loop."""
        logger.info("Health monitor thread started.")
        
        while self.running and not self.stop_event.is_set():
            try:
                self.run_all_checks()
                
                # Sleep for the specified interval
                for _ in range(HEALTH_CHECK_INTERVAL):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                # Continue monitoring even if there's an error
                time.sleep(60)  # Wait a minute before retrying
        
        logger.info("Health monitor thread stopped.")

# Global health monitor instance
health_monitor = None

def get_health_monitor(camera_manager):
    """Get the global health monitor instance."""
    global health_monitor
    if health_monitor is None:
        health_monitor = HealthMonitor(camera_manager)
    return health_monitor 