import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
import ipdb
from hailo_apps_infra.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from hailo_apps_infra.detection_pipeline import GStreamerDetectionApp
import logging
# ตั้งค่า Logging
logging.basicConfig(
    filename="logs/detections.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.new_variable = 42  # New variable example

    def new_function(self):  # New function example
        return "The meaning of life is: "

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
# Debugging breakpoint
#ipdb.set_trace()
# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        print("Buffer is None")
        return Gst.PadProbeReturn.OK

    user_data.increment()
    frame_count = user_data.get_count()
    print(f"Frame count: {frame_count}")

    format, width, height = get_caps_from_pad(pad)
    print(f"Caps from pad => Format: {format}, Width: {width}, Height: {height}")

    frame = None
    if user_data.use_frame and format and width and height:
        frame = get_numpy_from_buffer(buffer, format, width, height)
        if frame is None:
            print("Frame is None")

    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
    print(f"Detections found: {len(detections)}")

    detection_count = 0
    log_entries = []

    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()

        if label == "person":
            track_id = 0
            track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            if len(track) == 1:
                track_id = track[0].get_id()

            detection_count += 1
            log_entries.append(
                f"Frame {frame_count} - ID: {track_id}, Label: {label}, Confidence: {confidence:.2f}, BBox: {bbox}"
            )
            print(log_entries[-1])

    if user_data.use_frame and frame is not None:
        # Annotate frame
        cv2.putText(frame, f"Detections: {detection_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"{user_data.new_function()} {user_data.new_variable}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convert RGB to BGR before saving
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Save image with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        image_filename = f"outputs/detection_{timestamp}_f{frame_count}.jpg"
        os.makedirs("outputs", exist_ok=True)
        cv2.imwrite(image_filename, bgr_frame)
        print(f"Saved image: {image_filename}")

        # Log each detection with image path
        for entry in log_entries:
            logging.info(f"{entry} | Image: {image_filename}")

        # Optionally store in user_data
        user_data.set_frame(bgr_frame)

    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    try:
        app.run()
    except Exception as e:
        print(f"Error: {e}")
