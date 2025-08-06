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

#ocr = OCRProcessor(lang_list=['en', 'th'])
#frame, text = ocr.process_frame(your_image_array)

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

class VehicleLicensePlateDetector:
    """Handles vehicle detection, license plate detection, and OCR processing, and image saving"""

    def __init__(self, db_path="db/lpr_data.db",ocr_similarity_threshold=0.85, image_similarity_threshold=0.90, ocr_processor=None):
        self.db_path = os.getenv("DB_PATH", db_path) # ใช้ db_path จาก parameter หากไม่มีใน env
        self.hw_location = os.getenv("HEF_MODEL_PATH")
        self.model_zoo_url = os.getenv("MODEL_ZOO_URL")
        self.ocr_similarity_threshold = ocr_similarity_threshold
        self.image_similarity_threshold = image_similarity_threshold
        self.prev_ocr_label = None
        self.prev_plate_image = None
        self.hostname = socket.gethostname() # ใช้สำหรับการระบุว่ามาจากกล้องตัวไหน
        self.location = get_location()
        self.should_run = True
        # Initialize OCR Processor
        self.ocr = ocr_processor if ocr_processor else OCRProcessor(lang_list=['en', 'th'])
        # Initialize models
        try:
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
            logging.info("All models loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load models: {e}")
            raise

        self.init_database()

        # Initialize Picamera2 here to keep it open
        self.picam2 = Picamera2()
        try:
            # กำหนดค่าการตั้งค่ากล้องที่เหมาะสม (เช่นความละเอียด, FPS)
            # ควรเลือกความละเอียดที่เหมาะสมกับโมเดล AI เพื่อประสิทธิภาพที่ดี
            camera_config = self.picam2.create_preview_configuration(main={"size": (640, 480)}, lores={"size": (320, 240)}, display="main")
            self.picam2.configure(camera_config)
            self.picam2.start()
            self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous}) # ตั้งค่า Auto Focus
            logging.info("Picamera2 initialized and started.")
        except Exception as e:
            logging.error(f"Failed to initialize Picamera2: {e}")
            self.picam2 = None # ตั้งค่าเป็น None เพื่อป้องกันการใช้งานที่ไม่ถูกต้อง
            raise


    def init_database(self):
        """สร้างไดเรกทอรี `db/` และไฟล์ฐานข้อมูลหากยังไม่มี"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        conn = None
        try:
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
            logging.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def print_image_size(image_path):
        """Prints the size (height, width, channels) of an image."""
        image = cv2.imread(image_path)
        if image is None:
            logging.info(f"Error: Unable to load image from path: {image_path}")
        else:
            height, width, channels = image.shape
            logging.info(f"Image size: {height}x{width} (Height x Width) with {channels} channels.")

    def resize_with_letterbox(self, image, target_size=(640, 640), padding_value=(0, 0, 0)):
        """Resizes an image while maintaining aspect ratio and padding with letterbox."""
        if image is None or not isinstance(image, np.ndarray):
            logging.warning("resize_with_letterbox received Captured image is invalid input!")
            return None, None, None, None
        # Convert BGR to RGB (if needed) if it's BGR, as many models expect RGB
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        original_height, original_width, channels = image.shape
        target_height, target_width = target_size
        
        #original_aspect_ratio = original_width / original_height
        #target_aspect_ratio = target_width / target_height

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
        if self.picam2 is None:
            logging.error("Picamera2 is not initialized.")
            return None
        try:
            frame = self.picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame_bgr
        except Exception as e:
            logging.warning(f"Error capturing video frame: {e}")
            return None

    def save_image(self, image,timestamp, image_type, output_dir="lpr_images"):
        """Save an image with a timestamp-based filename"""
        if image is None or not isinstance(image, np.ndarray):
            logging.warning(f"Cannot save invalid image for type: {image_type}")
            return None
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/{timestamp}_{image_type}.jpg"
        try:
            cv2.imwrite(filename, image)
            logging.info(f"Image saved: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error saving image {filename}: {e}")
            return None

    def crop_license_plates(self, image, results):
        """Extract license plate regions from detected bounding boxes"""
        cropped_images = []

        for result in results:
            bbox = result.get("bbox")
            if not bbox or len(bbox) != 4:
                continue

            x_min, y_min, x_max, y_max = map(int, bbox)

            if x_min >= x_max or y_min >= y_max:
                logging.warning(f"Warning: Invalid bounding box coordinates: {bbox}")
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
        try:
            img1 = cv2.resize(img1, (w, h))
            img2 = cv2.resize(img2, (w, h))
            # Use histogram comparison
            hist1 = cv2.calcHist([img1], [0], None, [256], [0,256])
            hist2 = cv2.calcHist([img2], [0], None, [256], [0,256])
            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return score if 0 <= score <= 1 else max(0, min(1, score))
        except Exception as e:
            logging.error(f"Error comparing images: {e}")
            return 0

    def process_image(self):
        """Runs vehicle detection, license plate detection, and OCR on an image, with similarity check."""
        image = self.capture_video_frame()
        if image is None or not isinstance(image, np.ndarray):
            logging.info("Image capture failed or invalid image type!")
            return None, None, None, None
        else:
            logging.info("Capture image before process image :OK\n")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Resize image for vehicle detection model
        # Ensure the target_size matches the expected input shape of your vehicle_model
        resized_image_array = self.resize_with_letterbox(
            image, (self.vehicle_model.input_shape[0][1],self.vehicle_model.input_shape[0][2])
            )  
        if resized_image_array is None:
            logging.warning("Resized image is None. Skipping further processing.")
            return None, None, None, None
        
        detected_vehicles = self.vehicle_model(resized_image_array)
        detected_license_plates = self.lp_detection_model(resized_image_array)
        lp_text = None
        cropped_path = None

        if detected_license_plates and detected_license_plates.results:
            cropped_license_plates = self.crop_license_plates(image, detected_license_plates.results) # เดิมใช้ detected_license_plates.image แต่ลองใช้ image เดิมเพื่อครอป
            
            for index, cropped_plate in enumerate(cropped_license_plates):
                if cropped_plate is None or cropped_plate.size == 0:
                    logging.warning(f"Skipping empty or invalid cropped plate at index {index}")
                    continue
                # ประมวลผลด้วย OCR Model และ easyOCR ทั้งแบบภาพต้นฉบับและภาพหลังปรับปรุง เพื่อเปรียบเทียบผลข้อความที่อ่านได้
                # RAW Cropped license plate 
                ocr_results_lp_model  = self.lp_ocr_model.predict(cropped_plate)
                ocr_label_lp_model  = self.rearrange_detections(ocr_results_lp_model.results)
                logging.info(f"From RAW image frame, Detected OCR : {ocr_label_lp_model}  by {os.getenv('LICENSE_PLACE_OCR_MODEL')}")

                # Preprocess for OCR and then run OCR again (สำหรับการเพิ่มประสิทธิภาพในการอ่าน)
                processed_plate = preprocess_for_ocr(cropped_plate)
                if processed_plate is None:
                    logging.warning("Preprocessing for OCR resulted in None. Skipping OCR for this plate.")
                    continue
                ocr_results_lp_model_processed = self.lp_ocr_model.predict(processed_plate)
                ocr_label_lp_model_processed = self.rearrange_detections(ocr_results_lp_model_processed.results)
                logging.info(f"From processed image frame, Detected OCR : {ocr_label_lp_model_processed} by {os.getenv('LICENSE_PLACE_OCR_MODEL')}")

                # Process with EasyOCR for Read Thai license plate (temporary)
                result_easyOCR_raw, raw_frame_text = self.ocr.process_frame(cropped_plate)
                if result_easyOCR_raw is not None:
                    logging.info(f"Detected OCR (Raw Frame) : {raw_frame_text} by easyOCR")
             
                result_easyOCR_processed, processed_frame_text = self.ocr.process_frame(processed_plate)
                if result_easyOCR_processed is not None:
                    logging.info(f"Detected OCR (Processed Frame) : {processed_frame_text} by easyOCR")
                ocr_model_setting = os.getenv("OCR_MODEL")
                logging.info(f"OCR_MODEL setting is: {ocr_model_setting}")
                # Similarity checks
                current_lp_text = ""
                if ocr_model_setting  == "LICENSE_PLACE_OCR_MODEL":
                    current_lp_text  = ocr_label_lp_model
                elif ocr_model_setting  == "easyOCR_processed": #  use easyOCR with processed image frame
                    current_lp_text = processed_frame_text
                else: # Default or easyOCR_raw
                    current_lp_text = raw_frame_text
                # Calculate similarities
                text_similar = similar(current_lp_text, self.prev_ocr_label) if self.prev_ocr_label else 0
                img_similar = self.compare_images(cropped_plate, self.prev_plate_image) if self.prev_plate_image is not None else 0

                logging.info(f"Current LP: '{current_lp_text}', Previous LP: '{self.prev_ocr_label}' (Text Similarity: {text_similar:.2f})")
                logging.info(f"Image Similarity: {img_similar:.2f}")
                # Check for similarity thresholds
                if text_similar > self.ocr_similarity_threshold or img_similar > self.image_similarity_threshold:
                    logging.info("Similar plate detected, skipping save and database update.")
                    continue  # Skip saving and DB if too similar to previous

                # If it's a new unique detection, proceed to save
                lp_text = current_lp_text # Assign the detected LP text
                
                # Save images
                vehicle_image_path = self.save_image(image,timestamp, "vehicle_full_frame")
                license_plate_image_path = self.save_image(detected_license_plates.image_overlay,timestamp, "license_plate_detected") # อาจจะตัดบรรทัดนี้ออก
                cropped_path = self.save_image(cropped_plate,timestamp, f"cropped_plate_{index}")

                # Save to database
                self.save_to_database(lp_text, vehicle_image_path, license_plate_image_path, cropped_path,timestamp, self.location, self.hostname)
                logging.info(f"Saved unique plate: {lp_text} at {cropped_path}")
                self.save_image(processed_plate,timestamp, f"processed_plate{index}")

                # Update previous states
                self.prev_ocr_label = lp_text
                self.prev_plate_image = cropped_plate
                # Only process the first unique plate found in a frame to avoid redundant saves if multiple plates are detected
                # You might want to adjust this logic if you need to process all plates in a frame.
                break 
        return lp_text, detected_vehicles, detected_license_plates, cropped_path

    def rearrange_detections(self, ocr_results):
        """Rearranges OCR detection results into a single string for a readable format"""
        if not ocr_results:
            return "Unknown"
        extracted_text = []
        # Sort results based on x-coordinate to get correct order for horizontal text
        sorted_results = sorted(ocr_results, key=lambda x: x.get("bbox", [0])[0] if isinstance(x, dict) and "bbox" in x else 0)
        for res in sorted_results:
            if isinstance(res, dict) and "label" in res:
                extracted_text.append(res["label"])  # Extract text from label
        return "".join(extracted_text)
    
    def save_to_database(self, license_plate, detected_vehicles, detected_license_plates, cropped_path,timestamp,location,hostname):
        """Stores license plate and image path in SQLite"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lpr_data (license_plate, vehicle_image_path,license_plate_image_path,cropped_image_path, timestamp,location,hostname,sent_to_server) VALUES (?, ?, ?,?,?,?,?,?)", 
                       (license_plate, detected_vehicles, detected_license_plates, cropped_path, timestamp, location, hostname, 0))

            conn.commit()
            logging.info(f"✅ Saved to database: Plate {license_plate}, Image {detected_vehicles}")
        except sqlite3.Error as e:
            logging.error(f"Error saving to database: {e}")
        finally:
            if conn:
                conn.close()

    def run(self):
        """Main loop for continuous video processing.
        Continuous execution until user cancels"""
        logging.info("Starting detection loop. Press Ctrl+C to exit.")
        try:
            while self.should_run:
                self.process_image()
        except KeyboardInterrupt:
            logging.info("Process manually stopped via keyboard.")
        except Exception as e:
            logging.critical(f"An unhandled error occurred in the main loop: {e}")
        finally:
            logging.info("Detection system shutting down.")
            if self.picam2:
                self.picam2.stop()
                self.picam2.close()
                logging.info("Picamera2 stopped and closed.")
        
def main():
    ocr = OCRProcessor(lang_list=['en', 'th'])
    detector = VehicleLicensePlateDetector(ocr_processor=ocr)
    detector.run()
    
if __name__ == "__main__":
    main()
