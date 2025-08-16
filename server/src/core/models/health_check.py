"""
Health Check Model for System Monitoring

This model stores system health check results for comprehensive monitoring.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

# Import db from models package
from core.models import db

class HealthCheck(db.Model):
    """
    Health Check Model for system-wide health monitoring.
    
    This model stores comprehensive health check results including database,
    disk space, system resources, camera connectivity, and service status.
    """
    __tablename__ = 'health_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    overall_status = db.Column(db.String(20), nullable=False, index=True)  # PASS, FAIL, WARNING
    details = db.Column(db.JSON, nullable=True)  # Store comprehensive check details
    
    def __repr__(self):
        return f'<HealthCheck {self.timestamp}: {self.overall_status}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert health check to dictionary.
        
        Returns:
            Dictionary representation of health check
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'overall_status': self.overall_status,
            'details': self.details
        }
    
    @classmethod
    def get_latest_check(cls) -> Optional['HealthCheck']:
        """
        Get the most recent health check.
        
        Returns:
            Latest health check or None
        """
        return cls.query.order_by(cls.timestamp.desc()).first()
    
    @classmethod
    def get_failed_checks(cls, hours: int = 24) -> list:
        """
        Get failed health checks in the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of failed health checks
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(
            cls.overall_status == 'FAIL',
            cls.timestamp >= cutoff_time
        ).order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def get_health_summary(cls, hours: int = 24) -> Dict[str, Any]:
        """
        Get health summary for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with health summary
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_checks = cls.query.filter(
            cls.timestamp >= cutoff_time
        ).order_by(cls.timestamp.desc()).all()
        
        if not recent_checks:
            return {
                'overall_status': 'UNKNOWN',
                'last_check': None,
                'checks_count': 0,
                'pass_count': 0,
                'fail_count': 0,
                'warning_count': 0,
                'uptime_percent': 0.0
            }
        
        # Count by status
        pass_count = sum(1 for check in recent_checks if check.overall_status == 'PASS')
        fail_count = sum(1 for check in recent_checks if check.overall_status == 'FAIL')
        warning_count = sum(1 for check in recent_checks if check.overall_status == 'WARNING')
        
        # Calculate uptime percentage
        total_checks = len(recent_checks)
        uptime_percent = (pass_count / total_checks) * 100 if total_checks > 0 else 0.0
        
        # Determine overall status
        if fail_count > 0:
            overall_status = 'FAIL'
        elif warning_count > 0:
            overall_status = 'WARNING'
        else:
            overall_status = 'PASS'
        
        return {
            'overall_status': overall_status,
            'last_check': recent_checks[0].timestamp.isoformat(),
            'checks_count': total_checks,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'warning_count': warning_count,
            'uptime_percent': round(uptime_percent, 2)
        }
    
    @classmethod
    def cleanup_old_records(cls, days: int = 7) -> int:
        """
        Clean up health check records older than specified days.
        
        Args:
            days: Number of days to keep records
            
        Returns:
            Number of records deleted
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = cls.query.filter(
            cls.timestamp < cutoff_time
        ).delete()
        
        db.session.commit()
        return deleted_count
