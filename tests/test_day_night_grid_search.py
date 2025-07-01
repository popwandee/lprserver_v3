from picamera2 import Picamera2 
from libcamera import controls

import cv2
import time
import os
from datetime import datetime
import csv

# --- Configuration ---
# Base output directory for all grid search results
BASE_OUTPUT_DIR = "full_grid_search_roi_images" 

# Camera Resolution for still images
IMAGE_WIDTH, IMAGE_HEIGHT = 4608, 2592 # Full resolution for IMX708

# --- ROI Definition (based on full image dimensions) ---
# Assuming x_max = IMAGE_WIDTH and y_max = IMAGE_HEIGHT
roi_width = 2300
roi_height = 1200

# Calculate ROI coordinates
roi_x1_calc = IMAGE_WIDTH - roi_width - 400
roi_y1_calc = IMAGE_HEIGHT - roi_height - 500
roi_x2_calc = IMAGE_WIDTH - 400
roi_y2_calc = IMAGE_HEIGHT - 500

# Ensure ROI is within image bounds
ROI_X1 = max(0, roi_x1_calc)
ROI_Y1 = max(0, roi_y1_calc)
ROI_X2 = min(IMAGE_WIDTH, roi_x2_calc)
ROI_Y2 = min(IMAGE_HEIGHT, roi_y2_calc)

# --- Common Grid Search Parameters ---

# Focus Modes (Auto/Continuous and Manual)
AF_SETTINGS = [
    {"mode": controls.AfModeEnum.Auto.value, "range": controls.AfRangeEnum.Normal.value, "speed": None},
    {"mode": controls.AfModeEnum.Auto.value, "range": controls.AfRangeEnum.Macro.value, "speed": None},
    {"mode": controls.AfModeEnum.Auto.value, "range": controls.AfRangeEnum.Full.value, "speed": None},

    {"mode": controls.AfModeEnum.Continuous.value, "range": controls.AfRangeEnum.Normal.value, "speed": controls.AfSpeedEnum.Fast.value},
    {"mode": controls.AfModeEnum.Continuous.value, "range": controls.AfRangeEnum.Normal.value, "speed": controls.AfSpeedEnum.Normal.value},
]

# Manual Focus Lens Positions (Dioptres)
# Combined from your lists, focused on the relevant ranges
LENS_POSITIONS_MANUAL = [
    0.0,    # Infinity
    # Near 15-20m range
    0.05,   # ~20m
    0.06,   # ~16.67m
    0.065,  # ~15.38m
    0.07,   # ~14.28m
    0.08,   # ~12.5m
    # Further ranges you specified
    0.1,    # 10m
    0.2,    # 5m
    0.3,    # 3.33m
    0.4,    # 2.5m
    0.5,    # 2m
    0.6,    # 1.67m
    0.7     # 1.43m
]

# Sharpness values
SHARPNESS_VALUES = [0.0, 1.0, 2.0]

# Noise Reduction Mode (using common integer values if enums are not exposed)
NOISE_REDUCTION_MODES_TEST = [
    0, # Typically "Off"
    1, # Typically "Fast" or "Low Quality"
    2  # Typically "High Quality"
]

# --- Night Mode Specific Parameters ---
NIGHT_EXPOSURE_TIMES_US = [100000, 200000, 300000, 400000, 500000] # in microseconds (100ms to 500ms)
NIGHT_ANALOG_GAINS = [1.0, 2.0, 4.0, 8.0, 16.0] # High gains for low light

