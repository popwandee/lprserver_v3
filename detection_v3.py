import os
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler
import degirum as dg
import numpy as np
import cv2
import sqlite3
from datetime import datetime
from picamera2 import Picamera2
from libcamera import controls
from src.ocr_process import OCRProcessor
from difflib import SequenceMatcher
import requests
import socket
from flask import Flask, Response
import threading
from logging.handlers import TimedRotatingFileHandler

env_path = os.path.join(os.path.dirname(__file__), 'src', '.env.production')
load_dotenv(env_path)

app = Flask(__name__)

# Configure logging
LOG_FILE = os.getenv("DETECTION_LOG_FILE")
if not os.path.exists(LOG_FILE):
    logging.critical(f"Log file '{LOG_FILE}' does not exist or cannot be created.")
    # Define log directory and log file , create log file
    LOG_DIR = "log"
    LOG_FILE = os.path.join(LOG_DIR, "detection.log")
    os.makedirs(LOG_DIR, exist_ok=True)
# Create a logger 
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Capture DEBUG for Detailed debugging information, INFO for General event, WARNING for possible issues, ERROR for serious issue, CRITICAL for severe problem
# File handler (logs to a file)
file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7) #Keep logs from the last 7 days.
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)  # Ensure all levels are logged
# Console handler (logs to the terminal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))  # Simpler format
console_handler.setLevel(logging.INFO)  # Show INFO and above in terminal

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

#logger.debug("🛠 Debugging mode active.")  # Only in file
#logger.info("🚀 System initialized.")  # In both file & terminal
#logger.warning("⚠️ Low memory warning!")  # In both file & terminal
#logger.error("❌ Critical failure detected.")  # In both file & terminal

# ใช้ตัวแปรจาก .env.production
SERVER_URL = os.getenv("SERVER_URL")
# ตรวจสอบตำแหน่งที่ตั้ง
# ใช้ API ip-api.com เพื่อดึงข้อมูลตำแหน่งที่ตั้ง เป็นตำแหน่งคร่าวๆ ไม่แม่นยำ
def get_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        location = response.json()
        logging.debug(f"🌍 ตำแหน่งที่ตั้งจาก ip-api.com: {location['lat']}, {location['lon']}"
            f" ({location['city']}, {location['regionName']}, {location['country']})")
        
        location = f"{location['lat']}, {location['lon']}"
    except requests.RequestException as e:
        logging.debug(f"❌ ไม่สามารถดึงข้อมูลตำแหน่งที่ตั้ง: {e} ใช้พิกัด 0 , 0 แทน")
        location = f"0,0"
    return location


def similar(a, b):
    """Return a similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()
def preprocess_for_ocr(image):
    """
    Preprocess image to improve OCR results: 
    - Convert to grayscale
    - Increase contrast
    - Apply adaptive thresholding
    - Optionally, denoise or sharpen
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Histogram equalization for contrast
    gray = cv2.equalizeHist(gray)
    # Adaptive thresholding for varied lighting
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 31, 15)
    # Optionally: denoise or sharpen here if needed
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)  # keep 3 channels for model input

import threading
from flask import Flask, Response, jsonify
import cv2
import time

app = Flask(__name__)

class VehicleLicensePlateDetector:
    def __init__(self, ...):
        # ...init camera, model, etc...
        self.last_detection_result = None  # shared variable
        self.lock = threading.Lock()
        # ...init Picamera2 with main/lores stream...

    def detection_loop(self):
        while True:
            frame = self.picam2.capture_array("main")
            # ...AI detection...
            result = {"plate": "AB1234", "timestamp": time.time()}  # ตัวอย่างผลลัพธ์
            with self.lock:
                self.last_detection_result = result
            time.sleep(0.1)

    def get_last_result(self):
        with self.lock:
            return self.last_detection_result

detector = VehicleLicensePlateDetector(...)

# Start detection in background
threading.Thread(target=detector.detection_loop, daemon=True).start()

def gen_frames():
    while True:
        frame = detector.picam2.capture_array("lores")
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        if not ret:
            continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/last_detection')
def last_detection():
    result = detector.get_last_result()
    return jsonify(result if result else {})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)