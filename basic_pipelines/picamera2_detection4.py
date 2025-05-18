import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject
from datetime import datetime
import time
import threading
import numpy as np
from picamera2 import Picamera2
import cv2
import os
import logging
import ctypes

logging.basicConfig(level=logging.INFO)

# Initialize GStreamer
Gst.init(None)

# Shared frame buffer
last_frame = None

# === 1. Setup Picamera2 ===
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 640), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# === Detection Callback with Drawing and Saving ===
def on_buffer_probe(pad, info):
    global last_frame

    buf = info.get_buffer()
    if not buf:
        return Gst.PadProbeReturn.OK
    print("Buffer size:", buf.get_size())
    print("Buffer pts:", buf.pts)  # presentation timestamp
    print("Buffer dts:", buf.dts)  # decode timestamp
    print("Buffer duration:", buf.duration)
    
    logging.info(f"[BUFFER] from info.get_buffer: {buf}")
    logging.info(f"[INFO] buffer size: {buf.get_size()} bytes")
    #logging.info(f"buf properties:{buf.list_properties()}")

    logging.info(f"[PAD] from pad: {pad}")
    logging.info(f"PAD properties:{pad.list_properties()}")
    #logging.info(f"[INFO] pad size: {pad.get_size()} bytes")
    
    # Map the buffer and get detection results
    # Convert Gst.Buffer to numpy array (สมมติว่าคุณแปลงไปทำ OpenCV)
    result, mapinfo = buf.map(Gst.MapFlags.READ)
    if result:
        try:
            # Example: each detection is 7 float32: [x1, y1, x2, y2, class_id, confidence, reserved]
            float_data = np.frombuffer(mapinfo.data, dtype=np.float32)
            #frame_data = np.frombuffer(mapinfo.data, dtype=np.uint8)

            if len(float_data) % 7 == 0 and len(float_data) * 4 < 5000:  # detection เล็ก ๆ
                logging.info(f"[DETECTION] {len(float_data)//7} detections detected")
                detections = float_data.reshape(-1, 7)
                logging.info(f"[DEBUG] Buffer size: float_data length: {len(float_data)}")
                logging.info(f"[DEBUG]First 64 bytes: {float_data[:64]}")
            else:
                logging.warning(f"[WARNING] Buffer looks like raw frame data. Skipping.")
                logging.info(f"[DEBUG] Buffer size: float_data length: {len(float_data)}")
                logging.info(f"[DEBUG]First 64 bytes: {float_data[:64]}")
                logging.warning("[WARNING] Unexpected data length, cannot reshape into (-1, 7)")
                #return Gst.PadProbeReturn.OK
                return Gst.PadProbeReturn.OK
            

            # Copy the last frame for drawing
            if last_frame is not None:
                frame_copy = last_frame.copy()
                save_image = False

                for det in detections:
                    logging.info(f"det in detections: {detections}") # for debug
                    x1, y1, x2, y2, cls_id, conf, _ = det
                    if conf > 0.5:
                        save_image = True
                        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                        label = f"{int(cls_id)}:{conf:.2f}"
                        color = (0, 255, 0)

                        # Draw bounding box
                        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame_copy, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    # Save image if any detection > 0.5
                if save_image:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = f"detected_{ts}.jpg"
                    cv2.imwrite(save_path, frame_copy)
                    logging.info(f"[DETECTION] Saved image with detections: {save_path}")

        finally:
            buf.unmap(mapinfo)
        return Gst.PadProbeReturn.OK
    else:
        return Gst.PadProbeReturn.OK

# === 2. Setup GStreamer Pipeline ===
pipeline_str =(
"appsrc name=source is-live=true block=true format=3 "
"caps=video/x-raw,format=BGR,width=640,height=640,framerate=30/1 !"
"videoconvert ! videoscale ! queue name=q1 !"
"hailonet name=detector hef-path=/home/camuser/hailo/resources/yolov8m.hef batch-size=1 "
"nms-score-threshold=0.4 nms-iou-threshold=0.5 output-format-type=HAILO_FORMAT_TYPE_FLOAT32 ! identity name=identity_detection !"
"hailofilter so-path=/home/camuser/hailo/venv_hailo/lib/python3.11/site-packages/resources/libyolo_hailortpp_postprocess.so "
"function-name=filter_letterbox ! "
"identity name=identity_callback ! fakesink sync=false"
)
# autovideosink for GUI
# fakesink for headless
try:
    pipeline = Gst.parse_launch(pipeline_str)
except GLib.Error as e:
    print("GStreamer pipeline creation failed:")
    print(f"Message: {e.message}")
    print(f"Debug: {e.domain}, {e.code}")
    raise

appsrc = pipeline.get_by_name("source")
pipeline.set_state(Gst.State.PLAYING)
time.sleep(0.1) # delay 1 second
identity_detection = pipeline.get_by_name("identity_detection")

# Add probe to identity pad for inspection
if identity_detection:
    sinkpad = identity_detection.get_static_pad("sink")
    sinkpad.add_probe(Gst.PadProbeType.BUFFER, on_buffer_probe)
    logging.info("[INFO] identity_detection found in pipeline")
else:
    logging.error("[ERROR] identity_detection not found in pipeline")


identity_callback = pipeline.get_by_name("identity_callback")

# Add probe to identity pad for inspection
if identity_callback:
    sinkpad = identity_callback.get_static_pad("sink")
    sinkpad.add_probe(Gst.PadProbeType.BUFFER, on_buffer_probe)
    logging.info("[INFO] identity_callback found in pipeline")
else:
    logging.error("[ERROR] identity_callback not found in pipeline")

# === 3. Frame Pushing Thread ===
def push_frames():
    global last_frame
    frame_count = 0
    #while True:
    for frame_count in range(4): # debug 4 frames
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        last_frame = frame_bgr.copy()  # Keep the latest frame for drawing

        # === บันทึกภาพสำหรับ debug ทุก 60 เฟรม (2 วินาที) ===
        if frame_count % 60 == 0:
            filename = f"frame_{frame_count:04d}.jpg"
            cv2.imwrite(filename, frame_bgr)
            logging.info(f"[INFO] Saved {filename}")

        data = frame_bgr.tobytes()
        # Create GStreamer buffer and fill with image data
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)

        now = time.time_ns()
        buf.pts = buf.dts = now
        buf.duration = Gst.util_uint64_scale(1, Gst.SECOND, 30)
        
        retval = appsrc.emit("push-buffer", buf)
        if retval != Gst.FlowReturn.OK:
            logging.info("Push buffer failed:", retval)
            break
        else:
            logging.info(f"[INFO] Pushed frame {frame_count}")
        frame_count += 1
        time.sleep(1 / 30.0)
    # ปิด pipeline หลังส่งครบ
    pipeline.set_state(Gst.State.NULL)
    loop.quit()
# === 4. Run in Thread ===
thread = threading.Thread(target=push_frames, daemon=True)
thread.start()

# === 5. GLib run Main Loop ===
loop = GLib.MainLoop()
try:
    logging.info("[INFO] Running pipeline... Press Ctrl+C to exit.")
    loop.run()
except KeyboardInterrupt:
    logging.info("\n[INFO] Interrupted. Cleaning up...")
    pipeline.set_state(Gst.State.NULL)
    picam2.stop()
    picam2.close()
    logging.info("[INFO] Pipeline stopped.")