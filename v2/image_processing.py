#!/usr/bin/env python3
"""
Image Processing Module for AI Camera v2
Provides image processing utilities for detection and OCR
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

def resize_with_letterbox(image: np.ndarray, target_size: Tuple[int, int], 
                         color: Tuple[int, int, int] = (114, 114, 114)) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """
    Resize image with letterbox padding to maintain aspect ratio.
    
    Args:
        image: Input image
        target_size: Target size (width, height)
        color: Padding color (B, G, R)
    
    Returns:
        resized_image: Resized image with letterbox
        scale: Scale factor
        pad: Padding (x, y)
    """
    try:
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        # Calculate scale
        scale = min(target_w / w, target_h / h)
        
        # Calculate new dimensions
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h))
        
        # Calculate padding
        pad_x = (target_w - new_w) // 2
        pad_y = (target_h - new_h) // 2
        
        # Create padded image
        padded = np.full((target_h, target_w, 3), color, dtype=np.uint8)
        padded[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized
        
        return padded, scale, (pad_x, pad_y)
        
    except Exception as e:
        logger.error(f"Error in resize_with_letterbox: {e}")
        return image, 1.0, (0, 0)

def crop_license_plates(image: np.ndarray, detections: List[dict], 
                       scale: float = 1.0, pad: Tuple[int, int] = (0, 0)) -> List[np.ndarray]:
    """
    Crop license plate regions from image based on detections.
    
    Args:
        image: Original image
        detections: List of detection dictionaries with bounding boxes
        scale: Scale factor from letterbox resize
        pad: Padding from letterbox resize
    
    Returns:
        List of cropped license plate images
    """
    try:
        cropped_plates = []
        
        for detection in detections:
            if 'bbox' in detection:
                x1, y1, x2, y2 = detection['bbox']
                
                # Convert coordinates to integers
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Convert coordinates back to original image space
                x1 = int((x1 - pad[0]) / scale)
                y1 = int((y1 - pad[1]) / scale)
                x2 = int((x2 - pad[0]) / scale)
                y2 = int((y2 - pad[1]) / scale)
                
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

def draw_bounding_boxes(image: np.ndarray, detections: List[dict], 
                       color: Tuple[int, int, int] = (0, 255, 0), 
                       thickness: int = 2) -> np.ndarray:
    """
    Draw bounding boxes on image for detections.
    
    Args:
        image: Input image
        detections: List of detection dictionaries
        color: BGR color for bounding boxes
        thickness: Line thickness
    
    Returns:
        Image with bounding boxes drawn
    """
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
                    
                    # Calculate text position
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                    text_x = x1
                    text_y = y1 - 10 if y1 > 20 else y1 + 20
                    
                    # Draw text background
                    cv2.rectangle(result_image, 
                                (text_x, text_y - text_size[1] - 5),
                                (text_x + text_size[0], text_y + 5),
                                color, -1)
                    
                    # Draw text
                    cv2.putText(result_image, label, (text_x, text_y),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return result_image
        
    except Exception as e:
        logger.error(f"Error in draw_bounding_boxes: {e}")
        return image

def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image for OCR to improve text recognition.
    
    Args:
        image: Input image
    
    Returns:
        Preprocessed image
    """
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    except Exception as e:
        logger.error(f"Error in preprocess_for_ocr: {e}")
        return image

def enhance_image_for_detection(image: np.ndarray) -> np.ndarray:
    """
    Enhance image for better detection performance.
    
    Args:
        image: Input image
    
    Returns:
        Enhanced image
    """
    try:
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Error in enhance_image_for_detection: {e}")
        return image

def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image for model input.
    
    Args:
        image: Input image
    
    Returns:
        Normalized image
    """
    try:
        # Convert to float and normalize to [0, 1]
        normalized = image.astype(np.float32) / 255.0
        return normalized
        
    except Exception as e:
        logger.error(f"Error in normalize_image: {e}")
        return image

def denormalize_image(image: np.ndarray) -> np.ndarray:
    """
    Denormalize image from [0, 1] to [0, 255].
    
    Args:
        image: Normalized image
    
    Returns:
        Denormalized image
    """
    try:
        # Convert back to uint8
        denormalized = (image * 255).astype(np.uint8)
        return denormalized
        
    except Exception as e:
        logger.error(f"Error in denormalize_image: {e}")
        return image 