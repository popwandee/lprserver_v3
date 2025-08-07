from camera import Picamera2
from database import init_database, save_to_database
from image_processing import preprocess_for_ocr, resize_with_letterbox, crop_license_plates
from logging_config import logger
from model_loader import load_models
from ocr_process import OCRProcessor
from similarity import similar, compare_images
from utils import get_location
import numpy as np
import os
import sqlite3
from datetime import datetime
import socket

class VehicleLicensePlateDetector:
    """Handles vehicle detection, license plate detection, and OCR processing, and image saving"""

    def __init__(self, db_path="db/lpr_data.db", ocr_similarity_threshold=0.85, image_similarity_threshold=0.90, ocr_processor=None):
        self.db_path = os.getenv("DB_PATH", db_path)
        self.hw_location = os.getenv("HEF_MODEL_PATH")
        self.model_zoo_url = os.getenv("MODEL_ZOO_URL")
        self.ocr_similarity_threshold = ocr_similarity_threshold
        self.image_similarity_threshold = image_similarity_threshold
        self.prev_ocr_label = None
        self.prev_plate_image = None
        self.hostname = socket.gethostname()
        self.location = get_location()
        self.should_run = True
        self.ocr = ocr_processor if ocr_processor else OCRProcessor(lang_list=['en', 'th'])

        # Initialize models
        self.vehicle_model, self.lp_detection_model, self.lp_ocr_model = load_models(self.hw_location, self.model_zoo_url)

        init_database(self.db_path)

        # Initialize Picamera2 here to keep it open
        self.picam2 = Picamera2()
        self.configure_camera()

    def configure_camera(self):
        try:
            camera_config = self.picam2.create_preview_configuration(main={"size": (640, 480)}, lores={"size": (320, 240)}, display="main")
            self.picam2.configure(camera_config)
            self.picam2.start()
            self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
            logger.info("Picamera2 initialized and started.")
        except Exception as e:
            logger.error(f"Failed to initialize Picamera2: {e}")
            self.picam2 = None
            raise

    def process_image(self):
        """Runs vehicle detection, license plate detection, and OCR on an image, with similarity check."""
        image = self.capture_video_frame()
        if image is None or not isinstance(image, np.ndarray):
            logger.info("Image capture failed or invalid image type!")
            return None, None, None, None
        else:
            logger.info("Capture image before process image :OK\n")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        resized_image_array = resize_with_letterbox(image, (self.vehicle_model.input_shape[0][1], self.vehicle_model.input_shape[0][2]))

        if resized_image_array is None:
            logger.warning("Resized image is None. Skipping further processing.")
            return None, None, None, None

        detected_vehicles = self.vehicle_model(resized_image_array)
        detected_license_plates = self.lp_detection_model(resized_image_array)
        lp_text = None
        cropped_path = None

        if detected_license_plates and detected_license_plates.results:
            cropped_license_plates = crop_license_plates(image, detected_license_plates.results)

            for index, cropped_plate in enumerate(cropped_license_plates):
                if cropped_plate is None or cropped_plate.size == 0:
                    logger.warning(f"Skipping empty or invalid cropped plate at index {index}")
                    continue

                ocr_results_lp_model = self.lp_ocr_model.predict(cropped_plate)
                ocr_label_lp_model = self.rearrange_detections(ocr_results_lp_model.results)
                logger.info(f"From RAW image frame, Detected OCR : {ocr_label_lp_model}  by {os.getenv('LICENSE_PLACE_OCR_MODEL')}")

                processed_plate = preprocess_for_ocr(cropped_plate)
                if processed_plate is None:
                    logger.warning("Preprocessing for OCR resulted in None. Skipping OCR for this plate.")
                    continue
                ocr_results_lp_model_processed = self.lp_ocr_model.predict(processed_plate)
                ocr_label_lp_model_processed = self.rearrange_detections(ocr_results_lp_model_processed.results)
                logger.info(f"From processed image frame, Detected OCR : {ocr_label_lp_model_processed} by {os.getenv('LICENSE_PLACE_OCR_MODEL')}")

                current_lp_text = self.get_current_lp_text(ocr_label_lp_model, processed_plate)

                text_similar = similar(current_lp_text, self.prev_ocr_label) if self.prev_ocr_label else 0
                img_similar = compare_images(cropped_plate, self.prev_plate_image) if self.prev_plate_image is not None else 0

                logger.info(f"Current LP: '{current_lp_text}', Previous LP: '{self.prev_ocr_label}' (Text Similarity: {text_similar:.2f})")
                logger.info(f"Image Similarity: {img_similar:.2f}")

                if text_similar > self.ocr_similarity_threshold or img_similar > self.image_similarity_threshold:
                    logger.info("Similar plate detected, skipping save and database update.")
                    continue

                lp_text = current_lp_text
                vehicle_image_path = self.save_image(image, timestamp, "vehicle_full_frame")
                cropped_path = self.save_image(cropped_plate, timestamp, f"cropped_plate_{index}")

                save_to_database(lp_text, vehicle_image_path, cropped_path, timestamp, self.location, self.hostname)
                logger.info(f"Saved unique plate: {lp_text} at {cropped_path}")

                self.prev_ocr_label = lp_text
                self.prev_plate_image = cropped_plate
                break

        return lp_text, detected_vehicles, detected_license_plates, cropped_path

    def get_current_lp_text(self, ocr_label_lp_model, processed_plate):
        ocr_model_setting = os.getenv("OCR_MODEL")
        if ocr_model_setting == "LICENSE_PLACE_OCR_MODEL":
            return ocr_label_lp_model
        elif ocr_model_setting == "easyOCR_processed":
            return self.ocr.process_frame(processed_plate)[1]
        else:
            return self.ocr.process_frame(cropped_plate)[1]

    def capture_video_frame(self):
        """Capture frames continuously and process them in real-time"""
        if self.picam2 is None:
            logger.error("Picamera2 is not initialized.")
            return None
        try:
            frame = self.picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame_bgr
        except Exception as e:
            logger.warning(f"Error capturing video frame: {e}")
            return None

    def run(self):
        """Main loop for continuous video processing."""
        logger.info("Starting detection loop. Press Ctrl+C to exit.")
        try:
            while self.should_run:
                self.process_image()
        except KeyboardInterrupt:
            logger.info("Process manually stopped via keyboard.")
        except Exception as e:
            logger.critical(f"An unhandled error occurred in the main loop: {e}")
        finally:
            logger.info("Detection system shutting down.")
            if self.picam2:
                self.picam2.stop()
                self.picam2.close()
                logger.info("Picamera2 stopped and closed.")

def main():
    ocr = OCRProcessor(lang_list=['en', 'th'])
    detector = VehicleLicensePlateDetector(ocr_processor=ocr)
    detector.run()

if __name__ == "__main__":
    main()