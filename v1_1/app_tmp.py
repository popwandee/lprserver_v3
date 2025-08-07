import io
import time
import picamera2
import libcamera
from flask import Flask, render_template, Response, request, jsonify
import threading
import cv2
from datetime import datetime
import numpy as np

app = Flask(__name__)

# Global variable to hold the Picamera2 instance and camera status
camera = None
camera_in_use = False
camera_lock = threading.Lock() # To protect access to camera_in_use and camera instance

# Store current camera settings (optional, for display purposes)
current_settings = {
    "brightness": 0.0,
    "contrast": 1.0,
    "sharpness": 1.0,
    "exposure_mode": "auto", # 'auto', 'manual'
    "shutter_speed": 0,      # In microseconds, 0 for auto
    "focus_mode": "auto",    # 'auto', 'manual'
    "lens_position": 0.0,    # For manual focus, 0.0 for infinity
    "awb_mode": "auto",      # Auto White Balance mode
    "framerate": 30.0        # Max framerate, actual might be lower
}
# --- Camera Initialization and Streaming Functions ---

def initialize_camera():
    global camera, camera_in_use
    with camera_lock:
        if camera_in_use:
            print("Camera is already in use.")
            return False
        try:
            # Check if a camera is available and not being used by another process
            # This is a bit tricky with picamera2 as it tries to acquire the camera.
            # The error handling below is the primary way to check if it's already in use.

            camera = picamera2.Picamera2()
            
            # Configure the camera. You might want to adjust resolution, framerate, etc.
            # For streaming, a lower resolution might be better for performance.
            # Use 'lores' stream for efficient web streaming, 'main' for higher quality processing if needed
            camera_config = camera.create_still_configuration(
                main={"size": (1280, 720)}, # Or (640, 480) for lower bandwidth
                lores={"size": (640, 640)}, # 640x640 สำหรับ AI model
                display="lores"
            )
            camera.configure(camera_config)

            # Apply initial settings if available, or default to auto
            #apply_camera_settings(initial_setup=True) # Apply current_settings after initial configure
            
            # Start the camera preview/capture
            camera.start()
            print("Camera initialized and started.")
            camera_in_use = True
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            if "Camera is in use" in str(e) or "device or resource busy" in str(e).lower():
                print("Camera is likely already in use by another application.")
            camera = None
            camera_in_use = False
            return False

def stop_camera():
    global camera, camera_in_use
    with camera_lock:
        if camera and camera_in_use:
            try:
                camera.stop()
                camera.close()
                print("Camera stopped and closed.")
            except Exception as e:
                print(f"Error stopping camera: {e}")
            finally:
                camera = None
                camera_in_use = False
def apply_camera_settings(initial_setup=False):
    global camera, current_settings
    with camera_lock:
        if not camera:
            print("Camera not available to apply settings.")
            return

        controls = {}

        # Brightness (range -1.0 to 1.0)
        controls["Brightness"] = current_settings["brightness"]

        # Contrast (range 0.0 to approx 2.0 or 4.0, default 1.0)
        controls["Contrast"] = current_settings["contrast"]
        
        # Sharpness (range 0.0 to 4.0, default 1.0)
        controls["Sharpness"] = current_settings["sharpness"]

        # Exposure Mode (Auto vs. Manual Shutter Speed)
        if current_settings["exposure_mode"] == "manual":
            # Set Auto Exposure (AE) to Off, then apply ShutterSpeed
            controls["AeEnable"] = False
            controls["ExposureTime"] = int(current_settings["shutter_speed"]) # microsec
        else: # auto
            controls["AeEnable"] = True
            # When in auto mode, ExposureTime should ideally not be set or set to 0.
            # picamera2 automatically handles it when AeEnable is True.
            
        # Focus Mode (Auto vs. Manual)
        if hasattr(libcamera, "controls") and hasattr(libcamera.controls, "AfMode"):
            if current_settings["focus_mode"] == "manual":
                controls["AfMode"] = libcamera.controls.AfModeEnum.Manual
                controls["LensPosition"] = float(current_settings["lens_position"])
            else: # auto
                controls["AfMode"] = libcamera.controls.AfModeEnum.Auto
                # Trigger an auto focus scan if AF is enabled and not already running
                if camera.get_control("AfState") != libcamera.controls.AfStateEnum.Scanning:
                    controls["AfTrigger"] = libcamera.controls.AfTriggerEnum.Start
        else:
            print("Warning: Focus controls not available or not detected for this camera.")
            
        # White Balance
        # Not directly by current_settings["awb_mode"] as it's a string.
        # picamera2 has specific AWB modes in libcamera.controls.AwbModeEnum
        if hasattr(libcamera, "controls") and hasattr(libcamera.controls, "AwbMode"):
            if current_settings["awb_mode"] == "auto":
                controls["AwbMode"] = libcamera.controls.AwbModeEnum.Auto
            elif current_settings["awb_mode"] == "incandescent":
                controls["AwbMode"] = libcamera.controls.AwbModeEnum.Incandescent
            elif current_settings["awb_mode"] == "fluorescent":
                controls["AwbMode"] = libcamera.controls.AwbModeEnum.Fluorescent
            elif current_settings["awb_mode"] == "tungsten": # Often similar to Incandescent
                controls["AwbMode"] = libcamera.controls.AwbModeEnum.Tungsten
            elif current_settings["awb_mode"] == "daylight":
                controls["AwbMode"] = libcamera.controls.AwbModeEnum.Daylight
            elif current_settings["awb_mode"] == "cloudy":
                controls["AwbMode"] = libcamera.controls.AwbModeEnum.Cloudy
            else:
                print(f"Warning: Unknown AWB mode: {current_settings['awb_mode']}")
        else:
            print("Warning: AWB controls not available or not detected for this camera.")


        # Framerate - applied via stream configuration. 
        # For dynamic changes, you might need to re-configure the camera.
        # This example primarily sets it during initial config or on reconfigure.
        # It's generally better to set framerate during initial camera.configure().
        # However, for live adjustment, you can try setting FrameRate.
        if hasattr(libcamera, "controls") and hasattr(libcamera.controls, "FrameRate"):
            controls["FrameRate"] = float(current_settings["framerate"])
        
        try:
            camera.set_controls(controls)
            print(f"Applied camera controls: {controls}")
        except Exception as e:
            print(f"Failed to apply some camera controls: {e}")


