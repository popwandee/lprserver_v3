#!/usr/bin/env python3
"""
Configuration file for AI Camera v1.3

This file provides default configuration values for the system.

Author: AI Camera Team
Version: 1.3
Date: December 2024
"""

import os
from pathlib import Path

# Load environment variables from .env.production first
def load_env_file():
    """Load environment variables from .env.production file."""
    env_file = Path(__file__).parent.parent.parent / '.env.production'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key.strip()] = value

# Load environment variables
load_env_file()

# Flask Configuration
FLASK_HOST =  '0.0.0.0'
FLASK_PORT = int(5000)
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
DEBUG = "DEBUG"

# Base directory for the project - should be /home/camuser/aicamera/
current_file = Path(__file__)
BASE_DIR = str(current_file.parent.parent.parent.parent.absolute())  # Go up from core/src/v1_3/aicamera

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'db', 'lpr_data.db')
WEBSOCKET_LOG_FILE = os.path.join(BASE_DIR, "logs", "websocket.log")
DETECTION_LOG_FILE = os.path.join(BASE_DIR, "logs", "detection.log")
# AI Models Configuration
HEF_MODEL_PATH = "@local"
MODEL_ZOO_URL = "resources" 
VEHICLE_DETECTION_MODEL = "yolov8n_relu6_car--640x640_quant_hailort_hailo8_1"
LICENSE_PLATE_DETECTION_MODEL ="yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1"
LICENSE_PLATE_OCR_MODEL = "yolov8n_relu6_lp_ocr--256x128_quant_hailort_hailo8_1"
OCR_MODEL ="easyOCR_raw_image" 

# OCR Configuration
EASYOCR_LANGUAGES = ['en', 'th']

# Image Storage
IMAGE_SAVE_DIR =  os.path.join(BASE_DIR, 'captured_images')

# WebSocket server configuration
WEBSOCKET_SERVER_URL = os.getenv("WEBSOCKET_SERVER_URL")

# AI Camera Identification
AICAMERA_ID = os.getenv("AICAMERA_ID", "1")
CHECKPOINT_ID = os.getenv("CHECKPOINT_ID", "1")
LOCATION_LAT = "13.729610"
LOCATION_LON = "100.501443"

# Camera properties defaults
DEFAULT_RESOLUTION = (640, 640)
DEFAULT_FRAMERATE = 30
DEFAULT_BRIGHTNESS = 0.0  # -1.0 to 1.0
DEFAULT_CONTRAST = 1.0    # 0.0 to 2.0
DEFAULT_SATURATION = 1.0  # 0.0 to 2.0
DEFAULT_SHARPNESS = 1.0   # 0.0 to 4.0
DEFAULT_AWB_MODE = 0      # 0=auto, 1=fluorescent, etc.

# Detection Settings
DETECTION_INTERVAL = float( 0.1)
CONFIDENCE_THRESHOLD = float( 0.5)
PLATE_CONFIDENCE_THRESHOLD = float( 0.3)

# Threading intervals (in seconds)
SENDER_INTERVAL = 60.0    # How often the sender thread checks for new detections (1 minute)
HEALTH_SENDER_INTERVAL = 300.0  # How often health status is sent to server (5 minutes)

# Health monitoring interval (in seconds, 3600 seconds = 1 hour)
HEALTH_CHECK_INTERVAL = 3600

# WebSocket sender configuration
WEBSOCKET_SENDER_ENABLED = True  # Enable WebSocket sender
WEBSOCKET_CONNECTION_TIMEOUT = 30.0  # Connection timeout in seconds
WEBSOCKET_RETRY_INTERVAL = 60.0  # Retry connection interval in seconds
WEBSOCKET_MAX_RETRIES = 5  # Maximum connection retries before giving up

# Storage monitoring configuration
STORAGE_MONITOR_ENABLED = True  # Enable storage monitoring
STORAGE_MONITOR_INTERVAL = 300  # Storage monitoring interval in seconds (5 minutes)
STORAGE_MIN_FREE_SPACE_GB = 10.0  # Minimum free space in GB before cleanup
STORAGE_RETENTION_DAYS = 7  # Number of days to keep images
STORAGE_BATCH_SIZE = 100  # Number of files to delete in each batch
STORAGE_FOLDER_PATH = os.path.join(BASE_DIR, 'captured_images')  # Path to monitored folder

# Auto-startup configuration
AUTO_START_CAMERA = True      # Auto start camera on system startup
AUTO_START_STREAMING = True   # Auto start streaming when camera starts
AUTO_START_DETECTION = True   # Auto start detection when streaming starts
AUTO_START_HEALTH_MONITOR = True  # Auto start health monitoring when detection starts
AUTO_START_WEBSOCKET_SENDER = True  # Auto start WebSocket sender when health monitor starts
AUTO_START_STORAGE_MONITOR = True  # Auto start storage monitoring when WebSocket sender starts
STARTUP_DELAY = 5.0          # Delay in seconds between startup steps
HEALTH_MONITOR_STARTUP_DELAY = 5.0  # Delay before starting health monitoring (increased for model loading)
WEBSOCKET_SENDER_STARTUP_DELAY = 5.0  # Delay before starting WebSocket sender
STORAGE_MONITOR_STARTUP_DELAY = 5.0  # Delay before starting storage monitoring

# Create directories if they don't exist - all in BASE_DIR (aicamera/)
Path(IMAGE_SAVE_DIR).mkdir(parents=True, exist_ok=True)
if DATABASE_PATH:
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
# Create logs directory
Path(BASE_DIR, 'logs').mkdir(parents=True, exist_ok=True)

# Debug: Print BASE_DIR for verification
from v1_3.src.core.utils.logging_config import get_logger
logger = get_logger(__name__)
logger.info(f"Config BASE_DIR set to: {BASE_DIR}")
logger.info(f"IMAGE_SAVE_DIR: {IMAGE_SAVE_DIR}")
logger.info(f"DATABASE_PATH: {DATABASE_PATH}")
logger.info(f"LOGS directory: {os.path.join(BASE_DIR, 'logs')}")