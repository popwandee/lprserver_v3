# ocr_process.py
import cv2
import easyocr

class OCRProcessor:
    def __init__(self, lang_list=None):
        self.lang_list = lang_list if lang_list else ['en','th']
        self.reader = easyocr.Reader(self.lang_list)
        self.last_text = ""
    def process_frame(self, frame):
        try:
            # Convert to RGB for EasyOCR
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.reader.readtext(rgb_frame)

            # Concatenate all detected texts
            detected_text = " ".join([res[1] for res in results]).strip()

            if detected_text and detected_text != self.last_text:
                self.last_text = detected_text
                return frame, detected_text
        except Exception as e:
            print("Error in ocr_process.py class OCRProcessor def process_frame:", e)
            return None, None

    def rearrange_detections(self, ocr_results):
        """Rearranges OCR detection results into a single string for a readable format"""
        if not ocr_results:
            return "Unknown"
        extracted_text = []
        sorted_results = sorted(ocr_results, key=lambda x: x.get("bbox", [0])[0] if isinstance(x, dict) and "bbox" in x else 0)
        for res in sorted_results:
            if isinstance(res, dict) and "label" in res:
                extracted_text.append(res["label"])
        return "".join(extracted_text)