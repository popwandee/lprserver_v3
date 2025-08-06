import time
from picamera2 import Picamera2
from libcamera import controls # Import controls for camera properties
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import logging
import io
import threading
import queue 
import cv2
import json
from config import (
    BASE_DIR, DEFAULT_RESOLUTION, DEFAULT_FRAMERATE, DEFAULT_BRIGHTNESS, DEFAULT_CONTRAST,
    DEFAULT_SATURATION, DEFAULT_SHARPNESS, DEFAULT_AWB_MODE
)

logger = logging.getLogger(__name__)

class CameraHandler:
    _instance = None # Singleton instance

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of CameraHandler exists (Singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super(CameraHandler, cls).__new__(cls)
            cls._instance.picam2 = None
            cls._instance.is_initialized = False
            cls._instance.configure_camera_properties = {} # To store properties for re-initialization
        return cls._instance
    
    def __init__(self, frames_queue, metadata_queue=None):
        self.frames_queue = frames_queue if frames_queue is not None else queue.Queue(maxsize=10)
        self.metadata_queue = metadata_queue if metadata_queue is not None else queue.Queue(maxsize=10)     
        self.init_lock = threading.Lock()

    def initialize_camera(self, resolution=DEFAULT_RESOLUTION, framerate=DEFAULT_FRAMERATE,
                          brightness=DEFAULT_BRIGHTNESS, contrast=DEFAULT_CONTRAST,
                          saturation=DEFAULT_SATURATION, sharpness=DEFAULT_SHARPNESS,
                          awb_mode=DEFAULT_AWB_MODE):

        """
        Initializes the Picamera2 with specified properties.
        If the camera is already initialized, it deactivates and re-initializes it.
        """
        
        with self.init_lock:
            import inspect
            caller = inspect.stack()[1].function
            logger.debug(f"initialize_camera() called by: {caller}")
            if self.is_initialized:
                logger.warning("Camera is already initialized. Skipping re-initialization.")
                return
            if self.picam2:
                logger.info("Deactivating existing camera instance for re-initialization...")
                self.picam2.stop()
                self.picam2.close()
                self.picam2 = None
                self.is_initialized = False
                time.sleep(0.5) # Give some time to release resources

            try:
                self.picam2 = Picamera2()

                # Store properties to re-apply after restart
                self.configure_camera_properties = {
                    'resolution': resolution,
                    'framerate': framerate,
                    'brightness': brightness,
                    'contrast': contrast,
                    'saturation': saturation,
                    'sharpness': sharpness,
                    'awb_mode': awb_mode
                }

                # Define the camera configuration
                main_config = {"size": resolution}
                lores_config = {"size": (640, 480)} # For efficient streaming/preview

                config = self.picam2.create_video_configuration(main=main_config, lores=lores_config, encode="lores")
                self.picam2.configure(config)

                # Apply camera controls (brightness, contrast, etc.)
                self.apply_camera_controls(
                    brightness=brightness,
                    contrast=contrast,
                    saturation=saturation,
                    sharpness=sharpness,
                    awb_mode=awb_mode
                )

                self.picam2.start()
                self.is_initialized = True
                logger.info(f"Camera initialized with resolution: {resolution}, framerate: {framerate}")
                logger.info(f"Camera controls applied: Brightness={brightness}, Contrast={contrast}, Saturation={saturation}, Sharpness={sharpness},  AWBMode={awb_mode}")

            except Exception as e:
                self.is_initialized = False
                logger.error(f"Error initializing camera: {e}")
                self.picam2 = None # Ensure picam2 is None if initialization fails

    def apply_camera_controls(self, brightness, contrast, saturation, sharpness, awb_mode):
        """Applies various camera controls."""
        if not self.picam2 or not self.picam2.is_open:
            logger.warning("Try to apply Camera control => but Camera not started, cannot apply controls.")
            return

        try:
            # Note: Not all controls might be supported by your specific camera/firmware.
            # Refer to Picamera2 documentation for supported controls and their ranges.

            # Brightness, Contrast, Saturation, Sharpness are usually set via CameraControls
            # These are typically floats between 0.0 and 1.0 (for brightness) or 0.0 and 2.0 (others)
            self.picam2.set_controls({
                "Brightness": brightness,
                "Contrast": contrast,
                "Saturation": saturation,
                "Sharpness": sharpness
            })

            

            # AWB (Auto White Balance) Mode
            awb_modes_map = {
                'auto': controls.AwbModeEnum.Auto,
                'fluorescent': controls.AwbModeEnum.Fluorescent,
                'incandescent': controls.AwbModeEnum.Incandescent,
                'tungsten': controls.AwbModeEnum.Tungsten,
                'indoor': controls.AwbModeEnum.Indoor,
                'daylight': controls.AwbModeEnum.Daylight,
                'cloudy': controls.AwbModeEnum.Cloudy,
                'custom': controls.AwbModeEnum.Custom
            }
            if awb_mode in awb_modes_map:
                self.picam2.set_controls({"AwbMode": awb_modes_map[awb_mode]})
                logger.info(f"Set AwbMode: {awb_mode}.")
            else:
                logger.warning(f"Set AwbMode, Unsupported AWB mode: {awb_mode}. Using default 'auto'.")
                self.picam2.set_controls({"AwbMode": controls.AwbModeEnum.Auto})

            logger.info("Camera controls applied successfully.")

        except Exception as e:
            logger.error(f"Error applying camera controls: {e}")

    def preset_controls(self, mode="autofocus_day"):
        """
        Set camera controls for different modes:
        - autofocus_day
        - autofocus_night
        - manualfocus_day
        - manualfocus_night
        """
        if not self.picam2:
            logger.error("Camera not initialized.")
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
                logger.warning(f"Unknown mode: {mode}")
            logger.info(f"Camera controls set for mode: {mode}")
        except Exception as e:
            logger.error(f"Failed to set camera controls: {e}")

    def generate_frames(self):
        """
        Generator function to yield JPEG frames from the camera for Flask streaming.
        Uses the lores stream for efficiency.
        """
        logger.info("Starting video stream generator.")

        while self.is_initialized and self.picam2.started:
            try:
                # 1. จับภาพและ Metadata ด้วย capture_request()
                request = self.picam2.capture_request()
                frame_np = request.make_array("main") # รับเฟรมเป็น numpy array
                metadata = request.get_metadata() # รับ metadata
                request.release()

                # 2. แปลง numpy array เป็น JPEG เพื่อส่งไปยังเบราว์เซอร์ ผ่าน yield
                is_success, buffer = cv2.imencode(".jpg", frame_np)
                if not is_success:
                    logging.error("Failed to encode frame to JPEG.")
                    continue
                frame_bytes = buffer.tobytes()

                # ส่งเฟรม JPEG ไปยัง Flask Response ,Yield the frame for Flask to stream to the browser
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes  + b'\r\n')
                
                # 3. ใส่เฟรมและ metadata ลงในคิว
                if not self.frames_queue.full():
                    self.frames_queue.put(frame_np) # ส่ง numpy array ไป detection thread
                    self.metadata_queue.put(metadata) # ส่ง metadata ไปยัง Flask thread 
                else: # กรณี queue เต็ม (ให้เอาอันเก่าออกก่อน)
                    try:
                        self.frames_queue.get_nowait()
                        self.metadata_queue.get_nowait()
                    except queue.Empty: # กรณีคิวว่าง ไม่ต้องทำอะไร
                        pass
                    finally:# ใส่ frame ล่าสุดลง queue
                        self.frames_queue.put(frame_np)
                        self.metadata_queue.put(metadata)
                time.sleep(0.03) 
            except Exception as e:
                logger.error(f"Error generating frames: {e}")
                time.sleep(1) # Wait before retrying
            finally:
                logger.info("Video stream frame generator stopped.")


    def capture_frame_and_metadata(self):
        """
        Captures a request from the camera (main stream).
        Releases the request object internally.
        Returns: (numpy.ndarray, dict) or (None, None) if an error occurs.
        """
        if not self.is_initialized or not self.picam2:
            logger.warning("Camera not initialized or started. Cannot capture request.")
            return None, None
        request = None # Initialize request to None
        try:
            # Capture a request from the main stream for higher resolution
            request = self.picam2.capture_request()
            frame = request.make_array('main') # Get the image as a NumPy array
            metadata = request.get_metadata()   # Get the metadata as a dictionary
            return frame, metadata
        except Exception as e:
            logger.error(f"Error capturing request: {e}")
            return None, None
        finally:
            if request:
                request.release() # Ensure the request is always released

    def get_latest_camera_properties(self):
        """Returns the currently configured camera properties."""
        return self.configure_camera_properties
    
    def check_camera(self):
        """Checks if the camera is initialized and streaming."""
        component = "Camera"
        try:
            # ใช้ self.picam2.started หรือ self.picam2.is_open แทน
            if self.picam2 and self.picam2.started:
                 self._log_result(component, "PASS", "Camera initialized and streaming.")
                 return True
            else:
                 self._log_result(component, "FAIL", "Camera not initialized or not started.")
                 return False
        except Exception as e:
             self._log_result(component, "FAIL", f"Camera check failed: {e}")
             return False
        
    def close_camera(self):
        """Closes the camera resources."""
        if self.picam2:
            try:
                # ตรวจสอบว่ากล้องกำลังทำงานอยู่หรือไม่ก่อนที่จะหยุด
                if self.picam2.started:
                    self.picam2.stop()
                    logger.info("Camera stopped successfully.")
                self.picam2.close()
                self.picam2 = None
                self.is_initialized = False
                logger.info("Camera resources released.")
            except Exception as e:
                logger.error(f"Error closing camera: {e}")
        else:
            logger.info("Camera is not initialized, nothing to close.")