"""
Constants for LPR Server v3
ตามข้อกำหนด Variable Mapping และมาตรฐานการเขียนโค้ด
"""

# Health Check Status Constants
HEALTH_STATUS_PASS = "PASS"
HEALTH_STATUS_FAIL = "FAIL"
HEALTH_STATUS_WARNING = "WARNING"
HEALTH_STATUS_UNKNOWN = "UNKNOWN"

# Camera Status Constants
CAMERA_STATUS_ACTIVE = "active"
CAMERA_STATUS_INACTIVE = "inactive"
CAMERA_STATUS_MAINTENANCE = "maintenance"

# Blacklist Status Constants
BLACKLIST_STATUS_ACTIVE = True
BLACKLIST_STATUS_INACTIVE = False

# LPR Record Constants
LPR_CONFIDENCE_THRESHOLD_HIGH = 80.0
LPR_CONFIDENCE_THRESHOLD_MEDIUM = 60.0
LPR_CONFIDENCE_THRESHOLD_LOW = 0.0

# WebSocket Event Constants
WS_EVENT_CAMERA_REGISTER = "camera_register"
WS_EVENT_LPR_DATA = "lpr_data"
WS_EVENT_STATUS = "status"
WS_EVENT_ERROR = "error"
WS_EVENT_LPR_RESPONSE = "lpr_response"
WS_EVENT_NEW_LPR_RECORD = "new_lpr_record"
WS_EVENT_BLACKLIST_ALERT = "blacklist_alert"
WS_EVENT_JOIN_DASHBOARD = "join_dashboard"

# API Response Constants
API_SUCCESS = "success"
API_ERROR = "error"
API_MESSAGE = "message"

# Database Constants
DB_DEFAULT_PAGE_SIZE = 20
DB_MAX_PAGE_SIZE = 100

# File Storage Constants
IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp']
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Time Constants
DEFAULT_TIMEOUT_MINUTES = 5
DEFAULT_REFRESH_INTERVAL_SECONDS = 30
DEFAULT_BLACKLIST_CHECK_HOURS = 24

# Logging Constants
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# Security Constants
SECRET_KEY_MIN_LENGTH = 32
PASSWORD_MIN_LENGTH = 8

# Network Constants
WEBSOCKET_PORT = 8765
DEFAULT_HTTP_PORT = 5000
DEFAULT_NGINX_PORT = 80

# Error Messages
ERROR_MESSAGES = {
    'camera_not_found': 'Camera not found',
    'invalid_plate_number': 'Invalid plate number format',
    'database_error': 'Database operation failed',
    'file_upload_error': 'File upload failed',
    'websocket_connection_error': 'WebSocket connection failed',
    'blacklist_already_exists': 'License plate is already in blacklist',
    'blacklist_not_found': 'Blacklist entry not found',
    'invalid_date_format': 'Invalid date format',
    'permission_denied': 'Permission denied',
    'validation_error': 'Validation error'
}

# Success Messages
SUCCESS_MESSAGES = {
    'record_created': 'Record created successfully',
    'record_updated': 'Record updated successfully',
    'record_deleted': 'Record deleted successfully',
    'blacklist_added': 'License plate added to blacklist',
    'blacklist_removed': 'License plate removed from blacklist',
    'camera_registered': 'Camera registered successfully',
    'file_uploaded': 'File uploaded successfully'
}
