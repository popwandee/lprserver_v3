"""
Blacklist Service for License Plate Management

This service manages blacklisted license plates, including adding, removing,
checking, and processing LPR detections against the blacklist.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.models.blacklist_plate import BlacklistPlate
from core.models.lpr_record import LPRRecord
from core.models import db
from constants import BLACKLIST_STATUS_ACTIVE, BLACKLIST_STATUS_INACTIVE

logger = logging.getLogger(__name__)

class BlacklistService:
    """
    Service for managing blacklist functionality.
    
    This service provides:
    - Adding/removing license plates from blacklist
    - Checking if plates are blacklisted
    - Processing LPR detections against blacklist
    - Sending blacklist alerts
    - Blacklist statistics
    """
    
    def __init__(self):
        self.db_session = None
        self.socketio = None
    
    def initialize(self, db_session, socketio=None):
        """
        Initialize the Blacklist Service with dependencies.
        
        Args:
            db_session: Database session
            socketio: SocketIO instance for real-time alerts
        """
        self.db_session = db_session
        self.socketio = socketio
        logger.info("Blacklist service initialized")
    
    def add_to_blacklist(self, license_plate_text: str, reason: str, added_by: str, 
                        expiry_date: Optional[datetime] = None, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a license plate to blacklist.
        
        Args:
            license_plate_text: License plate to blacklist
            reason: Reason for blacklisting
            added_by: User who added the plate
            expiry_date: Optional expiry date
            notes: Optional additional notes
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Check if already exists
            existing = self.db_session.query(BlacklistPlate).filter_by(
                license_plate_text=license_plate_text,
                is_active=BLACKLIST_STATUS_ACTIVE
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'message': f'License plate {license_plate_text} is already in blacklist'
                }
            
            # Create new blacklist entry
            blacklist_entry = BlacklistPlate(
                license_plate_text=license_plate_text,
                reason=reason,
                added_by=added_by,
                expiry_date=expiry_date,
                notes=notes
            )
            
            self.db_session.add(blacklist_entry)
            self.db_session.commit()
            
            logger.info(f"Added {license_plate_text} to blacklist by {added_by}")
            
            return {
                'success': True,
                'message': f'License plate {license_plate_text} added to blacklist',
                'blacklist_id': blacklist_entry.id
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error adding to blacklist: {str(e)}")
            return {
                'success': False,
                'message': f'Error adding to blacklist: {str(e)}'
            }
    
    def remove_from_blacklist(self, blacklist_id: int, removed_by: str) -> Dict[str, Any]:
        """
        Remove a license plate from blacklist.
        
        Args:
            blacklist_id: ID of blacklist entry to remove
            removed_by: User who removed the plate
            
        Returns:
            Dictionary with operation result
        """
        try:
            blacklist_entry = self.db_session.query(BlacklistPlate).get(blacklist_id)
            
            if not blacklist_entry:
                return {
                    'success': False,
                    'message': 'Blacklist entry not found'
                }
            
            if not blacklist_entry.is_active:
                return {
                    'success': False,
                    'message': 'Blacklist entry is already inactive'
                }
            
            blacklist_entry.deactivate()
            self.db_session.commit()
            
            logger.info(f"Removed {blacklist_entry.license_plate_text} from blacklist by {removed_by}")
            
            return {
                'success': True,
                'message': f'License plate {blacklist_entry.license_plate_text} removed from blacklist'
            }
            
        except Exception as e:
            logger.error(f"Error removing from blacklist: {str(e)}")
            return {
                'success': False,
                'message': f'Error removing from blacklist: {str(e)}'
            }
    
    def check_blacklist(self, license_plate_text: str) -> Optional[BlacklistPlate]:
        """
        Check if a license plate is blacklisted.
        
        Args:
            license_plate_text: License plate to check
            
        Returns:
            BlacklistPlate object if found, None otherwise
        """
        return self.db_session.query(BlacklistPlate).filter_by(
            license_plate_text=license_plate_text,
            is_active=BLACKLIST_STATUS_ACTIVE
        ).first()
    
    def get_blacklist_entries(self, page: int = 1, per_page: int = 20, 
                            active_only: bool = True) -> Dict[str, Any]:
        """
        Get paginated blacklist entries.
        
        Args:
            page: Page number
            per_page: Items per page
            active_only: Whether to return only active entries
            
        Returns:
            Dictionary with blacklist entries and pagination info
        """
        try:
            query = self.db_session.query(BlacklistPlate)
            
            if active_only:
                query = query.filter_by(is_active=BLACKLIST_STATUS_ACTIVE)
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            entries = query.order_by(BlacklistPlate.created_at.desc())\
                .offset((page - 1) * per_page)\
                .limit(per_page)\
                .all()
            
            return {
                'success': True,
                'data': [entry.to_dict() for entry in entries],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting blacklist entries: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_lpr_detection(self, lpr_record: LPRRecord) -> bool:
        """
        Process LPR detection and check for blacklist.
        
        Args:
            lpr_record: LPR record to process
            
        Returns:
            True if blacklisted, False otherwise
        """
        try:
            # Check if plate is blacklisted
            blacklist_entry = self.check_blacklist(lpr_record.plate_number)
            
            if blacklist_entry:
                # Mark record as blacklisted
                lpr_record.is_blacklisted = True
                self.db_session.commit()
                
                # Send blacklist alert
                self.send_blacklist_alert(lpr_record, blacklist_entry)
                
                logger.warning(f"Blacklisted plate detected: {lpr_record.plate_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing LPR detection: {str(e)}")
            return False
    
    def send_blacklist_alert(self, lpr_record: LPRRecord, blacklist_entry: BlacklistPlate) -> None:
        """
        Send blacklist alert via WebSocket.
        
        Args:
            lpr_record: LPR record that triggered the alert
            blacklist_entry: Blacklist entry that matched
        """
        try:
            if self.socketio:
                alert_data = {
                    'type': 'blacklist_alert',
                    'lpr_record': lpr_record.to_dict(),
                    'blacklist_entry': blacklist_entry.to_dict(),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Send to dashboard room
                self.socketio.emit('blacklist_alert', alert_data, room='dashboard')
                
                # Send to health monitoring room
                self.socketio.emit('blacklist_alert', alert_data, room='health_monitoring')
                
                logger.info(f"Blacklist alert sent for plate: {lpr_record.plate_number}")
                
        except Exception as e:
            logger.error(f"Error sending blacklist alert: {str(e)}")
    
    def get_blacklist_statistics(self) -> Dict[str, Any]:
        """
        Get blacklist statistics.
        
        Returns:
            Dictionary with blacklist statistics
        """
        try:
            # Total active blacklist entries
            total_active = self.db_session.query(BlacklistPlate)\
                .filter_by(is_active=BLACKLIST_STATUS_ACTIVE)\
                .count()
            
            # Total inactive entries
            total_inactive = self.db_session.query(BlacklistPlate)\
                .filter_by(is_active=BLACKLIST_STATUS_INACTIVE)\
                .count()
            
            # Recent additions (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_additions = self.db_session.query(BlacklistPlate)\
                .filter(BlacklistPlate.created_at >= week_ago)\
                .count()
            
            # Blacklist detections today
            today = datetime.utcnow().date()
            today_detections = self.db_session.query(LPRRecord)\
                .filter(
                    LPRRecord.is_blacklisted == True,
                    db.func.date(LPRRecord.timestamp) == today
                )\
                .count()
            
            return {
                'success': True,
                'data': {
                    'total_active': total_active,
                    'total_inactive': total_inactive,
                    'recent_additions': recent_additions,
                    'today_detections': today_detections
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting blacklist statistics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def get_active_blacklist(cls) -> List[Dict[str, Any]]:
        """
        Get all active blacklist entries.
        
        Returns:
            List of active blacklist entries
        """
        try:
            entries = db.session.query(BlacklistPlate)\
                .filter_by(is_active=BLACKLIST_STATUS_ACTIVE)\
                .all()
            return [entry.to_dict() for entry in entries]
        except Exception as e:
            logger.error(f"Error getting active blacklist: {str(e)}")
            return []
    
    def search_blacklist(self, search_term: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Search blacklist entries.
        
        Args:
            search_term: Search term
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with search results
        """
        try:
            query = self.db_session.query(BlacklistPlate)\
                .filter(
                    db.or_(
                        BlacklistPlate.license_plate_text.contains(search_term),
                        BlacklistPlate.reason.contains(search_term),
                        BlacklistPlate.notes.contains(search_term)
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Get paginated results
            entries = query.order_by(BlacklistPlate.created_at.desc())\
                .offset((page - 1) * per_page)\
                .limit(per_page)\
                .all()
            
            return {
                'success': True,
                'data': [entry.to_dict() for entry in entries],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching blacklist: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
