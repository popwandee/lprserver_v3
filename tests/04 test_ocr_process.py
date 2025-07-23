import cv2
from picamera2 import Picamera2
from src.ocr_process import OCRProcessor

def test_image_ocr(image_path):
    print(f"Testing OCR on image: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load image.")
        return
    ocr = OCRProcessor(lang_list=['en', 'th'])
    frame, detected_text = ocr.process_frame(image)
    print("Detected text:", detected_text)
    # Simulate detection results for rearrange_detections
    # If you have bounding box/label dicts, use them; otherwise, skip this
    # Example: [{'bbox': [0,0,10,10], 'label': detected_text}]
    rearranged = ocr.rearrange_detections([{'bbox': [0,0,10,10], 'label': detected_text}])
    print("Rearranged text:", rearranged)

def test_picamera_ocr():
    print("Testing OCR on Picamera2 frame...")
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(camera_config)
    picam2.start()
    import time
    time.sleep(2)  # Let camera warm up
    frame = picam2.capture_array()
    picam2.close()
    ocr = OCRProcessor(lang_list=['en', 'th'])
    frame, detected_text = ocr.process_frame(frame)
    print("Detected text:", detected_text)
    rearranged = ocr.rearrange_detections([{'bbox': [0,0,10,10], 'label': detected_text}])
    print("Rearranged text:", rearranged)

if __name__ == "__main__":
    test_image_ocr("../assets/ocrtest.jpg")  # Adjust path if needed
    test_picamera_ocr()