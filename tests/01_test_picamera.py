import os
from datetime import datetime
from src.camera import CameraManager

# --- Setup Logging ---
from src.logging_config import setup_logging
setup_logging()
import logging
logging.info("เริ่มต้นโปรแกรม")

def main():
    logging.info("=== CameraManager Test Start ===")
    cam = CameraManager(main_size=(640, 480), lores_size=(320, 240), display="main")

    # Test camera initialization
    logging.info("Initializing camera...")
    cam.initialize_camera()
    if not cam.picam2:
        logging.error("Camera failed to initialize.")
        return

    # Test preset controls
    for mode in ["autofocus_day", "autofocus_night", "manualfocus_day", "manualfocus_night"]:
        logging.info(f"Setting preset controls: {mode}")
        cam.preset_controls(mode)

    # Test still image capture
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    still_path = f"img/test_still_{timestamp}.jpg"
    frame, metadata = cam.test_still_image(still_path)
    if metadata:
        logging.info(f"Still image metadata: {metadata}")
    else:
        logging.error("Failed to capture still image.")

    # Test video recording
    video_path = f"img/test_video_{timestamp}.mp4"
    video_metadata = cam.test_video_stream(video_path, duration=3)
    if video_metadata:
        logging.info(f"Video metadata: {video_metadata}")
    else:
        logging.error("Failed to record video.")

    # Test stop and reset
    logging.info("Stopping camera...")
    cam.stop_camera()
    logging.info("Resetting camera...")
    cam.reset_camera()
    logging.info("Stopping camera after reset...")
    cam.stop_camera()

    logging.info("=== CameraManager Test End ===")

if __name__ == "__main__":
    main()