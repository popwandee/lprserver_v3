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
from flask import Flask, Response, request, jsonify
import threading

env_path = os.path.join(os.path.dirname(__file__), 'src', '.env.production')
load_dotenv(env_path)

app = Flask(__name__)

# Logging setup
LOG_FILE = os.getenv("DETECTION_LOG_FILE", "log/detection.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

SERVER_URL = os.getenv("SERVER_URL")

def get_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        location = response.json()
        logging.debug(f"Location: {location['lat']}, {location['lon']} ({location['city']}, {location['regionName']}, {location['country']})")
        return f"{location['lat']}, {location['lon']}"
    except requests.RequestException as e:
        logging.debug(f"Cannot get location: {e}, using 0,0")
        return "0,0"

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def preprocess_for_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 31, 15)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

class VehicleLicensePlateDetector:
    def __init__(self, image_source="camera", image_folder=None, db_path="db/lpr_data.db", ocr_processor=None):
        self.image_source = image_source
        self.image_folder = image_folder
        self.db_path = db_path
        self.hw_location = os.getenv("HEF_MODEL_PATH")
        self.model_zoo_url = os.getenv("MODEL_ZOO_URL")
        self.prev_bg_frame = None
        self.bg_diff_threshold = 30
        self.bg_min_area = 5000
        self.ocr_similarity_threshold = 0.85
        self.image_similarity_threshold = 0.90
        self.prev_ocr_label = None
        self.prev_plate_image = None
        self.hostname = socket.gethostname()
        self.location = get_location()
        self.ocr = ocr_processor if ocr_processor else OCRProcessor(lang_list=['en', 'th'])

        self.vehicle_model = dg.load_model(
            model_name=os.getenv("VEHICLE_DETECTION_MODEL"),
            inference_host_address=self.hw_location,
            zoo_url=self.model_zoo_url
        )
        self.lp_detection_model = dg.load_model(
            model_name=os.getenv("LICENSE_PLACE_DETECTION_MODEL"),
            inference_host_address=self.hw_location,
            zoo_url=self.model_zoo_url,
            overlay_color=[(255, 255, 0), (0, 255, 0)]
        )
        self.lp_ocr_model = dg.load_model(
            model_name=os.getenv("LICENSE_PLACE_OCR_MODEL"),
            inference_host_address=self.hw_location,
            zoo_url=self.model_zoo_url,
            output_use_regular_nms=False,
            output_confidence_threshold=0.1
        )
        self.init_database()
        self.should_run = True
        self.lock = threading.Lock()
        if self.image_source == "camera":
            try:
                self.picam2 = Picamera2()
                video_config = self.picam2.create_video_configuration(
                    main={"size": (1280, 720), "format": "RGB888"},
                    lores={"size": (320, 240), "format": "RGB888"},
                    display="lores"
                )
                self.picam2.configure(video_config)
                self.picam2.start()
                logging.info("Picamera2 started successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Picamera2: {e}")
                raise
        elif self.image_source == "folder":
            assert self.image_folder is not None and os.path.isdir(self.image_folder), "Invalid image folder"
            self.image_list = sorted([
                os.path.join(self.image_folder, f)
                for f in os.listdir(self.image_folder)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])
            self.image_idx = 0

    def init_database(self):
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lpr_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT NOT NULL,
                vehicle_image_path TEXT NOT NULL,
                license_plate_image_path TEXT NOT NULL,
                cropped_image_path TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                location TEXT NOT NULL,
                hostname TEXT NOT NULL,
                sent_to_server INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def is_scene_changed(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.prev_bg_frame is None:
            self.prev_bg_frame = gray
            return False
        diff = cv2.absdiff(self.prev_bg_frame, gray)
        _, thresh = cv2.threshold(diff, self.bg_diff_threshold, 255, cv2.THRESH_BINARY)
        changed_area = np.sum(thresh > 0)
        self.prev_bg_frame = gray
        return changed_area > self.bg_min_area

    def resize_with_letterbox(self, image, target_size=(640, 640), padding_value=(0, 0, 0)):
        if image is None or not isinstance(image, np.ndarray):
            logging.warning("Captured image is invalid!")
            return None
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_height, original_width, channels = image.shape
        target_height, target_width = target_size
        scale_factor = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)
        offset_y = (target_height - new_height) // 2
        offset_x = (target_width - new_width) // 2
        letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image
        return letterboxed_image

    def capture_video_frame(self):
        if self.image_source == "camera":
            try:
                with self.lock:
                    frame = self.picam2.capture_array("main")
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return frame_bgr
            except Exception as e:
                logging.warning(f"Error capturing video frame: {e}")
                return None
        elif self.image_source == "folder":
            if self.image_idx >= len(self.image_list):
                self.should_run = False
                return None
            image_path = self.image_list[self.image_idx]
            image = cv2.imread(image_path)
            self.image_idx += 1
            return image

    def save_image(self, image, timestamp, image_type, output_dir="lpr_images"):
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/{timestamp}_{image_type}.jpg"
        cv2.imwrite(filename, image)
        return filename

    def crop_license_plates(self, image, results):
        cropped_images = []
        for result in results:
            bbox = result.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            x_min, y_min, x_max, y_max = map(int, bbox)
            if x_min >= x_max or y_min >= y_max:
                continue
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(image.shape[1], x_max)
            y_max = min(image.shape[0], y_max)
            cropped_images.append(image[y_min:y_max, x_min:x_max])
        return cropped_images

    def compare_images(self, img1, img2):
        if img1 is None or img2 is None:
            return 0
        h, w = 128, 128
        img1 = cv2.resize(img1, (w, h))
        img2 = cv2.resize(img2, (w, h))
        hist1 = cv2.calcHist([img1], [0], None, [256], [0,256])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0,256])
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return score if 0 <= score <= 1 else max(0, min(1, score))

    def rearrange_detections(self, ocr_results):
        if not ocr_results:
            return "Unknown"
        extracted_text = []
        for res in ocr_results:
            if isinstance(res, dict) and "label" in res:
                extracted_text.append(res["label"])
        return "".join(extracted_text)

    def save_to_database(self, license_plate, vehicle_image_path, license_plate_image_path, cropped_path, timestamp, location, hostname):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lpr_data (license_plate, vehicle_image_path, license_plate_image_path, cropped_image_path, timestamp, location, hostname, sent_to_server) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       (license_plate, vehicle_image_path, license_plate_image_path, cropped_path, timestamp, location, hostname, 0))
        conn.commit()
        conn.close()
        logging.info(f"✅ Saved to database: Plate {license_plate}, Image {vehicle_image_path}")

    def process_image(self):
        image = self.capture_video_frame()
        if image is None or not isinstance(image, np.ndarray):
            logging.warning("Image capture failed or invalid image type!")
            return
        if self.image_source == "camera" and not self.is_scene_changed(image):
            logging.info("No significant scene change detected, skipping detection.")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        resized_image_array = self.resize_with_letterbox(
            image, (self.vehicle_model.input_shape[0][1], self.vehicle_model.input_shape[0][2])
        )
        if resized_image_array is None:
            logging.warning("Resized image is None. Skipping detection.")
            return
        self.save_image(resized_image_array, timestamp, f"scene_change")
        detected_vehicles = self.vehicle_model(resized_image_array)
        detected_license_plates = self.lp_detection_model(resized_image_array)
        if detected_license_plates.results:
            cropped_license_plates = self.crop_license_plates(detected_license_plates.image, detected_license_plates.results)
            for index, cropped_plate in enumerate(cropped_license_plates):
                ocr_results = self.lp_ocr_model.predict(cropped_plate)
                ocr_label = self.rearrange_detections(ocr_results.results)
                processed_plate = preprocess_for_ocr(cropped_plate)
                ocr_results_processed = self.lp_ocr_model.predict(processed_plate)
                ocr_label_processed = self.rearrange_detections(ocr_results_processed.results)
                result_easyOCR, easyOCR_text_raw_frame = self.ocr.process_frame(cropped_plate)
                result_easyOCR, easyOCR_text_processed_frame = self.ocr.process_frame(processed_plate)
                ocr_model = os.getenv("OCR_MODEL")
                if ocr_model == "LICENSE_PLACE_OCR_MODEL":
                    text_similar = similar(ocr_label, self.prev_ocr_label) if self.prev_ocr_label else 0
                    lp_text = ocr_label
                elif ocr_model == "easyOCR_processed":
                    text_similar = similar(easyOCR_text_processed_frame, self.prev_ocr_label) if self.prev_ocr_label else 0
                    lp_text = easyOCR_text_processed_frame
                else:
                    text_similar = similar(easyOCR_text_raw_frame, self.prev_ocr_label) if self.prev_ocr_label else 0
                    lp_text = easyOCR_text_raw_frame
                img_similar = self.compare_images(cropped_plate, self.prev_plate_image) if self.prev_plate_image is not None else 0
                if text_similar > self.ocr_similarity_threshold or img_similar > self.image_similarity_threshold:
                    logging.info("Similar plate detected, skipping save and database update.")
                    continue
                vehicle_image_path = self.save_image(detected_vehicles.image_overlay, timestamp, "vehicle_detected")
                license_plate_image_path = self.save_image(detected_license_plates.image_overlay, timestamp, "license_plate_detected")
                cropped_path = self.save_image(cropped_plate, timestamp, f"cropped_plate_{index}")
                self.save_to_database(lp_text, vehicle_image_path, license_plate_image_path, cropped_path, timestamp, self.location, self.hostname)
                self.save_image(processed_plate, timestamp, f"processed_plate{index}")
                self.prev_ocr_label = lp_text
                self.prev_plate_image = cropped_plate
                logging.info(f"Saved unique plate: {lp_text} at {cropped_path}")
        else:
            logging.info("No license plate detected, continue....")

    def run(self):
        logging.info("Starting detection loop. Press Ctrl+C or send stop event via SocketIO to exit.")
        try:
            while self.should_run:
                self.process_image()
        except KeyboardInterrupt:
            logging.info("Process manually stopped via keyboard.")
        finally:
            logging.info("Detection system shutting down.")
            if self.image_source == "camera":
                try:
                    self.picam2.stop()
                    self.picam2.close()
                    logging.info("Picamera2 stopped and closed.")
                except Exception as e:
                    logging.error(f"Error closing Picamera2: {e}")

def gen_frames(camera):
    while True:
        frame = camera.capture_array("lores")
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # time.sleep(0.03)  # Optional: limit FPS

@app.route('/video_feed')
def video_feed():
    if not hasattr(app, "detector") or not hasattr(app.detector, "picam2"):
        return "Camera not initialized", 500
    return Response(gen_frames(app.detector.picam2), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_source', methods=['POST'])
def set_source():
    data = request.json
    source = data.get("source", "camera")
    folder = data.get("folder", None)
    app.detector = VehicleLicensePlateDetector(image_source=source, image_folder=folder, ocr_processor=OCRProcessor(lang_list=['en', 'th']))
    threading.Thread(target=app.detector.run, daemon=True).start()
    return jsonify({"status": "ok", "source": source, "folder": folder})

def main():
    # Default: start with camera
    app.detector = VehicleLicensePlateDetector(image_source="camera", ocr_processor=OCRProcessor(lang_list=['en', 'th']))
    threading.Thread(target=app.detector.run, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == "__main__":
    main()
