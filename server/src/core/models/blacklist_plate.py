"""
Blacklist Plate Model for managing blacklisted license plates

This model stores information about license plates that are blacklisted
including reasons, expiry dates, and management metadata.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

# Import db from models package
from core.models import db

class BlacklistPlate(db.Model):
    """
    Blacklist Plate Model for managing blacklisted license plates.
    
    This model includes:
    - License plate information
    - Blacklist reason and metadata
    - Expiry date and status
    - Management information
    """
    __tablename__ = 'blacklist_plates'
    
    id = db.Column(db.Integer, primary_key=True)
    license_plate_text = db.Column(db.String(20), nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    added_by = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlacklistPlate {self.license_plate_text}: {self.reason}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blacklist entry to dictionary.
        
        Returns:
            Dictionary representation of the blacklist entry
        """
        return {
            'id': self.id,
            'license_plate_text': self.license_plate_text,
            'reason': self.reason,
            'added_by': self.added_by,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def deactivate(self):
        """Deactivate the blacklist entry."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """
        Check if the blacklist entry is expired.
        
        Returns:
            True if expired, False otherwise
        """
        if not self.expiry_date:
            return False
        return datetime.utcnow() > self.expiry_date
    
    @classmethod
    def get_active_blacklist(cls) -> list:
        """
        Get all active blacklist entries.
        
        Returns:
            List of active blacklist entries
        """
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_by_plate_number(cls, plate_number: str) -> Optional['BlacklistPlate']:
        """
        Get blacklist entry by plate number.
        
        Args:
            plate_number: License plate number to search for
            
        Returns:
            BlacklistPlate object or None if not found
        """
        return cls.query.filter_by(
            license_plate_text=plate_number,
            is_active=True
        ).first()
