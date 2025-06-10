import os
from dotenv import load_dotenv
import logging
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


env_path = os.path.join(os.path.dirname(__file__), 'src', '.env.production')
load_dotenv(env_path)

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
file_handler = logging.FileHandler(LOG_FILE)
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

class VehicleLicensePlateDetector:
    """Handles vehicle detection, license plate detection, and OCR processing, and image saving"""

    def __init__(self, db_path="db/lpr_data.db",ocr_similarity_threshold=0.85, image_similarity_threshold=0.90, ocr_processor=None):
        self.db_path = os.getenv("DB_PATH")
        self.hw_location = os.getenv("HEF_MODEL_PATH")
        self.model_zoo_url = os.getenv("MODEL_ZOO_URL")
        self.ocr_similarity_threshold = ocr_similarity_threshold
        self.image_similarity_threshold = image_similarity_threshold
        self.prev_ocr_label = None
        self.prev_plate_image = None
        self.hostname = socket.gethostname() # ใช้สำหรับการระบุว่ามาจากกล้องตัวไหน
        self.location = location = get_location()
        # Initialize OCR Processor
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

        self.should_run = True  # Control flag for loop

        #@self.socketio.on("stop_detection")
        def handle_stop_detection():
            """Stop the detection process via SocketIO"""
            self.should_run = False
            logging.info("Received stop command, shutting down...")

    def init_database(self):
        """สร้างไดเรกทอรี `db/` และไฟล์ฐานข้อมูลหากยังไม่มี"""
    
        # ตรวจสอบและสร้างไดเรกทอรี db/ หากยังไม่มี
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        """ Create the SQLite database if it doesn't exist"""
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

    @staticmethod
    def print_image_size(image_path):

        image = cv2.imread(image_path)

        if image is None:
            logging.info(f"Error: Unable to load image from path: {image_path}")
        else:
            height, width, channels = image.shape
            logging.info(f"Image size: {height}x{width} (Height x Width)")

    def resize_with_letterbox(self, image, target_size=(640, 640), padding_value=(0, 0, 0)):

        if image is None or not isinstance(image, np.ndarray):
            logging.warning("Captured image is invalid!")
            return None, None, None, None
        # Convert BGR to RGB (if needed)
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        original_height, original_width, channels = image.shape
        
        target_height, target_width = target_size
        
        original_aspect_ratio = original_width / original_height
        target_aspect_ratio = target_width / target_height

        scale_factor = min(target_width / original_width, target_height / original_height)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)

        offset_y = (target_height - new_height) // 2 # Padding on the top 
        offset_x = (target_width - new_width) // 2 # Padding on the left 

        letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image

        return letterboxed_image


    def capture_video_frame(self):
        """Capture frames continuously and process them in real-time"""
        picam2 = Picamera2()
        try:
            picam2.start()
            frame = picam2.capture_array()
            # Picamera2 try adjusting focus here:
            # Set the AfMode (Autofocus Mode) to be continuous 
            # the nearest focus point is 10 centimeters.
            picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous}) 
            #picam2.start_and_capture_files("aurofocus.jpg", num_files=1, delay=0.5) # test to take  picture
            # Fixing the focus ,set the value to 0.0 for an infinite focus.
            # LensPosition value to 0.5 give approximately a 50 cm focal distance.
            #picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0})
            # to get a series of sharp images. set the autofocus to high speed
           # picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AfSpeed": controls.AfSpeedEnum.Fast})
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        except Exception as e:
            logging.warning(f"Error capturing video frame: {e}")
            frame_bgr = None
        finally:
            picam2.close()
        return frame_bgr

    def save_image(self, image,timestamp, image_type, output_dir="lpr_images"):
        """Save an image with a timestamp-based filename"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/{timestamp}_{image_type}.jpg"
        cv2.imwrite(filename, image)
        return filename

    def crop_license_plates(self, image, results):
        """Extract license plate regions from detected bounding boxes"""
        cropped_images = []

        for result in results:
            bbox = result.get("bbox")
            if not bbox or len(bbox) != 4:
                continue

            x_min, y_min, x_max, y_max = map(int, bbox)

            if x_min >= x_max or y_min >= y_max:
                print("Warning: Invalid bounding box, skipping...")
                continue

            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(image.shape[1], x_max)
            y_max = min(image.shape[0], y_max)

            cropped_images.append(image[y_min:y_max, x_min:x_max])

        return cropped_images

    def compare_images(self, img1, img2):
        """
        Compare two images using structural similarity or histogram.
        Returns a similarity ratio (0-1).
        """
        if img1 is None or img2 is None:
            return 0
        # Resize to the same shape
        h, w = 128, 128
        img1 = cv2.resize(img1, (w, h))
        img2 = cv2.resize(img2, (w, h))
        # Use histogram comparison
        hist1 = cv2.calcHist([img1], [0], None, [256], [0,256])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0,256])
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return score if 0 <= score <= 1 else max(0, min(1, score))

    def process_image(self):
        """Runs vehicle detection, license plate detection, and OCR on an image, with similarity check."""
        image = self.capture_video_frame()
        if image is None or not isinstance(image, np.ndarray):
            logging.info("Image capture failed or invalid image type!")
            return
        else:
            logging.info("Capture image before process image :OK\n")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        resized_image_array = self.resize_with_letterbox(
            image, (self.vehicle_model.input_shape[0][1],self.vehicle_model.input_shape[0][2])
            )  
      
        detected_vehicles = self.vehicle_model(resized_image_array)
        detected_license_plates = self.lp_detection_model(resized_image_array)

        if detected_license_plates.results:
            cropped_license_plates = self.crop_license_plates(detected_license_plates.image, detected_license_plates.results)
            
            for index, cropped_plate in enumerate(cropped_license_plates):
                # ประมวลผลด้วย OCR Model และ easyOCR ทั้งแบบภาพต้นฉบับและภาพหลังปรับปรุง เพื่อเปรียบเทียบผลข้อความที่อ่านได้
                # RAW Cropped license plate 
                ocr_results = self.lp_ocr_model.predict(cropped_plate)
                ocr_label = self.rearrange_detections(ocr_results.results)
                logging.info(f"From RAW image frame, Detected OCR : {ocr_label}  by {os.getenv('LICENSE_PLACE_OCR_MODEL')}")

                # Preprocess for OCR improvement
                processed_plate = preprocess_for_ocr(cropped_plate)
                
                # YOYOv8 LP OCR model read international (must improve for Thai)
                ocr_results = self.lp_ocr_model.predict(processed_plate)
                ocr_label = self.rearrange_detections(ocr_results.results)
                logging.info(f"From processed image frame, Detected OCR : {ocr_label} by {os.getenv('LICENSE_PLACE_OCR_MODEL')}")

                # easyOCR Read Thai license plate (temporary)
                result_easyOCR, easyOCR_text_raw_frame = self.ocr.process_frame(cropped_plate)
                if result_easyOCR is not None:
                    logging.info(f"From RAW image frame, Detected OCR : {easyOCR_text_raw_frame} by easyOCR")
                result_easyOCR, easyOCR_text_processed_frame = self.ocr.process_frame(processed_plate)
                if result_easyOCR is not None:
                    logging.info(f"From processed image frame, Detected OCR : {easyOCR_text_processed_frame} by easyOCR")
                ocr_model = os.getenv("OCR_MODEL")
                logging.info(f"OCR_MEDEL is :{ocr_model}")
                # Similarity checks
                if ocr_model == "LICENSE_PLACE_OCR_MODEL":
                    text_similar = similar(ocr_label, self.prev_ocr_label) if self.prev_ocr_label else 0
                    lp_text = ocr_label
                elif ocr_model == "easyOCR_processed": #  use easyOCR with processed image frame
                    text_similar = similar(easyOCR_text_processed_frame, self.prev_ocr_label) if self.prev_ocr_label else 0
                    lp_text = easyOCR_text_processed_frame
                else: # if OCR_MODEL is not set, use easyOCR instead
                    text_similar = similar(easyOCR_text_raw_frame, self.prev_ocr_label) if self.prev_ocr_label else 0
                    lp_text = easyOCR_text_raw_frame

                img_similar = self.compare_images(cropped_plate, self.prev_plate_image) if self.prev_plate_image is not None else 0
                logging.info(f"OCR {lp_text} and previous similarity: {text_similar:.2f}, Image similarity: {img_similar:.2f}")

                if text_similar > self.ocr_similarity_threshold or img_similar > self.image_similarity_threshold:
                    logging.info("Similar plate detected, skipping save and database update.")
                    continue  # Skip saving and DB if too similar to previous

                vehicle_image_path = self.save_image(detected_vehicles.image_overlay,timestamp, "vehicle_detected")
                license_plate_image_path = self.save_image(detected_license_plates.image_overlay,timestamp, "license_plate_detected")

                cropped_path = self.save_image(cropped_plate,timestamp, f"cropped_plate_{index}")

                self.save_to_database(lp_text, vehicle_image_path, license_plate_image_path, cropped_path,timestamp, self.location, self.hostname)
                logging.info(f"Saved unique plate: {lp_text} at {cropped_path}")
                self.save_image(processed_plate,timestamp, f"processed_plate{index}")
                self.prev_ocr_label = lp_text
                self.prev_plate_image = cropped_plate

                return lp_text, detected_vehicles, detected_license_plates, cropped_path
        logging.info("No license plate detected, continue....")
        return None, None

    def rearrange_detections(self, ocr_results):
        """Rearranges OCR results into a readable format"""
        if not ocr_results:
            return "Unknown"
        extracted_text = []
        for res in ocr_results:
            if isinstance(res, dict) and "label" in res:
                extracted_text.append(res["label"])  # Extract text from label
            else:
                logging.warning(f"Warning: Unexpected OCR output format: {res}")

        return "".join(extracted_text)
    
    def save_to_database(self, license_plate, detected_vehicles, detected_license_plates, cropped_path,timestamp,location,hostname):
        """Stores license plate and image path in SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lpr_data (license_plate, vehicle_image_path,license_plate_image_path,cropped_image_path, timestamp,location,hostname,sent_to_server) VALUES (?, ?, ?,?,?,?,?,?)", 
                       (license_plate, detected_vehicles, detected_license_plates, cropped_path, timestamp, location, hostname, 0))

        conn.commit()
        conn.close()
        logging.info(f"✅ Saved to database: Plate {license_plate}, Image {detected_vehicles}")
    
    def run(self):
        """Continuous execution until user cancels"""
        logging.info("Starting detection loop. Press Ctrl+C or send stop event via SocketIO to exit.")
        try:
            while self.should_run:
                self.process_image()
        except KeyboardInterrupt:
            logging.info("Process manually stopped via keyboard.")
        finally:
            logging.info("Detection system shutting down.")
        
def main():
    ocr = OCRProcessor(lang_list=['en', 'th'])
    detector = VehicleLicensePlateDetector(ocr_processor=ocr)
    detector.run()
    
if __name__ == "__main__":
    main()
