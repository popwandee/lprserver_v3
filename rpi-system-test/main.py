import sys
from src.system_info import gather_system_info
from src.camera_test import test_camera
from src.hailo_test import test_hailo_hardware
from src.object_detection import perform_object_detection
from utils.logger import log_status
import psutil

def main():
    log_status("Starting Raspberry Pi 5 system test...")

    # Gather system information
    system_info = gather_system_info()
    log_status(f"System Information: {system_info}")

    # Test camera
    camera_status = test_camera()
    log_status(f"Camera Test Status: {camera_status}")

    # Test Hailo-8 hardware
    #hailo_status = test_hailo_hardware()
    #log_status(f"Hailo-8 Test Status: {hailo_status}")

    # Perform object detection
    #detection_status = perform_object_detection()
    #log_status(f"Object Detection Status: {detection_status}")

    log_status("Raspberry Pi 5 system test completed.")
   
    for proc in psutil.process_iter(['pid', 'name', 'status', 'create_time', 'cmdline']):
        if proc.info['name'] and any(keyword in proc.info['name'].lower() for keyword in ['python', 'camera', 'hailo']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                status = proc.info['status']
                started = psutil.Process(pid).create_time()
                started_formatted = psutil.datetime.datetime.fromtimestamp(started).strftime('%Y-%m-%d-%H:%M:%S')
                cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else "N/A"
                print(f"pid {pid}, {status}, started={started_formatted}, {cmdline}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

if __name__ == "__main__":
    main()