# --- Main Grid Search Function ---
def run_grid_search(mode: str):
    """
    Runs a grid search for camera parameters based on the specified mode (day/night).

    Args:
        mode (str): "day" or "night".
    """
    mode = mode.lower()
    if mode not in ["day", "night"]:
        print("Error: Mode must be 'day' or 'night'.")
        return

    output_dir = os.path.join(BASE_OUTPUT_DIR, mode)
    log_file = os.path.join(output_dir, f"grid_search_log_{mode}.csv")

    # Set mode-specific base camera controls
    if mode == "day":
        ae_enable = True
        awb_mode = controls.AwbModeEnum.Auto.value
        brightness = 0.0
        contrast = 1.0
        exposure_time_values = [None] # Not controlling manually
        analog_gain_values = [None]   # Not controlling manually
        text_color = (0, 0, 255) # Blue for day
        print(f"\n--- Starting Grid Search for DAY Mode ({IMAGE_WIDTH}x{IMAGE_HEIGHT}) ---")
    else: # night mode
        ae_enable = False # Manual exposure for night
        awb_mode = controls.AwbModeEnum.Auto.value # Or Incandescent.value for more control
        brightness = 0.0 # Keep default or adjust based on observation
        contrast = 1.0   # Keep default or adjust
        exposure_time_values = NIGHT_EXPOSURE_TIMES_US
        analog_gain_values = NIGHT_ANALOG_GAINS
        text_color = (0, 255, 255) # Yellow for night (better visibility)
        print(f"\n--- Starting Grid Search for NIGHT Mode ({IMAGE_WIDTH}x{IMAGE_HEIGHT}) ---")

    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)})
    picam2.configure(camera_config)

    try:
        picam2.start()
        print(f"Picamera2 started for {mode} mode.")
        time.sleep(2) # Give camera a moment to settle after start

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        fieldnames = [
            'timestamp', 'filename', 'mode', 'focus_mode', 'af_range', 'af_speed',
            'lens_position_requested', 'lens_position_actual', 'sharpness_requested',
            'noise_reduction_mode_requested',
            'exposure_time_requested', 'analog_gain_requested', # Added for night mode
            'exposure_time_us_actual', 'analog_gain_actual',
            'brightness_actual', 'contrast_actual'
        ]
        
        with open(log_file, 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()

            print(f"Logs will be saved to: {log_file}")
            
            # --- Grid Search Loops ---
            for exp_time in exposure_time_values:
                for gain in analog_gain_values:
                    # Loop through AF Modes
                    for af_setting in AF_SETTINGS:
                        current_af_mode = af_setting["mode"]
                        current_af_range = af_setting["range"]
                        current_af_speed = af_setting["speed"]

                        for sharpness in SHARPNESS_VALUES:
                            for noise_red_mode in NOISE_REDUCTION_MODES_TEST:
                                try:
                                    controls_to_set = {
                                        "AeEnable": ae_enable,
                                        "AwbEnable": awb_mode,
                                        "Sharpness": sharpness,
                                        "Brightness": brightness,
                                        "Contrast": contrast,
                                        "AfMode": current_af_mode,
                                        "AfRange": current_af_range,
                                    }
                                    
                                    if mode == "night":
                                        controls_to_set["ExposureTime"] = exp_time
                                        controls_to_set["AnalogueGain"] = gain

                                    # Try to set NoiseReductionMode using integer values
                                    if noise_red_mode is not None:
                                        try:
                                            controls_to_set["NoiseReductionMode"] = noise_red_mode
                                        except Exception as nre:
                                            print(f"Warning: Could not set NoiseReductionMode={noise_red_mode}: {nre}")
                                            controls_to_set["NoiseReductionMode"] = "UNSUPPORTED"
                                            
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

                                    # --- Draw ROI on the image ---
                                    cv2.rectangle(frame_bgr, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0, 255, 0), 5) # Green rectangle
                                    
                                    # --- Add parameters text to the image ---
                                    actual_lens_pos = metadata.get('LensPosition', 'N/A')
                                    
                                    text_line1 = f"Mode: {mode.upper()}, Focus: {str(controls.AfModeEnum(current_af_mode)).split('.')[-1]}"
                                    text_line2 = f"Range: {str(controls.AfRangeEnum(current_af_range)).split('.')[-1]}, Speed: {str(controls.AfSpeedEnum(current_af_speed)).split('.')[-1] if current_af_speed else 'N/A'}"
                                    
                                    nr_display_map = {0: "Off", 1: "Fast", 2: "HighQuality"}
                                    nr_display = nr_display_map.get(noise_red_mode, str(noise_red_mode))
                                    
                                    text_line3 = f"Sharpness: {sharpness:.1f}, NR Mode: {nr_display}"
                                    
                                    if mode == "night":
                                        text_line4 = f"Req Exp: {exp_time}us, Req Gain: {gain:.1f}x"
                                        text_line5 = f"Actual Exp: {metadata.get('ExposureTime', 'N/A')} us, Gain: {metadata.get('AnalogueGain', 'N/A'):.1f}x"
                                        text_line6 = f"Actual Lens: {actual_lens_pos:.3f}" if isinstance(actual_lens_pos, (float, int)) else f"Actual Lens: {actual_lens_pos}"
                                        text_y_offset = 180
                                    else:
                                        text_line4 = f"Actual Exp: {metadata.get('ExposureTime', 'N/A')} us, Gain: {metadata.get('AnalogueGain', 'N/A'):.1f}x"
                                        text_line5 = f"Actual Lens: {actual_lens_pos:.3f}" if isinstance(actual_lens_pos, (float, int)) else f"Actual Lens: {actual_lens_pos}"
                                        text_line6 = "" # Clear this line
                                        text_y_offset = 150 # Adjust vertical spacing for fewer lines

                                    font_scale = 2
                                    font_thickness = 2
                                    
                                    cv2.putText(frame_bgr, text_line1, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    cv2.putText(frame_bgr, text_line2, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    cv2.putText(frame_bgr, text_line3, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    cv2.putText(frame_bgr, text_line4, (20, text_y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    cv2.putText(frame_bgr, text_line5, (20, text_y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    if text_line6:
                                        cv2.putText(frame_bgr, text_line6, (20, text_y_offset + 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)


                                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                                    filename = f"{timestamp_str}.jpg"
                                    filepath = os.path.join(output_dir, filename)
                                    
                                    cv2.imwrite(filepath, frame_bgr)
                                    print(f"  Saved {filepath}")

                                    csv_writer.writerow({
                                        'timestamp': timestamp_str,
                                        'filename': filename,
                                        'mode': mode,
                                        'focus_mode': str(controls.AfModeEnum(current_af_mode)).split('.')[-1],
                                        'af_range': str(controls.AfRangeEnum(current_af_range)).split('.')[-1],
                                        'af_speed': str(controls.AfSpeedEnum(current_af_speed)).split('.')[-1] if current_af_speed else 'N/A',
                                        'lens_position_requested': 'N/A',
                                        'lens_position_actual': actual_lens_pos,
                                        'sharpness_requested': sharpness,
                                        'noise_reduction_mode_requested': nr_display,
                                        'exposure_time_requested': exp_time if mode == "night" else 'N/A',
                                        'analog_gain_requested': gain if mode == "night" else 'N/A',
                                        'exposure_time_us_actual': metadata.get('ExposureTime', 'N/A'),
                                        'analog_gain_actual': metadata.get('AnalogueGain', 'N/A'),
                                        'brightness_actual': metadata.get('Brightness', 'N/A'),
                                        'contrast_actual': metadata.get('Contrast', 'N/A')
                                    })

                                except Exception as e:
                                    print(f"Error processing {mode.upper()} AF Mode {str(controls.AfModeEnum(current_af_mode)).split('.')[-1]} with Range {str(controls.AfRangeEnum(current_af_range)).split('.')[-1]}, Sharpness {sharpness}, NR {noise_red_mode}: {e}")
                                    continue
            
            # --- Manual Focus Loop ---
            # These loops run for both day and night
            for lens_pos in LENS_POSITIONS_MANUAL:
                for sharpness in SHARPNESS_VALUES:
                    for noise_red_mode in NOISE_REDUCTION_MODES_TEST:
                        # For night mode manual focus, we also iterate through exposure/gain
                        for exp_time in (NIGHT_EXPOSURE_TIMES_US if mode == "night" else [None]):
                            for gain in (NIGHT_ANALOG_GAINS if mode == "night" else [None]):
                                try:
                                    controls_to_set = {
                                        "AeEnable": ae_enable,
                                        "AwbEnable": awb_mode,
                                        "Sharpness": sharpness,
                                        "Brightness": brightness,
                                        "Contrast": contrast,
                                        "AfMode": controls.AfModeEnum.Manual.value,
                                        "LensPosition": lens_pos
                                    }
                                    
                                    if mode == "night":
                                        controls_to_set["ExposureTime"] = exp_time
                                        controls_to_set["AnalogueGain"] = gain

                                    if noise_red_mode is not None:
                                        try:
                                            controls_to_set["NoiseReductionMode"] = noise_red_mode
                                        except Exception as nre:
                                            print(f"Warning: Could not set NoiseReductionMode={noise_red_mode}: {nre}")
                                            controls_to_set["NoiseReductionMode"] = "UNSUPPORTED"

                                    picam2.set_controls(controls_to_set)
                                    print(f"\n--- Setting {mode.upper()} Mode=Manual, Lens={lens_pos:.3f}, Sharpness={sharpness:.1f}, NR={noise_red_mode}, Exp={exp_time} Gain={gain} ---")
                                    
                                    time.sleep(2)

                                    request = picam2.capture_request()
                                    frame = request.make_array("main")
                                    metadata = request.get_metadata()
                                    request.release()

                                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                                    # --- Draw ROI on the image ---
                                    cv2.rectangle(frame_bgr, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0, 255, 0), 5) # Green rectangle

                                    # --- Add parameters text to the image ---
                                    approx_dist_m = "inf" if lens_pos == 0 else f"{1/lens_pos:.2f}"
                                    text_line1 = f"Mode: {mode.upper()}, Focus: Manual, Lens Pos: {lens_pos:.3f} ({approx_dist_m}m)"
                                    
                                    nr_display_map = {0: "Off", 1: "Fast", 2: "HighQuality"}
                                    nr_display = nr_display_map.get(noise_red_mode, str(noise_red_mode))

                                    text_line2 = f"Sharpness: {sharpness:.1f}, NR Mode: {nr_display}"
                                    
                                    if mode == "night":
                                        text_line3 = f"Req Exp: {exp_time}us, Req Gain: {gain:.1f}x"
                                        text_line4 = f"Actual Exp: {metadata.get('ExposureTime', 'N/A')} us, Gain: {metadata.get('AnalogueGain', 'N/A'):.1f}x"
                                        text_line5 = "" # Clear this line
                                        text_y_offset = 150
                                    else:
                                        text_line3 = f"Actual Exp: {metadata.get('ExposureTime', 'N/A')} us, Gain: {metadata.get('AnalogueGain', 'N/A'):.1f}x"
                                        text_line4 = ""
                                        text_line5 = ""
                                        text_y_offset = 120 # Adjust vertical spacing for fewer lines

                                    font_scale = 2
                                    font_thickness = 2
                                    
                                    cv2.putText(frame_bgr, text_line1, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    cv2.putText(frame_bgr, text_line2, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    cv2.putText(frame_bgr, text_line3, (20, text_y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    if text_line4:
                                        cv2.putText(frame_bgr, text_line4, (20, text_y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
                                    if text_line5:
                                        cv2.putText(frame_bgr, text_line5, (20, text_y_offset + 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)

                                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                                    filename = f"{timestamp_str}.jpg"
                                    filepath = os.path.join(output_dir, filename)
                                    
                                    cv2.imwrite(filepath, frame_bgr)
                                    print(f"  Saved {filepath}")

                                    csv_writer.writerow({
                                        'timestamp': timestamp_str,
                                        'filename': filename,
                                        'mode': mode,
                                        'focus_mode': 'Manual',
                                        'af_range': 'N/A',
                                        'af_speed': 'N/A',
                                        'lens_position_requested': lens_pos,
                                        'lens_position_actual': metadata.get('LensPosition', 'N/A'),
                                        'sharpness_requested': sharpness,
                                        'noise_reduction_mode_requested': nr_display,
                                        'exposure_time_requested': exp_time if mode == "night" else 'N/A',
                                        'analog_gain_requested': gain if mode == "night" else 'N/A',
                                        'exposure_time_us_actual': metadata.get('ExposureTime', 'N/A'),
                                        'analog_gain_actual': metadata.get('AnalogueGain', 'N/A'),
                                        'brightness_actual': metadata.get('Brightness', 'N/A'),
                                        'contrast_actual': metadata.get('Contrast', 'N/A')
                                    })

                                except Exception as e:
                                    print(f"Error processing {mode.upper()} Manual Mode, Lens={lens_pos:.3f}, Sharpness={sharpness:.1f}, NR={noise_red_mode}, Exp={exp_time} Gain={gain}: {e}")
                                    continue 

    finally:
        picam2.stop()
        picam2.close()
        print(f"\nCamera stopped and closed for {mode} mode.")
        print(f"All {mode} grid search images saved to: {output_dir}")
        print(f"Log file saved to: {log_file}")

# --- How to Run ---
if __name__ == "__main__":
    # Run for Day Mode
    #print("--- Starting DAY mode grid search ---")
    #run_grid_search("day")

    # Run for Night Mode
    # IMPORTANT: Change physical conditions (lighting) before running night mode!
    print("\n--- Starting NIGHT mode grid search ---")
    print("Please ensure the environment is dark enough for night testing.")
    input("Press Enter to continue with NIGHT mode grid search...") # Wait for user
    run_grid_search("night")

    print("\nGrid Search completed for selected modes.")