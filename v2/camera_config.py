"""
Camera Configuration Module
รวมการตั้งค่ากล้องทั้งหมดไว้ในที่เดียว เพื่อลดความซ้ำซ้อน
"""

import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env.production')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Camera Stream Configuration
# ทั้ง main และ lores stream ใช้ 640x640 เพื่อความสม่ำเสมอ
# Main stream สำหรับ detection และ lores stream สำหรับ video feed
DETECTION_RESOLUTION = (640, 640)  # Main stream สำหรับ detection
VIDEO_FEED_RESOLUTION = (640, 640)  # Lores stream สำหรับ video feed

# Camera Settings
DEFAULT_FRAMERATE = 30
DEFAULT_BRIGHTNESS = 0.0  # -1.0 to 1.0
DEFAULT_CONTRAST = 1.0    # 0.0 to 2.0
DEFAULT_SATURATION = 1.0  # 0.0 to 2.0
DEFAULT_SHARPNESS = 1.0   # 0.0 to 4.0
DEFAULT_AWB_MODE = 0      # 0=auto, 1=fluorescent, 2=incandescent, 3=tungsten, 4=horizon, 5=daylight, 6=cloudy, 7=shade, 8=custom

# Auto Focus Settings
AUTO_FOCUS_MODE = 2       # Auto focus mode
AUTO_FOCUS_TRIGGER = 0    # Start auto focus

# Stream Configuration
MAIN_STREAM_CONFIG = {
    "size": DETECTION_RESOLUTION,
    "format": "XBGR8888"  # กลับไปใช้ XBGR8888 สำหรับ main stream
}

LORES_STREAM_CONFIG = {
    "size": VIDEO_FEED_RESOLUTION,
    "format": "XBGR8888"  # ใช้ XBGR8888 สำหรับ lores stream
}

# Camera Configuration
CAMERA_CONFIG = {
    "main": MAIN_STREAM_CONFIG,
    "lores": LORES_STREAM_CONFIG,
    "encode": "main",  # Encode main stream for display
    "buffer_count": 4  # ลดจาก 6 เป็น 4 เพื่อลด memory usage
}

# Default Camera Settings
DEFAULT_CAMERA_SETTINGS = {
    'resolution': DETECTION_RESOLUTION,
    'framerate': DEFAULT_FRAMERATE,
    'brightness': DEFAULT_BRIGHTNESS,
    'contrast': DEFAULT_CONTRAST,
    'saturation': DEFAULT_SATURATION,
    'sharpness': DEFAULT_SHARPNESS,
    'awb_mode': DEFAULT_AWB_MODE
}

def get_camera_config():
    """Get camera configuration"""
    return CAMERA_CONFIG

def get_default_settings():
    """Get default camera settings"""
    return DEFAULT_CAMERA_SETTINGS.copy()

def get_detection_resolution():
    """Get resolution for detection (main stream)"""
    return DETECTION_RESOLUTION

def get_video_feed_resolution():
    """Get resolution for video feed (lores stream)"""
    return VIDEO_FEED_RESOLUTION 