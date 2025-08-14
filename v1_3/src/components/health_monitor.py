#!/usr/bin/env python3
"""
Health Monitor Component for AI Camera v1.3

This component monitors the health status of various system components
including camera, disk space, CPU/RAM, detection models, database,
and network connectivity.

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import os
import shutil
import logging
import time
import psutil
import socket
import importlib.util
from datetime import datetime
from typing import Dict, Any, Optional, List
from threading import Thread, Event

from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.core.config import (
    IMAGE_SAVE_DIR, VEHICLE_DETECTION_MODEL, LICENSE_PLATE_DETECTION_MODEL,
    EASYOCR_LANGUAGES, HEALTH_CHECK_INTERVAL, BASE_DIR
)

logger = get_logger(__name__)


class HealthMonitor:
    """
    Health Monitor Component for system health monitoring.
    
    This component monitors:
    - Camera status and streaming
    - Disk space availability
    - CPU and RAM usage
    - Detection model availability
    - EasyOCR initialization
    - Database connectivity
    - Network connectivity
    """
    
    def __init__(self, logger=None):
        """
        Initialize Health Monitor.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or get_logger(__name__)
        self.db_manager = None
        self.camera_manager = None
        self.detection_manager = None
        self.running = False
        self.stop_event = Event()
        self.monitor_thread = None
        
        self.logger.info("HealthMonitor initialized")
    
    def initialize(self) -> bool:
        """
        Initialize Health Monitor with database connection.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Get database manager from DI container
            from v1_3.src.core.dependency_container import get_service
            self.db_manager = get_service('database_manager')
            
            if not self.db_manager:
                self.logger.error("Database manager not available")
                return False
            
            # Initialize database manager if not already initialized
            if not self.db_manager.connection:
                if not self.db_manager.initialize():
                    self.logger.error("Failed to initialize database manager")
                    return False
            
            # Get other services
            self.camera_manager = get_service('camera_manager')
            self.detection_manager = get_service('detection_manager')
            
            # Create health_checks table if it doesn't exist
            self._create_health_checks_table()
            
            self.logger.info("HealthMonitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize HealthMonitor: {e}")
            return False
    
    def _create_health_checks_table(self):
        """Create health_checks table if it doesn't exist."""
        try:
            if not self.db_manager or not self.db_manager.connection:
                self.logger.error("Database connection not available")
                return
            
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db_manager.connection.commit()
            self.logger.info("Health checks table created/verified")
            
        except Exception as e:
            self.logger.error(f"Failed to create health_checks table: {e}")
    
    def _log_result(self, component: str, status: str, message: str, details: Dict[str, Any] = None):
        """
        Log health check result to database.
        
        Args:
            component: Component being checked
            status: Status result ('PASS', 'FAIL', 'WARNING')
            message: Status message
            details: Additional details as dictionary
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Log to logger
            self.logger.info(f"Health Check - {component}: {status} - {message}")
            
            # Store in database
            if self.db_manager and self.db_manager.connection:
                cursor = self.db_manager.connection.cursor()
                details_json = None
                if details:
                    import json
                    details_json = json.dumps(details)
                
                cursor.execute("""
                    INSERT INTO health_checks (timestamp, component, status, message, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, component, status, message, details_json))
                self.db_manager.connection.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log health check result: {e}")
    
    def check_camera(self) -> bool:
        """
        Check if camera is initialized and streaming.
        
        Returns:
            bool: True if camera is healthy, False otherwise
        """
        component = "Camera"
        try:
            if not self.camera_manager:
                self._log_result(component, "FAIL", "Camera manager not available")
                return False
            
            status = self.camera_manager.get_status()
            if not status:
                self._log_result(component, "FAIL", "Unable to get camera status")
                return False
            
            initialized = status.get('initialized', False)
            streaming = status.get('streaming', False)
            
            if initialized and streaming:
                self._log_result(component, "PASS", "Camera initialized and streaming", {
                    'initialized': initialized,
                    'streaming': streaming,
                    'frame_count': status.get('frame_count', 0),
                    'average_fps': status.get('average_fps', 0.0)
                })
                return True
            elif initialized and not streaming:
                self._log_result(component, "WARNING", "Camera initialized but not streaming", {
                    'initialized': initialized,
                    'streaming': streaming
                })
                return False
            else:
                self._log_result(component, "FAIL", "Camera not initialized", {
                    'initialized': initialized,
                    'streaming': streaming
                })
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"Camera check failed: {e}")
            return False
    
    def check_disk_space(self, path: str = None, required_gb: float = 1.0) -> bool:
        """
        Check available disk space.
        
        Args:
            path: Path to check disk space for
            required_gb: Required free space in GB
            
        Returns:
            bool: True if sufficient disk space, False otherwise
        """
        component = "Disk Space"
        try:
            check_path = path or IMAGE_SAVE_DIR
            total, used, free = shutil.disk_usage(check_path)
            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            used_percent = (used / total) * 100
            
            details = {
                'path': check_path,
                'total_gb': round(total_gb, 2),
                'used_gb': round(used_gb, 2),
                'free_gb': round(free_gb, 2),
                'used_percent': round(used_percent, 1),
                'required_gb': required_gb
            }
            
            if free_gb >= required_gb:
                self._log_result(component, "PASS", 
                    f"Disk space OK: {free_gb:.2f} GB free ({used_percent:.1f}% used)", details)
                return True
            else:
                self._log_result(component, "FAIL", 
                    f"Low disk space: {free_gb:.2f} GB free (required {required_gb} GB)", details)
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"Disk space check failed: {e}")
            return False
    
    def check_cpu_ram(self) -> bool:
        """
        Check CPU and RAM usage.
        
        Returns:
            bool: True if system resources are healthy, False otherwise
        """
        component = "CPU & RAM"
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # RAM usage
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            ram_total_gb = memory.total / (1024**3)
            ram_available_gb = memory.available / (1024**3)
            ram_used_gb = memory.used / (1024**3)
            
            # CPU temperature (if available)
            cpu_temp = None
            temp_info = ""
            try:
                temps = psutil.sensors_temperatures()
                if temps and 'cpu_thermal' in temps:
                    cpu_temp = temps['cpu_thermal'][0].current
                    temp_info = f", CPU temp: {cpu_temp:.1f}°C"
            except:
                pass
            
            details = {
                'cpu_percent': round(cpu_percent, 1),
                'cpu_count': cpu_count,
                'ram_total_gb': round(ram_total_gb, 2),
                'ram_used_gb': round(ram_used_gb, 2),
                'ram_available_gb': round(ram_available_gb, 2),
                'ram_percent': round(ram_percent, 1),
                'cpu_temp': cpu_temp
            }
            
            # Check if usage is within acceptable limits
            cpu_ok = cpu_percent < 90
            ram_ok = ram_percent < 90
            
            if cpu_ok and ram_ok:
                self._log_result(component, "PASS", 
                    f"System resources OK: CPU {cpu_percent:.1f}%, RAM {ram_percent:.1f}%{temp_info}", details)
                return True
            else:
                issues = []
                if not cpu_ok:
                    issues.append(f"CPU usage high: {cpu_percent:.1f}%")
                if not ram_ok:
                    issues.append(f"RAM usage high: {ram_percent:.1f}%")
                
                self._log_result(component, "WARNING", f"System resources: {'; '.join(issues)}{temp_info}", details)
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"CPU/RAM check failed: {e}")
            return False
    
    def check_model_loading(self) -> bool:
        """
        Check if detection models are available and loadable using degirum library.
        
        Returns:
            bool: True if models are available, False otherwise
        """
        component = "Detection Models"
        try:
            # First, try to get detection service status via API
            try:
                import requests
                response = requests.get('http://localhost/detection/status', timeout=5)
                if response.status_code == 200:
                    detection_data = response.json()
                    if detection_data.get('success'):
                        detection_status = detection_data.get('status', {})
                        processor_status = detection_status.get('detection_processor_status', {})
                        
                        details = {
                            'models_loaded': processor_status.get('models_loaded', False),
                            'vehicle_model_available': processor_status.get('vehicle_model_available', False),
                            'lp_detection_model_available': processor_status.get('lp_detection_model_available', False),
                            'lp_ocr_model_available': processor_status.get('lp_ocr_model_available', False),
                            'easyocr_available': processor_status.get('easyocr_available', False),
                            'detection_resolution': processor_status.get('detection_resolution', 'unknown'),
                            'last_update': processor_status.get('last_update', 'unknown'),
                            'method': 'detection_service_api'
                        }
                        
                        # Check if essential models are loaded
                        essential_models_ok = (
                            processor_status.get('vehicle_model_available', False) and 
                            processor_status.get('lp_detection_model_available', False)
                        )
                        
                        if essential_models_ok:
                            self._log_result(component, "PASS", 
                                f"Detection models loaded successfully via detection service API", details)
                            return True
                        else:
                            missing = []
                            if not processor_status.get('vehicle_model_available', False):
                                missing.append('vehicle detection')
                            if not processor_status.get('lp_detection_model_available', False):
                                missing.append('license plate detection')
                            
                            self._log_result(component, "FAIL", 
                                f"Missing essential detection models: {', '.join(missing)}", details)
                            return False
            except Exception as e:
                self.logger.warning(f"Could not access detection service API: {e}")
                # Continue to fallback method
            
            # Fallback: Try to check models using degirum directly
            try:
                import degirum as dg
                
                models_loaded = 0
                available_models = []
                missing_models = []
                
                # Check vehicle detection model
                try:
                    vehicle_model = dg.load_model(
                        model_name=VEHICLE_DETECTION_MODEL,
                        inference_host_address=HEF_MODEL_PATH,
                        zoo_url=MODEL_ZOO_URL
                    )
                    if vehicle_model:
                        available_models.append(VEHICLE_DETECTION_MODEL)
                        models_loaded += 1
                    else:
                        missing_models.append(VEHICLE_DETECTION_MODEL)
                except Exception as e:
                    missing_models.append(f"{VEHICLE_DETECTION_MODEL} (error: {str(e)})")
                
                # Check license plate detection model
                try:
                    lp_model = dg.load_model(
                        model_name=LICENSE_PLATE_DETECTION_MODEL,
                        inference_host_address=HEF_MODEL_PATH,
                        zoo_url=MODEL_ZOO_URL
                    )
                    if lp_model:
                        available_models.append(LICENSE_PLATE_DETECTION_MODEL)
                        models_loaded += 1
                    else:
                        missing_models.append(LICENSE_PLATE_DETECTION_MODEL)
                except Exception as e:
                    missing_models.append(f"{LICENSE_PLATE_DETECTION_MODEL} (error: {str(e)})")
                
                details = {
                    'models_loaded': models_loaded,
                    'available_models': available_models,
                    'missing_models': missing_models,
                    'method': 'direct_degirum_check'
                }
                
                if models_loaded >= 2:  # At least vehicle + LP detection
                    self._log_result(component, "PASS", 
                        f"Detection models available via degirum ({models_loaded} models)", details)
                    return True
                else:
                    self._log_result(component, "FAIL", 
                        f"Missing detection models via degirum: {', '.join(missing_models)}", details)
                    return False
                    
            except ImportError:
                self._log_result(component, "FAIL", "degirum library not available")
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"Model loading check failed: {e}")
            return False
    
    def check_easyocr_init(self) -> bool:
        """
        Check if EasyOCR can be imported and initialized.
        
        Returns:
            bool: True if EasyOCR is available, False otherwise
        """
        component = "EasyOCR"
        try:
            # Try to import EasyOCR
            import easyocr
            
            # Try to initialize with supported languages
            reader = easyocr.Reader(EASYOCR_LANGUAGES)
            
            details = {
                'languages': EASYOCR_LANGUAGES,
                'version': easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'
            }
            
            self._log_result(component, "PASS", 
                f"EasyOCR initialized successfully with languages: {', '.join(EASYOCR_LANGUAGES)}", details)
            return True
            
        except ImportError as e:
            self._log_result(component, "FAIL", f"EasyOCR not available: {e}")
            return False
        except Exception as e:
            self._log_result(component, "FAIL", f"EasyOCR initialization failed: {e}")
            return False
    
    def check_database_connection(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            bool: True if database is accessible, False otherwise
        """
        component = "Database"
        try:
            if not self.db_manager:
                self._log_result(component, "FAIL", "Database manager not available")
                return False
            
            if not self.db_manager.connection:
                self._log_result(component, "FAIL", "Database connection not established")
                return False
            
            # Test database connection with a simple query
            cursor = self.db_manager.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result:
                # Get database info
                cursor.execute("PRAGMA database_list")
                db_info = cursor.fetchall()
                
                details = {
                    'database_path': self.db_manager.database_path,
                    'connection_active': True,
                    'database_count': len(db_info)
                }
                
                self._log_result(component, "PASS", "Database connection active", details)
                return True
            else:
                self._log_result(component, "FAIL", "Database query test failed")
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"Database connection check failed: {e}")
            return False
    
    def check_network_connectivity(self) -> bool:
        """
        Check network connectivity to external services.
        
        Returns:
            bool: True if network connectivity is good, False otherwise
        """
        component = "Network Connectivity"
        try:
            # Test Google DNS (8.8.8.8)
            google_dns_ok = False
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                google_dns_ok = True
            except:
                pass
            
            # Test localhost WebSocket server (optional for health monitoring)
            websocket_ok = False
            try:
                socket.create_connection(("localhost", 5000), timeout=3)
                websocket_ok = True
            except:
                pass
            
            details = {
                'google_dns': google_dns_ok,
                'websocket_server': websocket_ok
            }
            
            # Only require Google DNS for basic connectivity
            if google_dns_ok:
                if websocket_ok:
                    self._log_result(component, "PASS", 
                        "Network connectivity OK: Google DNS and WebSocket server accessible", details)
                else:
                    self._log_result(component, "PASS", 
                        "Network connectivity OK: Google DNS accessible (WebSocket optional)", details)
                return True
            else:
                self._log_result(component, "FAIL", 
                    "Network connectivity failed: Cannot reach Google DNS", details)
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"Network connectivity check failed: {e}")
            return False
    
    def check_storage_management(self) -> bool:
        """
        Check storage management system.
        
        Returns:
            bool: True if storage management is healthy, False otherwise
        """
        component = "Storage Management"
        try:
            # Get storage service from DI container
            from v1_3.src.core.dependency_container import get_service
            storage_service = get_service('storage_service')
            
            if not storage_service:
                self._log_result(component, "FAIL", "Storage service not available")
                return False
            
            # Get storage status
            status_data = storage_service.get_storage_status()
            
            if not status_data.get('success'):
                self._log_result(component, "FAIL", f"Storage service error: {status_data.get('error', 'Unknown error')}")
                return False
            
            status = status_data.get('data', {})
            disk_usage = status.get('disk_usage', {})
            free_gb = disk_usage.get('free_gb', 0)
            
            details = {
                'free_space_gb': round(free_gb, 2),
                'total_space_gb': round(disk_usage.get('total_gb', 0), 2),
                'used_space_gb': round(disk_usage.get('used_gb', 0), 2),
                'usage_percentage': round(disk_usage.get('usage_percentage', 0), 1),
                'monitoring_active': status.get('status', {}).get('running', False)
            }
            
            # Check if free space is sufficient (at least 5 GB)
            if free_gb >= 5.0:
                self._log_result(component, "PASS", 
                    f"Storage management OK: {free_gb:.2f} GB free space available", details)
                return True
            else:
                self._log_result(component, "FAIL", 
                    f"Low storage space: {free_gb:.2f} GB free (minimum 5 GB required)", details)
                return False
                
        except Exception as e:
            self._log_result(component, "FAIL", f"Storage management check failed: {e}")
            return False
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks and return comprehensive status.
        
        Returns:
            Dict containing overall health status and component details
        """
        try:
            self.logger.info("Starting comprehensive health check")
            
            # Run all checks
            checks = {
                'camera': self.check_camera(),
                'disk_space': self.check_disk_space(),
                'cpu_ram': self.check_cpu_ram(),
                'models': self.check_model_loading(),
                'easyocr': self.check_easyocr_init(),
                'database': self.check_database_connection(),
                'network': self.check_network_connectivity(),
                'storage': self.check_storage_management()
            }
            
            # Determine overall status - be more lenient with non-critical checks
            failed_checks = sum(1 for status in checks.values() if not status)
            total_checks = len(checks)
            
            # Check which specific checks failed
            failed_check_names = [name for name, status in checks.items() if not status]
            
            # Critical checks: camera, models, database
            critical_checks = ['camera', 'models', 'database', 'storage']
            critical_failures = [check for check in failed_check_names if check in critical_checks]
            
            # Non-critical checks: network (can be warning)
            non_critical_failures = [check for check in failed_check_names if check not in critical_checks]
            
            if len(critical_failures) == 0:
                if len(non_critical_failures) == 0:
                    overall_status = "healthy"
                elif len(non_critical_failures) <= 2:
                    overall_status = "healthy"  # Non-critical failures don't affect overall status
                else:
                    overall_status = "warning"
            elif len(critical_failures) == 1:
                overall_status = "warning"
            else:
                overall_status = "critical"
            
            # Get latest health check results
            latest_checks = self.get_latest_health_checks(10)
            
            result = {
                'overall_status': overall_status,
                'checks_passed': total_checks - failed_checks,
                'checks_failed': failed_checks,
                'total_checks': total_checks,
                'component_status': checks,
                'latest_checks': latest_checks,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Health check completed: {overall_status} ({total_checks - failed_checks}/{total_checks} passed)")
            return result
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_latest_health_checks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get latest health check results from database.
        
        Args:
            limit: Number of recent checks to retrieve
            
        Returns:
            List of health check results
        """
        try:
            if not self.db_manager or not self.db_manager.connection:
                return []
            
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT timestamp, component, status, message, details
                FROM health_checks
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                result = {
                    'timestamp': row[0],
                    'component': row[1],
                    'status': row[2],
                    'message': row[3],
                    'details': row[4]
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to get latest health checks: {e}")
            return []
    
    def start_monitoring(self, interval: int = None) -> bool:
        """
        Start continuous health monitoring.
        
        Args:
            interval: Monitoring interval in seconds
            
        Returns:
            bool: True if monitoring started successfully, False otherwise
        """
        try:
            if self.running:
                self.logger.warning("Health monitoring already running")
                return True
            
            self.stop_event.clear()
            self.running = True
            monitor_interval = interval or HEALTH_CHECK_INTERVAL
            
            self.monitor_thread = Thread(target=self._monitor_loop, args=(monitor_interval,))
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info(f"Health monitoring started with {monitor_interval}s interval")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start health monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        try:
            if not self.running:
                return
            
            self.stop_event.set()
            self.running = False
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            self.logger.info("Health monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping health monitoring: {e}")
    
    def _monitor_loop(self, interval: int):
        """Background monitoring loop."""
        try:
            while not self.stop_event.is_set():
                # Run health checks
                health_result = self.run_all_checks()
                
                # Wait for next check
                self.stop_event.wait(interval)
                
        except Exception as e:
            self.logger.error(f"Health monitoring loop error: {e}")
        finally:
            self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current health monitor status.
        
        Returns:
            Dict containing monitor status
        """
        return {
            'initialized': self.db_manager is not None,
            'monitoring': self.running,
            'last_check': datetime.now().isoformat() if self.running else None
        }
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            self.stop_monitoring()
            self.logger.info("HealthMonitor cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during HealthMonitor cleanup: {e}")