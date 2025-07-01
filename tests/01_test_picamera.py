import os
import logging
import json
from picamera2 import Picamera2, Preview
from libcamera import controls
import time
from datetime import datetime

# --- Configuration ---
LOG_FILENAME = "log/picamera2_metadata.log"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_FILENAME),
                        logging.StreamHandler()
                    ])

def capture_image_and_metadata():
    logging.info("Initializing Picamera2...")
    picam2 = None # Initialize picam2 to None

    try:
        picam2 = Picamera2()

        # Configure the camera.
        # You can adjust resolution here if needed. For Camera Module 3,
        # a good default for still capture might be the native resolution or a common one.
        # This example uses a common 4:3 aspect ratio suitable for many purposes.
        capture_config = picam2.create_still_configuration(main={"size": (1920, 1440)},
                                                          lores={"size": (640, 480)},
                                                          display="lores")
        picam2.configure(capture_config)

        # Start the camera. No preview required.
        picam2.start()
        logging.info("Camera started. Waiting for auto-exposure and auto-white-balance to settle...")

        # Give the camera a moment to settle auto-exposure and auto-white-balance
        # This can prevent overly dark or bright first images
        picam2.set_controls({"AeEnable": True, "AwbEnable": True, "FrameRate": 30.0})
        # Wait a bit longer for stabilization if needed, adjust as per your environment

        time.sleep(5) # Give it 5 seconds to settle
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        OUTPUT_FILENAME = f"img/{timestamp_str}.jpg"

        logging.info(f"Capturing image to {OUTPUT_FILENAME}...")
        # Capture the image
        request = picam2.capture_request()
        request.save("main", OUTPUT_FILENAME)
        logging.info(f"Image saved successfully to {OUTPUT_FILENAME}")

        # --- Extract and Log Metadata ---
        metadata = request.get_metadata()
        logging.info("--- Image Metadata ---")
        logging.info(json.dumps(metadata, indent=4))
        logging.info("--------------------")
        request.release()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if picam2:
            logging.info("Stopping camera...")
            picam2.stop()
            picam2.close()
            logging.info("Camera stopped and resources released.")

if __name__ == "__main__":
    capture_image_and_metadata()
