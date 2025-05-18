import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject

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

# === 1. Setup Picamera2 ===
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# === Detection Callback ===
def on_buffer_probe(pad, info):
    buf = info.get_buffer()
    if not buf:
        return Gst.PadProbeReturn.OK
    
    success, mapinfo = buf.map(Gst.MapFlags.READ)
    if success:
        print("Buffer size:", mapinfo.size)
        print("First 64 bytes:", mapinfo.data[:64])
        buf.unmap(mapinfo)

    # Pull metadata from buffer (encoded by hailofilter / hailotracker)
    #meta = buf.get_meta("GstVideoRegionOfInterestMeta")
    for meta in buf.iterate_meta():
        print("Meta:", meta)

    if meta:
        print("ROI Metadata found")  # Debug line
    else:
        # Optionally parse buffer with ctypes or custom logic (depends on your Hailo pipeline setup)
        logging.info("Received buffer, size=%d", buf.get_size())

    return Gst.PadProbeReturn.OK

# === 2. Setup GStreamer Pipeline ===
pipeline_str =(
"appsrc name=source is-live=true block=true format=3 caps=video/x-raw,format=BGR,width=640,height=640,framerate=30/1 !"
"videoconvert !"
"videoscale !"
"queue name=q1 !"
"hailonet name=detector hef-path=/home/camuser/hailo/resources/yolov8m.hef batch-size=1 "
"nms-score-threshold=0.4 nms-iou-threshold=0.5 output-format-type=HAILO_FORMAT_TYPE_FLOAT32 !"
"hailofilter so-path=/home/camuser/hailo/venv_hailo/lib/python3.11/site-packages/resources/libyolo_hailortpp_postprocess.so function-name=filter_letterbox !"
"identity name=identity_callback !"
"fakesink sync=false"
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
identity = pipeline.get_by_name("identity_callback")


# Add probe to identity pad for inspection
sinkpad = identity.get_static_pad("sink")
sinkpad.add_probe(Gst.PadProbeType.BUFFER, on_buffer_probe)

pipeline.set_state(Gst.State.PLAYING)

# === 3. Frame Pushing Thread ===
def push_frames():
    frame_count = 0
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # === บันทึกภาพสำหรับ debug ทุก 60 เฟรม (2 วินาที) ===
        if frame_count % 60 == 0:
            filename = f"frame_{frame_count:04d}.jpg"
            cv2.imwrite(filename, frame_bgr)
            print(f"[INFO] Saved {filename}")

        data = frame_bgr.tobytes()
        # Create GStreamer buffer and fill with image data
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)

        now = time.time_ns()
        buf.pts = buf.dts = now
        buf.duration = Gst.util_uint64_scale(1, Gst.SECOND, 30)
        
        retval = appsrc.emit("push-buffer", buf)
        if retval != Gst.FlowReturn.OK:
            print("Push buffer failed:", retval)
            break
        else:
            print(f"[INFO] Pushed frame {frame_count}")
        frame_count += 1
        time.sleep(1 / 30.0)

# === 4. Run in Thread ===
thread = threading.Thread(target=push_frames, daemon=True)
thread.start()

# === 5. GLib run Main Loop ===
loop = GLib.MainLoop()
try:
    print("[INFO] Running pipeline... Press Ctrl+C to exit.")
    loop.run()
except KeyboardInterrupt:
    print("\n[INFO] Interrupted. Cleaning up...")
    pipeline.set_state(Gst.State.NULL)
    picam2.stop()
    picam2.close()
    print("[INFO] Pipeline stopped.")