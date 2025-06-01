import cv2
import matplotlib.pyplot as plt
import numpy as np
import degirum as dg
from pprint import pprint


def read_image_as_rgb(image_path):
    # Load the image in BGR format (default in OpenCV)
    image_bgr = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if image_bgr is None:
        raise ValueError(f"Error: Unable to load image from path:{image_path}")

        # Convert the image from BGR to RGB
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        return image_rgb

def print_image_size(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if image is None:
        print(f"Error: Unable to load image from path: {image_path}")
    else:
        # Get the image size (height, width, channels)
        height, width, channels = image.shape
        print(f"Image size: {height}x{width} (Height x Width)")

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

def resize_with_letterbox(image_path, target_shape, padding_value=(0,0,0)):
    """
    Resize an image to a target shape while maintaining the aspect ratio.
    The image is resized with letterboxing, meaning it will be padded with a specified color if necessary.
    
    :param image_path (str): Path to the input image.
    :param target_shape (tuple): Tuple (batch_size, target_height, target_width, channels) for the target size.
    :param padding_value (tuple): RGB Color values for padding in RGB format (default is black padding).

    :return: Resized image with letterboxing applied.
    letterboxed_image (numpy.ndarray): The resized image with letterboxing applied.
    scale (float): The scale factor ratio used for resizing the origial image.
    pad_top (int): The top padding applied to the image.
    pad_left (int): The left padding applied to the image.
    """
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

# prepare the input image
image_path = 'assets/Car.jpg'
print_image_size(image_path)
original_image_array = read_image_as_rgb(image_path)


# Resize the image with letterboxing and visualize the result
target_shape = (1, 416, 416, 3)  # Batch size of 1, target height and width of 416 and 3 channels
resized_image_array, scale_factor, offset_y, offset_x = resize_with_letterbox(image_path, target_shape)
#display_images([resized_image_array[0]], title="Resized Image with Letterboxing and Original Image")

model = dg.load_model(
    model_name = 'tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2',
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
pprint(inference_result.results)

## ต่อไปการประมวลผลผลลัพธ์จากโมเดล
# Process the inference results
def process_inference_results(inference_result, input_shape, num_classes, label_dictionary, confidence_threshold=0.5):
    # unpack the input shape
    batch_size, input_height, input_width, channels = input_shape
    new_inference_results = []
    output_array = inference_result.reshape(-1)
    index = 0
    for class_id in range(num_classes):
        num_detections = int(output_array[index])
        index += 1

        if num_detections == 0:
            continue

        for _ in range(num_detections):

            if index + 5 > len(output_array) :
                break

            