# ocr_process.py
import easyocr
import cv2

class OCRProcessor:
    def __init__(self, lang_list=['en']):
        self.reader = easyocr.Reader(lang_list, gpu=False)
        self.last_text = None

    def process_frame(self, frame):
        # Convert to RGB for EasyOCR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.reader.readtext(rgb_frame)

        # Concatenate all detected texts
        detected_text = " ".join([res[1] for res in results]).strip()

        if detected_text and detected_text != self.last_text:
            self.last_text = detected_text
            return frame, detected_text
        return None, None

