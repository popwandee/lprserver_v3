#!/usr/bin/env python3
"""
Storage Service for AI Camera v1.3

This service provides business logic for storage management including
disk space monitoring, file cleanup, and storage analytics.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

class StorageService:
    """
    Storage Service for managing disk space and file cleanup.
    
    Provides:
    - Storage status monitoring
    - File cleanup coordination
    - Storage analytics and reporting
    - Configuration management
    """
    
    def __init__(self, storage_monitor=None, logger=None):
        self.logger = logger or get_logger(__name__)
        self.storage_monitor = storage_monitor
        self.last_status_check = None
        self.storage_alerts = []
    
    def initialize(self) -> bool:
        """Initialize Storage Service with dependencies."""
        try:
            if not self.storage_monitor:
                self.storage_monitor = get_service('storage_monitor')
            
            if not self.storage_monitor:
                self.logger.error("Storage monitor not available")
                return False
            
            # Initialize storage monitor
            if not self.storage_monitor.initialize():
                self.logger.error("Failed to initialize storage monitor")
                return False
            
            self.logger.info("Storage Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Storage Service: {e}")
            return False
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get comprehensive storage status."""
        try:
            if not self.storage_monitor:
                self.logger.error("Storage monitor not available")
                return self._create_error_response("Storage monitor not available")
            
            self.logger.debug("Getting storage status from monitor")
            status = self.storage_monitor.get_storage_status()
            self.logger.debug(f"Storage status received: {status}")
            self.last_status_check = datetime.now()
            
            # Add service-level information
            status['service_status'] = {
                'initialized': True,
                'last_check': self.last_status_check.isoformat(),
                'alerts_count': len(self.storage_alerts)
            }
            
            # Check for critical conditions
            disk_usage = status.get('disk_usage', {})
            if disk_usage.get('free_gb', 0) < 5.0:
                self._add_alert('CRITICAL', f"Very low disk space: {disk_usage.get('free_gb', 0):.2f} GB free")
            
            return {
                'success': True,
                'data': status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting storage status: {e}")
            return self._create_error_response(str(e))
    
    def start_storage_monitoring(self, interval: int = None) -> Dict[str, Any]:
        """Start continuous storage monitoring."""
        try:
            if not self.storage_monitor:
                return self._create_error_response("Storage monitor not available")
            
            success = self.storage_monitor.start_monitoring(interval)
            
            if success:
                return {
                    'success': True,
                    'message': f"Storage monitoring started (interval: {interval or 300}s)",
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._create_error_response("Failed to start storage monitoring")
                
        except Exception as e:
            self.logger.error(f"Error starting storage monitoring: {e}")
            return self._create_error_response(str(e))
    
    def stop_storage_monitoring(self) -> Dict[str, Any]:
        """Stop continuous storage monitoring."""
        try:
            if not self.storage_monitor:
                return self._create_error_response("Storage monitor not available")
            
            self.storage_monitor.stop_monitoring()
            
            return {
                'success': True,
                'message': "Storage monitoring stopped",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping storage monitoring: {e}")
            return self._create_error_response(str(e))
    
    def perform_manual_cleanup(self) -> Dict[str, Any]:
        """Perform manual cleanup of old files."""
        try:
            if not self.storage_monitor:
                return self._create_error_response("Storage monitor not available")
            
            cleanup_stats = self.storage_monitor.cleanup_old_files()
            
            return {
                'success': True,
                'message': f"Manual cleanup completed: {cleanup_stats['total_deleted']} files deleted",
                'data': {
                    'cleanup_stats': cleanup_stats,
                    'space_freed_mb': cleanup_stats['space_freed_mb']
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error performing manual cleanup: {e}")
            return self._create_error_response(str(e))
    
    def update_storage_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update storage configuration."""
        try:
            if not self.storage_monitor:
                return self._create_error_response("Storage monitor not available")
            
            # Validate configuration
            validation_errors = self._validate_configuration(config)
            if validation_errors:
                return self._create_error_response(f"Configuration validation failed: {', '.join(validation_errors)}")
            
            success = self.storage_monitor.update_configuration(config)
            
            if success:
                return {
                    'success': True,
                    'message': "Storage configuration updated successfully",
                    'data': {
                        'updated_config': config
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._create_error_response("Failed to update storage configuration")
                
        except Exception as e:
            self.logger.error(f"Error updating storage configuration: {e}")
            return self._create_error_response(str(e))
    
    def get_storage_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get storage analytics for the specified period."""
        try:
            if not self.storage_monitor:
                return self._create_error_response("Storage monitor not available")
            
            # Get current status
            status = self.storage_monitor.get_storage_status()
            
            # Calculate analytics
            analytics = {
                'period_days': days,
                'current_usage': {
                    'disk_usage_gb': status.get('disk_usage', {}).get('used_gb', 0),
                    'folder_size_mb': status.get('folder_stats', {}).get('total_size_mb', 0),
                    'file_count': status.get('file_counts', {}).get('total_files', 0)
                },
                'cleanup_history': status.get('cleanup_stats', {}),
                'alerts': self.storage_alerts[-10:],  # Last 10 alerts
                'recommendations': self._generate_recommendations(status)
            }
            
            return {
                'success': True,
                'data': analytics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting storage analytics: {e}")
            return self._create_error_response(str(e))
    
    def get_storage_alerts(self) -> Dict[str, Any]:
        """Get storage alerts."""
        try:
            return {
                'success': True,
                'data': {
                    'alerts': self.storage_alerts,
                    'total_alerts': len(self.storage_alerts),
                    'critical_alerts': len([a for a in self.storage_alerts if a['level'] == 'CRITICAL']),
                    'warning_alerts': len([a for a in self.storage_alerts if a['level'] == 'WARNING'])
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting storage alerts: {e}")
            return self._create_error_response(str(e))
    
    def clear_storage_alerts(self) -> Dict[str, Any]:
        """Clear all storage alerts."""
        try:
            alert_count = len(self.storage_alerts)
            self.storage_alerts.clear()
            
            return {
                'success': True,
                'message': f"Cleared {alert_count} storage alerts",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error clearing storage alerts: {e}")
            return self._create_error_response(str(e))
    
    def _validate_configuration(self, config: Dict[str, Any]) -> List[str]:
        """Validate storage configuration parameters."""
        errors = []
        
        if 'min_free_space_gb' in config:
            try:
                value = float(config['min_free_space_gb'])
                if value < 1.0 or value > 100.0:
                    errors.append('min_free_space_gb must be between 1.0 and 100.0 GB')
            except (ValueError, TypeError):
                errors.append('min_free_space_gb must be a valid number')
        
        if 'retention_days' in config:
            try:
                value = int(config['retention_days'])
                if value < 1 or value > 365:
                    errors.append('retention_days must be between 1 and 365 days')
            except (ValueError, TypeError):
                errors.append('retention_days must be a valid integer')
        
        if 'batch_size' in config:
            try:
                value = int(config['batch_size'])
                if value < 1 or value > 1000:
                    errors.append('batch_size must be between 1 and 1000')
            except (ValueError, TypeError):
                errors.append('batch_size must be a valid integer')
        
        if 'monitor_interval' in config:
            try:
                value = int(config['monitor_interval'])
                if value < 60 or value > 3600:
                    errors.append('monitor_interval must be between 60 and 3600 seconds')
            except (ValueError, TypeError):
                errors.append('monitor_interval must be a valid integer')
        
        return errors
    
    def _add_alert(self, level: str, message: str):
        """Add a storage alert."""
        alert = {
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.storage_alerts.append(alert)
        
        if level == 'CRITICAL':
            self.logger.critical(f"Storage Alert: {message}")
        else:
            self.logger.warning(f"Storage Alert: {message}")
    
    def _generate_recommendations(self, status: Dict[str, Any]) -> List[str]:
        """Generate storage recommendations based on current status."""
        recommendations = []
        
        disk_usage = status.get('disk_usage', {})
        free_gb = disk_usage.get('free_gb', 0)
        
        if free_gb < 5.0:
            recommendations.append("CRITICAL: Very low disk space. Consider immediate cleanup or storage expansion.")
        elif free_gb < 10.0:
            recommendations.append("WARNING: Low disk space. Schedule cleanup soon.")
        
        folder_stats = status.get('folder_stats', {})
        folder_size_mb = folder_stats.get('total_size_mb', 0)
        
        if folder_size_mb > 1000:  # More than 1 GB
            recommendations.append("Consider reducing retention period to save disk space.")
        
        file_counts = status.get('file_counts', {})
        unsent_files = file_counts.get('unsent_files', 0)
        
        if unsent_files > 100:
            recommendations.append("High number of unsent files. Check network connectivity.")
        
        return recommendations
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            'success': False,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }

def create_storage_service(storage_monitor=None, logger=None):
    """Factory function to create Storage Service."""
    return StorageService(storage_monitor, logger)
