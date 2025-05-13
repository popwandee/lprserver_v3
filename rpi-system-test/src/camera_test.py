import cv2
import os
from datetime import datetime
from utils.logger import log_status

import subprocess

def list_camera_devices():
    try:
        # Use v4l2-ctl to list video devices
        result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True, check=True)
        devices_output = result.stdout.strip()

        # Parse the output into a dictionary
        devices = {}
        current_device = None
        for line in devices_output.splitlines():
            if not line.startswith("\t"):  # Device category line
                current_device = line.strip()
                devices[current_device] = []
            elif current_device:  # Device paths under the current category
                devices[current_device].append(line.strip())

        # Return the parsed devices dictionary
        return devices
    except FileNotFoundError:
        print("v4l2-ctl is not installed. Please install it using: sudo apt install v4l-utils")
        return {}
    except subprocess.CalledProcessError as e:
        print(f"Error while listing devices: {e}")
        return {}

def list_cameras():
    index = 0
    available_cameras = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
        available_cameras.append(index)
        cap.release()
        index += 1
    return available_cameras

def get_camera_properties(camera_index):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return None
    properties = {
        'width': cap.get(cv2.CAP_PROP_FRAME_WIDTH),
        'height': cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'fourcc': cap.get(cv2.CAP_PROP_FOURCC)
    }
    cap.release()
    return properties

def take_picture(camera_index, save_path):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        log_status(f"Camera {camera_index} could not be opened.")
        return False
    ret, frame = cap.read()
    if ret:
        # Add timestamp suffix to the file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(save_path)
        save_path_with_timestamp = f"{base}_{timestamp}{ext}"
        
        cv2.imwrite(save_path_with_timestamp, frame)
        log_status(f"Picture taken and saved to {save_path_with_timestamp}.")
        cap.release()
        return True
    else:
        log_status(f"Failed to take picture from camera {camera_index}.")
        cap.release()
        return False

def test_camera():
    """Tests camera functionality."""
    devices = list_camera_devices()
    if not devices:
        return "No cameras found."

    # Filter only rp1-cfe devices
    target_device = "'rp1-cfe (platform:1f00128000.csi)'"
    if target_device not in devices:
        log_status(f"Target device '{target_device}' not found.")
        return f"Target device '{target_device}' not found."

    log_status(f"Available cameras for '{target_device}': {devices[target_device]}")

    # Test each camera in the target device list recursively
    available_cameras = []
    for path in devices[target_device]:
        save_path = os.path.join(os.getcwd(), 'test_picture.jpg')
        log_status(f"Attempting to take picture from {path}...")
        if take_picture(path, save_path):
            available_cameras.append(path)
            log_status(f"Camera at {path} is available. Picture saved to {save_path}.")
        else:
            log_status(f"Camera at {path} is not available.")

    if available_cameras:
        log_status(f"Available cameras: {available_cameras}")
        return f"Available cameras: {available_cameras}"
    else:
        log_status("No valid cameras found for the target device.")
        return "No valid cameras found for the target device."

if __name__ == "__main__":
    result = test_camera()
    print(result)