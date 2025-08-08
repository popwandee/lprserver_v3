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
    # Create log directory if not specified
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
    
    # ตั้งชื่อไฟล์ตามวันที่
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"aicamera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # Create formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='D',               # Daily rotation
        interval=1,
        backupCount=31,         # Keep 15 files
        encoding='utf-8'
    )
    file_handler.namer = lambda name: name.replace(".log", "") + ".log"
    file_handler.setFormatter(detailed_formatter)
    # ลบไฟล์ที่เกิน 31 วัน
    for f in log_dir.glob("aicamera_*.log"):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if datetime.now() - mtime > timedelta(days=15):
                f.unlink()
        except Exception as e:
            root_logger.warning(f"Failed to delete old log file {f}: {e}")

    return root_logger
    

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name (str): Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

