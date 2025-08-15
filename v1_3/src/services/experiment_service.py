#!/usr/bin/env python3
"""
Experiment Service for AI Camera v1.3

This service manages camera experiments and research functionality:
- Experiment configuration and execution
- Data collection and logging
- Image capture with metadata
- License plate detection and OCR
- Results analysis and reporting
- Night mode lens comparison experiments

Author: AI Camera Team
Version: 1.3.2
Date: August 10, 2025
"""

import os
import json
import csv
import cv2
import subprocess
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Use absolute imports
from v1_3.src.core.utils.logging_config import get_logger
from v1_3.src.core.config import (
    IMAGE_SAVE_DIR, LICENSE_PLATE_DETECTION_MODEL, 
    EASYOCR_LANGUAGES, HEF_MODEL_PATH, MODEL_ZOO_URL,
    EXPERIMENT_ENABLED, EXPERIMENT_RESULTS_DIR
)

logger = get_logger(__name__)


class ExperimentService:
    """
    Experiment Service for managing camera experiments and research.
    
    This service provides:
    - Experiment configuration and execution
    - Data collection and logging
    - Image capture with metadata
    - License plate detection and OCR
    - Results analysis and reporting
    - Night mode lens comparison experiments
    """
    
    def __init__(self, app_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Experiment Service.
        
        Args:
            app_config: Application configuration dictionary
        """
        self.app_config = app_config or {}
        self.results_dir = self.app_config.get("EXPERIMENT_RESULTS_DIR", EXPERIMENT_RESULTS_DIR)
        self.csv_path = os.path.join(self.results_dir, "experiment_log.csv")
        
        # Create results directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Initialize EasyOCR
        try:
            import easyocr
            self.reader = easyocr.Reader(EASYOCR_LANGUAGES)
            logger.info("EasyOCR initialized successfully")
        except ImportError:
            logger.warning("EasyOCR not available - OCR functionality will be limited")
            self.reader = None
        
        # Initialize Hailo model for license plate detection
        self.lp_detection_model = None
        try:
            import degirum as dg
            if LICENSE_PLATE_DETECTION_MODEL and HEF_MODEL_PATH:
                self.lp_detection_model = dg.load_model(
                    model_name=LICENSE_PLATE_DETECTION_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL
                )
                logger.info("License plate detection model loaded successfully")
            else:
                logger.warning("License plate detection model not configured")
        except ImportError:
            logger.warning("Degirum not available - license plate detection will be limited")
        except Exception as e:
            logger.error(f"Error loading license plate detection model: {e}")
        
        # Ensure CSV file exists
        self._ensure_csv_exists()
        
        logger.info(f"Experiment Service initialized with results directory: {self.results_dir}")
    
    def _ensure_csv_exists(self):
        """Ensure CSV log file exists with proper headers."""
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "ExperimentID", "ExperimentType", "CameraType", "LensCover", 
                    "Distance(m)", "LicenseTextCropped", "LicenseTextFull", "ConfidenceCrop", 
                    "ConfidenceFull", "SharpnessLaplacian", "BlurGaussian", "ExposureTime", 
                    "AnalogueGain", "DigitalGain", "LensPosition", "FocusFoM", "AfState", 
                    "SensorTemperature", "FrameDuration", "Lux", "ImagePath", "MetadataPath"
                ])
            logger.info(f"Created experiment log CSV: {self.csv_path}")
    
    def run_experiment_step(self, experiment_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single experiment step.
        
        Args:
            experiment_config: Configuration for the experiment step
            
        Returns:
            Dict containing experiment results
        """
        try:
            distance = experiment_config.get("distance_m")
            camera_type = experiment_config.get("camera_type")
            lens_cover = experiment_config.get("lens_cover")
            is_night_mode = experiment_config.get("is_night_mode", False)
            experiment_id = experiment_config.get("experiment_id", "unknown")
            
            logger.info(f"Starting experiment step: {camera_type} at {distance}m with {lens_cover} cover (night: {is_night_mode})")
            
            # Generate timestamp and file names
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"{timestamp}_{camera_type}_{lens_cover}_{distance}m.jpg"
            metadata_name = f"{timestamp}_{camera_type}_{lens_cover}_{distance}m.json"
            image_path = os.path.join(self.results_dir, image_name)
            metadata_path = os.path.join(self.results_dir, metadata_name)
            
            # 1. Capture image with rpicam-still
            capture_success = self._capture_image_with_metadata(
                image_path, metadata_path, experiment_config
            )
            
            if not capture_success:
                return {
                    "status": "error",
                    "error": "Failed to capture image",
                    "timestamp": timestamp
                }
            
            # 2. Extract metadata
            metadata = self._extract_metadata(metadata_path)
            
            # 3. Process image for license plate detection
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "status": "error",
                    "error": "Could not read captured image",
                    "timestamp": timestamp
                }
            
            # Detect and crop license plate
            cropped_plate_image = None
            license_plate_detected = "Failed"
            
            if self.lp_detection_model:
                try:
                    # Resize image for YOLO model
                    resized_image = self._resize_with_letterbox(image, (640, 640))
                    if resized_image is not None:
                        # Detect license plates
                        detected_plates = self.lp_detection_model(resized_image)
                        if detected_plates and detected_plates.results:
                            # Crop detected license plates
                            cropped_plates = self._crop_license_plates(image, detected_plates.results)
                            if cropped_plates:
                                cropped_plate_image = cropped_plates[0]  # Use first detected plate
                                license_plate_detected = "Good"
                except Exception as e:
                    logger.error(f"Error during license plate detection: {e}")
            
            # 4. Perform OCR on cropped and full images
            license_text_cropped = "No Plate Detected"
            license_text_full = "No Text"
            confidence_cropped = 0.0
            confidence_full = 0.0
            
            if self.reader:
                if cropped_plate_image is not None:
                    license_text_cropped, confidence_cropped = self._read_text_with_easyocr(cropped_plate_image)
                
                license_text_full, confidence_full = self._read_text_with_easyocr(image)
            
            # 5. Analyze image quality
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            sharpness_laplacian = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            
            # Calculate blur using Gaussian filter
            try:
                from skimage import filters
                blur_gaussian = filters.gaussian(gray_image, sigma=1).std()
            except ImportError:
                # Fallback blur calculation
                blur_gaussian = np.std(gray_image)
            
            # 6. Save results to CSV
            self._save_csv_row(
                timestamp, experiment_id, experiment_config.get("experiment_type", "Unknown"),
                camera_type, lens_cover, distance, license_text_cropped, license_text_full,
                confidence_cropped, confidence_full, sharpness_laplacian, blur_gaussian,
                metadata.get("ExposureTime"), metadata.get("AnalogueGain"), metadata.get("DigitalGain"),
                metadata.get("LensPosition"), metadata.get("FocusFoM"), metadata.get("AfState"),
                metadata.get("SensorTemperature"), metadata.get("FrameDuration"), metadata.get("Lux"),
                image_path, metadata_path
            )
            
            return {
                "status": "success",
                "timestamp": timestamp,
                "image_path": image_path,
                "metadata_path": metadata_path,
                "license_text_cropped": license_text_cropped,
                "license_text_full": license_text_full,
                "confidence_cropped": confidence_cropped,
                "confidence_full": confidence_full,
                "sharpness_laplacian": sharpness_laplacian,
                "blur_gaussian": blur_gaussian,
                "metadata": metadata,
                "license_plate_detected": license_plate_detected,
                "experiment_config": experiment_config
            }
            
        except Exception as e:
            logger.error(f"Error in experiment step: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
    
    def _capture_image_with_metadata(self, image_path: str, metadata_path: str, 
                                   experiment_config: Dict[str, Any]) -> bool:
        """
        Capture image using rpicam-still with metadata.
        
        Args:
            image_path: Path to save captured image
            metadata_path: Path to save metadata
            experiment_config: Experiment configuration
            
        Returns:
            bool: True if capture successful, False otherwise
        """
        try:
            cmd = [
                "rpicam-still", "-o", image_path,
                "--metadata", metadata_path, "--metadata-format", "json",
                "--timeout", "1000", "--autofocus-on-capture"
            ]
            
            # Apply night mode parameters if enabled
            if experiment_config.get("is_night_mode", False):
                exposure_time = experiment_config.get("exposure_time_us", 499989)
                analog_gain = experiment_config.get("analog_gain", 16.0)
                manual_lens_pos = experiment_config.get("lens_position", 0.07)
                sharpness_val = experiment_config.get("sharpness", 2.0)
                noise_red_mode = experiment_config.get("noise_reduction_mode", 0)
                
                cmd.extend([
                    "--exposure", str(exposure_time),
                    "--gain", str(analog_gain),
                    "--manual-focus", str(manual_lens_pos),
                    "--sharpness", str(sharpness_val),
                    "--denoise", str(noise_red_mode)
                ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Image captured successfully: {image_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"rpicam-still failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return False
    
    def _extract_metadata(self, metadata_path: str) -> Dict[str, Any]:
        """
        Extract metadata from JSON file.
        
        Args:
            metadata_path: Path to metadata JSON file
            
        Returns:
            Dict containing extracted metadata
        """
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            return {
                "ExposureTime": metadata.get("ExposureTime"),
                "AnalogueGain": metadata.get("AnalogueGain"),
                "DigitalGain": metadata.get("DigitalGain"),
                "LensPosition": metadata.get("LensPosition"),
                "FocusFoM": metadata.get("FocusFoM"),
                "AfState": metadata.get("AfState"),
                "SensorTemperature": metadata.get("SensorTemperature"),
                "FrameDuration": metadata.get("FrameDuration"),
                "Lux": metadata.get("Lux")
            }
        except FileNotFoundError:
            logger.warning(f"Metadata file not found: {metadata_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from metadata file: {metadata_path}")
            return {}
    
    def _resize_with_letterbox(self, image: np.ndarray, target_size: tuple = (640, 640)) -> Optional[np.ndarray]:
        """
        Resize image with letterbox padding for YOLO model.
        
        Args:
            image: Input image
            target_size: Target size (width, height)
            
        Returns:
            Resized image with letterbox padding
        """
        if image is None or not isinstance(image, np.ndarray):
            logger.error("Invalid image input for resize_with_letterbox")
            return None
        
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        original_height, original_width, channels = image.shape
        target_width, target_height = target_size
        
        scale_factor = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        letterboxed_image = np.full((target_height, target_width, channels), 0, dtype=np.uint8)
        
        offset_y = (target_height - new_height) // 2
        offset_x = (target_width - new_width) // 2
        letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image
        
        return letterboxed_image
    
    def _crop_license_plates(self, image: np.ndarray, results: List[Dict]) -> List[np.ndarray]:
        """
        Crop license plates from image based on detection results.
        
        Args:
            image: Input image
            results: Detection results from YOLO model
            
        Returns:
            List of cropped license plate images
        """
        cropped_images = []
        
        for result in results:
            bbox = result.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            
            x_min, y_min, x_max, y_max = map(int, bbox)
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(image.shape[1], x_max)
            y_max = min(image.shape[0], y_max)
            
            if x_min >= x_max or y_min >= y_max:
                logger.warning(f"Invalid bounding box coordinates: {bbox}")
                continue
            
            cropped_images.append(image[y_min:y_max, x_min:x_max])
        
        return cropped_images
    
    def _read_text_with_easyocr(self, img: np.ndarray) -> tuple:
        """
        Read text from image using EasyOCR.
        
        Args:
            img: Input image
            
        Returns:
            Tuple of (text, confidence)
        """
        if img is None or img.size == 0:
            return "No Image", 0.0
        
        if self.reader is None:
            return "EasyOCR not available", 0.0
        
        try:
            results = self.reader.readtext(img)
            if results:
                text = " ".join([res[1] for res in results])
                confidence = np.mean([res[2] for res in results])
                return text, confidence
            else:
                return "No Text", 0.0
        except Exception as e:
            logger.error(f"Error during EasyOCR processing: {e}")
            return "OCR Error", 0.0
    
    def _save_csv_row(self, timestamp: str, experiment_id: str, experiment_type: str,
                     camera_type: str, lens_cover: str, distance: float,
                     license_text_cropped: str, license_text_full: str,
                     confidence_cropped: float, confidence_full: float,
                     sharpness_laplacian: float, blur_gaussian: float,
                     exposure_time: Optional[float], analogue_gain: Optional[float],
                     digital_gain: Optional[float], lens_position: Optional[float],
                     focus_fom: Optional[float], af_state: Optional[str],
                     sensor_temperature: Optional[float], frame_duration: Optional[float],
                     lux: Optional[float], image_path: str, metadata_path: str):
        """
        Save experiment results to CSV file.
        
        Args:
            All experiment data to be logged
        """
        try:
            with open(self.csv_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, experiment_id, experiment_type, camera_type, lens_cover,
                    distance, license_text_cropped, license_text_full, confidence_cropped,
                    confidence_full, sharpness_laplacian, blur_gaussian, exposure_time,
                    analogue_gain, digital_gain, lens_position, focus_fom, af_state,
                    sensor_temperature, frame_duration, lux, image_path, metadata_path
                ])
        except Exception as e:
            logger.error(f"Error saving CSV row: {e}")
    
    def summarize_results(self, experiment_id: str) -> Dict[str, Any]:
        """
        Summarize experiment results from CSV.
        
        Args:
            experiment_id: ID of the experiment to summarize
            
        Returns:
            Dictionary containing summary data
        """
        try:
            results = []
            with open(self.csv_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("ExperimentID") == experiment_id:
                        results.append(row)
            
            if not results:
                return {
                    "experiment_id": experiment_id,
                    "total_records": 0,
                    "summary_by_camera_type": {},
                    "message": "No results found for this experiment"
                }
            
            summary_data = {
                "experiment_id": experiment_id,
                "total_records": len(results),
                "summary_by_camera_type": {},
                "overall_stats": {
                    "avg_sharpness": 0.0,
                    "avg_confidence_cropped": 0.0,
                    "correct_ocr_count": 0,
                    "total_ocr_attempts": 0
                }
            }
            
            # Calculate statistics by camera type
            for row in results:
                cam_type = row.get("CameraType", "N/A")
                if cam_type not in summary_data["summary_by_camera_type"]:
                    summary_data["summary_by_camera_type"][cam_type] = {
                        "correct_ocr_count": 0,
                        "total_ocr_attempts": 0,
                        "avg_sharpness": [],
                        "avg_confidence_cropped": []
                    }
                
                # Count correct OCR
                if row.get("LicenseTextCropped") == "กก 6014 อุบลราชธานี":
                    summary_data["summary_by_camera_type"][cam_type]["correct_ocr_count"] += 1
                    summary_data["overall_stats"]["correct_ocr_count"] += 1
                
                if row.get("LicenseTextCropped") != "No Plate Detected":
                    summary_data["summary_by_camera_type"][cam_type]["total_ocr_attempts"] += 1
                    summary_data["overall_stats"]["total_ocr_attempts"] += 1
                
                # Collect numerical data
                try:
                    sharpness = float(row.get("SharpnessLaplacian", 0))
                    confidence = float(row.get("ConfidenceCrop", 0))
                    
                    summary_data["summary_by_camera_type"][cam_type]["avg_sharpness"].append(sharpness)
                    summary_data["summary_by_camera_type"][cam_type]["avg_confidence_cropped"].append(confidence)
                except ValueError:
                    pass
            
            # Calculate averages
            for cam_type, data in summary_data["summary_by_camera_type"].items():
                data["avg_sharpness"] = np.mean(data["avg_sharpness"]) if data["avg_sharpness"] else 0
                data["avg_confidence_cropped"] = np.mean(data["avg_confidence_cropped"]) if data["avg_confidence_cropped"] else 0
                data["accuracy_rate"] = (data["correct_ocr_count"] / data["total_ocr_attempts"]) if data["total_ocr_attempts"] > 0 else 0
            
            # Calculate overall averages
            all_sharpness = []
            all_confidence = []
            for data in summary_data["summary_by_camera_type"].values():
                if data["avg_sharpness"] > 0:
                    all_sharpness.append(data["avg_sharpness"])
                if data["avg_confidence_cropped"] > 0:
                    all_confidence.append(data["avg_confidence_cropped"])
            
            summary_data["overall_stats"]["avg_sharpness"] = np.mean(all_sharpness) if all_sharpness else 0
            summary_data["overall_stats"]["avg_confidence_cropped"] = np.mean(all_confidence) if all_confidence else 0
            summary_data["overall_stats"]["accuracy_rate"] = (
                summary_data["overall_stats"]["correct_ocr_count"] / 
                summary_data["overall_stats"]["total_ocr_attempts"]
            ) if summary_data["overall_stats"]["total_ocr_attempts"] > 0 else 0
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Error summarizing results: {e}")
            return {
                "experiment_id": experiment_id,
                "error": str(e),
                "total_records": 0,
                "summary_by_camera_type": {}
            }
    
    def get_experiment_details(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment configuration details.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Dictionary containing experiment details
        """
        # This would typically load from a database or config file
        # For now, return a placeholder
        return {
            "experiment_id": experiment_id,
            "name": f"Experiment {experiment_id}",
            "type": "Night Mode Lens Comparison",
            "status": "completed"
        }
    
    def get_available_experiments(self) -> List[Dict[str, Any]]:
        """
        Get list of available experiments.
        
        Returns:
            List of experiment configurations
        """
        return [
            {
                "id": "night_mode_lens_comparison",
                "name": "Night Mode Lens Comparison",
                "description": "Compare lens performance in night mode",
                "parameters": {
                    "camera_types": ["IMX708", "IMX708Wide", "IMX708NoIR"],
                    "lens_covers": ["Curve", "Flat"],
                    "distances": list(range(1, 11)),  # 1-10 meters
                    "night_mode": True
                }
            },
            {
                "id": "day_mode_lens_comparison",
                "name": "Day Mode Lens Comparison",
                "description": "Compare lens performance in day mode",
                "parameters": {
                    "camera_types": ["IMX708", "IMX708Wide", "IMX708NoIR"],
                    "lens_covers": ["Curve", "Flat"],
                    "distances": list(range(1, 11)),  # 1-10 meters
                    "night_mode": False
                }
            }
        ]
