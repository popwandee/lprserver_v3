"""
Database Service for Data Management

This service provides centralized database operations and data management
including connection handling, migrations, and data cleanup.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.models.lpr_record import LPRRecord
from core.models.camera import Camera
from core.models.blacklist_plate import BlacklistPlate
from core.models.health_check import HealthCheck

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for managing database operations and data lifecycle.
    """
    
    def __init__(self):
        self.db_session = None
        self.app_config = None
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self, db_session, app_config):
        """
        Initialize Database Service.
        
        Args:
            db_session: Database session for operations
            app_config: Application configuration
        """
        self.db_session = db_session
        self.app_config = app_config
        logger.info("Database service initialized")
    
    def initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            # Create database engine
            self.engine = create_engine(
                self.app_config.SQLALCHEMY_DATABASE_URI,
                echo=self.app_config.DEBUG
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create all tables
            from core.models import Base
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return False
    
    def get_session(self):
        """Get a new database session."""
        if self.SessionLocal:
            return self.SessionLocal()
        return self.db_session
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            self.db_session.execute(text('SELECT 1'))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            stats = {}
            
            # Count records in each table
            stats['lpr_records_count'] = self.db_session.query(LPRRecord).count()
            stats['cameras_count'] = self.db_session.query(Camera).count()
            stats['blacklist_plates_count'] = self.db_session.query(BlacklistPlate).count()
            stats['health_checks_count'] = self.db_session.query(HealthCheck).count()
            
            # Get recent activity
            yesterday = datetime.utcnow() - timedelta(days=1)
            stats['recent_lpr_records'] = self.db_session.query(LPRRecord)\
                .filter(LPRRecord.timestamp >= yesterday)\
                .count()
            
            # Get database size
            stats['database_size_mb'] = self._get_database_size()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        Clean up old data based on retention policy.
        
        Args:
            days: Number of days to keep data
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cleanup_results = {}
            
            # Clean up old LPR records
            old_lpr_records = self.db_session.query(LPRRecord)\
                .filter(LPRRecord.timestamp < cutoff_date)\
                .all()
            
            for record in old_lpr_records:
                # Remove associated image file
                if record.image_path and os.path.exists(record.image_path):
                    try:
                        os.remove(record.image_path)
                    except OSError as e:
                        logger.warning(f"Failed to remove image file {record.image_path}: {str(e)}")
            
            deleted_lpr_count = self.db_session.query(LPRRecord)\
                .filter(LPRRecord.timestamp < cutoff_date)\
                .delete()
            
            cleanup_results['lpr_records_deleted'] = deleted_lpr_count
            
            # Clean up old health checks (keep only last 7 days)
            health_cutoff = datetime.utcnow() - timedelta(days=7)
            deleted_health_count = self.db_session.query(HealthCheck)\
                .filter(HealthCheck.timestamp < health_cutoff)\
                .delete()
            
            cleanup_results['health_checks_deleted'] = deleted_health_count
            
            # Commit changes
            self.db_session.commit()
            
            logger.info(f"Data cleanup completed: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {str(e)}")
            self.db_session.rollback()
            return {}
    
    def optimize_database(self) -> bool:
        """Optimize database performance."""
        try:
            # For SQLite, run VACUUM to optimize
            if 'sqlite' in self.app_config.SQLALCHEMY_DATABASE_URI.lower():
                self.db_session.execute(text('VACUUM'))
                self.db_session.commit()
                logger.info("Database optimization completed")
                return True
            else:
                # For other databases, could implement specific optimizations
                logger.info("Database optimization not implemented for this database type")
                return True
                
        except Exception as e:
            logger.error(f"Database optimization failed: {str(e)}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create database backup.
        
        Args:
            backup_path: Path where backup should be saved
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            if 'sqlite' in self.app_config.SQLALCHEMY_DATABASE_URI.lower():
                # For SQLite, copy the database file
                db_path = self.app_config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    import shutil
                    shutil.copy2(db_path, backup_path)
                    logger.info(f"Database backup created: {backup_path}")
                    return True
            else:
                # For other databases, implement specific backup logic
                logger.warning("Database backup not implemented for this database type")
                return False
                
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restore successful, False otherwise
        """
        try:
            if 'sqlite' in self.app_config.SQLALCHEMY_DATABASE_URI.lower():
                # For SQLite, copy the backup file to database location
                db_path = self.app_config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
                if os.path.exists(backup_path):
                    import shutil
                    shutil.copy2(backup_path, db_path)
                    logger.info(f"Database restored from: {backup_path}")
                    return True
            else:
                # For other databases, implement specific restore logic
                logger.warning("Database restore not implemented for this database type")
                return False
                
        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            return False
    
    def _get_database_size(self) -> float:
        """Get database file size in MB."""
        try:
            db_path = self.app_config.SQLALCHEMY_DATABASE_URI
            if db_path.startswith('sqlite:///'):
                db_file = db_path.replace('sqlite:///', '')
                if os.path.exists(db_file):
                    size_bytes = os.path.getsize(db_file)
                    return size_bytes / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.error(f"Failed to get database size: {str(e)}")
        
        return 0.0
    
    def get_table_info(self) -> List[Dict[str, Any]]:
        """Get information about database tables."""
        try:
            # This is a simplified version - could be expanded for different databases
            tables = [
                {
                    'name': 'lpr_records',
                    'description': 'License plate recognition records',
                    'columns': [
                        'id', 'camera_id', 'plate_number', 'confidence', 
                        'timestamp', 'image_path', 'location_lat', 'location_lon'
                    ]
                },
                {
                    'name': 'cameras',
                    'description': 'Camera information',
                    'columns': [
                        'camera_id', 'name', 'location', 'status', 
                        'last_activity', 'created_at'
                    ]
                },
                {
                    'name': 'blacklist_plates',
                    'description': 'Blacklisted license plates',
                    'columns': [
                        'id', 'plate_number', 'reason', 'added_by', 
                        'created_at', 'is_active'
                    ]
                },
                {
                    'name': 'health_checks',
                    'description': 'System health check records',
                    'columns': [
                        'id', 'timestamp', 'overall_status', 'details'
                    ]
                }
            ]
            
            return tables
            
        except Exception as e:
            logger.error(f"Failed to get table info: {str(e)}")
            return []
    
    def execute_custom_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        try:
            result = self.db_session.execute(text(query), params or {})
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Custom query execution failed: {str(e)}")
            return []
