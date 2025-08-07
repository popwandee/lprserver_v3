#!/usr/bin/env python3
"""
Logging Configuration for AI Camera v1.3

This module provides centralized logging configuration for the entire
application with support for different log levels, file rotation,
and structured logging.

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup application logging configuration.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir (Optional[str]): Directory for log files
        max_bytes (int): Maximum size of log file before rotation
        backup_count (int): Number of backup log files to keep
        
    Returns:
        logging.Logger: Configured root logger
    """
    # Create log directory if not specified
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
    
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    all_log_file = log_dir / "aicamera.log"
    file_handler = logging.handlers.RotatingFileHandler(
        all_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error log file
    error_log_file = log_dir / "aicamera_error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Create application logger
    app_logger = logging.getLogger('aicamera')
    app_logger.info(f"Logging initialized - Level: {level}, Directory: {log_dir}")
    
    return app_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str):
    """
    Set the logging level for the root logger.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Update all handlers
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(getattr(logging, level.upper()))
    
    logging.getLogger('aicamera').info(f"Log level changed to: {level}")


def log_system_info():
    """
    Log system information for debugging purposes.
    """
    logger = logging.getLogger('aicamera')
    
    import platform
    import psutil
    import sys
    
    logger.info("=== System Information ===")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python Version: {platform.python_version()}")
    logger.info(f"Architecture: {platform.architecture()[0]}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"CPU Count: {psutil.cpu_count()}")
    logger.info(f"Memory Total: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    logger.info(f"Disk Total: {psutil.disk_usage('/').total / (1024**3):.2f} GB")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"PID: {os.getpid()}")
    logger.info("==========================")


if __name__ == "__main__":
    # Test logging configuration
    logger = setup_logging(level="DEBUG")
    log_system_info()
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

