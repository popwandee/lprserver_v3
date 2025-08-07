import cv2
import numpy as np
import easyocr
import threading
import time
import logging
from datetime import datetime
import os
import queue
from ..config import (
    VEHICLE_DETECTION_MODEL, LICENSE_PLATE_DETECTION_MODEL,
    EASYOCR_LANGUAGES, IMAGE_SAVE_DIR, DETECTION_INTERVAL
)
from image_processing import resize_with_letterbox, crop_license_plates, draw_bounding_boxes
import degirum as dg
import uuid # For generating unique filenames
from camera_handler import CameraHandler
from database_manager import DatabaseManager # We'll create this next

logger = logging.getLogger(__name__)
env_path = os.path.join(os.path.dirname(__file__), '.env.production')
load_dotenv(env_path)
class DetectionProcessor:
    def __init__(self, frames_queue):
        self.camera_handler = CameraHandler(frames_queue)
        self.db_manager = DatabaseManager() # Initialize DB manager
        self.reader = easyocr.Reader(EASYOCR_LANGUAGES) # Initialize EasyOCR
        self.load_detection_models()
        self.running = False
        self.frames_queue = frames_queue # Store the queue instance

    def load_detection_models(self):
        """
        Loads the pre-trained vehicle and license plate detection models.
        Replace with your actual model loading logic (e.g., YOLO, OpenCV DNN, etc.).
        """
        logger.info("Loading detection models...")
        try:
            # Model & OCR setup
            vehicle_detection_model = dg.load_model(
                model_name=os.getenv("VEHICLE_DETECTION_MODEL"),
                inference_host_address=os.getenv("HEF_MODEL_PATH"),
                zoo_url=os.getenv("MODEL_ZOO_URL")
            )

            lp_detection_model = dg.load_model(
                model_name=os.getenv("LICENSE_PLATE_DETECTION_MODEL"),
                inference_host_address=os.getenv("HEF_MODEL_PATH"),
                zoo_url=os.getenv("MODEL_ZOO_URL"),
                overlay_color=[(255, 255, 0), (0, 255, 0)]
            )

            lp_ocr_model = dg.load_model(
                model_name=os.getenv("LICENSE_PLATE_OCR_MODEL"),
                inference_host_address=os.getenv("HEF_MODEL_PATH"),
                zoo_url=os.getenv("MODEL_ZOO_URL"),
                output_use_regular_nms=False,
                output_confidence_threshold=0.1
            )
            
            self.vehicle_detection_model = vehicle_detection_model
            self.lp_detection_model = lp_detection_model
            self.lp_ocr_model = lp_ocr_model
            logger.info(f"Detection models loaded {vehicle_detection_model} and {lp_detection_model} ")
            #logger.info("Detection models loaded successfully (placeholders).")
        except Exception as e:
            logger.error(f"Error loading detection models: {e}")
            self.vehicle_detection_model = None
            self.lp_detection_model = None
            self.lp_ocr_model = None
    def detect_vehicles(self, frame):
        """
        Performs vehicle detection on the given frame.
        Returns a list of bounding boxes (x, y, w, h) for detected vehicles.
        """
        logger.debug(f'Captured frame with shape: {frame.shape}')
        logger.debug("Performing vehicle detection...")
        resized = resize_with_letterbox(frame, (self.vehicle_model.input_shape[0][1], self.vehicle_model.input_shape[0][2]))
        vehicle_results = self.vehicle_detection_model(resized)
        vehicle_boxes = getattr(vehicle_results, "results", [])
        logger.debug(f"Detected {len(vehicle_boxes)} vehicles in the frame.")
        detections = []
        # Example: If using a model, it would look something like this:
        # results = self.vehicle_net(frame)
        # for *xyxy, conf, cls in results[0].boxes.data.tolist():
        #     if conf > threshold and cls_id == vehicle_class_id:
        #         x1, y1, x2, y2 = map(int, xyxy)
        #         detections.append({'box': [x1, y1, x2-x1, y2-y1], 'confidence': conf})
        # For now, let's return an empty list or a dummy box for testing
        return detections

    def detect_license_plates(self, frame, vehicle_boxes=None):
        """
        Performs license plate detection.
        If vehicle_boxes are provided, it searches within those regions.
        Otherwise, it searches the entire frame.
        Returns a list of dictionaries with 'box' (x, y, w, h) and 'confidence'.
        """
        logger.debug("Performing license plate detection...")
        lp_detections = []
        regions_to_search = []

        if vehicle_boxes:
            for v_box in vehicle_boxes:
                x, y, w, h = v_box['box']
                # Add some padding around the vehicle to ensure LP is not missed at edges
                pad_x = int(w * 0.1)
                pad_y = int(h * 0.1)
                x1 = max(0, x - pad_x)
                y1 = max(0, y - pad_y)
                x2 = min(frame.shape[1], x + w + pad_x)
                y2 = min(frame.shape[0], y + h + pad_y)
                regions_to_search.append(frame[y1:y2, x1:x2])
        else:
            regions_to_search.append(frame) # Search entire frame if no vehicles

        for region in regions_to_search:
            if region.shape[0] == 0 or region.shape[1] == 0:
                continue # Skip empty regions

            # --- Placeholder for actual license plate detection logic ---
            # Similar to vehicle detection, this would involve your LP model
            # For now, let's assume a dummy detection for testing
            # if self.lp_net:
            #     lp_results = self.lp_net(region)
            #     for *xyxy, conf, cls in lp_results[0].boxes.data.tolist():
            #         if conf > lp_threshold:
            #             x1, y1, x2, y2 = map(int, xyxy)
            #             lp_detections.append({'box': [x1, y1, x2-x1, y2-y1], 'confidence': conf})
            pass # No actual LP detection placeholder for now, rely on OCR directly if no LP model

        # If you don't have a separate LP detection model, EasyOCR can sometimes find text
        # in the whole image or a region. We'll use it after this for the actual OCR.
        return lp_detections

    def perform_ocr(self, image):
        """
        Performs OCR on the given image (likely a cropped license plate).
        Returns the detected text.
        """
        if image is None or image.size == 0:
            return ""
        try:
            # Convert to grayscale might help OCR performance
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Apply some preprocessing if needed, e.g., thresholding, denoising
            # _, processed_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            results = self.reader.readtext(gray_image) # Use gray_image or processed_image
            
            detected_texts = [text for (bbox, text, prob) in results]
            return " ".join(detected_texts)
        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return ""

    def process_frame(self, frame, metadata):
        """
        Processes a single frame: performs detection, OCR, saves images, and logs to DB.
        """
        if frame is None:
            logger.warning("Received empty frame for processing.")
            return

        detection_time = datetime.now()
        original_filename = f"{detection_time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.jpg"
        original_filepath = os.path.join(IMAGE_SAVE_DIR, original_filename)

        # 1. Save original image
        cv2.imwrite(original_filepath, frame)
        logger.debug(f"Saved original image: {original_filepath}")

        vehicle_boxes = []
        if self.vehicle_net:
            vehicle_boxes = self.detect_vehicles(frame)

        lp_boxes = []
        if self.lp_net:
            lp_boxes = self.detect_license_plates(frame, vehicle_boxes)
        else:
            # If no dedicated LP model, try to use EasyOCR directly on the whole frame
            # or promising regions. For simplicity, let's just use it on full frame initially
            # or if a vehicle is detected, on the vehicle region.
            # This part needs careful refinement based on your exact models.
            if vehicle_boxes:
                for v_box in vehicle_boxes:
                    x, y, w, h = v_box['box']
                    cropped_vehicle = frame[y:y+h, x:x+w]
                    # Attempt OCR on the vehicle region, or a likely LP location within it
                    # This is a simplification; a dedicated LP detector is far better.
                    # For now, let's assume we get a "potential LP region" from somewhere
                    # or that EasyOCR directly finds text.
                    pass
            # If no LP model and no vehicle, or if we want to try on the whole frame
            # For a true LPR, you'd want robust LP detection.
            
            # For demonstration, let's just say a license plate was "detected"
            # and use a dummy bounding box for OCR if no actual LP detection model is used.
            # In a real scenario, lp_boxes would come from your LP detection model.
            # Example: if you have a known area for LP or a very simple model.
            
            # If no LP_NET, and we *still* want to try OCR, we need to define regions
            # For simplicity, let's assume for this step, if we reach here,
            # we're relying on either `self.lp_net` (if it exists) or
            # will just perform OCR on the whole image (less efficient/accurate).
            # We'll refine this. For now, let's prioritize using a dedicated LP model.

        
        if not lp_boxes and not vehicle_boxes:
            logger.info("No vehicles or license plates detected in this frame.")
            # Still save metadata to DB if desired, even without detections
            self.db_manager.insert_camera_metadata(
                timestamp=detection_time,
                frame_id=str(uuid.uuid4()), # Unique ID for this frame's metadata
                exposure_time=metadata.get('ExposureTime', 0),
                analog_gain=metadata.get('AnalogGain', 0),
                digital_gain=metadata.get('DigitalGain', 0),
                lux=metadata.get('Lux', 0),
                colour_temperature=metadata.get('ColourTemperature', 0),
                lens_position=metadata.get('LensPosition', 0),
                focus_state=metadata.get('FocusState', 0),
                image_filename=original_filename
            )
            return

        # Prepare image for drawing bounding boxes
        frame_with_boxes = frame.copy()
        
        detection_results = []

        # Process detected license plates
        for i, lp_box_data in enumerate(lp_boxes):
            x, y, w, h = lp_box_data['box']
            lp_confidence = lp_box_data.get('confidence', 0.0) # Get confidence if available

            # Ensure coordinates are within image bounds
            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(frame.shape[1], x + w), min(frame.shape[0], y + h)

            if x2 <= x1 or y2 <= y1:
                logger.warning(f"Invalid LP bounding box dimensions: {x,y,w,h}. Skipping.")
                continue

            cropped_lp = frame[y1:y2, x1:x2]
            lp_text = self.perform_ocr(cropped_lp)
            
            lp_image_filename = f"{detection_time.strftime('%Y%m%d_%H%M%S')}_lp_{i}_{uuid.uuid4().hex}.jpg"
            lp_image_filepath = os.path.join(IMAGE_SAVE_DIR, lp_image_filename)
            cv2.imwrite(lp_image_filepath, cropped_lp)
            logger.debug(f"Saved cropped license plate: {lp_image_filepath}")

            # Draw bounding box for LP on frame_with_boxes
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2) # Green for LP
            cv2.putText(frame_with_boxes, f"{lp_text} ({lp_confidence:.2f})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            detection_results.append({
                'license_plate_text': lp_text,
                'lp_confidence': lp_confidence,
                'lp_box_x': x1, 'lp_box_y': y1, 'lp_box_w': w, 'lp_box_h': h,
                'lp_image_filename': lp_image_filename
            })

        # Process detected vehicles (if any, and draw on frame_with_boxes)
        for v_box_data in vehicle_boxes:
            x, y, w, h = v_box_data['box']
            v_confidence = v_box_data.get('confidence', 0.0)

            x1, y1 = max(0, x), max(0, y)
            x2, y2 = min(frame.shape[1], x + w), min(frame.shape[0], y + h)

            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (255, 0, 0), 2) # Blue for vehicle
            cv2.putText(frame_with_boxes, f"Vehicle ({v_confidence:.2f})", (x1, y1 - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            # You might want to link vehicles to their LPs if they overlap

        # Save image with bounding boxes
        processed_filename = f"{detection_time.strftime('%Y%m%d_%H%M%S')}_processed_{uuid.uuid4().hex}.jpg"
        processed_filepath = os.path.join(IMAGE_SAVE_DIR, processed_filename)
        cv2.imwrite(processed_filepath, frame_with_boxes)
        logger.debug(f"Saved processed image: {processed_filepath}")

        # Insert metadata and detection results into the database
        frame_id = str(uuid.uuid4()) # Unique ID for this frame's metadata
        self.db_manager.insert_camera_metadata(
            timestamp=detection_time,
            frame_id=frame_id,
            exposure_time=metadata.get('ExposureTime', 0),
            analog_gain=metadata.get('AnalogGain', 0),
            digital_gain=metadata.get('DigitalGain', 0),
            lux=metadata.get('Lux', 0),
            colour_temperature=metadata.get('ColourTemperature', 0),
            lens_position=metadata.get('LensPosition', 0),
            focus_state=metadata.get('FocusState', 0),
            image_filename=original_filename,
            processed_image_filename=processed_filename
        )

        for result in detection_results:
            self.db_manager.insert_detection_result(
                frame_id=frame_id,
                license_plate_text=result['license_plate_text'],
                lp_confidence=result['lp_confidence'],
                lp_box_x=result['lp_box_x'],
                lp_box_y=result['lp_box_y'],
                lp_box_w=result['lp_box_w'],
                lp_box_h=result['lp_box_h'],
                lp_image_filename=result['lp_image_filename']
            )
        
        logger.info(f"Frame processed and results saved for frame_id: {frame_id}. Detections: {len(detection_results)}")

    def run(self):
        """
        Main loop for the detection processor thread.
        Continuously captures frames and processes them.
        """
        self.running = True
        logger.info("Detection processor thread started.")
        while self.running:
            try:
                #frame, metadata = self.camera_handler.capture_frame_and_metadata()
                # Get the frame from the queue with a timeout
                frame_bytes = self.frames_queue.get(timeout=1)
                logger.debug(f"Retrieved frame from queue for processing {frame_bytes}.")
                # Convert bytes to an OpenCV image
                #image = self.bytes_to_image(frame_bytes)
                # Get metadata (assuming it's a separate process now)
                metadata = {}
                # Process the frame
                #self.process_frame(image, metadata)
                # Signal that the frame has been processed
                #self.frames_queue.task_done()
                time.sleep(DETECTION_INTERVAL) # Control processing frequency
            except queue.Empty:
                logger.debug("No frames in queue to process. Waiting for new frames...")
                continue
            except Exception as e:
                logger.error(f"Error in detection processing loop: {e}")
        logger.info("Detection processor thread stopped.")

    def stop(self):
        """Stops the detection processor thread."""
        self.running = False
        logger.info("Stopping detection processor thread...")