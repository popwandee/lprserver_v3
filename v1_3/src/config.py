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

# AI Models Configuration
VEHICLE_DETECTION_MODEL = os.getenv('VEHICLE_DETECTION_MODEL', None)
LICENSE_PLATE_DETECTION_MODEL = os.getenv('LICENSE_PLATE_DETECTION_MODEL', None)

# OCR Configuration
EASYOCR_LANGUAGES = ['en', 'th']

# Image Storage
IMAGE_SAVE_DIR = os.getenv('IMAGE_SAVE_DIR', '/tmp/captured_images')

# Detection Settings
DETECTION_INTERVAL = float(os.getenv('DETECTION_INTERVAL', 0.1))

# Create directories if they don't exist
Path(IMAGE_SAVE_DIR).mkdir(parents=True, exist_ok=True)