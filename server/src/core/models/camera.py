"""
Camera Model for managing camera information

This model stores camera metadata including location, status, and connectivity information.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

# Import db from models package
from core.models import db

class Camera(db.Model):
    """
    Camera Model for managing camera information.
    
    This model includes:
    - Camera identification and metadata
    - Location information
    - Status and connectivity tracking
    - Configuration settings
    """
    __tablename__ = 'cameras'
    
    camera_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='inactive', index=True)  # active, inactive, maintenance
    last_activity = db.Column(db.DateTime, nullable=True, index=True)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    port = db.Column(db.Integer, default=8765)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Camera {self.camera_id}: {self.name}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert camera to dictionary.
        
        Returns:
            Dictionary representation of the camera
        """
        return {
            'camera_id': self.camera_id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'status': self.status,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'ip_address': self.ip_address,
            'port': self.port,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active_cameras(cls) -> list:
        """
        Get all active cameras.
        
        Returns:
            List of active cameras
        """
        return cls.query.filter_by(status='active').all()
    
    @classmethod
    def get_camera_by_id(cls, camera_id: str) -> Optional['Camera']:
        """
        Get camera by ID.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Camera object or None if not found
        """
        return cls.query.get(camera_id)
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_status(self, status: str):
        """
        Set camera status.
        
        Args:
            status: New status (active, inactive, maintenance)
        """
        self.status = status
        self.updated_at = datetime.utcnow()
