import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
from picamera2 import Picamera2
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
from datetime import datetime
import time

# ตั้งค่า Logging
logging.basicConfig(
    filename="logs/detections.log",
    level=logging.DEBUG, # INFO, DEBUG, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(message)s"
)
# Initialize GStreamer
Gst.init(None)

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.frame_save_path = "saved_frames"
        os.makedirs(self.frame_save_path, exist_ok=True)

    def save_frame(self, frame, count):
        filename = os.path.join(self.frame_save_path, f"frame_{count}.jpg")
        cv2.imwrite(filename, frame)
        logging.info(f"[{datetime.now()}] Saved frame: {filename}")
# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
# Debugging breakpoint
#ipdb.set_trace()
# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        logging.warning("Buffer is None")
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()
    frame_count = user_data.get_count()
    string_to_print = f"Frame count: {user_data.get_count()}\n"
    logging.info(f"Frame count [user_data.get_count()]: {user_data.get_count()}")


    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)
    logging.info(f"cas from the pad is \nFormat: {format}, Width: {width}, Height: {height}")


    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    # Get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)
        if frame is not None:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            user_data.save_frame(frame_bgr, frame_count)
            logging.info(f"Frame shape [frame.shape]: {frame.shape}")
        else:
            logging.warning("Frame is None")
    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
    print(f"Detections [len(detections)]: {len(detections)}")
    logging.info(f"[{datetime.now()}] Frame {frame_count}: {len(detections)} detections")


    # Parse (Get) the detections
    detection_count = 0
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        logging.info(f"Detection: Label={label}, Confidence={confidence:.2f}, BBox={bbox}")
        # Print the detection information
        if label == "person":
            # Get track ID
            track_id = 0
            track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            if len(track) == 1:
                track_id = track[0].get_id()
            string_to_print += (f"Detection: ID: {track_id} Label: {label} Confidence: {confidence:.2f}\n")
            print(f"Detection: ID [track_id]: {track_id} Label [label]: {label} Confidence [confidence]: {confidence:.2f}\n")
            detection_count += 1
    #ipdb.set_trace()
    if user_data.use_frame:
        # Note: using imshow will not work here, as the callback function is not running in the main thread
        # Let's print the detection count to the frame
        cv2.putText(frame, f"Detections: {detection_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Example of how to use the new_variable and new_function from the user_data
        # Let's print the new_variable and the result of the new_function to the frame
        cv2.putText(frame, f"{user_data.new_function()} {user_data.new_variable}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Convert the frame to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)

    print(string_to_print)
    return Gst.PadProbeReturn.OK
def push_frame():
    # Grab frame from picamera2
    frame = picam2.capture_array("main")
    data = frame.tobytes()
    
    # Create buffer
    buf = Gst.Buffer.new_allocate(None, len(data), None)
    success, info = buf.map(Gst.MapFlags.WRITE)
    if success:
        # memoryview ช่วยให้เขียนลง buffer ได้
        info.data = memoryview(data)
        buf.unmap(info)
    
    buf.pts = buf.dts = time.time_ns()
    buf.duration = Gst.util_uint64_scale(1, Gst.SECOND, 30)
    
    # Push buffer
    retval = appsrc.emit("push-buffer", buf)
    if retval != Gst.FlowReturn.OK:
        print("Failed to push buffer:", retval)
        loop.quit()
    return True  # continue calling


if __name__ == "__main__":
    # Initialize GStreamer
    Gst.init(None)

    # Setup Picamera2
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(video_config)
    picam2.start()

    # GStreamer pipeline
    pipeline_str = """
    appsrc name=source is-live=true block=true format=GST_FORMAT_TIME 
    caps=video/x-raw,format=RGB,width=640,height=480,framerate=30/1 
    ! videoconvert 
    ! video/x-raw,format=RGB 
    ! autovideosink
    """

    pipeline = Gst.parse_launch(pipeline_str)
    appsrc = pipeline.get_by_name("source")

    # Start pipeline
    pipeline.set_state(Gst.State.PLAYING)

    # Create a GLib MainLoop to run GStreamer in the background
    loop = GLib.MainLoop()

    # Schedule the frame push every 1/30 second
    GLib.timeout_add(int(1000 / 30), push_frame)

    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        pipeline.set_state(Gst.State.NULL)
    picam2.stop()
    picam2.close()
