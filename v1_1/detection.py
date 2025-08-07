import threading
import time
import cv2
import os
import numpy as np
import degirum as dg
from flask import Flask, Response
from dotenv import load_dotenv
from datetime import datetime
from src.camera import CameraManager
from src.image_processing import (
    preprocess_for_ocr, resize_with_letterbox, crop_license_plates, draw_bounding_boxes
)
from src.ocr_process import OCRProcessor
from src.similarity import similar, compare_images
from src.database import DatabaseManager
from src.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

# --- Flask App for Video Streaming ---
app = Flask(__name__)
frame_lock = threading.Lock()
global_frame = None

env_path = os.path.join(os.path.dirname(__file__), 'src', '.env.production')
load_dotenv(env_path)

def flask_video_stream():
    """Flask video stream generator."""
    global global_frame
    while True:
        with frame_lock:
            if global_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', global_frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    """Route for video streaming."""
    return Response(flask_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask():
    app.run(host='0.0.0.0', port=5000, threaded=True)

# --- Object Detection Thread ---
class DetectionThread(threading.Thread):
    def __init__(self, cam_manager, db_manager, ocr_processor, vehicle_model, lp_detection_model, lp_ocr_model):
        super().__init__()
        self.cam_manager = cam_manager
        self.db_manager = db_manager
        self.ocr = ocr_processor
        self.vehicle_model = vehicle_model
        self.lp_detection_model = lp_detection_model
        self.lp_ocr_model = lp_ocr_model
        self.should_run = True
        self.prev_ocr_label = None
        self.prev_plate_image = None

    def run(self):
        global global_frame
        logger.info("Object detection thread started")
        while self.should_run:
            try:
                frame, metadata = self.cam_manager.get_request("main") # 'main' Or 'lores' for low resolution
                if frame is None:
                    logger.error("Failed to get frame from camera.")
                    time.sleep(0.1)
                    continue
                logging.debug(f'Captured frame with shape: {frame.shape}, metadata: {metadata}')

                # Convert to BGR if your model expects it (OpenCV default is BGR)
                # picamera2's default format might be RGB, depending on configuration
                #if frame.shape[2] == 4:  # BGRA/RGBA
                #    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                #elif frame.shape[2] == 3:
                #    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                #else:
                #    frame_bgr = frame # Assuming it's already BGR or grayscale
                logging.debug(f'Frame converted to BGR with shape: {frame.shape}')
                logging.debug(f'frame_bgr dtype: {frame.dtype}, min: {np.min(frame)}, max: {np.max(frame)}')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_dir = "output"
                os.makedirs(base_dir, exist_ok=True)
                frame_path = os.path.join(base_dir, f"frame_{timestamp}.jpg")
                cv2.imwrite(frame_path, frame) #สีเพี้ยน
                
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # สีปกติของ OpenCV คือ BGR
                frame_bgr_path = os.path.join(base_dir, f"frame_bgr_{timestamp}.jpg")
                cv2.imwrite(frame_bgr_path, frame_bgr)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)# สีปกติ
                frame_rgb_path = os.path.join(base_dir, f"frame_rgb_{timestamp}.jpg")
                cv2.imwrite(frame_rgb_path, frame_rgb)
                # Perform object detection on frame_bgr
                # 1. Vehicle Detection
                resized = resize_with_letterbox(frame, (self.vehicle_model.input_shape[0][1], self.vehicle_model.input_shape[0][2]))
                vehicle_results = self.vehicle_model(resized)
                vehicle_boxes = getattr(vehicle_results, "results", [])

                # Draw vehicle bounding boxes
                frame_with_vehicles = draw_bounding_boxes(frame, vehicle_boxes, color=(0,255,0), thickness=2)

                # 2. License Plate Detection (on each vehicle)
                lp_boxes = []
                for vbox in vehicle_boxes:
                    v_crop = crop_license_plates(frame, [vbox])
                    if not v_crop or v_crop[0] is None:
                        continue
                    if v_crop[0].shape[2] == 4:
                        v_crop_bgr = cv2.cvtColor(v_crop[0], cv2.COLOR_BGRA2BGR)
                    else:
                        v_crop_bgr = v_crop[0]
                    lp_results = self.lp_detection_model(resize_with_letterbox(v_crop_bgr, (self.lp_detection_model.input_shape[0][1], self.lp_detection_model.input_shape[0][2])))
                    lp_boxes += getattr(lp_results, "results", [])

                frame_with_lp = draw_bounding_boxes(frame_with_vehicles, lp_boxes, color=(0,0,255), thickness=2)

                # 3. OCR on each license plate
                for idx, lp_box in enumerate(lp_boxes):
                    lp_crop = crop_license_plates(frame, [lp_box])
                    if not lp_crop or lp_crop[0] is None:
                        continue

                    # Preprocess for OCR
                    processed_lp = preprocess_for_ocr(lp_crop[0])
                    ocr_text = self.ocr.process_frame(processed_lp)[1]

                    # Similarity check
                    text_sim = similar(ocr_text, self.prev_ocr_label) if self.prev_ocr_label else 0
                    img_sim = compare_images(lp_crop[0], self.prev_plate_image) if self.prev_plate_image is not None else 0

                    if text_sim > 0.85 or img_sim > 0.90:
                        logger.info("Duplicate plate detected, skipping.")
                        continue

                    # Save images
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_dir = "output"
                    os.makedirs(base_dir, exist_ok=True)
                    orig_path = os.path.join(base_dir, f"orig_{timestamp}.jpg")
                    veh_path = os.path.join(base_dir, f"vehicle_{timestamp}.jpg")
                    lp_path = os.path.join(base_dir, f"lp_{timestamp}_{idx}.jpg")
                    cv2.imwrite(orig_path, frame)
                    cv2.imwrite(veh_path, frame_with_vehicles)
                    cv2.imwrite(lp_path, lp_crop[0])

                    # Save to DB
                    self.db_manager.save_to_database(
                        license_plate=ocr_text,
                        vehicle_image_path=veh_path,
                        license_plate_image_path=lp_path,
                        cropped_image_path=lp_path,
                        timestamp=timestamp,
                        location="",
                        hostname=os.uname().nodename if hasattr(os, "uname") else ""
                    )
                    logger.info(f"OCR: {ocr_text} | Saved images and DB record.")

                    self.prev_ocr_label = ocr_text
                    self.prev_plate_image = lp_crop[0]  

                # Update global frame for streaming
                with frame_lock:
                    global_frame = frame_with_lp

                time.sleep(0.05)
            except Exception as e:
                logger.error(f"Error getting frame from camera: {e}")
                time.sleep(0.1)
                continue

