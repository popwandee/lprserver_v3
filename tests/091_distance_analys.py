import os
import cv2
import time
import csv
import numpy as np
import easyocr
import degirum as dg
from datetime import datetime
from picamera2 import Picamera2
from skimage import filters
from skimage.metrics import structural_similarity as ssim
import pandas as pd
import matplotlib.pyplot as plt
import json

# 📁 เตรียม directory
os.makedirs("images", exist_ok=True)
os.makedirs("plates", exist_ok=True)
def resize_with_letterbox(image_path, target_shape, padding_value=(0,0,0)):
    # Load the image from the given path
    image = cv2.imread(image_path)
    
    # Check if the image was loaded successfully
    if image is None:
        raise ValueError(f"Error: Unable to load image from path: {image_path}")
    
    # Convert the image from BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Get the original image dimensions (height, width, channels)
    original_height, original_width, channels = image.shape
    
    # Extract target shape dimensions (height, width) from target_shape
    target_height, target_width = target_shape[1], target_shape[2]
    
    # Calculate the aspect ratios (Scale factors for width and height)
    original_aspect_ratio = original_width / original_height
    target_aspect_ratio = target_width / target_height

    # Choose the smaller scale factor to fit the image within the target dimensions
    # This ensures that the image fits within the target dimensions without distortion
    # and maintains the aspect ratio
    scale_factor = min(target_width / original_width, target_height / original_height)
    
    # Calculate the new dimensions of the image after scaling
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    
    # Resize the image to the new dimensions
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    # Create a new image with the target shape and fill it with the padding value
    letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)
    
    # Calculate padding offsets
    offset_y = (target_height - new_height) // 2 # Padding on the top 
    offset_x = (target_width - new_width) // 2 # Padding on the left 
    
    # Place the resized image in the letterbox background
    letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image
    
    # pencv backend (default), ใช้ input (H, W, C) เท่านั้น don't add batch dimension
    #final_image = np.expand_dims(letterboxed_image, axis=0)  # Add batch dimension
    
    # return the letterboxed image with batch dimension; scaling ratio, and padding (top, left)
    return letterboxed_image, scale_factor, offset_y, offset_x

# 🧠 OCR ด้วย EasyOCR
reader = easyocr.Reader(['en'])
def ocr_text(image):
    result = reader.readtext(image)
    if result:
        best = max(result, key=lambda r: r[2])
        return best[1], best[2]
    return "", 0

# 📈 วัด sharpness, blur, size
def analyze_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = filters.gaussian(gray, sigma=1).std()
    return lap_var, blur_score, image.shape[1], image.shape[0]

def read_image_as_rgb(image_path):
    # Load the image in BGR format (default in OpenCV)
    image_bgr = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if image_bgr is None:
        raise ValueError(f"Error: Unable to load image from path:{image_path}")

    # Convert the image from BGR to RGB
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return image_rgb
def display_images(images, title="Images", figsize=(15, 5)):
    num_images = len(images)
    fig, axes = plt.subplots(1, num_images, figsize=figsize)
    if num_images == 1:
        axes = [axes]  # Ensure axes is iterable Make it a list if there's only one image
    for ax, imgage in zip(axes, images):
        ax.imshow(imgage)
        ax.axis('off')
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()
# 🧪 Main
def main():
    csv_path = "results_alpr_experiment.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "filename", "distance_m", "method", "ocr_text", "confidence", "bbox",
            "sharpness", "blur_score", "width_px", "height_px", "plate_path"
        ])

        for filename in os.listdir("experiment_results"):
            if not filename.endswith(".jpg"):
                print("no image found")
                continue
            # Read the image from the experiment results directory
            print(f"Processing {filename}...")
            #image_path = os.path.join("experiment_results", filename)

            image_path = f"experiment_results/{filename}"

            image = read_image_as_rgb(image_path)
            display_images(image)
            
            distance = int(filename.split("_")[-1].replace("m.jpg", ""))

            # Resize the image with letterboxing and visualize the result
            target_shape = (1, 640, 640, 3)  # Batch size of 1, target height and width of 640 and 3 channels
            resized_image_array, scale_factor, offset_y, offset_x = resize_with_letterbox(image_path, target_shape)
            #display_images([resized_image_array[0]], title="Resized Image with Letterboxing and Original Image")

            model = dg.load_model(
                #model_name = 'yolov8n_relu6_car--640x640_quant_hailort_hailo8_1',
                model_name = 'yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1',
                inference_host_address='@local',
                zoo_url ='resources'
            )
            print(f"Model input shape: {model.input_shape[0]}")

            # Prepare the image for model input
            resized_image_array, scale_factor, offset_y, offset_x = resize_with_letterbox(image_path, model.input_shape[0])  
            print(f"Resized image shape: {resized_image_array.shape}")

            # Run inference on the model
            inference_result = model(resized_image_array)

            # Print the inference result
            print(f"Inference Results Structure: {inference_result.results}")
            if not inference_result.results:
                print(f"No detection in {filename}")
                continue
            print(f"Keys Available in First Result: {inference_result.results[0].keys()}")

            print(json.dumps(inference_result.results, indent=2))
          

    print("✅ Experiment complete. Results saved to:", csv_path)

def analyze():


    df = pd.read_csv("results_alpr_experiment.csv")

    # กราฟ: Confidence ต่อระยะ
    pivot = df.pivot_table(index="distance_m", columns="method", values="confidence", aggfunc="mean")
    pivot.plot(marker="o", title="OCR Confidence vs Distance")
    plt.ylabel("OCR Confidence")
    plt.grid(True)
    plt.show()

    # กราฟ: Sharpness
    pivot_sharp = df.pivot_table(index="distance_m", columns="method", values="sharpness", aggfunc="mean")
    pivot_sharp.plot(marker="o", title="Sharpness vs Distance")
    plt.ylabel("Sharpness (Laplacian Variance)")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # capture_images()  # ← ถ้าอยากให้ถ่ายภาพอัตโนมัติ เปิดบรรทัดนี้
    main()
    analyze()