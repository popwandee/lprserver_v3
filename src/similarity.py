import cv2
import logging
from difflib import SequenceMatcher
from skimage.metrics import structural_similarity as ssim
import numpy as np

"""
    ตัวอย่างการเรียกใช้ใน main script
    from src.similarity import compare_images, ssim_similarity, similar

    # เปรียบเทียบภาพสองเฟรม
    similarity_score = ssim_similarity(frame1, frame2)
    if similarity_score < 0.95:
        print("Detected movement or change in the scene!")

    # เปรียบเทียบข้อความ
    text_score = similar("ABC123", "ABC124")
"""

def ssim_similarity(img1, img2):
    """
    Compare two images using Structural Similarity Index (SSIM).
    Returns a similarity ratio (0-1).
    """
    if img1 is None or img2 is None:
        return 0
    try:
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        img1_gray = cv2.resize(img1_gray, (128, 128))
        img2_gray = cv2.resize(img2_gray, (128, 128))
        score, _ = ssim(img1_gray, img2_gray, full=True)
        return score
    except Exception as e:
        logging.error(f"Error in SSIM comparison: {e}")
        return 0
    
def compare_images(img1, img2):
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

def similar(a, b):
    """Return a similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()