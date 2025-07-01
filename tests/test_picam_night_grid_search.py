from picamera2 import Picamera2
from libcamera import controls
import cv2
import time
import os
from datetime import datetime

# --- Configuration ---
OUTPUT_DIR = "night_full_grid_search_images"
LENS_POSITIONS = [0.0, 0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.2, 1.5]

# Parameters for Grid Search
# Exposure Time (in microseconds) - ลองช่วงที่กว้างขึ้น
EXPOSURE_TIMES = [100000, 200000, 300000, 400000, 500000, 600000, 700000] 
# Analog Gain (multiplier) - ค่าจะขึ้นอยู่กับเซ็นเซอร์, โดยทั่วไป 1.0, 2.0, 4.0, 8.0, 16.0
ANALOG_GAINS = [1.0, 2.0, 4.0, 8.0, 16.0] 

# Fixed Camera Settings
NIGHT_BRIGHTNESS = 0.0   # เริ่มต้นที่ค่ากลาง (0.0)
NIGHT_CONTRAST = 1.0     # เริ่มต้นที่ค่ากลาง (1.0)
NIGHT_SHARPNESS = 1.0    # เริ่มต้นที่ค่ากลาง (1.0)

# --- Setup Picamera2 ---
picam2 = Picamera2()
# กำหนดค่า configuration สำหรับกล้อง
# ใช้ความละเอียดที่เหมาะสมสำหรับการตรวจสอบ
camera_config = picam2.create_still_configuration(main={"size": (1280, 720)}) 
picam2.configure(camera_config)

try:
    picam2.start()
    print("Picamera2 started.")

    # ตรวจสอบและสร้างโฟลเดอร์สำหรับบันทึกภาพ
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    # --- Full Grid Search Loop ---
    print("Starting Full Grid Search for Night Time Parameters (Lens, Exposure, Gain)...")
    
    # Outer loop for Lens Position
    for lens_pos in LENS_POSITIONS:
        # Set Lens Position first for the current iteration
        try:
            picam2.set_controls({
                "AfMode": controls.AfModeEnum.Manual, 
                "LensPosition": lens_pos
            })
            print(f"\n--- Setting LensPosition to: {lens_pos:.2f} ---")
            time.sleep(1) # Give camera time to adjust focus

        except Exception as e:
            print(f"Error setting LensPosition {lens_pos:.2f}: {e}. Skipping this LensPosition.")
            continue # Skip to the next LensPosition if setting fails
    
        # Inner loops for Exposure Time and Analog Gain
        for exp_time in EXPOSURE_TIMES:
            for anal_gain in ANALOG_GAINS:
                # Apply current exposure and gain parameters
                try:
                    picam2.set_controls({
                        "AeEnable": False,               # Disable Auto Exposure for manual control
                        "ExposureTime": exp_time,
                        "AnalogueGain": anal_gain,
                        "AwbEnable": controls.AwbModeEnum.Auto.value, 
                        "Brightness": NIGHT_BRIGHTNESS,
                        "Contrast": NIGHT_CONTRAST,
                        "Sharpness": NIGHT_SHARPNESS
                    })
                    print(f"  Applying settings: Exp={exp_time}us, Gain={anal_gain}")
                    time.sleep(0.5) # Give the camera a bit of time to apply new settings

                    # Capture frame
                    frame = picam2.capture_array()
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # Add parameters text to the image
                    # Formatted for better readability on image
                    text_params_line1 = f"Lens: {lens_pos:.2f} (1/{1/lens_pos if lens_pos != 0 else 'inf'}m)"
                    text_params_line2 = f"Exp: {exp_time} us, Gain: {anal_gain:.1f}x"
                    
                    cv2.putText(frame_bgr, text_params_line1, (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA) # Green text
                    cv2.putText(frame_bgr, text_params_line2, (20, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA) # Green text

                    # Create filename based on current timestamp
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] # YYYYMMDD_HHMMSS_milliseconds
                    filename = os.path.join(OUTPUT_DIR, f"{timestamp_str}.jpg")
                    
                    cv2.imwrite(filename, frame_bgr)
                    print(f"    Saved {filename}")

                except Exception as e:
                    print(f"    Error processing Exp={exp_time}us, Gain={anal_gain}x for Lens={lens_pos:.2f}: {e}")
                    # If an error occurs, you might want to skip to the next iteration for gain/exposure
                    continue 

finally:
    picam2.stop()
    picam2.close()
    print("\nCamera stopped and closed.")
    print(f"All full grid search images saved to: {OUTPUT_DIR}")
