#!/usr/bin/env python3
"""
Test Detection Step by Step
ทดสอบการทำงานของ detection models แบบขั้นตอน โดยใช้ภาพจาก static/images
"""

import os
import sys
import cv2
import numpy as np
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from config import (
    BASE_DIR, VEHICLE_DETECTION_MODEL, 
    LICENSE_PLATE_DETECTION_MODEL, LICENSE_PLATE_OCR_MODEL,
    EASYOCR_LANGUAGES, HEF_MODEL_PATH, MODEL_ZOO_URL
)
from camera_config import get_detection_resolution
from image_processing import crop_license_plates, draw_bounding_boxes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StepByStepDetector:
    """Step-by-step detection tester"""
    
    def __init__(self):
        self.vehicle_model = None
        self.lp_detection_model = None
        self.lp_ocr_model = None
        self.ocr_reader = None
        self.test_results = []
        
    def load_models(self) -> bool:
        """Load all detection and OCR models"""
        try:
            logger.info("🔧 Loading detection models...")
            
            import degirum as dg
            
            models_loaded = 0
            
            # Vehicle detection model
            if VEHICLE_DETECTION_MODEL:
                logger.info(f"Loading vehicle detection model: {VEHICLE_DETECTION_MODEL}")
                self.vehicle_model = dg.load_model(
                    model_name=VEHICLE_DETECTION_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL
                )
                logger.info("✅ Vehicle detection model loaded")
                models_loaded += 1
            
            # License plate detection model
            if LICENSE_PLATE_DETECTION_MODEL:
                logger.info(f"Loading license plate detection model: {LICENSE_PLATE_DETECTION_MODEL}")
                self.lp_detection_model = dg.load_model(
                    model_name=LICENSE_PLATE_DETECTION_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL
                )
                logger.info("✅ License plate detection model loaded")
                models_loaded += 1
            
            # License plate OCR model
            if LICENSE_PLATE_OCR_MODEL:
                logger.info(f"Loading license plate OCR model: {LICENSE_PLATE_OCR_MODEL}")
                self.lp_ocr_model = dg.load_model(
                    model_name=LICENSE_PLATE_OCR_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL
                )
                logger.info("✅ License plate OCR model loaded")
                models_loaded += 1
            
            # EasyOCR for fallback
            try:
                import easyocr
                self.ocr_reader = easyocr.Reader(EASYOCR_LANGUAGES)
                logger.info("✅ EasyOCR loaded")
                models_loaded += 1
            except Exception as e:
                logger.warning(f"Failed to load EasyOCR: {e}")
            
            logger.info(f"Total models loaded: {models_loaded}")
            return models_loaded >= 3
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def step1_vehicle_detection(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Step 1: Vehicle Detection"""
        logger.info("\n🚗 STEP 1: VEHICLE DETECTION")
        logger.info("="*50)
        
        if not self.vehicle_model:
            logger.error("❌ No vehicle detection model available")
            return []
        
        try:
            detection_res = get_detection_resolution()
            logger.info(f"Input image shape: {image.shape}")
            
            # Ensure frame is in BGR format for detection models
            if len(image.shape) == 3:
                if image.shape[2] == 4:  # BGRA
                    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
                elif image.shape[2] == 3:  # RGB
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            elif len(image.shape) == 2:  # Grayscale
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            # Resize frame to detection resolution if needed
            if image.shape[:2] != detection_res:
                image = cv2.resize(image, detection_res)
                logger.info(f"Resized to {detection_res}")
            
            # Perform detection
            results = self.vehicle_model(image)
            vehicle_boxes = getattr(results, "results", [])
            
            logger.info(f"🔍 Vehicles detected: {len(vehicle_boxes)}")
            
            # Log details of each detection
            for i, box in enumerate(vehicle_boxes):
                if 'bbox' in box:
                    x1, y1, x2, y2 = box['bbox']
                    label = box.get('label', 'Unknown')
                    confidence = box.get('score', 0)
                    logger.info(f"  Vehicle {i+1}: {label} (conf: {confidence:.3f}) at ({x1:.1f},{y1:.1f})-({x2:.1f},{y2:.1f})")
            
            return vehicle_boxes
            
        except Exception as e:
            logger.error(f"❌ Error in vehicle detection: {e}")
            return []
    
    def step2_license_plate_detection(self, image: np.ndarray, vehicle_boxes: List[Dict]) -> List[Dict[str, Any]]:
        """Step 2: License Plate Detection"""
        logger.info("\n🔢 STEP 2: LICENSE PLATE DETECTION")
        logger.info("="*50)
        
        if not self.lp_detection_model:
            logger.error("❌ No license plate detection model available")
            return []
        
        try:
            detection_res = get_detection_resolution()
            logger.info(f"Input image shape: {image.shape}")
            logger.info(f"Vehicle boxes to search in: {len(vehicle_boxes)}")
            
            # Ensure frame is in BGR format for detection models
            if len(image.shape) == 3:
                if image.shape[2] == 4:  # BGRA
                    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
                elif image.shape[2] == 3:  # RGB
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            elif len(image.shape) == 2:  # Grayscale
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            # Resize frame to detection resolution if needed
            if image.shape[:2] != detection_res:
                image = cv2.resize(image, detection_res)
                logger.info(f"Resized to {detection_res}")
            
            all_lp_boxes = []
            
            # Detect license plates within each vehicle area
            for i, vehicle_box in enumerate(vehicle_boxes):
                if 'bbox' in vehicle_box:
                    # Convert bounding box coordinates to integers
                    x1, y1, x2, y2 = vehicle_box['bbox']
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Ensure coordinates are within frame bounds
                    x1 = max(0, min(x1, image.shape[1] - 1))
                    y1 = max(0, min(y1, image.shape[0] - 1))
                    x2 = max(x1 + 1, min(x2, image.shape[1]))
                    y2 = max(y1 + 1, min(y2, image.shape[0]))
                    
                    logger.info(f"  Searching in vehicle {i+1} area: ({x1},{y1})-({x2},{y2})")
                    
                    # Crop vehicle area
                    vehicle_roi = image[y1:y2, x1:x2]
                    if vehicle_roi.size > 0:
                        # Detect license plates in vehicle ROI
                        results = self.lp_detection_model(vehicle_roi)
                        lp_boxes = getattr(results, "results", [])
                        
                        logger.info(f"    Found {len(lp_boxes)} license plates in vehicle {i+1}")
                        
                        # Adjust coordinates back to original frame
                        for lp_box in lp_boxes:
                            if 'bbox' in lp_box:
                                lp_x1, lp_y1, lp_x2, lp_y2 = lp_box['bbox']
                                lp_x1, lp_y1, lp_x2, lp_y2 = int(lp_x1), int(lp_y1), int(lp_x2), int(lp_y2)
                                lp_box['bbox'] = [lp_x1 + x1, lp_y1 + y1, lp_x2 + x1, lp_y2 + y1]
                                
                                # Log license plate details
                                label = lp_box.get('label', 'Unknown')
                                confidence = lp_box.get('score', 0)
                                logger.info(f"      LP: {label} (conf: {confidence:.3f}) at ({lp_x1 + x1},{lp_y1 + y1})-({lp_x2 + x1},{lp_y2 + y1})")
                        
                        all_lp_boxes.extend(lp_boxes)
            
            logger.info(f"🔍 Total license plates detected: {len(all_lp_boxes)}")
            return all_lp_boxes
            
        except Exception as e:
            logger.error(f"❌ Error in license plate detection: {e}")
            return []
    
    def step3_filter_valid_plates(self, lp_boxes: List[Dict], image_shape: Tuple[int, int, int]) -> List[Dict]:
        """Step 3: Filter Valid License Plates"""
        logger.info("\n✅ STEP 3: FILTER VALID LICENSE PLATES")
        logger.info("="*50)
        
        if not lp_boxes:
            logger.info("No license plates to filter")
            return []
        
        valid_boxes = []
        frame_h, frame_w = image_shape[:2]
        
        # Minimum size requirements for OCR (in pixels)
        min_width = 256
        min_height = 128
        
        logger.info(f"Minimum size requirement: {min_width}x{min_height} pixels")
        
        for i, box in enumerate(lp_boxes):
            if 'bbox' in box:
                x1, y1, x2, y2 = box['bbox']
                
                # Convert coordinates to integers
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Calculate box dimensions
                width = x2 - x1
                height = y2 - y1
                
                logger.info(f"  License plate {i+1}: {width}x{height} pixels")
                
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
                        logger.info(f"    ✅ Valid: {width}x{height} at ({x1},{y1})-({x2},{y2})")
                    else:
                        logger.warning(f"    ❌ Invalid coordinates: ({x1},{y1})-({x2},{y2})")
                else:
                    logger.warning(f"    ❌ Too small: {width}x{height} (min: {min_width}x{min_height})")
        
        logger.info(f"🔍 Valid license plates: {len(valid_boxes)}/{len(lp_boxes)}")
        return valid_boxes
    
    def step4_ocr_processing(self, image: np.ndarray, valid_lp_boxes: List[Dict]) -> List[Dict[str, Any]]:
        """Step 4: OCR Processing"""
        logger.info("\n📝 STEP 4: OCR PROCESSING")
        logger.info("="*50)
        
        if not valid_lp_boxes:
            logger.info("No valid license plates for OCR")
            return []
        
        ocr_results = []
        cropped_plates = crop_license_plates(image, valid_lp_boxes)
        
        for i, cropped_plate in enumerate(cropped_plates):
            if cropped_plate is not None and cropped_plate.size > 0:
                logger.info(f"\n  Processing license plate {i+1}: {cropped_plate.shape}")
                
                # Save cropped plate for inspection
                cropped_path = f"test_cropped_plate_{i+1}.jpg"
                cv2.imwrite(cropped_path, cropped_plate)
                logger.info(f"    Saved: {cropped_path}")
                
                # Perform OCR
                ocr_text = self.perform_ocr(cropped_plate)
                
                ocr_result = {
                    'plate_index': i+1,
                    'cropped_path': cropped_path,
                    'ocr_text': ocr_text,
                    'success': bool(ocr_text.strip())
                }
                
                ocr_results.append(ocr_result)
                
                if ocr_text.strip():
                    logger.info(f"    ✅ OCR Success: '{ocr_text}'")
                else:
                    logger.warning(f"    ❌ OCR Failed: No text detected")
        
        logger.info(f"📝 OCR Results: {len([r for r in ocr_results if r['success']])}/{len(ocr_results)} successful")
        return ocr_results
    
    def perform_ocr(self, image: np.ndarray) -> str:
        """Perform OCR on the license plate image"""
        if image is None or image.size == 0:
            return ""
        
        try:
            h, w = image.shape[:2]
            
            # Check bounding box size requirements
            min_width, min_height = 256, 128
            
            if w < min_width or h < min_height:
                return ""
            
            # If image is larger than required, resize down to (256, 128)
            target_size = (256, 128)  # width, height
            if w > min_width or h > min_height:
                image = cv2.resize(image, target_size)
            
            # Convert to grayscale for better OCR results
            if len(image.shape) == 3:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
                    
                    # Use image for Hailo OCR
                    ocr_results = self.lp_ocr_model.predict(ocr_input)
                    
                    # Extract text from results
                    if hasattr(ocr_results, 'results') and ocr_results.results:
                        ocr_label = self.rearrange_detections(ocr_results.results)
                        
                        if ocr_label and ocr_label != "Unknown":
                            return ocr_label
                        
                except Exception as e:
                    logger.warning(f"Hailo OCR failed: {e}")
            
            # Fallback to EasyOCR (better for Thai text)
            if self.ocr_reader:
                try:
                    # Use grayscale image for EasyOCR
                    easyocr_results = self.ocr_reader.readtext(gray_image)
                    
                    # Extract text from results
                    detected_texts = []
                    for (bbox, text, confidence) in easyocr_results:
                        if confidence > 0.5:  # Confidence threshold
                            detected_texts.append(text)
                    
                    if detected_texts:
                        detected_text = " ".join(detected_texts).strip()
                        return detected_text
                        
                except Exception as e:
                    logger.warning(f"EasyOCR failed: {e}")
            
            return ""
            
        except Exception as e:
            logger.error(f"Error in OCR: {e}")
            return ""
    
    def rearrange_detections(self, ocr_results):
        """Rearrange OCR detections to get the most likely text"""
        if not ocr_results:
            return ""
        
        # Sort by confidence and get the highest confidence result
        sorted_results = sorted(ocr_results, key=lambda x: x.get('confidence', 0), reverse=True)
        if sorted_results:
            return sorted_results[0].get('label', '')
        return ""
    
    def step5_save_results(self, image: np.ndarray, vehicle_boxes: List[Dict], 
                          valid_lp_boxes: List[Dict], ocr_results: List[Dict], 
                          image_path: str) -> str:
        """Step 5: Save Results"""
        logger.info("\n💾 STEP 5: SAVE RESULTS")
        logger.info("="*50)
        
        try:
            # Draw vehicle boxes (green)
            image_with_vehicles = draw_bounding_boxes(image, vehicle_boxes, color=(0, 255, 0), thickness=2)
            
            # Draw license plate boxes (red)
            image_with_all_boxes = draw_bounding_boxes(image_with_vehicles, valid_lp_boxes, color=(255, 0, 0), thickness=3)
            
            # Save result image
            result_path = f"test_result_{os.path.basename(image_path)}"
            cv2.imwrite(result_path, image_with_all_boxes)
            logger.info(f"✅ Saved result image: {result_path}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
            return ""
    
    def test_image(self, image_path: str) -> Dict[str, Any]:
        """Test detection pipeline on a single image"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 TESTING IMAGE: {os.path.basename(image_path)}")
        logger.info(f"{'='*80}")
        
        result = {
            'image_path': image_path,
            'vehicles_detected': 0,
            'license_plates_detected': 0,
            'valid_license_plates': 0,
            'ocr_success': 0,
            'ocr_results': [],
            'result_image_path': '',
            'errors': []
        }
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                error_msg = f"Failed to load image: {image_path}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
                return result
            
            logger.info(f"📸 Loaded image: {image.shape}")
            
            # Step 1: Vehicle Detection
            vehicle_boxes = self.step1_vehicle_detection(image)
            result['vehicles_detected'] = len(vehicle_boxes)
            
            if not vehicle_boxes:
                logger.info("🚫 No vehicles detected, skipping remaining steps")
                return result
            
            # Step 2: License Plate Detection
            lp_boxes = self.step2_license_plate_detection(image, vehicle_boxes)
            result['license_plates_detected'] = len(lp_boxes)
            
            if not lp_boxes:
                logger.info("🚫 No license plates detected")
                return result
            
            # Step 3: Filter Valid License Plates
            valid_lp_boxes = self.step3_filter_valid_plates(lp_boxes, image.shape)
            result['valid_license_plates'] = len(valid_lp_boxes)
            
            if not valid_lp_boxes:
                logger.info("🚫 No valid license plates found after filtering")
                return result
            
            # Step 4: OCR Processing
            ocr_results = self.step4_ocr_processing(image, valid_lp_boxes)
            result['ocr_results'] = ocr_results
            result['ocr_success'] = len([r for r in ocr_results if r['success']])
            
            # Step 5: Save Results
            result_image_path = self.step5_save_results(image, vehicle_boxes, valid_lp_boxes, ocr_results, image_path)
            result['result_image_path'] = result_image_path
            
        except Exception as e:
            error_msg = f"Error processing image {image_path}: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def run_tests(self):
        """Run tests on all images in static/images"""
        logger.info("🚀 STARTING STEP-BY-STEP DETECTION TESTS")
        logger.info("="*80)
        
        # Load models
        if not self.load_models():
            logger.error("❌ Failed to load models, cannot run tests")
            return
        
        # Get list of test images
        static_images_dir = os.path.join(BASE_DIR, 'static', 'images')
        test_images = []
        
        for filename in os.listdir(static_images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(static_images_dir, filename))
        
        logger.info(f"📁 Found {len(test_images)} test images")
        
        # Test each image
        for image_path in test_images:
            result = self.test_image(image_path)
            self.test_results.append(result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*80)
        logger.info("📊 DETECTION PIPELINE TEST SUMMARY")
        logger.info("="*80)
        
        total_images = len(self.test_results)
        successful_images = len([r for r in self.test_results if not r['errors']])
        
        logger.info(f"📈 Total images tested: {total_images}")
        logger.info(f"✅ Successfully processed: {successful_images}")
        logger.info(f"❌ Failed: {total_images - successful_images}")
        
        total_vehicles = sum(r['vehicles_detected'] for r in self.test_results)
        total_lp_detected = sum(r['license_plates_detected'] for r in self.test_results)
        total_valid_lp = sum(r['valid_license_plates'] for r in self.test_results)
        total_ocr_success = sum(r['ocr_success'] for r in self.test_results)
        
        logger.info(f"\n🎯 Detection Results:")
        logger.info(f"  🚗 Total vehicles detected: {total_vehicles}")
        logger.info(f"  🔢 Total license plates detected: {total_lp_detected}")
        logger.info(f"  ✅ Total valid license plates: {total_valid_lp}")
        logger.info(f"  📝 Total successful OCR: {total_ocr_success}")
        
        # Print detailed results for each image
        for i, result in enumerate(self.test_results, 1):
            logger.info(f"\n📸 Image {i}: {os.path.basename(result['image_path'])}")
            logger.info(f"  🚗 Vehicles: {result['vehicles_detected']}")
            logger.info(f"  🔢 License Plates: {result['license_plates_detected']}")
            logger.info(f"  ✅ Valid Plates: {result['valid_license_plates']}")
            logger.info(f"  📝 OCR Success: {result['ocr_success']}")
            
            if result['ocr_results']:
                for ocr in result['ocr_results']:
                    if ocr['success']:
                        logger.info(f"    ✅ Plate {ocr['plate_index']}: '{ocr['ocr_text']}'")
                    else:
                        logger.info(f"    ❌ Plate {ocr['plate_index']}: No text detected")
            
            if result['errors']:
                for error in result['errors']:
                    logger.error(f"    Error: {error}")

if __name__ == "__main__":
    detector = StepByStepDetector()
    detector.run_tests() 