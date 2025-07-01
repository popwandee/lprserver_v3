import cv2
import pandas as pd
import numpy as np
import os

def is_blurry(image_path, threshold=100.0):
    """
    Analyzes the blurriness of an image using the Laplacian variance method.

    Args:
        image_path (str): The path to the image file.
        threshold (float): The variance threshold. Below this, the image is considered blurry.

    Returns:
        tuple: A tuple containing:
            - str: "blur" if the image is blurry, "sharp" otherwise.
            - float: The computed Laplacian variance.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Warning: Could not read image at {image_path}. Skipping.")
            return "error", 0.0

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < threshold:
            return "blur", laplacian_var
        else:
            return "sharp", laplacian_var
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return "error", 0.0

def analyze_image_sharpness(output_dir,log_file_path, output_log_file_path, blur_threshold=100.0):
    """
    Reads an existing log file, analyzes the sharpness of each image listed,
    and updates the log file with blurriness information.

    Args:
        log_file_path (str): The path to the input CSV log file.
        output_log_file_path (str): The path to save the updated CSV log file.
        blur_threshold (float): The variance threshold for determining blurriness.
    """
    if not os.path.exists(log_file_path):
        print(f"Error: Input log file not found at {log_file_path}")
        return

    try:
        df = pd.read_csv(log_file_path)
    except Exception as e:
        print(f"Error reading CSV file {log_file_path}: {e}")
        return

    # Check if 'image_path' column exists
    if 'filename' not in df.columns:
        print(f"Error: 'image_path' column not found in {log_file_path}. Please ensure the column exists.")
        return

    # Initialize new columns
    df['laplacian_variance'] = np.nan
    df['is_blurry'] = 'N/A'

    for index, row in df.iterrows():
        image_path = os.path.join(output_dir,row['filename'])
        status, variance = is_blurry(image_path, threshold=blur_threshold)
        
        df.at[index, 'laplacian_variance'] = variance
        df.at[index, 'is_blurry'] = status

    df.to_csv(output_log_file_path, index=False)
    print(f"Analysis complete. Updated log file saved to {output_log_file_path}")

# --- Example Usage ---
if __name__ == "__main__":
    
    # 2. Run the blur analysis
    output_dir = "full_grid_search_roi_images/night/"
    input_log_csv = 'full_grid_search_roi_images/night/grid_search_log_night.csv'  # Your existing log file from the grid search
    output_log_csv = 'full_grid_search_roi_images/night_analyzed_image_log.csv' # Where the results will be saved
    blur_detection_threshold = 100.0 # Adjust this threshold as needed based on your images

    analyze_image_sharpness(output_dir,input_log_csv, output_log_csv, blur_detection_threshold)

    # Optional: Display the analyzed log file
    print("\n--- Content of analyzed_image_log.csv ---")
    try:
        analyzed_df = pd.read_csv(output_log_csv)
        print(analyzed_df.head())
    except Exception as e:
        print(f"Could not read the analyzed log file: {e}")
