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
    def print_image_size(image_path):
        # Load the image
        image = cv2.imread(image_path)

        # Check if the image was loaded successfully
        if image is None:
            print(f"Error: Unable to load image from path: {image_path}")
        else:
            # Get the image size (height, width, channels)
            height, width, channels = image.shape
            print(f"Image size: {height}x{width} (Height x Width)")

    def resize_with_letterbox(image, target_shape, padding_value=(0,0,0)):
        """
        Resize an image to a target shape while maintaining the aspect ratio.
        The image is resized with letterboxing, meaning it will be padded with a specified color if necessary.
        
        :param image_path (str): Path to the input image.
        :param target_shape (tuple): Tuple (batch_size, target_height, target_width, channels) for the target size.
        :param padding_value (tuple): RGB Color values for padding in RGB format (default is black padding).

        :return: Resized image with letterboxing applied.
        letterboxed_image (numpy.ndarray): The resized image with letterboxing applied.
        scale (float): The scale factor ratio used for resizing the origial image.
        pad_top (int): The top padding applied to the image.
        pad_left (int): The left padding applied to the image.
        """
        # Load the image from the given path
        #image = cv2.imread(image_path)
        
        # Check if the image was loaded successfully
        if image is None:
            raise ValueError(f"Error: Unable to load image from path: {image}")
        else:
            print(f"Type of image is:{type(image)}")
        # Convert the image from BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Get the original image dimensions (height, width, channels)
        original_height, original_width, channels = image.shape
        
        # Extract target shape dimensions (height, width) from target_shape
        target_height, target_width = target_shape[1], target_shape[2]
        
        # Calculate the aspect ratios (Scale factors for width and height)
        original_aspect_ratio = original_width / original_height
        target_aspect_ratio = target_width / target_height

        # Choose the smaller scale factor to fit the image within the target dimensions
        # This ensures that the image fits within the target dimensions without distortion
        # and maintains the aspect ratio
        scale_factor = min(target_width / original_width, target_height / original_height)
        
        # Calculate the new dimensions of the image after scaling
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # Resize the image to the new dimensions
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Create a new image with the target shape and fill it with the padding value
        letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)
        
        # Calculate padding offsets
        offset_y = (target_height - new_height) // 2 # Padding on the top 
        offset_x = (target_width - new_width) // 2 # Padding on the left 
        
        # Place the resized image in the letterbox background
        letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image
        
        # pencv backend (default), ใช้ input (H, W, C) เท่านั้น don't add batch dimension
        #final_image = np.expand_dims(letterboxed_image, axis=0)  # Add batch dimension
        
        # return the letterboxed image with batch dimension; scaling ratio, and padding (top, left)
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        resized_image_array, scale_factor, offset_y, offset_x = self.resize_with_letterbox(image, self.vehicle_model.input_shape[0])  # image array,
        pprint(f"scale factor: {scale_factor}")
        pprint(f"resized image{len(resized_image_array)}")
    
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
