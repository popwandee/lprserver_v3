#!/usr/bin/env python3
"""
Health Monitor Template for v1.3 Application

This is a simplified template version for testing the systemd service.
It provides basic health monitoring without complex system checks.
"""

import threading
import time
import logging
from datetime import datetime
import psutil
import json

logger = logging.getLogger(__name__)

class HealthMonitorTemplate:
    """
    Template Health Monitor for testing purposes
    
    Features:
    - Basic system health monitoring
    - Component health checks
    - Thread-safe operations
    - Periodic health reporting
    """
    
    def __init__(self, camera_manager=None, detection_processor=None):
        self.camera_manager = camera_manager
        self.detection_processor = detection_processor
        
        # Monitoring state
        self.monitoring = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        
        # Health data
        self.health_data = {}
        self.last_check_time = None
        self.check_interval = 5  # seconds
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Health Monitor Template initialized")
    
    def start_monitoring(self):
        """Start health monitoring"""
        with self.lock:
            if self.monitoring:
                logger.info("Health monitoring already active")
                return True
            
            try:
                self.stop_event.clear()
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_worker,
                    daemon=True
                )
                self.monitoring_thread.start()
                self.monitoring = True
                logger.info("Health monitoring started (template)")
                return True
            except Exception as e:
                logger.error(f"Failed to start health monitoring: {e}")
                return False
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        with self.lock:
            if not self.monitoring:
                logger.info("Health monitoring not active")
                return True
            
            try:
                self.stop_event.set()
                if self.monitoring_thread and self.monitoring_thread.is_alive():
                    self.monitoring_thread.join(timeout=5)
                self.monitoring = False
                logger.info("Health monitoring stopped")
                return True
            except Exception as e:
                logger.error(f"Failed to stop health monitoring: {e}")
                return False
    
    def _monitoring_worker(self):
        """Health monitoring worker"""
        logger.info("Health monitoring worker started")
        
        while not self.stop_event.is_set():
            try:
                # Perform health check
                health_status = self._perform_health_check()
                
                # Store health data
                with self.lock:
                    self.health_data = health_status
                    self.last_check_time = datetime.now()
                
                # Log health status
                if health_status.get('overall_status') == 'unhealthy':
                    logger.warning(f"System health check failed: {health_status}")
                else:
                    logger.debug(f"Health check passed: {health_status}")
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitoring worker: {e}")
                time.sleep(self.check_interval)
        
        logger.info("Health monitoring worker stopped")
    
    def _perform_health_check(self):
        """Perform comprehensive health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'system': self._check_system_health(),
            'camera': self._check_camera_health(),
            'detection': self._check_detection_health(),
            'overall_status': 'healthy'
        }
        
        # Determine overall status
        if (health_status['system']['status'] == 'unhealthy' or
            health_status['camera']['status'] == 'unhealthy' or
            health_status['detection']['status'] == 'unhealthy'):
            health_status['overall_status'] = 'unhealthy'
        
        return health_status
    
    def _check_system_health(self):
        """Check system health"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_health = {
                'cpu_usage_percent': round(cpu_percent, 2),
                'memory_usage_percent': round(memory.percent, 2),
                'memory_available_mb': round(memory.available / 1024 / 1024, 2),
                'disk_usage_percent': round(disk.percent, 2),
                'disk_free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                'status': 'healthy'
            }
            
            # Check thresholds
            if (cpu_percent > 90 or memory.percent > 90 or disk.percent > 90):
                system_health['status'] = 'unhealthy'
            
            return system_health
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_camera_health(self):
        """Check camera health"""
        if not self.camera_manager:
            return {
                'status': 'unknown',
                'message': 'Camera manager not available'
            }
        
        try:
            camera_health = self.camera_manager.health_check()
            return camera_health
        except Exception as e:
            logger.error(f"Error checking camera health: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_detection_health(self):
        """Check detection processor health"""
        if not self.detection_processor:
            return {
                'status': 'unknown',
                'message': 'Detection processor not available'
            }
        
        try:
            detection_health = self.detection_processor.health_check()
            return detection_health
        except Exception as e:
            logger.error(f"Error checking detection health: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def get_health_status(self):
        """Get current health status"""
        with self.lock:
            return self.health_data.copy()
    
    def get_component_health(self, component):
        """Get health status for specific component"""
        health_data = self.get_health_status()
        return health_data.get(component, {})
    
    def is_healthy(self):
        """Check if system is overall healthy"""
        health_data = self.get_health_status()
        return health_data.get('overall_status') == 'healthy'
    
    def run(self):
        """Start monitoring and keep running"""
        self.start_monitoring()
        
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Health monitor interrupted")
        finally:
            self.stop_monitoring()
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()
        logger.info("Health monitor cleaned up")
