import time
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
import libcamera

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

if __name__ == "__main__":
    # Capture an image with resolution 1536x864
    picam = configure_camera(size=(1536, 864))
    capture_image(picam, "test-python1536-864.jpg")

    # Capture an image with resolution 2304x1296
    picam = configure_camera(size=(2304, 1296))
    capture_image(picam, "test-python2304-1296.jpg")

    # Uncomment the following line to capture a time-lapse
    capture_timeslapse()

    # Uncomment the following line to record a video
    record_video("test.h264", duration=10)








