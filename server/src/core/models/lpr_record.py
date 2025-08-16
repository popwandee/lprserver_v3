"""
LPR Record Model for storing license plate recognition data

This model stores all LPR detection records including plate numbers,
confidence scores, timestamps, and location data.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

# Import db from models package
from core.models import db

class LPRRecord(db.Model):
    """
    LPR Record Model for storing license plate recognition data.
    
    This model includes:
    - Basic LPR data (plate number, confidence, timestamp)
    - Camera information (camera_id)
    - Location data (GPS coordinates)
    - Blacklist status and reason
    """
    __tablename__ = 'lpr_records'
    
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), db.ForeignKey('cameras.camera_id'), nullable=False, index=True)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    confidence = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    image_path = db.Column(db.String(255))
    location = db.Column(db.String(100))
    location_lat = db.Column(db.Float, nullable=True)  # GPS latitude
    location_lon = db.Column(db.Float, nullable=True)  # GPS longitude
    is_blacklisted = db.Column(db.Boolean, default=False, index=True)  # Flag for blacklist detection
    blacklist_reason = db.Column(db.Text, nullable=True)  # Reason if blacklisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LPRRecord {self.plate_number} from {self.camera_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert record to dictionary.
        
        Returns:
            Dictionary representation of the record
        """
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'plate_number': self.plate_number,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'image_path': self.image_path,
            'location': self.location,
            'location_lat': self.location_lat,
            'location_lon': self.location_lon,
            'is_blacklisted': self.is_blacklisted,
            'blacklist_reason': self.blacklist_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_blacklist_detections(cls, hours: int = 24) -> list:
        """
        Get blacklist detections in the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of blacklisted records
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(
            cls.is_blacklisted == True,
            cls.timestamp >= cutoff_time
        ).order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def get_by_plate_number(cls, plate_number: str, limit: int = 100) -> list:
        """
        Get records by plate number.
        
        Args:
            plate_number: License plate number to search for
            limit: Maximum number of records to return
            
        Returns:
            List of records matching the plate number
        """
        return cls.query.filter_by(plate_number=plate_number).order_by(
            cls.timestamp.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_recent_detections(cls, hours: int = 24, limit: int = 100) -> list:
        """
        Get recent detections in the last N hours.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of records to return
            
        Returns:
            List of recent records
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(
            cls.timestamp >= cutoff_time
        ).order_by(cls.timestamp.desc()).limit(limit).all()
