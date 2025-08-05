#!/usr/bin/env python3
"""
Simple Detection Pipeline Test
ทดสอบระบบ detection โดยใช้ OpenCV เท่านั้น เพื่อทดสอบ image processing pipeline
"""

import os
import cv2
import numpy as np
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleDetectionTester:
    """Simple detection tester using OpenCV"""
    
    def __init__(self):
        self.test_results = []
        
    def simulate_vehicle_detection(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Simulate vehicle detection using simple image processing"""
        try:
            logger.info(f"Simulating vehicle detection on frame: {frame.shape}")
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area (simulate vehicle detection)
            vehicle_boxes = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > 5000:  # Minimum area for vehicle
                    x, y, w, h = cv2.boundingRect(contour)
                    # Create vehicle box
                    vehicle_box = {
                        'bbox': [x, y, x + w, y + h],
                        'confidence': 0.8,
                        'label': f'vehicle_{i}'
                    }
                    vehicle_boxes.append(vehicle_box)
            
            logger.info(f"Simulated vehicle detection: {len(vehicle_boxes)} vehicles found")
            return vehicle_boxes
            
        except Exception as e:
            logger.error(f"Error in simulated vehicle detection: {e}")
            return []
    
    def simulate_license_plate_detection(self, frame: np.ndarray, vehicle_boxes: List[Dict] = None) -> List[Dict[str, Any]]:
        """Simulate license plate detection using simple image processing"""
        try:
            logger.info(f"Simulating license plate detection on frame: {frame.shape}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply morphological operations to find rectangular regions
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            lp_boxes = []
            
            # If vehicle boxes provided, only look within vehicle areas
            if vehicle_boxes:
                for vehicle_box in vehicle_boxes:
                    if 'bbox' in vehicle_box:
                        vx1, vy1, vx2, vy2 = vehicle_box['bbox']
                        vx1, vy1, vx2, vy2 = int(vx1), int(vy1), int(vx2), int(vy2)
                        
                        # Look for license plate-like contours within vehicle area
                        for i, contour in enumerate(contours):
                            x, y, w, h = cv2.boundingRect(contour)
                            
                            # Check if contour is within vehicle area
                            if vx1 <= x <= vx2 and vy1 <= y <= vy2:
                                # Check aspect ratio (license plates are typically rectangular)
                                aspect_ratio = w / h if h > 0 else 0
                                if 2.0 <= aspect_ratio <= 5.0 and w > 50 and h > 20:
                                    lp_box = {
                                        'bbox': [x, y, x + w, y + h],
                                        'confidence': 0.7,
                                        'label': f'license_plate_{i}'
                                    }
                                    lp_boxes.append(lp_box)
            else:
                # Look for license plate-like contours in entire frame
                for i, contour in enumerate(contours):
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio (license plates are typically rectangular)
                    aspect_ratio = w / h if h > 0 else 0
                    if 2.0 <= aspect_ratio <= 5.0 and w > 50 and h > 20:
                        lp_box = {
                            'bbox': [x, y, x + w, y + h],
                            'confidence': 0.7,
                            'label': f'license_plate_{i}'
                        }
                        lp_boxes.append(lp_box)
            
            logger.info(f"Simulated license plate detection: {len(lp_boxes)} plates found")
            return lp_boxes
            
        except Exception as e:
            logger.error(f"Error in simulated license plate detection: {e}")
            return []
    
    def simulate_ocr(self, image: np.ndarray) -> str:
        """Simulate OCR processing"""
        try:
            h, w = image.shape[:2]
            logger.info(f"Simulating OCR on image: {image.shape}")
            
            # Check size requirements
            min_width, min_height = 256, 128
            
            if w < min_width or h < min_height:
                logger.info(f"Image too small ({w}x{h}), skipping OCR")
                return ""
            
            # Resize if needed
            if w > min_width or h > min_height:
                target_size = (256, 128)
                image = cv2.resize(image, target_size)
                logger.info(f"Resized image to {target_size}")
            
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply preprocessing
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Simulate text detection (for testing purposes)
            # In real scenario, this would be Hailo OCR or EasyOCR
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 5:  # If enough contours, simulate text found
                simulated_text = "ABC123"  # Simulated license plate text
                logger.info(f"Simulated OCR result: '{simulated_text}'")
                return simulated_text
            else:
                logger.info("Simulated OCR: No text pattern found")
                return ""
            
        except Exception as e:
            logger.error(f"Error in simulated OCR: {e}")
            return ""
    
    def crop_license_plates(self, image: np.ndarray, detections: List[dict]) -> List[np.ndarray]:
        """Crop license plate regions from image"""
        try:
            cropped_plates = []
            
            for detection in detections:
                if 'bbox' in detection:
                    x1, y1, x2, y2 = detection['bbox']
                    
                    # Convert coordinates to integers
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Ensure coordinates are within image bounds
                    x1 = max(0, min(x1, image.shape[1] - 1))
                    y1 = max(0, min(y1, image.shape[0] - 1))
                    x2 = max(x1 + 1, min(x2, image.shape[1]))
                    y2 = max(y1 + 1, min(y2, image.shape[0]))
                    
                    if x2 > x1 and y2 > y1:
                        cropped = image[y1:y2, x1:x2]
                        cropped_plates.append(cropped)
            
            return cropped_plates
            
        except Exception as e:
            logger.error(f"Error in crop_license_plates: {e}")
            return []
    
    def draw_bounding_boxes(self, image: np.ndarray, detections: List[dict], 
                           color: Tuple[int, int, int] = (0, 255, 0), 
                           thickness: int = 2) -> np.ndarray:
        """Draw bounding boxes on image"""
        try:
            result_image = image.copy()
            
            for detection in detections:
                if 'bbox' in detection:
                    x1, y1, x2, y2 = detection['bbox']
                    
                    # Convert coordinates to integers
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Ensure coordinates are within image bounds
                    x1 = max(0, min(x1, image.shape[1] - 1))
                    y1 = max(0, min(y1, image.shape[0] - 1))
                    x2 = max(x1 + 1, min(x2, image.shape[1]))
                    y2 = max(y1 + 1, min(y2, image.shape[0]))
                    
                    # Draw rectangle
                    cv2.rectangle(result_image, (x1, y1), (x2, y2), color, thickness)
                    
                    # Add label if available
                    if 'label' in detection:
                        label = detection['label']
                        if 'confidence' in detection:
                            label += f" {detection['confidence']:.2f}"
                        
                        cv2.putText(result_image, label, (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            return result_image
            
        except Exception as e:
            logger.error(f"Error in draw_bounding_boxes: {e}")
            return image
    
    def test_image(self, image_path: str) -> Dict[str, Any]:
        """Test detection pipeline on a single image"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing image: {os.path.basename(image_path)}")
        logger.info(f"{'='*60}")
        
        result = {
            'image_path': image_path,
            'vehicles_detected': 0,
            'license_plates_detected': 0,
            'valid_license_plates': 0,
            'ocr_results': [],
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
            
            logger.info(f"Original image shape: {image.shape}")
            
            # Resize to detection resolution (640x640)
            detection_res = (640, 640)
            if image.shape[:2] != detection_res:
                image = cv2.resize(image, detection_res)
                logger.info(f"Resized image to {detection_res}")
            
            # Step 1: Vehicle Detection
            logger.info("\n--- Step 1: Vehicle Detection ---")
            vehicle_boxes = self.simulate_vehicle_detection(image)
            result['vehicles_detected'] = len(vehicle_boxes)
            
            if not vehicle_boxes:
                logger.info("No vehicles detected, skipping license plate detection")
                return result
            
            # Step 2: License Plate Detection
            logger.info("\n--- Step 2: License Plate Detection ---")
            lp_boxes = self.simulate_license_plate_detection(image, vehicle_boxes)
            result['license_plates_detected'] = len(lp_boxes)
            
            if not lp_boxes:
                logger.info("No license plates detected")
                return result
            
            # Step 3: Filter Valid License Plates (size check)
            logger.info("\n--- Step 3: Filter Valid License Plates ---")
            valid_lp_boxes = []
            for box in lp_boxes:
                if 'bbox' in box:
                    x1, y1, x2, y2 = box['bbox']
                    width = x2 - x1
                    height = y2 - y1
                    
                    # Check minimum size for OCR
                    if width >= 100 and height >= 50:  # Relaxed requirements for testing
                        valid_lp_boxes.append(box)
                        logger.info(f"Valid license plate: {width}x{height}")
                    else:
                        logger.warning(f"License plate too small: {width}x{height}")
            
            result['valid_license_plates'] = len(valid_lp_boxes)
            
            if not valid_lp_boxes:
                logger.info("No valid license plates found after filtering")
                return result
            
            # Step 4: OCR Processing
            logger.info("\n--- Step 4: OCR Processing ---")
            cropped_plates = self.crop_license_plates(image, valid_lp_boxes)
            
            for i, cropped_plate in enumerate(cropped_plates):
                if cropped_plate is not None and cropped_plate.size > 0:
                    logger.info(f"Processing cropped plate {i+1}: {cropped_plate.shape}")
                    
                    # Save cropped plate for inspection
                    cropped_path = f"test_cropped_plate_{i+1}_{os.path.basename(image_path)}"
                    cv2.imwrite(cropped_path, cropped_plate)
                    logger.info(f"Saved cropped plate: {cropped_path}")
                    
                    # Perform simulated OCR
                    ocr_text = self.simulate_ocr(cropped_plate)
                    
                    ocr_result = {
                        'plate_index': i+1,
                        'cropped_path': cropped_path,
                        'ocr_text': ocr_text,
                        'success': bool(ocr_text.strip())
                    }
                    
                    result['ocr_results'].append(ocr_result)
                    
                    if ocr_text.strip():
                        logger.info(f"✅ OCR Success: '{ocr_text}'")
                    else:
                        logger.warning(f"❌ OCR Failed: No text detected")
            
            # Step 5: Draw Results
            logger.info("\n--- Step 5: Draw Results ---")
            # Draw vehicle boxes (green)
            image_with_vehicles = self.draw_bounding_boxes(image, vehicle_boxes, color=(0, 255, 0), thickness=2)
            # Draw license plate boxes (red)
            image_with_all_boxes = self.draw_bounding_boxes(image_with_vehicles, valid_lp_boxes, color=(0, 0, 255), thickness=3)
            
            # Save result image
            result_path = f"test_result_{os.path.basename(image_path)}"
            cv2.imwrite(result_path, image_with_all_boxes)
            logger.info(f"Saved result image: {result_path}")
            
        except Exception as e:
            error_msg = f"Error processing image {image_path}: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def run_tests(self):
        """Run tests on all images in static/images"""
        logger.info("Starting Simple Detection Pipeline Tests")
        logger.info("="*60)
        
        # Get list of test images
        static_images_dir = 'static/images'
        if not os.path.exists(static_images_dir):
            logger.error(f"Directory not found: {static_images_dir}")
            return
        
        test_images = []
        for filename in os.listdir(static_images_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')) and not filename.startswith('.'):
                test_images.append(os.path.join(static_images_dir, filename))
        
        logger.info(f"Found {len(test_images)} test images")
        
        # Test each image
        for image_path in test_images:
            result = self.test_image(image_path)
            self.test_results.append(result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*60)
        logger.info("SIMPLE DETECTION PIPELINE TEST SUMMARY")
        logger.info("="*60)
        
        total_images = len(self.test_results)
        successful_images = len([r for r in self.test_results if not r['errors']])
        
        logger.info(f"Total images tested: {total_images}")
        logger.info(f"Successfully processed: {successful_images}")
        logger.info(f"Failed: {total_images - successful_images}")
        
        total_vehicles = sum(r['vehicles_detected'] for r in self.test_results)
        total_lp_detected = sum(r['license_plates_detected'] for r in self.test_results)
        total_valid_lp = sum(r['valid_license_plates'] for r in self.test_results)
        total_ocr_success = sum(len([ocr for ocr in r['ocr_results'] if ocr['success']]) for r in self.test_results)
        
        logger.info(f"\nDetection Results:")
        logger.info(f"  Total vehicles detected: {total_vehicles}")
        logger.info(f"  Total license plates detected: {total_lp_detected}")
        logger.info(f"  Total valid license plates: {total_valid_lp}")
        logger.info(f"  Total successful OCR: {total_ocr_success}")
        
        # Print detailed results for each image
        for i, result in enumerate(self.test_results, 1):
            logger.info(f"\nImage {i}: {os.path.basename(result['image_path'])}")
            logger.info(f"  Vehicles: {result['vehicles_detected']}")
            logger.info(f"  License Plates: {result['license_plates_detected']}")
            logger.info(f"  Valid Plates: {result['valid_license_plates']}")
            logger.info(f"  OCR Success: {len([ocr for ocr in result['ocr_results'] if ocr['success']])}")
            
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
    tester = SimpleDetectionTester()
    tester.run_tests()