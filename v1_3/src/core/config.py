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

# Flask Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'db', 'lpr_data.db')

# AI Models Configuration
VEHICLE_DETECTION_MODEL = os.getenv('VEHICLE_DETECTION_MODEL', None)
LICENSE_PLATE_DETECTION_MODEL = os.getenv('LICENSE_PLATE_DETECTION_MODEL', None)
LICENSE_PLATE_OCR_MODEL = os.getenv('LICENSE_PLATE_OCR_MODEL', None)

# Hailo AI Configuration  
HEF_MODEL_PATH = os.getenv('HEF_MODEL_PATH', 'hailo')
MODEL_ZOO_URL = os.getenv('MODEL_ZOO_URL', 'https://hailo-model-zoo.s3.eu-west-2.amazonaws.com')

# OCR Configuration
EASYOCR_LANGUAGES = ['en', 'th']

# Image Storage
IMAGE_SAVE_DIR = os.getenv('IMAGE_SAVE_DIR', os.path.join(BASE_DIR, 'captured_images'))

# WebSocket server configuration
WEBSOCKET_SERVER_URL = os.getenv("WEBSOCKET_SERVER_URL")

# Camera properties defaults
DEFAULT_RESOLUTION = (640, 640)
DEFAULT_FRAMERATE = 30
DEFAULT_BRIGHTNESS = 0.0  # -1.0 to 1.0
DEFAULT_CONTRAST = 1.0    # 0.0 to 2.0
DEFAULT_SATURATION = 1.0  # 0.0 to 2.0
DEFAULT_SHARPNESS = 1.0   # 0.0 to 4.0
DEFAULT_AWB_MODE = 0      # 0=auto, 1=fluorescent, etc.

# Detection Settings
DETECTION_INTERVAL = float(os.getenv('DETECTION_INTERVAL', 0.1))

# Threading intervals (in seconds)
SENDER_INTERVAL = 60.0    # How often the sender thread checks for new detections (1 minute)

# Health monitoring interval (in seconds, 3600 seconds = 1 hour)
HEALTH_CHECK_INTERVAL = 3600

# Create directories if they don't exist
Path(IMAGE_SAVE_DIR).mkdir(parents=True, exist_ok=True)
if DATABASE_PATH:
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)