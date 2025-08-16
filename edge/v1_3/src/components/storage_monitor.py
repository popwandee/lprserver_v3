#!/usr/bin/env python3
"""
Storage Monitor Component for AI Camera v1.3

This component monitors disk space and manages the captured_images folder
to prevent disk space issues by automatically cleaning up old images.
"""

import os
import time
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from threading import Thread, Event

from v1_3.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)

class StorageMonitor:
    """
    Storage Monitor Component for disk space management.
    
    Features:
    - Monitor disk space usage
    - Clean up old images from captured_images folder
    - Prioritize deletion based on database status (sent vs unsent)
    - Configurable thresholds and retention policies
    """
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger(__name__)
        self.db_manager = None
        self.running = False
        self.stop_event = Event()
        self.monitor_thread = None
        
        # Configuration
        from v1_3.src.core.config import (
            STORAGE_FOLDER_PATH, STORAGE_MIN_FREE_SPACE_GB, STORAGE_RETENTION_DAYS,
            STORAGE_BATCH_SIZE, STORAGE_MONITOR_INTERVAL
        )
        
        self.folder_path = STORAGE_FOLDER_PATH
        self.min_free_space_gb = STORAGE_MIN_FREE_SPACE_GB
        self.retention_days = STORAGE_RETENTION_DAYS
        self.batch_size = STORAGE_BATCH_SIZE
        self.monitor_interval = STORAGE_MONITOR_INTERVAL
        self.last_cleanup_time = None
        self.cleanup_stats = {
            'total_files_deleted': 0,
            'sent_files_deleted': 0,
            'unsent_files_deleted': 0,
            'last_cleanup': None,
            'disk_space_freed_gb': 0.0
        }
    
    def initialize(self) -> bool:
        """Initialize Storage Monitor with database connection."""
        try:
            from v1_3.src.core.dependency_container import get_service
            self.db_manager = get_service('database_manager')
            
            if not self.db_manager:
                self.logger.error("Database manager not available")
                return False
            
            # Create captured_images folder if it doesn't exist
            Path(self.folder_path).mkdir(parents=True, exist_ok=True)
            
            self.logger.info("Storage Monitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Storage Monitor: {e}")
            return False
    
    def get_disk_usage(self, path: str = None) -> Dict[str, float]:
        """Get disk usage statistics for the specified path."""
        try:
            target_path = path or self.folder_path
            total, used, free = shutil.disk_usage(target_path)
            
            return {
                'total_gb': total / (1024 ** 3),
                'used_gb': used / (1024 ** 3),
                'free_gb': free / (1024 ** 3),
                'usage_percentage': (used / total) * 100
            }
        except Exception as e:
            self.logger.error(f"Error getting disk usage: {e}")
            return {
                'total_gb': 0.0,
                'used_gb': 0.0,
                'free_gb': 0.0,
                'usage_percentage': 0.0
            }
    
    def get_folder_size(self, folder_path: str = None) -> Dict[str, int]:
        """Get folder size and file count statistics."""
        try:
            target_path = folder_path or self.folder_path
            total_size = 0
            file_count = 0
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
            
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 ** 2),
                'file_count': file_count
            }
        except Exception as e:
            self.logger.error(f"Error getting folder size: {e}")
            return {
                'total_size_bytes': 0,
                'total_size_mb': 0.0,
                'file_count': 0
            }
    
    def get_files_by_status(self) -> Tuple[List[str], List[str]]:
        """Get lists of sent and unsent image files from database."""
        sent_files = []
        unsent_files = []
        
        try:
            if not self.db_manager:
                return sent_files, unsent_files
            
            # Query database for image files and their status
            query = """
                SELECT image_path, status, created_at 
                FROM detection_results 
                WHERE image_path IS NOT NULL 
                ORDER BY created_at ASC
            """
            
            results = self.db_manager.execute_query(query)
            
            for row in results:
                image_path = row[0]
                status = row[1]
                
                # Check if file exists
                if os.path.exists(image_path):
                    if status == 'sent':
                        sent_files.append(image_path)
                    else:
                        unsent_files.append(image_path)
            
            self.logger.debug(f"Found {len(sent_files)} sent files and {len(unsent_files)} unsent files")
            
        except Exception as e:
            self.logger.error(f"Error getting files by status: {e}")
        
        return sent_files, unsent_files
    
    def cleanup_old_files(self) -> Dict[str, int]:
        """Clean up old files based on retention policy and disk space."""
        cleanup_stats = {
            'total_deleted': 0,
            'sent_deleted': 0,
            'unsent_deleted': 0,
            'space_freed_mb': 0.0
        }
        
        try:
            # Check if cleanup is needed
            disk_usage = self.get_disk_usage()
            if disk_usage['free_gb'] >= self.min_free_space_gb:
                self.logger.debug("Sufficient disk space available")
                return cleanup_stats
            
            self.logger.info(f"Low disk space detected: {disk_usage['free_gb']:.2f} GB free")
            
            # Get files by status
            sent_files, unsent_files = self.get_files_by_status()
            
            # Calculate retention limit
            retention_limit = time.time() - (self.retention_days * 86400)
            
            # Filter files by age and sort by modification time
            old_sent_files = [
                f for f in sent_files 
                if os.path.getmtime(f) < retention_limit
            ]
            old_sent_files.sort(key=lambda x: os.path.getmtime(x))
            
            old_unsent_files = [
                f for f in unsent_files 
                if os.path.getmtime(f) < retention_limit
            ]
            old_unsent_files.sort(key=lambda x: os.path.getmtime(x))
            
            # Delete files: sent files first, then unsent files
            files_to_delete = old_sent_files + old_unsent_files
            
            for file_path in files_to_delete[:self.batch_size]:
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    
                    cleanup_stats['total_deleted'] += 1
                    cleanup_stats['space_freed_mb'] += file_size / (1024 ** 2)
                    
                    if file_path in old_sent_files:
                        cleanup_stats['sent_deleted'] += 1
                        self.logger.debug(f"Deleted sent file: {file_path}")
                    else:
                        cleanup_stats['unsent_deleted'] += 1
                        self.logger.debug(f"Deleted unsent file: {file_path}")
                    
                except Exception as e:
                    self.logger.error(f"Error deleting file {file_path}: {e}")
            
            # Update cleanup statistics
            self.cleanup_stats['total_files_deleted'] += cleanup_stats['total_deleted']
            self.cleanup_stats['sent_files_deleted'] += cleanup_stats['sent_deleted']
            self.cleanup_stats['unsent_files_deleted'] += cleanup_stats['unsent_deleted']
            self.cleanup_stats['disk_space_freed_gb'] += cleanup_stats['space_freed_mb'] / 1024
            self.cleanup_stats['last_cleanup'] = datetime.now().isoformat()
            self.last_cleanup_time = datetime.now()
            
            if cleanup_stats['total_deleted'] > 0:
                self.logger.info(
                    f"Cleanup completed: {cleanup_stats['total_deleted']} files deleted "
                    f"({cleanup_stats['sent_deleted']} sent, {cleanup_stats['unsent_deleted']} unsent), "
                    f"{cleanup_stats['space_freed_mb']:.2f} MB freed"
                )
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        
        return cleanup_stats
    
    def get_storage_status(self) -> Dict[str, any]:
        """Get comprehensive storage status."""
        try:
            self.logger.debug("Getting disk usage")
            disk_usage = self.get_disk_usage()
            self.logger.debug(f"Disk usage: {disk_usage}")
            
            self.logger.debug("Getting folder stats")
            folder_stats = self.get_folder_size()
            self.logger.debug(f"Folder stats: {folder_stats}")
            
            self.logger.debug("Getting files by status")
            sent_files, unsent_files = self.get_files_by_status()
            self.logger.debug(f"Files by status - Sent: {len(sent_files)}, Unsent: {len(unsent_files)}")
            
            return {
                'disk_usage': disk_usage,
                'folder_stats': folder_stats,
                'file_counts': {
                    'sent_files': len(sent_files),
                    'unsent_files': len(unsent_files),
                    'total_files': len(sent_files) + len(unsent_files)
                },
                'cleanup_stats': self.cleanup_stats,
                'configuration': {
                    'folder_path': self.folder_path,
                    'min_free_space_gb': self.min_free_space_gb,
                    'retention_days': self.retention_days,
                    'batch_size': self.batch_size,
                    'monitor_interval': self.monitor_interval
                },
                'status': {
                    'running': self.running,
                    'last_cleanup': self.last_cleanup_time.isoformat() if self.last_cleanup_time else None,
                    'needs_cleanup': disk_usage['free_gb'] < self.min_free_space_gb
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting storage status: {e}")
            return {}
    
    def start_monitoring(self, interval: int = None) -> bool:
        """Start continuous storage monitoring."""
        if self.running:
            self.logger.warning("Storage monitoring is already running")
            return True
        
        try:
            self.monitor_interval = interval or self.monitor_interval
            self.stop_event.clear()
            self.running = True
            
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info(f"Storage monitoring started (interval: {self.monitor_interval}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start storage monitoring: {e}")
            self.running = False
            return False
    
    def stop_monitoring(self):
        """Stop continuous storage monitoring."""
        if not self.running:
            return
        
        try:
            self.stop_event.set()
            self.running = False
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            self.logger.info("Storage monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping storage monitoring: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while not self.stop_event.is_set():
            try:
                # Perform cleanup if needed
                self.cleanup_old_files()
                
                # Wait for next check
                self.stop_event.wait(self.monitor_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                self.stop_event.wait(60)  # Wait 1 minute on error
    
    def update_configuration(self, config: Dict[str, any]) -> bool:
        """Update storage monitor configuration."""
        try:
            if 'min_free_space_gb' in config:
                self.min_free_space_gb = float(config['min_free_space_gb'])
            
            if 'retention_days' in config:
                self.retention_days = int(config['retention_days'])
            
            if 'batch_size' in config:
                self.batch_size = int(config['batch_size'])
            
            if 'monitor_interval' in config:
                self.monitor_interval = int(config['monitor_interval'])
            
            if 'folder_path' in config:
                self.folder_path = str(config['folder_path'])
            
            self.logger.info("Storage monitor configuration updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False
