from picamera2 import Picamera2
from libcamera import controls
import logging
import time

class CameraManager:
    def __init__(self, main_size=(640, 480), lores_size=(320, 240), display="main"):
        self.picam2 = None
        self.main_size = main_size
        self.lores_size = lores_size
        self.display = display
        self.is_configured = False

    def initialize_camera(self):
        try:
            self.picam2 = Picamera2()
            camera_config = self.picam2.create_preview_configuration(
                main={"size": self.main_size},
                lores={"size": self.lores_size},
                display=self.display
            )
            self.picam2.configure(camera_config)
            self.picam2.start()
            self.is_configured = True
            logging.info("Picamera2 initialized and started.")
        except Exception as e:
            logging.error(f"Failed to initialize Picamera2: {e}")
            self.picam2 = None
            self.is_configured = False

    def preset_controls(self, mode="autofocus_day"):
        """
        Set camera controls for different modes:
        - autofocus_day
        - autofocus_night
        - manualfocus_day
        - manualfocus_night
        """
        if not self.picam2:
            logging.error("Camera not initialized.")
            return
        try:
            if mode == "autofocus_day":
                self.picam2.set_controls({
                    "AfMode": controls.AfModeEnum.Continuous,
                    "ExposureTime": 10000,  # Example: 10ms
                    "AnalogueGain": 1.0
                })
            elif mode == "autofocus_night":
                self.picam2.set_controls({
                    "AfMode": controls.AfModeEnum.Continuous,
                    "ExposureTime": 30000,  # Example: 30ms
                    "AnalogueGain": 8.0
                })
            elif mode == "manualfocus_day":
                self.picam2.set_controls({
                    "AfMode": controls.AfModeEnum.Manual,
                    "LensPosition": 1.0,
                    "ExposureTime": 10000,
                    "AnalogueGain": 1.0
                })
            elif mode == "manualfocus_night":
                self.picam2.set_controls({
                    "AfMode": controls.AfModeEnum.Manual,
                    "LensPosition": 1.0,
                    "ExposureTime": 30000,
                    "AnalogueGain": 8.0
                })
            else:
                logging.warning(f"Unknown mode: {mode}")
            logging.info(f"Camera controls set for mode: {mode}")
        except Exception as e:
            logging.error(f"Failed to set camera controls: {e}")

    def get_request(self, stream="main"):
        """
        Capture a request from the camera and return (frame, metadata).
        stream: "main" or "lores"
        """
        if not self.picam2:
            logging.error("Try to get request but Camera not initialized.")
            return None, None
        try:
            request = self.picam2.capture_request()
            frame = request.make_array(stream)
            metadata = request.get_metadata()
            request.release()

            logging.info(f"Captured {stream} resolution stream with metadata.")
            return frame, metadata
        except Exception as e:
            logging.error(f"Failed to capture {stream} frame: {e}")
            return
        
    def test_still_image(self, output_path):
        """Capture a still image and save to output_path. Returns (frame, metadata)"""
        if not self.picam2:
            logging.error("Camera not initialized.")
            return None, None
        try:
            request = self.picam2.capture_request()
            request.save("main", output_path)
            metadata = request.get_metadata()
            request.release()
            logging.info(f"Still image captured and saved to {output_path}")
            return None, metadata  # If you want to return the frame, use: request.make_array("main")
        except Exception as e:
            logging.error(f"Failed to capture still image: {e}")
            return None, None

    def test_video_stream(self, output_path, duration=5):
        """Record a video for the given duration (seconds) and save to output_path. Returns metadata."""
        if not self.picam2:
            logging.error("Camera not initialized.")
            return None
        try:
            self.picam2.start_recording(output_path)
            logging.info(f"Started video recording to {output_path}")
            time.sleep(duration)
            self.picam2.stop_recording()
            logging.info(f"Stopped video recording to {output_path}")
            # Metadata for video is not always available; return empty dict or custom info
            return {"duration": duration, "output_path": output_path}
        except Exception as e:
            logging.error(f"Failed to record video: {e}")
            return None

    def stop_camera(self):
        if self.picam2:
            try:
                self.picam2.stop()
                self.picam2.close()
                logging.info("Picamera2 stopped and closed.")
            except Exception as e:
                logging.error(f"Error stopping camera: {e}")
            finally:
                self.picam2 = None
                self.is_configured = False

    def reset_camera(self):
        self.stop_camera()