def main():
    # Camera setup
    cam_manager = CameraManager(main_size=(640, 640), lores_size=(320, 240), display="main")
    cam_manager.initialize_camera()

    # Model & OCR setup
    vehicle_model = dg.load_model(
        model_name=os.getenv("VEHICLE_DETECTION_MODEL"),
        inference_host_address=os.getenv("HEF_MODEL_PATH"),
        zoo_url=os.getenv("MODEL_ZOO_URL")
    )

    lp_detection_model = dg.load_model(
        model_name=os.getenv("LICENSE_PLACE_DETECTION_MODEL"),
        inference_host_address=os.getenv("HEF_MODEL_PATH"),
        zoo_url=os.getenv("MODEL_ZOO_URL"),
        overlay_color=[(255, 255, 0), (0, 255, 0)]
    )

    lp_ocr_model = dg.load_model(
        model_name=os.getenv("LICENSE_PLACE_OCR_MODEL"),
        inference_host_address=os.getenv("HEF_MODEL_PATH"),
        zoo_url=os.getenv("MODEL_ZOO_URL"),
        output_use_regular_nms=False,
        output_confidence_threshold=0.1
    )
    ocr_processor = OCRProcessor(lang_list=['en', 'th'])
    db_manager = DatabaseManager()

    # Start detection thread
    detection_thread = DetectionThread(
        cam_manager, db_manager, ocr_processor, vehicle_model, lp_detection_model, lp_ocr_model
    )
    detection_thread.start()
    try:
        # Start Flask video stream (main thread)
        start_flask()
    except KeyboardInterrupt:
        logger.info("User requested shutdown (KeyboardInterrupt).")
    finally:
        # Cleanup
        detection_thread.should_run = False # สั่งให้ detection thread หยุด
        detection_thread.join() # รอ thread จบ
        cam_manager.stop_camera() # ปิดกล้อง 
        logger.info("System shutdown complete.")

if __name__ == "__main__":
    main()