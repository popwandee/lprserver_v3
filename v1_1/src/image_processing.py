import cv2
import numpy as np
from collections import Counter
import logging

def denoise_image_gaussian(image):
    """Reduce noise using Gaussian blur."""
    return cv2.GaussianBlur(image, (5, 5), 0)

def denoise_image(image):
    """Reduce noise using Gaussian blur."""
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

def enhance_night_image(image):
    """Improve low-light image quality."""
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    enhanced = cv2.merge((l, a, b))
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

def sharpen_image(image):
    """Enhance edges using a sharpening kernel."""
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)

def detect_rotation(image):
    """Detect rotation angle of the image using Hough Transform."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

    if lines is None:
        return 0

    angles = []
    for rho, theta in lines[:, 0]:
        angle = (theta * 180 / np.pi) - 90
        angles.append(angle)

    median_angle = np.median(angles)
    return median_angle

def is_ocr_friendly(image):
    """Check basic OCR readability conditions."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(thresh, 50, 150)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    rotated = detect_rotation(gray)
    return {
        "contrast_ok": np.mean(gray) > 60,
        "sharpness_ok": blur_score > 100,
        "angle_ok": abs(rotated) < 5
    }

def rotate_image(image, angle):
    """Rotate image around its center by the given angle."""
    angle=detect_rotation(image)
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h))

def get_dominant_color(image):
    """Return the most common color in the image (approximate)."""
    # Resize to reduce computation, convert to RGB
    small_img = cv2.resize(image, (64, 64))
    colors = small_img.reshape((-1, 3))  # Flatten pixels
    color_counts = Counter(map(tuple, colors))
    dominant = color_counts.most_common(1)[0][0]
    return dominant  # Returns (B, G, R) tuple

def preprocess_for_ocr(image):
    """
    Preprocess image to improve OCR results: 
    - Convert to grayscale
    - Increase contrast
    - Apply adaptive thresholding
    - Optionally, denoise or sharpen
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray) # Histogram equalization for contrast
    # Adaptive thresholding for varied lighting
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 31, 15)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)  # keep 3 channels for model input

def resize_with_letterbox(image, target_size=(640, 640), padding_value=(0, 0, 0)):
    """Resizes an image while maintaining aspect ratio and padding with letterbox."""
    if image is None or not isinstance(image, np.ndarray):
        logging.warning("resize_with_letterbox received Captured image is invalid input!")
        return None, None, None, None
    logging.info(f"Resizing image from shape {image.shape} to target size {target_size}")
    if len(image.shape) != 3 or image.shape[2] not in [3, 4]:
        logging.error(f"Invalid image shape: {image.shape}. Expected 3 channels (RGB/BGR) or 4 channels (RGBA).")
        return None, None, None, None
    # Force image to 3 channels (BGR) for all models
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    channels = 3
    padding_value = (0, 0, 0)
    
    original_height, original_width, channels = image.shape
    target_height, target_width = target_size

    scale_factor = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)

    offset_y = (target_height - new_height) // 2  # Padding on the top 
    offset_x = (target_width - new_width) // 2  # Padding on the left 

    letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image

    return letterboxed_image

def crop_license_plates(image, results):
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

def draw_bounding_boxes(image, results, color=(0,255,0), thickness=2):
    img = image.copy()
    for result in results:
        bbox = result.get("bbox")
        if bbox and len(bbox) == 4:
            x_min, y_min, x_max, y_max = map(int, bbox)
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, thickness)
    return img