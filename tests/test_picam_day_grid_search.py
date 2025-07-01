from picamera2 import Picamera2
from libcamera import controls
import cv2
import time
import os
from datetime import datetime
import csv # For logging to CSV

# --- Configuration ---
OUTPUT_DIR = "full_grid_search_images_v5" # Changed output directory name again for clarity
LOG_FILE = os.path.join(OUTPUT_DIR, "full_grid_search_log_v5.csv")

# --- Grid Search Parameters ---

# 1. Auto Focus Modes and Parameters
AF_SETTINGS = [
    {"mode": controls.AfModeEnum.Auto.value, "range": controls.AfRangeEnum.Normal.value, "speed": None},
    {"mode": controls.AfModeEnum.Auto.value, "range": controls.AfRangeEnum.Macro.value, "speed": None},
    {"mode": controls.AfModeEnum.Auto.value, "range": controls.AfRangeEnum.Full.value, "speed": None},

    {"mode": controls.AfModeEnum.Continuous.value, "range": controls.AfRangeEnum.Normal.value, "speed": controls.AfSpeedEnum.Fast.value},
    {"mode": controls.AfModeEnum.Continuous.value, "range": controls.AfRangeEnum.Normal.value, "speed": controls.AfSpeedEnum.Normal.value},
]

# 2. Manual Focus Lens Positions (Dioptres)
LENS_POSITIONS_MANUAL = [
    0.0, 0.05, 0.06, 0.07, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7
]

# 3. Sharpness
SHARPNESS_VALUES = [0.0, 1.0, 2.0]

# 4. Noise Reduction Mode
# Using common integer values for NoiseReductionMode
# If these also cause "not advertised" errors, then control might not be available.
NOISE_REDUCTION_MODES_TEST = [
    0, # Typically "Off"
    1, # Typically "Fast" or "Low Quality"
    2  # Typically "High Quality"
]

# --- Other Fixed Camera Settings (Daytime Defaults) ---
AE_ENABLE = True
AWB_ENABLE = controls.AwbModeEnum.Auto.value
BRIGHTNESS = 0.0
CONTRAST = 1.0

# --- Setup Picamera2 ---
picam2 = Picamera2()
camera_config = picam2.create_still_configuration()
picam2.configure(camera_config)

