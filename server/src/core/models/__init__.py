# Models package
from flask_sqlalchemy import SQLAlchemy

# Create a single db instance for all models
db = SQLAlchemy()

from .camera import Camera
from .lpr_record import LPRRecord
from .blacklist_plate import BlacklistPlate
from .health_check import HealthCheck

__all__ = ['db', 'Camera', 'LPRRecord', 'BlacklistPlate', 'HealthCheck']
