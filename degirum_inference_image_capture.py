import os
import degirum as dg
import numpy as np
import cv2
import sqlite3
from datetime import datetime
from picamera2 import Picamera2
from flask_socketio import SocketIO

class VehicleLicensePlateDetector:
    """Handles vehicle detection, license plate detection, and OCR processing, and image saving"""

    def __init__(self, db_path="lpr_data.db", hw_location="@local", model_zoo_url="resources"):
        self.db_path = db_path 
        self.hw_location = hw_location
        self.model_zoo_url = model_zoo_url
        
        # Load models
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
        # Initialize SQLite database
        self.init_database()

        # SocketIO Setup
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        detected_vehicles = self.vehicle_model(image)
        detected_license_plates = self.lp_detection_model(image)

        # Save detected images
        vehicle_image_path = self.save_image(detected_vehicles.image_overlay, "vehicle_detected")
        license_plate_image_path = self.save_image(detected_license_plates.image_overlay, "license_plate_detected")

        if detected_license_plates.results:
            cropped_license_plates = self.crop_license_plates(detected_license_plates.image, detected_license_plates.results)
            
            for index, cropped_plate in enumerate(cropped_license_plates):
                 # Save cropped image
                cropped_path = self.save_image(cropped_plate, f"cropped_plate_{index}")

                # Perform OCR
                ocr_results = self.lp_ocr_model.predict(cropped_plate)
                ocr_label = self.rearrange_detections(ocr_results.results)
                # Save to database
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