try:
    picam2.start()
    print("Picamera2 started.")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    fieldnames = [
        'timestamp', 'filename', 'focus_mode', 'af_range', 'af_speed',
        'lens_position_requested', 'lens_position_actual', 'sharpness_requested',
        'exposure_time_us_actual', 'analog_gain_actual',
        'brightness_actual', 'contrast_actual', 'noise_reduction_mode_requested'
    ]
    
    with open(LOG_FILE, 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()

        print(f"Starting Full Grid Search. Logs will be saved to: {LOG_FILE}")
        
        # --- Grid Search Loop for AF Modes ---
        for af_setting in AF_SETTINGS:
            current_af_mode = af_setting["mode"]
            current_af_range = af_setting["range"]
            current_af_speed = af_setting["speed"]

            for sharpness in SHARPNESS_VALUES:
                for noise_red_mode in NOISE_REDUCTION_MODES_TEST:
                    try:
                        controls_to_set = {
                            "AeEnable": AE_ENABLE,
                            "AwbEnable": AWB_ENABLE,
                            "Sharpness": sharpness,
                            "Brightness": BRIGHTNESS,
                            "Contrast": CONTRAST,
                            "AfMode": current_af_mode,
                            "AfRange": current_af_range,
                        }
                        
                        # Try to set NoiseReductionMode using integer values
                        if noise_red_mode is not None:
                            try:
                                controls_to_set["NoiseReductionMode"] = noise_red_mode # Changed key here
                            except Exception as nre:
                                print(f"Warning: Could not set NoiseReductionMode={noise_red_mode}: {nre}")
                                controls_to_set["NoiseReductionMode"] = "UNSUPPORTED" # Mark as unsupported for logging
                                

                        if current_af_mode == controls.AfModeEnum.Continuous.value and current_af_speed is not None:
                            controls_to_set["AfSpeed"] = current_af_speed
                        
                        picam2.set_controls(controls_to_set)
                        
                        settle_time = 2.5 if current_af_mode in [controls.AfModeEnum.Auto.value, controls.AfModeEnum.Continuous.value] else 1.0
                        time.sleep(settle_time) 

                        request = picam2.capture_request()
                        frame = request.make_array("main")
                        metadata = request.get_metadata()
                        request.release()

                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                        actual_lens_pos = metadata.get('LensPosition', 'N/A')
                        
                        text_line1 = f"Mode: {str(controls.AfModeEnum(current_af_mode)).split('.')[-1]}"
                        text_line2 = f"Range: {str(controls.AfRangeEnum(current_af_range)).split('.')[-1]}, Speed: {str(controls.AfSpeedEnum(current_af_speed)).split('.')[-1] if current_af_speed else 'N/A'}"
                        
                        # Mapping integer NR values to readable strings for display
                        nr_display_map = {
                            0: "Off",
                            1: "Fast",
                            2: "HighQuality"
                        }
                        nr_display = nr_display_map.get(noise_red_mode, str(noise_red_mode))
                        
                        text_line3 = f"Sharpness: {sharpness:.1f}, NR Mode: {nr_display}"
                        text_line4 = f"Actual Exp: {metadata.get('ExposureTime', 'N/A')} us, Gain: {metadata.get('AnalogueGain', 'N/A'):.1f}x"
                        text_line5 = f"Actual Lens: {actual_lens_pos:.3f}" if isinstance(actual_lens_pos, (float, int)) else f"Actual Lens: {actual_lens_pos}"

                        text_color = (0, 0, 255)
                        font_scale = 0.7
                        font_thickness = 2
                        
                        cv2.putText(frame_bgr, text_line1, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                        cv2.putText(frame_bgr, text_line2, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                        cv2.putText(frame_bgr, text_line3, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                        cv2.putText(frame_bgr, text_line4, (20, 140), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                        cv2.putText(frame_bgr, text_line5, (20, 170), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)

                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = f"{timestamp_str}.jpg"
                        filepath = os.path.join(OUTPUT_DIR, filename)
                        
                        cv2.imwrite(filepath, frame_bgr)
                        print(f"  Saved {filepath}")

                        csv_writer.writerow({
                            'timestamp': timestamp_str,
                            'filename': filename,
                            'focus_mode': str(controls.AfModeEnum(current_af_mode)).split('.')[-1],
                            'af_range': str(controls.AfRangeEnum(current_af_range)).split('.')[-1],
                            'af_speed': str(controls.AfSpeedEnum(current_af_speed)).split('.')[-1] if current_af_speed else 'N/A',
                            'lens_position_requested': 'N/A',
                            'lens_position_actual': actual_lens_pos,
                            'sharpness_requested': sharpness,
                            'exposure_time_us_actual': metadata.get('ExposureTime', 'N/A'),
                            'analog_gain_actual': metadata.get('AnalogueGain', 'N/A'),
                            'brightness_actual': metadata.get('Brightness', 'N/A'),
                            'contrast_actual': metadata.get('Contrast', 'N/A'),
                            'noise_reduction_mode_requested': nr_display # Log the readable string
                        })

                    except Exception as e:
                        print(f"Error processing AF Mode {str(controls.AfModeEnum(current_af_mode)).split('.')[-1]} with Range {str(controls.AfRangeEnum(current_af_range)).split('.')[-1]}, Sharpness {sharpness}, NR {noise_red_mode}: {e}")
                        continue
        
        # --- Manual Focus Loop ---
        for lens_pos in LENS_POSITIONS_MANUAL:
            for sharpness in SHARPNESS_VALUES:
                for noise_red_mode in NOISE_REDUCTION_MODES_TEST:
                    try:
                        controls_to_set = {
                            "AeEnable": AE_ENABLE,
                            "AwbEnable": AWB_ENABLE,
                            "Sharpness": sharpness,
                            "Brightness": BRIGHTNESS,
                            "Contrast": CONTRAST,
                            "AfMode": controls.AfModeEnum.Manual.value,
                            "LensPosition": lens_pos
                        }
                        
                        if noise_red_mode is not None:
                            try:
                                controls_to_set["NoiseReductionMode"] = noise_red_mode
                            except Exception as nre:
                                print(f"Warning: Could not set NoiseReductionMode={noise_red_mode}: {nre}")
                                controls_to_set["NoiseReductionMode"] = "UNSUPPORTED"

                        picam2.set_controls(controls_to_set)
                        print(f"\n--- Setting Mode=Manual, Lens={lens_pos:.3f}, Sharpness={sharpness:.1f}, NR={noise_red_mode} ---")
                        
                        time.sleep(1.5)

                        request = picam2.capture_request()
                        frame = request.make_array("main")
                        metadata = request.get_metadata()
                        request.release()

                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                        approx_dist_m = "inf" if lens_pos == 0 else f"{1/lens_pos:.2f}"
                        text_line1 = f"Mode: Manual, Lens Pos: {lens_pos:.3f} ({approx_dist_m}m)"
                        
                        nr_display_map = {
                            0: "Off",
                            1: "Fast",
                            2: "HighQuality"
                        }
                        nr_display = nr_display_map.get(noise_red_mode, str(noise_red_mode))

                        text_line2 = f"Sharpness: {sharpness:.1f}, NR Mode: {nr_display}"
                        text_line3 = f"Actual Exp: {metadata.get('ExposureTime', 'N/A')} us, Gain: {metadata.get('AnalogueGain', 'N/A'):.1f}x"
                        
                        text_color = (0, 0, 255)
                        font_scale = 0.7
                        font_thickness = 2
                        
                        cv2.putText(frame_bgr, text_line1, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                        cv2.putText(frame_bgr, text_line2, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                        cv2.putText(frame_bgr, text_line3, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)

                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = f"{timestamp_str}.jpg"
                        filepath = os.path.join(OUTPUT_DIR, filename)
                        
                        cv2.imwrite(filepath, frame_bgr)
                        print(f"  Saved {filepath}")

                        csv_writer.writerow({
                            'timestamp': timestamp_str,
                            'filename': filename,
                            'focus_mode': 'Manual',
                            'af_range': 'N/A',
                            'af_speed': 'N/A',
                            'lens_position_requested': lens_pos,
                            'lens_position_actual': metadata.get('LensPosition', 'N/A'),
                            'sharpness_requested': sharpness,
                            'exposure_time_us_actual': metadata.get('ExposureTime', 'N/A'),
                            'analog_gain_actual': metadata.get('AnalogueGain', 'N/A'),
                            'brightness_actual': metadata.get('Brightness', 'N/A'),
                            'contrast_actual': metadata.get('Contrast', 'N/A'),
                            'noise_reduction_mode_requested': nr_display # Log the readable string
                        })

                    except Exception as e:
                        print(f"Error processing Manual Mode, Lens={lens_pos:.3f}, Sharpness={sharpness:.1f}, NR={noise_red_mode}: {e}")
                        continue 

finally:
    picam2.stop()
    picam2.close()
    print("\nCamera stopped and closed.")
    print(f"All full grid search images saved to: {OUTPUT_DIR}")
    print(f"Log file saved to: {LOG_FILE}")