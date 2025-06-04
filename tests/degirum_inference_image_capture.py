import os
import degirum as dg
import numpy as np
import cv2
import sqlite3
from datetime import datetime
from picamera2 import Picamera2
from flask_socketio import SocketIO
from pprint import pprint

class VehicleLicensePlateDetector:
    """Handles vehicle detection, license plate detection, and OCR processing, and image saving"""

    def __init__(self, db_path="lpr_data.db", hw_location="@local", model_zoo_url="resources"):
        self.db_path = db_path 
        self.hw_location = hw_location
        self.model_zoo_url = model_zoo_url
        
        self.vehicle_model = dg.load_model(
            model_name="yolov8n_relu6_car--640x640_quant_hailort_hailo8_1",
            inference_host_address=self.hw_location,
            zoo_url=self.model_zoo_url
        )

        self.lp_detection_model = dg.load_model(
            model_name="yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1",
            inference_host_address=self.hw_location,
            zoo_url=self.model_zoo_url,
            overlay_color=[(255, 255, 0), (0, 255, 0)]
        )

        self.lp_ocr_model = dg.load_model(
            model_name="yolov8n_relu6_lp_ocr--256x128_quant_hailort_hailo8_1",
            inference_host_address=self.hw_location,
            zoo_url=self.model_zoo_url,
            output_use_regular_nms=False,
            output_confidence_threshold=0.1
        )

        self.init_database()

        self.socketio = SocketIO(cors_allowed_origins="*")
        self.should_run = True  # Control flag for loop

        @self.socketio.on("stop_detection")
        def handle_stop_detection():
            """Stop the detection process via SocketIO"""
            self.should_run = False
            print("Received stop command, shutting down...")

    def init_database(self):
        """ Create the SQLite database if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lpr_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT NOT NULL,
                image_path TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def print_image_size(image_path):

        image = cv2.imread(image_path)

        if image is None:
            print(f"Error: Unable to load image from path: {image_path}")
        else:
            height, width, channels = image.shape
            print(f"Image size: {height}x{width} (Height x Width)")

    def resize_with_letterbox(self, image, target_size=(640, 640), padding_value=(0, 0, 0)):

        if image is None or not isinstance(image, np.ndarray):
            print("Captured image is invalid!")
            return None, None, None, None
        # Convert BGR to RGB (if needed)
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        original_height, original_width, channels = image.shape
        
        target_height, target_width = target_size
        
        original_aspect_ratio = original_width / original_height
        target_aspect_ratio = target_width / target_height

        scale_factor = min(target_width / original_width, target_height / original_height)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)

        offset_y = (target_height - new_height) // 2 # Padding on the top 
        offset_x = (target_width - new_width) // 2 # Padding on the left 

        letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image

        return letterboxed_image, scale_factor, offset_y, offset_x

    def capture_image(self):
        """Capture image using Picamera2"""
        picam2 = Picamera2()
        try:
            picam2.start()
        
            image = picam2.capture_array()
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error capturing image: {e}")
            return None
        finally:
            picam2.close()
        return image_bgr

    def capture_video(self):
        """Capture frames continuously and process them in real-time"""
        picam2 = Picamera2()
        picam2.start()
        
        try:
            while True:
                frame = picam2.capture_array()  # Capture frame from stream
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to OpenCV format
                """Process a single frame (example: convert to grayscale)"""
                processed_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                
                return processed_frame
        except KeyboardInterrupt:
            print("Video capture stopped.")
        finally:
            picam2.close()

    def save_image(self, image, image_type, output_dir="lpr_images"):
        """Save an image with a timestamp-based filename"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{timestamp}_{image_type}.jpg"
        cv2.imwrite(filename, image)
        return filename

    def crop_license_plates(self, image, results):
        """Extract license plate regions from detected bounding boxes"""
        cropped_images = []

        for result in results:
            bbox = result.get("bbox")
            if not bbox or len(bbox) != 4:
                continue

            x_min, y_min, x_max, y_max = map(int, bbox)

            if x_min >= x_max or y_min >= y_max:
                print("Warning: Invalid bounding box, skipping...")
                continue

            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(image.shape[1], x_max)
            y_max = min(image.shape[0], y_max)

            cropped_images.append(image[y_min:y_max, x_min:x_max])

        return cropped_images

    def process_image(self):
        """Runs vehicle detection, license plate detection, and OCR on an image"""
        image = self.capture_image()
        if image is None or not isinstance(image, np.ndarray):
            print("Image capture failed or invalid image type!")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        resized_image_array, scale_factor, offset_y, offset_x = self.resize_with_letterbox(
            image, (self.vehicle_model.input_shape[0][1],self.vehicle_model.input_shape[0][2])
            )  

        detected_vehicles = self.vehicle_model(image)
        detected_license_plates = self.lp_detection_model(image)

        vehicle_image_path = self.save_image(detected_vehicles.image_overlay, "vehicle_detected")
        license_plate_image_path = self.save_image(detected_license_plates.image_overlay, "license_plate_detected")

        if detected_license_plates.results:
            cropped_license_plates = self.crop_license_plates(detected_license_plates.image, detected_license_plates.results)
            
            for index, cropped_plate in enumerate(cropped_license_plates):
                cropped_path = self.save_image(cropped_plate, f"cropped_plate_{index}")

                ocr_results = self.lp_ocr_model.predict(cropped_plate)
                ocr_label = self.rearrange_detections(ocr_results.results)

                self.save_to_database(ocr_label, cropped_path)

                detected_license_plates.results[index]["label"] = ocr_label

        return detected_license_plates.results

    def rearrange_detections(self, ocr_results):
        """Rearranges OCR results into a readable format"""
        if not ocr_results:
            return "Unknown"
        extracted_text = []
        for res in ocr_results:
            if isinstance(res, dict) and "label" in res:
                extracted_text.append(res["label"])  # Extract text from label
            else:
                print(f"Warning: Unexpected OCR output format: {res}")

        return "".join(extracted_text)
    
    def save_to_database(self, license_plate, image_path):
        """Stores license plate and image path in SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO lpr_data (license_plate, image_path, timestamp) VALUES (?, ?, ?)", 
                       (license_plate, image_path, timestamp))
        conn.commit()
        conn.close()
        print(f"✅ Saved to database: Plate {license_plate}, Image {image_path}")
    
    def run(self):
        """Continuous execution until user cancels"""
        print("Starting detection loop. Press Ctrl+C or send stop event via SocketIO to exit.")
        try:
            while self.should_run:
                self.process_image()
        except KeyboardInterrupt:
            print("Process manually stopped via keyboard.")
        finally:
            print("Detection system shutting down.")

def main():
    detector = VehicleLicensePlateDetector()
    detector.run()
    

if __name__ == "__main__":
    main()
