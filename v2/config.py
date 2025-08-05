import os
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__),  '.env.production')
load_dotenv(env_path)

SECRET_KEY= os.getenv("SECRET_KEY")
# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR,'db', 'lpr_data.db')

# Image saving paths
IMAGE_SAVE_DIR = os.path.join(BASE_DIR, 'captured_images')
# Ensure the directory exists
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

# Model paths (replace with your actual model paths)
VEHICLE_DETECTION_MODEL =  os.getenv("VEHICLE_DETECTION_MODEL")
LICENSE_PLATE_DETECTION_MODEL = os.getenv("LICENSE_PLATE_DETECTION_MODEL")
LICENSE_PLATE_OCR_MODEL = os.getenv("LICENSE_PLACE_OCR_MODEL")
# Ensure model paths are set
EASYOCR_LANGUAGES = ['en', 'th']  

# WebSocket server configuration
WEBSOCKET_SERVER_URL = os.getenv("WEBSOCKET_SERVER_URL") 

# Camera properties defaults
DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_FRAMERATE = 30
DEFAULT_BRIGHTNESS = 0.0 # -1.0 to 1.0
DEFAULT_CONTRAST = 1.0   # 0.0 to 2.0
DEFAULT_SATURATION = 1.0 # 0.0 to 2.0
DEFAULT_SHARPNESS = 1.0  # 0.0 to 4.0
DEFAULT_AWB_MODE = 'auto' # 'auto', 'fluorescent', 'incandescent', 'tungsten',  'horizon', 'daylight', 'cloudy', 'shade', 'custom'

# Threading intervals (in seconds)
DETECTION_INTERVAL = 0.1 # How often the detection thread tries to get a frame
SENDER_INTERVAL = 60.0   # How often the sender thread checks for new detections (1 minute)

# Flask app configuration
FLASK_PORT = 5000
FLASK_HOST = '0.0.0.0' # Listen on all interfaces

# Health monitoring interval (in seconds, 3600 seconds = 1 hour)
HEALTH_CHECK_INTERVAL = 3600