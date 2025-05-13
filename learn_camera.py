import time
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
import libcamera
from datetime import datetime
import numpy as np
import cv2

def configure_camera(size, hflip=1, vflip=1):
    """Configure the camera with the given resolution and transformations."""
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"size": size})
    config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
    picam.configure(config)
    return picam

def capture_image(picam, filename, delay=2):
    """Start the camera, wait for a delay, capture an image, and close the camera."""
    picam.start()
    time.sleep(delay)
    picam.capture_file(filename)
    picam.close()

def capture_timeslapse(interval=3, count=10):
    """Capture a series of images for a time-lapse effect."""
    picam = Picamera2()
    config = picam.create_preview_configuration()
    picam.configure(config)
    picam.start()
    for i in range(1, count + 1):
        picam.capture_file(f"timeslapse{i}.jpg")
        print(f"Captured image {i}")
        time.sleep(interval)
    picam.stop()
    picam.close()

def record_video(filename, duration=10, bitrate=10000000):
    """Record a video for a specified duration."""
    picam = Picamera2()
    video_config = picam.create_video_configuration()
    picam.configure(video_config)

    encoder = H264Encoder(bitrate)
    picam.start_recording(encoder, filename)
    print(f"Recording video: {filename}")
    time.sleep(duration)
    picam.stop_recording()
    print(f"Video recording stopped: {filename}")

def detect_and_save_changes(interval=10, threshold=0.5):
    """Detect significant changes between frames and save the image if changes exceed the threshold."""
    picam = Picamera2()
    config = picam.create_preview_configuration(main={"size": (640, 480)})
    picam.configure(config)
    picam.start()

    prev_frame = None

    try:
        while True:
            # Capture the current frame
            current_frame = picam.capture_array()
            gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Compute the absolute difference between frames
                diff = cv2.absdiff(prev_frame, gray_frame)
                non_zero_count = np.count_nonzero(diff)
                total_pixels = diff.size
                change_ratio = non_zero_count / total_pixels

                if change_ratio > threshold:
                    # Save the image with a timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"alert_{timestamp}.jpg"
                    cv2.imwrite(filename, current_frame)
                    print(f"Significant change detected! Image saved as {filename}")

            # Update the previous frame
            prev_frame = gray_frame

            # Wait for the specified interval
            for _ in range(int(interval * 10)):  # Check every 0.1 seconds
                if cv2.waitKey(100) & 0xFF == ord('q'):  # Press 'q' to quit
                    print("Detection stopped by user (q pressed).")
                    return

    except KeyboardInterrupt:
        print("Detection stopped by user (Ctrl+C).")
    finally:
        picam.stop()
        picam.close()
        cv2.destroyAll_windows()

if __name__ == "__main__":
    while True:
        print("\nSelect an option:")
        print("1. Capture an image (1536x864)")
        print("2. Capture an image (2304x1296)")
        print("3. Capture a time-lapse")
        print("4. Record a video")
        print("5. Detect and save changes")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            picam = configure_camera(size=(1536, 864))
            capture_image(picam, "test-python1536-864.jpg")
        elif choice == "2":
            picam = configure_camera(size=(2304, 1296))
            capture_image(picam, "test-python2304-1296.jpg")
        elif choice == "3":
            interval = int(input("Enter interval between frames (seconds): "))
            count = int(input("Enter number of frames: "))
            capture_timeslapse(interval=interval, count=count)
        elif choice == "4":
            filename = input("Enter filename for the video (e.g., test.h264): ")
            duration = int(input("Enter duration of the video (seconds): "))
            record_video(filename, duration=duration)
        elif choice == "5":
            interval = int(input("Enter interval between frames (seconds): "))
            threshold = float(input("Enter change detection threshold (0.0 - 1.0): "))
            detect_and_save_changes(interval=interval, threshold=threshold)
        elif choice == "6":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")








