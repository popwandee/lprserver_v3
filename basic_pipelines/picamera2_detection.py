import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject

import time
import threading
import numpy as np
from picamera2 import Picamera2

# Initialize GStreamer
Gst.init(None)

# === 1. Setup Picamera2 ===
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# === 2. Setup GStreamer Pipeline ===
pipeline_str = """
appsrc name=source is-live=true block=true format=3 caps=video/x-raw,format=RGB,width=1280,height=720,framerate=30/1 !
videoconvert !
videoscale !
video/x-raw,format=RGB,width=1280,height=720 !
autovideosink sync=false
"""
pipeline = Gst.parse_launch(pipeline_str)

# Get appsrc element
appsrc = pipeline.get_by_name("source")

# Set pipeline to playing
pipeline.set_state(Gst.State.PLAYING)

# === 3. Thread to feed frames ===
def push_frames():
    while True:
        frame = picam2.capture_array()
        data = frame.tobytes()

        # Create GStreamer buffer and fill with image data
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)

        buf.pts = buf.dts = time.time_ns()
        buf.duration = Gst.util_uint64_scale(1, Gst.SECOND, 30)

        retval = appsrc.emit("push-buffer", buf)
        if retval != Gst.FlowReturn.OK:
            print("Push buffer failed:", retval)
            break

        time.sleep(1 / 30.0)  # match framerate

# Start frame pushing in background
thread = threading.Thread(target=push_frames, daemon=True)
thread.start()

# Run GLib loop (to keep GStreamer alive)
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    print("Interrupted, stopping...")
    pipeline.set_state(Gst.State.NULL)
    picam2.stop()
    picam2.close()
    loop.quit()
    print("Pipeline stopped.")
# Cleanup
pipeline.set_state(Gst.State.NULL)
picam2.stop()
picam2.close()
print("Pipeline stopped.")
# End of script
# Note: This script captures frames from the Picamera2 and pushes them to a GStreamer pipeline.
# The pipeline processes the frames and displays them using autovideosink.
# The script runs indefinitely until interrupted (e.g., Ctrl+C).
# The frame rate is set to 30 FPS, and the resolution is 1280x720.
# The GStreamer pipeline can be modified to include additional processing elements as needed.
# The script uses threading to continuously capture and push frames to the GStreamer pipeline.
# The Picamera2 library is used to interface with the camera, and GStreamer is used for video processing.