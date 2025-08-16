#!/usr/bin/env python3
"""
Logging Configuration Utility for AI Camera v1.3

This module provides centralized logging configuration for the entire
application with support for different log levels, file rotation,
and structured logging.

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

import os
import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


def setup_logging(
    level: str = "DEBUG",
    log_dir: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir (Optional[str]): Directory for log files
        max_bytes (int): Maximum size of log file before rotation
        backup_count (int): Number of backup log files to keep
    
    Returns:
        logging.Logger: Configured logger
    """
    # Use centralized log directory at project root
    if log_dir is None:
        # Point to aicamera/logs directory (same level as v1_3)
        project_root = Path(__file__).parent.parent.parent.parent
        log_dir = project_root / "logs"
    
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Use single log file with date rotation, not timestamp-based names
    log_file = log_dir / "aicamera.log"

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)  # Console shows INFO and above
    root_logger.addHandler(console_handler)
    
    # Add file handler with daily rotation
    try:
        file_handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when='D',               # Daily rotation
            interval=1,
            backupCount=30,         # Keep 30 days of logs
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(numeric_level)  # File gets all levels
        root_logger.addHandler(file_handler)
        
        # Clean up old log files beyond retention period
        _cleanup_old_logs(log_dir, days_to_keep=30)
        
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Log initial message to verify logging is working
    root_logger.info(f"Logging initialized - Level: {level}, Log dir: {log_dir}")
    
    return root_logger


def _cleanup_old_logs(log_dir: Path, days_to_keep: int = 30):
    """Clean up old log files beyond retention period."""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        for log_file in log_dir.glob("aicamera.log.*"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    log_file.unlink()
                    print(f"Deleted old log file: {log_file}")
            except Exception as e:
                print(f"Failed to delete old log file {log_file}: {e}")
    except Exception as e:
        print(f"Error during log cleanup: {e}")
    

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name (str): Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

