import os
import degirum as dg, degirum_tools
import matplotlib.pyplot as plt
import numpy as np
import cv2
from datetime import datetime
import easyocr
from picamera2 import Picamera2


def capture_image():
    """Capture an image from the PiCamera2"""
    picam2 = Picamera2()
    picam2.start()
    
    # Capture image
    image = picam2.capture_array()
    
    # Convert from RGB to BGR for OpenCV
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    return image_bgr

def read_text_from_image(image):
    """Use EasyOCR to read text from an image"""
    reader = easyocr.Reader(['en','th'])  # Load OCR model for English
    results = reader.readtext(image)

    extracted_text = [res[1] for res in results]  # Extract only text
    return extracted_text

def crop_images(image, results):
    """
    Crops regions of interest (ROIs) from an image based on inference results.

    Args:
        image (numpy.ndarray): The input image as a NumPy array.
        results (list of dict): A list of inference results, each containing:
            - bbox (list of float): Bounding box in [x_min, y_min, x_max, y_max] format.
            - category_id (int): Class ID (ignored in this function).
            - label (str): Label of the detected object (ignored in this function).
            - score (float): Confidence score (ignored in this function).

    Returns:
        list of numpy.ndarray: A list of cropped image regions.
    """
    cropped_images = []

    for result in results:
        bbox = result.get('bbox')
        if not bbox or len(bbox) != 4:
            continue
        # Convert bbox to integer pixel coordinates
        x_min, y_min, x_max, y_max = map(int, bbox)

        if x_min >= x_max or y_min >= y_max:
            print("Warning : Invalid bounding box, skipping....")
            continue

        # Ensure the bounding box is within image bounds
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(image.shape[1], x_max)
        y_max = min(image.shape[0], y_max)

        # Crop the region of interest
        cropped = image[y_min:y_max, x_min:x_max]
        cropped_images.append(cropped)

    return cropped_images

def display_images(images, title="Images", figsize=(15, 5)):
    """
    Display a list of images in a single row using Matplotlib.

    Parameters:
    - images (list): List of images (NumPy arrays) to display.
    - title (str): Title for the plot.
    - figsize (tuple): Size of the figure.
    """
    num_images = len(images)
    fig, axes = plt.subplots(1, num_images, figsize=figsize)
    if num_images == 1:
        axes = [axes]  # Make it iterable for a single image
    for ax, image in zip(axes, images):
        image_rgb = image[:, :, ::-1]  # Convert BGR to RGB
        ax.imshow(image_rgb)
        ax.axis('off')
    fig.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.show()

def save_images(images, filename="lpr",output_dir="lpr_images"):
    """
    Save a list of images instead of displaying them.

    Parameters:
    - images (list): List of images (NumPy arrays) to save.
    - output_dir (str): Directory to save images.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Ensure input is a list of images
    if isinstance(images, np.ndarray) and images.dtype == np.uint8:
        images = list(images)  # Convert object array back to a list

    # Process each image
    for idx, image_array in enumerate(images):
        if isinstance(image_array, np.ndarray):  # Ensure it's a valid image
            image_bgr = image_array  # Skip conversion for grayscale images
    
            print(f"Type of image is:{type(image_bgr)}\n")
            if idx > 0:
                output_path = os.path.join(output_dir, f"{filename}_{idx}.jpg")
            else:
                output_path = os.path.join(output_dir, f"{filename}.jpg")
            cv2.imwrite(output_path, image_bgr)
            print(f"Saved {len(images)} images to '{output_path}'")

def rearrange_detections(detections):
    # Sort characters by leftmost x-coordinate
    detections_sorted = sorted(detections, key=lambda det: det["bbox"][0])
    # Concatenate labels to form the license plate string
    return "".join([det["label"] for det in detections_sorted])


def main():
    hw_location = "@local"
    lp_det_model_zoo_url = "resources"
    lp_det_model_name = "yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1"
    lp_ocr_model_zoo_url = "resources"
    lp_ocr_model_name = "yolov8n_relu6_lp_ocr--256x128_quant_hailort_hailo8_1"
    
    '''
    # Create a compound cropping model with 50% crop extent
    crop_model = degirum_tools.CroppingAndClassifyingCompoundModel(
        lp_det_model,
        lp_ocr_model,
        5.0
    )

    # Detect license plate boxes
    inference_result = crop_model(image_source)

    # display combined results
    with degirum_tools.Display("License Plates") as display:
        display.show_image(inference_result)
    print(f"Inference result from multimodel:{inference_result}")
    '''
    # Load license plate detection and license plate OCR models
    lp_det_model=dg.load_model(
        model_name=lp_det_model_name,
        inference_host_address=hw_location,
        zoo_url=lp_det_model_zoo_url,
        token='',
        overlay_color=[(255,255,0),(0,255,0)]
    )
    lp_ocr_model=dg.load_model(
        model_name=lp_ocr_model_name,
        inference_host_address=hw_location,
        zoo_url=lp_ocr_model_zoo_url,
        token='',
        output_use_regular_nms=False,
        output_confidence_threshold=0.1
    )


    """Capture an image, process it with EasyOCR, and display results"""
    image_source = capture_image()
    #image_source = "assets/Car.jpg" #for test only
    # Generate timestamp in the format YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # run the model inference
    detected_license_plates = lp_det_model(image_source) 
    print(f"Detected license plate with lp_det_model: {detected_license_plates}")

    # visualize the results of the detection model.
    display_images([detected_license_plates.image_overlay], title="License Plate Detection Result")
    # Save the image results of the detection model.
    print(f"Spec image from detected license plate:{type(detected_license_plates.image_overlay)}\n{detected_license_plates.image_overlay}")
    image_name = f"{timestamp}_panorama"
    save_images([detected_license_plates.image_overlay],image_name)

    if detected_license_plates.results:
        # List of cropped license plates
        cropped_license_plates = crop_images(detected_license_plates.image, detected_license_plates.results)

        # Display cropped license plates
        display_images(cropped_license_plates, title="Cropped License Plates", figsize=(3, 2))
        # Save the image results of the detection model.
        print(f"Spec image from crop_images:{type(cropped_license_plates)}\n{cropped_license_plates}")
        # Convert list to NumPy array
        image_array = np.array(cropped_license_plates, dtype=np.uint8)
        image_name = f"{timestamp}_plate"
        save_images(image_array,image_name)
        for index, cropped_license_plate in enumerate(cropped_license_plates):
            ocr_results = lp_ocr_model.predict(cropped_license_plate)
            ocr_label = rearrange_detections(ocr_results.results)
            detected_license_plates.results[index]["label"] = ocr_label
            text_results = read_text_from_image(cropped_license_plate)
            print("easyOCR Detected Text:", text_results)
            image_name = f"{timestamp}_plate_easyocr"
            save_images([cropped_license_plate],image_name)

        display_images([detected_license_plates.image_overlay], title="License Plate Recognition Result")
        print('Save image of License plate ocr_label', ocr_label)
        image_name = f"{timestamp}_plate_ocr"
        save_images([detected_license_plates.image_overlay],image_name)

        

        

        # Save image for reference
        cv2.imwrite("captured_image.jpg", detected_license_plates.image_overlay)


if __name__ == "__main__":
    main()