def generate_frames():
    global camera, camera_in_use
    with camera_lock:
        if not camera or not camera_in_use:
            print("Camera not available for streaming. Attempting to initialize.")
            if not initialize_camera():
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n'
                       b'Error: Camera not available or in use.\r\n\r\n')
                return

    while True:
        with camera_lock: # Protect camera access during frame capture
            if not camera or not camera_in_use:
                print("Camera was unexpectedly stopped during streaming.")
                break # Exit the loop if camera is no longer active

            try:
                # Capture a frame from the 'lores' stream if configured, otherwise 'main'
                # Use array=True to get a NumPy array directly
                frame_np = camera.capture_array("lores") # Capture from lores stream for efficiency
                # --- DEBUGGING STEP: Print the shape and number of dimensions ---
                print(f"Captured frame_np shape: {frame_np.shape}, ndim: {frame_np.ndim}")

                # Convert to BGR for OpenCV
                #if frame_np.ndim == 3: # Check if it's a 3-channel image (like RGB or BGR)
                    # Assume it's RGB from picamera2's capture_array if it's 3-channel
                #    frame = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                #elif frame_np.ndim == 2: # Check if it's a 2-channel (grayscale) image
                #    frame = cv2.cvtColor(frame_np, cv2.COLOR_GRAY2BGR)
                #else:
                #    print(f"Warning: Unexpected frame_np dimensions: {frame_np.ndim}. Attempting direct conversion.")
                    # Fallback for unexpected formats, might still fail
                #    frame = cv2.cvtColor(frame_np, cv2.COLOR_YUV420p2BGR) # Or other formats you expect
                frame = frame_np

                # Add timestamp to the frame
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Milliseconds
                
                # Dynamic text color based on background (simple example)
                # If image is generally dark, use white text; if bright, use black.
                avg_pixel_val = np.mean(frame)
                text_color = (0, 255, 0) # Green by default
                if avg_pixel_val < 100: # Dark image
                    text_color = (255, 255, 255) # White
                elif avg_pixel_val > 200: # Bright image
                    text_color = (0, 0, 0) # Black

                cv2.putText(frame, now, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2, cv2.LINE_AA)

                # Encode back to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    print("Failed to encode frame to JPEG.")
                    continue
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                # No time.sleep() here, as picamera2 typically operates at its configured framerate
                # Adding sleep might reduce actual framerate below what's configured.

            except Exception as e:
                print(f"Error capturing/processing frame: {e}")
                if "Camera has been closed" in str(e) or "device or resource busy" in str(e).lower():
                    print("Camera likely disconnected or taken over by another process.")
                    stop_camera() # Attempt to clean up
                    break # Exit streaming loop
                break # Exit the loop on other errors

# --- Flask Routes ---

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html', current_settings=current_settings)

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Supplies frames to the img src."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_status')
def camera_status():
    global camera_in_use
    with camera_lock:
        status = "in_use" if camera_in_use else "available"
        return {"status": status}

@app.route('/start_camera')
def start_camera_route():
    if initialize_camera():
        return jsonify({"message": "Camera started successfully."})
    else:
        return jsonify({"message": "Failed to start camera. It might be in use or an error occurred."}), 500

@app.route('/stop_camera')
def stop_camera_route():
    stop_camera()
    return jsonify({"message": "Camera stopped."})

@app.route('/apply_settings', methods=['POST'])
def apply_settings_route():
    global current_settings
    data = request.json
    
    # Update current_settings with received data
    for key, value in data.items():
        if key in current_settings:
            # Type conversion based on expected type
            if isinstance(current_settings[key], float):
                current_settings[key] = float(value)
            elif isinstance(current_settings[key], int):
                current_settings[key] = int(value)
            elif isinstance(current_settings[key], str):
                current_settings[key] = str(value)
        else:
            print(f"Warning: Unknown setting received: {key}")

    print(f"Received settings: {data}")
    apply_camera_settings() # Apply the new settings to the camera

    return jsonify({"message": "Settings applied successfully.", "new_settings": current_settings})

@app.route('/get_settings')
def get_settings_route():
    global current_settings
    # Optionally, read actual current settings from camera if available and supported
    # For now, return the internal state
    return jsonify(current_settings)


if __name__ == '__main__':
    # Attempt to initialize camera on startup
    initialize_camera()
    
    # Run the Flask app
    # host='0.0.0.0' makes it accessible from other devices on the network
    # debug=True allows for auto-reloading during development (remove for production)
    app.run(host='0.0.0.0', port=5000, debug=False) # Set debug to False for production

    # Ensure camera is stopped when the Flask app exits
    stop_camera()