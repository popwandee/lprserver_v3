# picamera.py
from picamera2 import Picamera2
import cv2

class CameraStream:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 640)}))
        self.picam2.start()

    def get_frame(self):
        frame = self.picam2.capture_array()
        return frame
    
    def close_camera(self):
        self.picam2.stop()
        self.picam2.close()
        return "OK"
