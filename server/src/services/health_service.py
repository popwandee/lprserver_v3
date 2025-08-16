"""
Health Service for System Monitoring

This service provides comprehensive health monitoring for all system components
including database, disk space, services, and real-time status updates.
"""

import os
import shutil
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from flask_socketio import emit
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.models.health_check import HealthCheck
from core.models.camera import Camera
from constants import HEALTH_STATUS_PASS, HEALTH_STATUS_FAIL, HEALTH_STATUS_WARNING

logger = logging.getLogger(__name__)

class HealthService:
    """
    Service for monitoring system health and providing real-time status updates.
    """
    
    def __init__(self):
        self.db_session = None
        self.socketio = None
        self.last_check = None
        self.health_status = {}
    
    def initialize(self, db_session, socketio=None):
        """
        Initialize the Health Service with dependencies.
        
        Args:
            db_session: Database session for storing health check results
            socketio: SocketIO instance for real-time updates
        """
        self.db_session = db_session
        self.socketio = socketio
        logger.info("Health service initialized")
    
    def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all system components.
        
        Returns:
            Dictionary containing health status of all components
        """
        logger.info("Performing comprehensive health check")
        
        health_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': HEALTH_STATUS_PASS,
            'components': {}
        }
        
        # Check database connectivity
        db_status = self._check_database()
        health_results['components']['database'] = db_status
        
        # Check disk space
        disk_status = self._check_disk_space()
        health_results['components']['disk_space'] = disk_status
        
        # Check system resources
        system_status = self._check_system_resources()
        health_results['components']['system_resources'] = system_status
        
        # Check camera connectivity
        camera_status = self._check_camera_connectivity()
        health_results['components']['cameras'] = camera_status
        
        # Check service status
        service_status = self._check_service_status()
        health_results['components']['services'] = service_status
        
        # Determine overall status
        overall_status = self._determine_overall_status(health_results['components'])
        health_results['overall_status'] = overall_status
        
        # Store health check result
        self._store_health_check(health_results)
        
        # Update real-time status
        self.health_status = health_results
        self._emit_health_update(health_results)
        
        self.last_check = datetime.utcnow()
        logger.info(f"Health check completed. Overall status: {overall_status}")
        
        return health_results
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            # Test database connection
            from sqlalchemy import text
            self.db_session.execute(text('SELECT 1'))
            
            # Check database size
            db_size = self._get_database_size()
            
            return {
                'status': HEALTH_STATUS_PASS,
                'message': 'Database connection successful',
                'details': {
                    'size_mb': db_size,
                    'connection_time_ms': 0  # Could be measured if needed
                }
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': HEALTH_STATUS_FAIL,
                'message': f'Database connection failed: {str(e)}',
                'details': {}
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        try:
            # Check storage directory
            storage_path = os.environ.get('IMAGE_STORAGE_PATH', 'storage/images')
            if not os.path.exists(storage_path):
                os.makedirs(storage_path, exist_ok=True)
            
            disk_usage = shutil.disk_usage(storage_path)
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            usage_percent = (used_gb / total_gb) * 100
            
            # Determine status based on usage
            if usage_percent > 90:
                status = HEALTH_STATUS_FAIL
                message = 'Disk space critically low'
            elif usage_percent > 80:
                status = HEALTH_STATUS_WARNING
                message = 'Disk space running low'
            else:
                status = HEALTH_STATUS_PASS
                message = 'Disk space adequate'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'total_gb': round(total_gb, 2),
                    'used_gb': round(used_gb, 2),
                    'free_gb': round(free_gb, 2),
                    'usage_percent': round(usage_percent, 2)
                }
            }
        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}")
            return {
                'status': HEALTH_STATUS_FAIL,
                'message': f'Disk space check failed: {str(e)}',
                'details': {}
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Determine status
            if cpu_percent > 90 or memory_percent > 90:
                status = HEALTH_STATUS_WARNING
                message = 'High system resource usage'
            elif cpu_percent > 80 or memory_percent > 80:
                status = HEALTH_STATUS_WARNING
                message = 'Moderate system resource usage'
            else:
                status = HEALTH_STATUS_PASS
                message = 'System resources normal'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'cpu_percent': round(cpu_percent, 2),
                    'memory_percent': round(memory_percent, 2),
                    'memory_available_gb': round(memory.available / (1024**3), 2)
                }
            }
        except Exception as e:
            logger.error(f"System resource check failed: {str(e)}")
            return {
                'status': HEALTH_STATUS_FAIL,
                'message': f'System resource check failed: {str(e)}',
                'details': {}
            }
    
    def _check_camera_connectivity(self) -> Dict[str, Any]:
        """Check camera connectivity status."""
        try:
            # Get all cameras from database
            cameras = self.db_session.query(Camera).all()
            
            if not cameras:
                return {
                    'status': HEALTH_STATUS_WARNING,
                    'message': 'No cameras registered',
                    'details': {
                        'total_cameras': 0,
                        'connected_cameras': 0,
                        'disconnected_cameras': 0
                    }
                }
            
            # Check last activity for each camera
            now = datetime.utcnow()
            connected_count = 0
            disconnected_count = 0
            
            for camera in cameras:
                # Consider camera connected if last activity was within 5 minutes
                if camera.last_activity and (now - camera.last_activity) < timedelta(minutes=5):
                    connected_count += 1
                else:
                    disconnected_count += 1
            
            total_cameras = len(cameras)
            
            if disconnected_count == total_cameras:
                status = HEALTH_STATUS_FAIL
                message = 'All cameras disconnected'
            elif disconnected_count > 0:
                status = HEALTH_STATUS_WARNING
                message = f'{disconnected_count} camera(s) disconnected'
            else:
                status = HEALTH_STATUS_PASS
                message = 'All cameras connected'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'total_cameras': total_cameras,
                    'connected_cameras': connected_count,
                    'disconnected_cameras': disconnected_count
                }
            }
        except Exception as e:
            logger.error(f"Camera connectivity check failed: {str(e)}")
            return {
                'status': HEALTH_STATUS_WARNING,
                'message': 'Camera connectivity check failed - no cameras table',
                'details': {
                    'total_cameras': 0,
                    'connected_cameras': 0,
                    'disconnected_cameras': 0,
                    'error': str(e)
                }
            }
    
    def _check_service_status(self) -> Dict[str, Any]:
        """Check status of running services."""
        try:
            # Check if required processes are running
            services_status = {}
            
            # Check for gunicorn process
            gunicorn_running = any('gunicorn' in proc.info['name'].lower() 
                                  for proc in psutil.process_iter(['pid', 'name']))
            services_status['gunicorn'] = {
                'running': gunicorn_running,
                'status': HEALTH_STATUS_PASS if gunicorn_running else HEALTH_STATUS_FAIL
            }
            
            # Check for nginx process
            nginx_running = any('nginx' in proc.info['name'].lower() 
                              for proc in psutil.process_iter(['pid', 'name']))
            services_status['nginx'] = {
                'running': nginx_running,
                'status': HEALTH_STATUS_PASS if nginx_running else HEALTH_STATUS_FAIL
            }
            
            # Determine overall service status
            all_running = all(service['running'] for service in services_status.values())
            
            return {
                'status': HEALTH_STATUS_PASS if all_running else HEALTH_STATUS_FAIL,
                'message': 'All services running' if all_running else 'Some services not running',
                'details': services_status
            }
        except Exception as e:
            logger.error(f"Service status check failed: {str(e)}")
            return {
                'status': HEALTH_STATUS_FAIL,
                'message': f'Service status check failed: {str(e)}',
                'details': {}
            }
    
    def _determine_overall_status(self, components: Dict[str, Any]) -> str:
        """Determine overall system status based on component statuses."""
        statuses = [comp['status'] for comp in components.values()]
        
        if HEALTH_STATUS_FAIL in statuses:
            return HEALTH_STATUS_FAIL
        elif HEALTH_STATUS_WARNING in statuses:
            return HEALTH_STATUS_WARNING
        else:
            return HEALTH_STATUS_PASS
    
    def _store_health_check(self, health_results: Dict[str, Any]):
        """Store health check result in database."""
        try:
            health_check = HealthCheck(
                timestamp=datetime.utcnow(),
                overall_status=health_results['overall_status'],
                details=health_results
            )
            self.db_session.add(health_check)
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Failed to store health check: {str(e)}")
            self.db_session.rollback()
    
    def _emit_health_update(self, health_results: Dict[str, Any]):
        """Emit health update via WebSocket."""
        if self.socketio:
            try:
                self.socketio.emit('health_update', health_results, namespace='/health')
            except Exception as e:
                logger.error(f"Failed to emit health update: {str(e)}")
    
    def _get_database_size(self) -> float:
        """Get database file size in MB."""
        try:
            db_path = os.environ.get('DATABASE_URL', 'lprserver.db')
            if db_path.startswith('sqlite:///'):
                db_file = db_path.replace('sqlite:///', '')
                if os.path.exists(db_file):
                    size_bytes = os.path.getsize(db_file)
                    return size_bytes / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.error(f"Failed to get database size: {str(e)}")
        
        return 0.0
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get health check history for the specified number of hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of health check records
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            health_checks = self.db_session.query(HealthCheck)\
                .filter(HealthCheck.timestamp >= since)\
                .order_by(HealthCheck.timestamp.desc())\
                .all()
            
            return [
                {
                    'timestamp': hc.timestamp.isoformat(),
                    'overall_status': hc.overall_status,
                    'details': hc.details
                }
                for hc in health_checks
            ]
        except Exception as e:
            logger.error(f"Failed to get health history: {str(e)}")
            return []
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get current health status without performing a new check.
        
        Returns:
            Current health status or empty dict if no check has been performed
        """
        return self.health_status if self.health_status else {}
