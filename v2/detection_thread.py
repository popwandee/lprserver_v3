#!/usr/bin/env python3
"""
Simple Detection Thread for AI Camera v2
Comprehensive vehicle and license plate detection with OCR and database storage
"""

import os
import threading
import time
import cv2
import numpy as np
import logging
import queue
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

# Import our custom modules
from config import (
    BASE_DIR, IMAGE_SAVE_DIR, VEHICLE_DETECTION_MODEL, 
    LICENSE_PLATE_DETECTION_MODEL, LICENSE_PLATE_OCR_MODEL,
    EASYOCR_LANGUAGES, DETECTION_INTERVAL, HEF_MODEL_PATH, MODEL_ZOO_URL
)
from camera_config import get_detection_resolution, get_video_feed_resolution
from image_processing import (
    resize_with_letterbox, crop_license_plates, draw_bounding_boxes,
    preprocess_for_ocr
)
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class DetectionThread(threading.Thread):
    """
    Detection thread that processes frames for vehicle and license plate detection.
    Integrates with the simple camera manager and saves results to database.
    """
    
    def __init__(self, camera_manager, frames_queue: queue.Queue, db_manager: DatabaseManager):
        super().__init__()
        self.camera_manager = camera_manager
        self.frames_queue = frames_queue
        self.db_manager = db_manager
        self.running = False
        self.daemon = True
        
        # Model instances
        self.vehicle_model = None
        self.lp_detection_model = None
        self.lp_ocr_model = None
        self.ocr_reader = None
        
        # Detection state
        self.prev_ocr_text = None
        self.prev_plate_image = None
        self.detection_count = 0
        
        # Ensure image save directory exists
        os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
        
        logger.info("Simple Detection Thread initialized")

    def load_models(self) -> bool:
        """
        Load detection and OCR models with proper error handling.
        Returns True if all models loaded successfully.
        """
        try:
            logger.info("Loading detection models...")
            
            # Load Hailo models using the same approach as test_models.py (working approach)
            try:
                import degirum as dg
                
                # Get configuration from config.py
                from config import HEF_MODEL_PATH, MODEL_ZOO_URL
                
                logger.info(f"HEF_MODEL_PATH: {HEF_MODEL_PATH}")
                logger.info(f"MODEL_ZOO_URL: {MODEL_ZOO_URL}")
                
                models_loaded = 0
                
                # Vehicle detection model
                if VEHICLE_DETECTION_MODEL:
                    logger.info(f"Loading vehicle detection model: {VEHICLE_DETECTION_MODEL}")
                    self.vehicle_model = dg.load_model(
                        model_name=VEHICLE_DETECTION_MODEL,
                        inference_host_address=HEF_MODEL_PATH,
                        zoo_url=MODEL_ZOO_URL
                    )
                    logger.info("✅ Vehicle detection model loaded successfully")
                    models_loaded += 1
                
                # License plate detection model
                if LICENSE_PLATE_DETECTION_MODEL:
                    logger.info(f"Loading license plate detection model: {LICENSE_PLATE_DETECTION_MODEL}")
                    self.lp_detection_model = dg.load_model(
                        model_name=LICENSE_PLATE_DETECTION_MODEL,
                        inference_host_address=HEF_MODEL_PATH,
                        zoo_url=MODEL_ZOO_URL,
                        overlay_color=[(255, 255, 0), (0, 255, 0)]
                    )
                    logger.info("✅ License plate detection model loaded successfully")
                    models_loaded += 1
                
                # License plate OCR model
                if LICENSE_PLATE_OCR_MODEL:
                    logger.info(f"Loading license plate OCR model: {LICENSE_PLATE_OCR_MODEL}")
                    
                    try:
                        self.lp_ocr_model = dg.load_model(
                            model_name=LICENSE_PLATE_OCR_MODEL,
                            inference_host_address=HEF_MODEL_PATH,
                            zoo_url=MODEL_ZOO_URL,
                            output_use_regular_nms=False,
                            output_confidence_threshold=0.1
                        )
                        logger.info("✅ License plate OCR model loaded successfully")
                        models_loaded += 1
                        
                        # Test model with dummy input to verify it works
                        try:
                            test_input = np.zeros((128, 256, 3), dtype=np.uint8)
                            test_result = self.lp_ocr_model.predict(test_input)
                            logger.info("✅ OCR model test prediction successful")
                        except Exception as test_e:
                            logger.warning(f"OCR model test prediction failed: {test_e}")
                            
                    except Exception as e:
                        logger.error(f"Failed to load OCR model: {e}")
                        logger.error(f"Model name: {LICENSE_PLATE_OCR_MODEL}")
                        logger.error(f"HEF_MODEL_PATH: {HEF_MODEL_PATH}")
                        logger.error(f"MODEL_ZOO_URL: {MODEL_ZOO_URL}")
                
                logger.info(f"✅ All Hailo models loaded successfully. Total models: {models_loaded}")
                    
            except ImportError:
                logger.warning("Degirum not available, using fallback detection methods")
            except Exception as e:
                logger.error(f"Error loading Hailo models: {e}")
                logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            
            # Load EasyOCR as fallback or additional OCR
            try:
                import easyocr
                self.ocr_reader = easyocr.Reader(EASYOCR_LANGUAGES)
                logger.info(f"EasyOCR loaded with languages: {EASYOCR_LANGUAGES}")
            except ImportError:
                logger.warning("EasyOCR not available, OCR functionality will be limited")
            except Exception as e:
                logger.error(f"Error loading EasyOCR: {e}")
            
            # Check if we have at least one detection method
            models_available = 0
            if self.vehicle_model:
                models_available += 1
                logger.info("✅ Vehicle detection model available")
            if self.lp_detection_model:
                models_available += 1
                logger.info("✅ License plate detection model available")
            if self.lp_ocr_model:
                models_available += 1
                logger.info("✅ License plate OCR model available")
            
            if models_available == 0:
                logger.warning("⚠️ No detection models loaded, using basic frame processing")
            else:
                logger.info(f"✅ Detection system ready with {models_available} models")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False

    def detect_vehicles(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect vehicles in the frame using main stream (640x640).
        Returns list of vehicle detections with bounding boxes.
        """
        if not self.vehicle_model:
            logger.debug("No vehicle detection model available")
            return []
        
        try:
            detection_res = get_detection_resolution()
            logger.info(f"Using main frame for vehicle detection: {frame.shape}")
            
            # Ensure frame is in BGR format for detection models
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # BGRA
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                elif frame.shape[2] == 3:  # RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for models
                # If already BGR, use as is
            elif len(frame.shape) == 2:  # Grayscale
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                logger.info(f"Converted grayscale frame to BGR: {frame.shape}")
            
            # Resize frame to detection resolution if needed
            if frame.shape[:2] != detection_res:
                frame = cv2.resize(frame, detection_res)
                logger.info(f"Resized frame from {frame.shape} to {detection_res} for detection")
            
            # Perform detection on resized frame
            results = self.vehicle_model(frame)
            vehicle_boxes = getattr(results, "results", [])
            
            logger.debug(f"Vehicle detection results: {len(vehicle_boxes)} vehicles detected")
            return vehicle_boxes
            
        except Exception as e:
            logger.error(f"Error in vehicle detection: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            return []

    def detect_license_plates(self, frame: np.ndarray, vehicle_boxes: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Detect license plates in the frame using main stream (640x640).
        If vehicle_boxes provided, only detect within vehicle areas.
        Returns list of license plate detections with bounding boxes.
        """
        if not self.lp_detection_model:
            logger.debug("No license plate detection model available")
            return []
        
        try:
            detection_res = get_detection_resolution()
            logger.info(f"Using main frame for license plate detection: {frame.shape}")
            
            # Ensure frame is in BGR format for detection models
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # BGRA
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                elif frame.shape[2] == 3:  # RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for models
                # If already BGR, use as is
            elif len(frame.shape) == 2:  # Grayscale
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                logger.info(f"Converted grayscale frame to BGR: {frame.shape}")
            
            # Resize frame to detection resolution if needed
            if frame.shape[:2] != detection_res:
                frame = cv2.resize(frame, detection_res)
                logger.info(f"Resized frame from {frame.shape} to {detection_res} for detection")
            
            # If vehicle_boxes provided, detect license plates only within vehicle areas
            if vehicle_boxes:
                all_lp_boxes = []
                for vehicle_box in vehicle_boxes:
                    if 'bbox' in vehicle_box:
                        # Convert bounding box coordinates to integers
                        x1, y1, x2, y2 = vehicle_box['bbox']
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Ensure coordinates are within frame bounds
                        x1 = max(0, min(x1, frame.shape[1] - 1))
                        y1 = max(0, min(y1, frame.shape[0] - 1))
                        x2 = max(x1 + 1, min(x2, frame.shape[1]))
                        y2 = max(y1 + 1, min(y2, frame.shape[0]))
                        
                        # Crop vehicle area
                        vehicle_roi = frame[y1:y2, x1:x2]
                        if vehicle_roi.size > 0:
                            # Detect license plates in vehicle ROI
                            results = self.lp_detection_model(vehicle_roi)
                            lp_boxes = getattr(results, "results", [])
                            
                            # Adjust coordinates back to original frame
                            for lp_box in lp_boxes:
                                if 'bbox' in lp_box:
                                    lp_x1, lp_y1, lp_x2, lp_y2 = lp_box['bbox']
                                    # Convert to integers and adjust
                                    lp_x1, lp_y1, lp_x2, lp_y2 = int(lp_x1), int(lp_y1), int(lp_x2), int(lp_y2)
                                    lp_box['bbox'] = [lp_x1 + x1, lp_y1 + y1, lp_x2 + x1, lp_y2 + y1]
                            
                            all_lp_boxes.extend(lp_boxes)
                
                logger.debug(f"License plate detection results: {len(all_lp_boxes)} plates detected within vehicles")
                return all_lp_boxes
            else:
                # Detect license plates in entire frame
                results = self.lp_detection_model(frame)
                lp_boxes = getattr(results, "results", [])
                
                logger.debug(f"License plate detection results: {len(lp_boxes)} plates detected")
                return lp_boxes
            
        except Exception as e:
            logger.error(f"Error in license plate detection: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            return []

    def perform_ocr(self, image: np.ndarray) -> str:
        """
        Perform OCR on the license plate image according to new requirements.
        Returns detected text.
        """
        if image is None or image.size == 0:
            return ""
        
        try:
            h, w = image.shape[:2]
            logger.info(f"Original OCR image size: {image.shape}")
            
            # Check bounding box size requirements
            min_width, min_height = 256, 128
            
            if w < min_width or h < min_height:
                logger.info(f"Bounding box too small ({w}x{h}), skipping OCR")
                return ""
            
            # If image is larger than required, resize down to (256, 128)
            target_size = (256, 128)  # width, height
            if w > min_width or h > min_height:
                logger.info(f"Resizing large image from ({w}, {h}) to {target_size}")
                image = cv2.resize(image, target_size)
            
            # Convert to grayscale for better OCR results
            if len(image.shape) == 3:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                logger.info(f"Converted to grayscale for OCR: {gray_image.shape}")
            else:
                gray_image = image
            
            # Try Hailo OCR model first
            if self.lp_ocr_model:
                try:
                    # Ensure image is in correct format for Hailo model
                    ocr_input = gray_image.copy()
                    
                    # Ensure image is in correct format (uint8)
                    if ocr_input.dtype != np.uint8:
                        ocr_input = ocr_input.astype(np.uint8)
                    
                    # Convert grayscale to BGR for Hailo model
                    if len(ocr_input.shape) == 2:
                        ocr_input = cv2.cvtColor(ocr_input, cv2.COLOR_GRAY2BGR)
                    
                    logger.info(f"Hailo OCR input shape: {ocr_input.shape}, dtype: {ocr_input.dtype}")
                    
                    # Use image for Hailo OCR
                    ocr_results = self.lp_ocr_model.predict(ocr_input)
                    logger.info(f"Hailo OCR results: {ocr_results}")
                    
                    # Extract text from results
                    if hasattr(ocr_results, 'results') and ocr_results.results:
                        ocr_label = self.rearrange_detections(ocr_results.results)
                        logger.info(f"From Hailo OCR, Detected text: {ocr_label}")
                        
                        if ocr_label and ocr_label != "Unknown":
                            return ocr_label
                        
                except Exception as e:
                    logger.warning(f"Hailo OCR failed: {e}")
                    logger.warning(f"Error details: {type(e).__name__}: {str(e)}")
            
            # Fallback to EasyOCR (better for Thai text)
            if self.ocr_reader:
                try:
                    # Use grayscale image for EasyOCR
                    easyocr_results = self.ocr_reader.readtext(gray_image)
                    logger.info(f"EasyOCR results: {easyocr_results}")
                    
                    # Extract text from results
                    detected_texts = []
                    for (bbox, text, confidence) in easyocr_results:
                        if confidence > 0.5:  # Confidence threshold
                            detected_texts.append(text)
                    
                    if detected_texts:
                        detected_text = " ".join(detected_texts).strip()
                        logger.info(f"From EasyOCR, Detected text: {detected_text}")
                        return detected_text
                        
                except Exception as e:
                    logger.warning(f"EasyOCR failed: {e}")
                    logger.warning(f"Error details: {type(e).__name__}: {str(e)}")
            
            return ""
            
        except Exception as e:
            logger.error(f"Error in OCR: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            return ""

    def rearrange_detections(self, ocr_results):
        """
        Rearranges OCR detection results into a single string for a readable format.
        Same as detection_v1.py
        """
        if not ocr_results:
            return "Unknown"
        extracted_text = []
        # Sort results based on x-coordinate to get correct order for horizontal text
        sorted_results = sorted(ocr_results, key=lambda x: x.get("bbox", [0])[0] if isinstance(x, dict) and "bbox" in x else 0)
        for res in sorted_results:
            if isinstance(res, dict) and "label" in res:
                extracted_text.append(res["label"])  # Extract text from label
        return "".join(extracted_text)

    def save_image_with_timestamp(self, image: np.ndarray, prefix: str = "image") -> str:
        """
        Save image with timestamp and unique identifier.
        Returns the filename.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            unique_id = uuid.uuid4().hex[:8]
            filename = f"{prefix}_{timestamp}_{unique_id}.jpg"
            filepath = os.path.join(IMAGE_SAVE_DIR, filename)
            
            cv2.imwrite(filepath, image)
            logger.debug(f"Saved image: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return ""

    def filter_valid_license_plates(self, lp_boxes: List[Dict], frame_shape: Tuple[int, int, int]) -> List[Dict]:
        """
        Filter license plate boxes to ensure they meet minimum size requirements for OCR.
        
        Args:
            lp_boxes: List of license plate detection boxes
            frame_shape: Shape of the frame (height, width, channels)
        
        Returns:
            Filtered list of valid license plate boxes
        """
        if not lp_boxes:
            return []
        
        valid_boxes = []
        frame_h, frame_w = frame_shape[:2]
        
        # Minimum size requirements for OCR (in pixels)
        min_width = 256   # Minimum width for license plate (Hailo OCR requirement)
        min_height = 128  # Minimum height for license plate (Hailo OCR requirement)
        
        for box in lp_boxes:
            if 'bbox' in box:
                x1, y1, x2, y2 = box['bbox']
                
                # Convert coordinates to integers
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Calculate box dimensions
                width = x2 - x1
                height = y2 - y1
                
                # Check if box meets minimum size requirements
                if width >= min_width and height >= min_height:
                    # Ensure box is within frame bounds
                    x1 = max(0, min(x1, frame_w - 1))
                    y1 = max(0, min(y1, frame_h - 1))
                    x2 = max(x1 + 1, min(x2, frame_w))
                    y2 = max(y1 + 1, min(y2, frame_h))
                    
                    if x2 > x1 and y2 > y1:
                        # Update box with validated coordinates
                        box['bbox'] = [x1, y1, x2, y2]
                        valid_boxes.append(box)
                        logger.info(f"Valid license plate box: {width}x{height} at ({x1},{y1})-({x2},{y2})")
                    else:
                        logger.warning(f"Invalid license plate box coordinates: ({x1},{y1})-({x2},{y2})")
                else:
                    logger.warning(f"License plate box too small: {width}x{height} (min: {min_width}x{min_height})")
        
        logger.info(f"Filtered {len(lp_boxes)} license plate boxes to {len(valid_boxes)} valid boxes")
        return valid_boxes

    def check_similarity(self, current_text: str, current_image: np.ndarray) -> bool:
        """
        Check if current detection is similar to previous detection.
        Uses the same approach as detection_v1.py
        """
        # Text similarity using SequenceMatcher (same as detection_v1.py)
        if self.prev_ocr_text and current_text:
            from difflib import SequenceMatcher
            text_similar = SequenceMatcher(None, current_text, self.prev_ocr_text).ratio()
            if text_similar > 0.85:  # Same threshold as detection_v1.py
                logger.info(f"Text similarity: {text_similar:.2f} - Similar text detected")
                return True
        
        # Image similarity using histogram comparison (same as detection_v1.py)
        if self.prev_plate_image is not None and current_image is not None:
            try:
                # Resize to the same shape
                h, w = 128, 128
                img1 = cv2.resize(self.prev_plate_image, (w, h))
                img2 = cv2.resize(current_image, (w, h))
                
                # Use histogram comparison
                hist1 = cv2.calcHist([img1], [0], None, [256], [0,256])
                hist2 = cv2.calcHist([img2], [0], None, [256], [0,256])
                hist1 = cv2.normalize(hist1, hist1).flatten()
                hist2 = cv2.normalize(hist2, hist2).flatten()
                score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                img_similar = score if 0 <= score <= 1 else max(0, min(1, score))
                
                if img_similar > 0.90:  # Same threshold as detection_v1.py
                    logger.info(f"Image similarity: {img_similar:.2f} - Similar image detected")
                    return True
                    
            except Exception as e:
                logger.debug(f"Error in image similarity check: {e}")
        
        return False

    def process_frame(self, frame: np.ndarray) -> None:
        """
        Process a single frame using main stream (high quality) for detection.
        New workflow:
        1. Detect vehicles
        2. If vehicles found, save vehicle image
        3. Detect license plates within vehicle areas
        4. If license plates found, draw bounding boxes and save
        5. Perform OCR on license plate regions
        """
        if frame is None or not isinstance(frame, np.ndarray):
            logger.info("Image capture failed or invalid image type!")
            return
        
        try:
            timestamp = datetime.now()
            self.detection_count += 1
            
            logger.debug(f"Processing main frame {self.detection_count}: {frame.shape}")
            
            # 1. Detect vehicles using main frame (high quality)
            vehicle_boxes = self.detect_vehicles(frame)
            
            # 2. Only proceed if vehicles are detected
            if not vehicle_boxes:
                logger.debug(f"Frame {self.detection_count}: No vehicles detected, skipping processing")
                return
            
            logger.info(f"Frame {self.detection_count}: {len(vehicle_boxes)} vehicles detected, proceeding with processing")
            
            # 3. Use main frame for saving (640x640) - only when vehicles detected
            main_frame = frame  # Use the frame directly from main stream
            
            # 4. Save Type 1: Vehicle detected frame (original)
            original_filename = self.save_image_with_timestamp(main_frame, "vehicle_detected")
            logger.info(f"Saved vehicle detected frame: {original_filename}")
            
            # 5. Detect license plates within vehicle areas
            lp_boxes = self.detect_license_plates(frame, vehicle_boxes)
            
            # 6. Process license plates if found
            cropped_license_plates = []  # Initialize outside the if block
            if lp_boxes:
                # Filter out license plate boxes that are too small for OCR
                filtered_lp_boxes = self.filter_valid_license_plates(lp_boxes, frame.shape)
                if filtered_lp_boxes:
                    # 7. Save Type 2: Vehicle frame with license plate bounding boxes
                    frame_with_lp_boxes = draw_bounding_boxes(main_frame, filtered_lp_boxes, color=(255, 0, 0), thickness=3)
                    lp_boxes_filename = self.save_image_with_timestamp(frame_with_lp_boxes, "vehicle_with_lp_boxes")
                    logger.info(f"Saved vehicle frame with license plate boxes: {lp_boxes_filename}")
                    
                    # 8. Crop and process license plates
                    cropped_license_plates = crop_license_plates(frame, filtered_lp_boxes)
                    
            # 9. Process each cropped license plate
            if cropped_license_plates:
                for index, cropped_plate in enumerate(cropped_license_plates):
                    if cropped_plate is None or cropped_plate.size == 0:
                        logger.warning(f"Skipping empty or invalid cropped plate at index {index}")
                        continue
                    
                    # Check for similarity with previous detection
                    if self.check_similarity("", cropped_plate):
                        logger.info("Similar plate detected, skipping save and database update.")
                        continue
                    
                    # 10. Perform OCR
                    ocr_text = self.perform_ocr(cropped_plate)
                    
                    # Check text similarity
                    if self.check_similarity(ocr_text, cropped_plate):
                        logger.info("Similar plate text detected, skipping save and database update.")
                        continue
                    
                    # 11. Save Type 3: Cropped license plate image
                    cropped_path = self.save_image_with_timestamp(cropped_plate, f"cropped_plate_{index}")
                    logger.info(f"Saved cropped license plate: {cropped_path}")
                    
                    # 12. Save to database only when license plate is detected and OCR successful
                    if ocr_text.strip():
                        try:
                            self.db_manager.insert_detection_result(
                                license_plate=ocr_text,
                                vehicle_image_path=original_filename,
                                license_plate_image_path=lp_boxes_filename,
                                cropped_image_path=cropped_path,
                                timestamp=timestamp,
                                location="",
                                hostname=os.uname().nodename if hasattr(os, "uname") else "",
                                confidence=0.0
                            )
                            logger.info(f"Saved unique plate to database: {ocr_text} at {cropped_path}")
                        except Exception as e:
                            logger.error(f"Error saving to database: {e}")
                    else:
                        logger.debug("No text detected in license plate, skipping database save")
                    
                    # Update previous states
                    self.prev_ocr_text = ocr_text
                    self.prev_plate_image = cropped_plate.copy()
                    
                    # Only process the first unique plate found in a frame
                    break
                else:
                    logger.info("No valid license plate boxes found after filtering")
                    # Save vehicle detection to database when no valid license plates
                    try:
                        self.db_manager.insert_vehicle_detection(
                            vehicle_image_path=original_filename,
                            license_plate_image_path="",
                            timestamp=timestamp,
                            location="",
                            hostname=os.uname().nodename if hasattr(os, "uname") else ""
                        )
                        logger.info(f"Vehicle detected but no valid license plates found - saved vehicle detection to database")
                    except Exception as e:
                        logger.error(f"Error saving vehicle detection to database: {e}")
            else:
                logger.info("No license plates detected")
                # Save vehicle detection to database when no license plates
                try:
                    self.db_manager.insert_vehicle_detection(
                        vehicle_image_path=original_filename,
                        license_plate_image_path="",
                        timestamp=timestamp,
                        location="",
                        hostname=os.uname().nodename if hasattr(os, "uname") else ""
                    )
                    logger.info(f"Vehicle detected but no license plates found - saved vehicle detection to database")
                except Exception as e:
                    logger.error(f"Error saving vehicle detection to database: {e}")
            
            logger.debug(f"Frame {self.detection_count} processed")
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")

    def run(self):
        """
        Main detection loop.
        """
        logger.info("Starting detection thread...")
        
        # Load models
        if not self.load_models():
            logger.error("Failed to load models, detection thread will exit")
            return
        
        self.running = True
        
        while self.running:
            try:
                # Get main frame from camera manager for detection (640x640)
                if self.camera_manager.is_initialized and self.camera_manager.streaming:
                    frame = self.camera_manager.get_frame()  # Use main stream for detection
                    if frame is not None:
                        self.process_frame(frame)
                    else:
                        logger.debug("No main frame available from camera")
                        time.sleep(0.1)
                else:
                    logger.debug("Camera not ready for detection")
                    time.sleep(1)
                
                # Control processing frequency
                time.sleep(DETECTION_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(1)
        
        logger.info("Detection thread stopped")

    def stop(self):
        """
        Stop the detection thread.
        """
        logger.info("Stopping detection thread...")
        self.running = False 