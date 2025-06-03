import cv2
import matplotlib.pyplot as plt
import numpy as np
import degirum as dg
from pprint import pprint
import json

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

def post_process_tiny_yolov4(outputs, image_shape):
    """แปลง output จากโมเดล Hailo-8 YOLOv4 ให้เป็น bounding boxes"""
    boxes = []
    confidences = []
    
    for scale in ['conv19', 'conv21']:  # ใช้ทั้ง 13x13 และ 26x26
        centers = outputs[f'{scale}_centers']
        scales = outputs[f'{scale}_scales']
        obj_probs = outputs[f'{scale}_obj']
        class_probs = outputs[f'{scale}_probs']
        
        for i in range(centers.shape[0]):  # ไล่ตาม grid cell
            for j in range(centers.shape[1]):
                for anchor in range(centers.shape[2] // 2):  # ใช้ anchor boxes
                    conf = obj_probs[i, j, anchor]
                    if conf > 0.5:  # ตั้ง threshold
                        center_x, center_y = centers[i, j, anchor].astype(float)
                        width, height = scales[i, j, anchor]
                        x1 = int((center_x - width / 2) * image_shape[1])
                        y1 = int((center_y - height / 2) * image_shape[0])
                        x2 = int((center_x + width / 2) * image_shape[1])
                        y2 = int((center_y + height / 2) * image_shape[0])
                        
                        boxes.append([x1, y1, x2, y2])
                        confidences.append(conf)
    
                        print(f"Centers shape: {centers.shape}")  # ตรวจสอบว่ามีค่าถูกต้องหรือไม่
                        print(f"Sample value: {centers[i, j, anchor]}")  # ตรวจสอบค่าที่กำลังดึงมาใช้งาน
    return boxes, confidences

def draw_boxes(image, boxes):
    """วาด bounding box ลงบนภาพ"""
    for box in boxes:
        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return image

def save_image(image, filename="lpr_images/output.jpg"):
    """บันทึกภาพที่มี bounding box"""
    cv2.imwrite(filename, image)


# Process the inference results
def process_inference_results(inference_result, input_shape, num_classes, label_dictionary, confidence_threshold=0.5):
    # unpack the input shape (batch is unused but include for flexibility)
    batch_size, input_height, input_width, channels = input_shape

    # Initialize an empty list to store detection results
    new_inference_results = []
    # Reshape and flatten the raw output tensor for parsing
    output_array = inference_result.reshape(-1)

    # Initialize and index pointer to traverse the output array
    index = 0

    # Loop through each class ID to process its detections
    for class_id in range(num_classes):
        # Read the number of detections for this class from the output array
        num_detections = int(output_array[index])
        index += 1 # Move to the next entry in the array
        # Skip processing if there are no detections for this class
        if num_detections == 0:
            continue
        # Iterate through each detection for this class
        for _ in range(num_detections):
            # Ensure there is enough data to process the next detection
            '''ใน YOLO output ที่คุณกำลังใช้บน Hailo-8 โมเดลจะส่งออกค่าที่เกี่ยวข้องกับ bounding box detection 
            ในแต่ละ anchor ตามโครงสร้างที่คล้ายกับนี้:
            center_x (ตำแหน่งศูนย์กลางแกน X)
            center_y (ตำแหน่งศูนย์กลางแกน Y)
            width (ความกว้างของ bounding box)
            height (ความสูงของ bounding box)
            confidence score (ค่าความน่าจะเป็นว่าวัตถุถูกตรวจจับ)
            เนื่องจาก bounding box หนึ่งต้องใช้ 5 ค่า ในการประมวลผล การใช้เงื่อนไข index + 5 > len(output_array) 
            จึงเป็นการ ตรวจสอบให้แน่ใจว่ามีข้อมูลเพียงพอ ก่อนที่จะดึงค่าออกมาเพื่อป้องกัน IndexError
            '''
            if index + 5 > len(output_array) :
                # Break to prevent accessing out-of-bound indices
                break
            # Extract confidence score and bounding box values
            score = float(output_array[index + 4])
            y_min, x_min, y_max, x_max = map(float, output_array[index: index + 4])
            index += 5 # Move index to the next detection entry

            # Skip detection if the confidence score is below the threshold
            if score < confidence_threshold:
                continue

            # Convert bounding box coordinates to absulute pixel values
            x_min = x_min * input_width
            y_min = y_min * input_height
            x_max = x_max * input_width
            y_max = y_max * input_height

            # Create a detection result with bbox, score, and class label
            result = {
                "bbox": [x_min, y_min, x_max, y_max], # Bounding box in pixel coordinates
                "score": score, # Confidence score of the detection
                "category_id": class_id, # Class ID of the detected object
                "label": label_dictionary.get(str(class_id), f"class_{class_id}"), # Class label or fallback
            }
            new_inference_results.append(result) # Store the formatted detection
        # Stop parsing if remaining output is padded with zeros (no more detections)
        if index >= len(output_array) or all(v ==0 for v in output_array[index:]):
            break
    # Return the final list of detection results
    return new_inference_results

# prepare the input image
image_path = 'assets/Cat.jpg'
print_image_size(image_path)
original_image_array = read_image_as_rgb(image_path)


# Resize the image with letterboxing and visualize the result
target_shape = (1, 416, 416, 3)  # Batch size of 1, target height and width of 416 and 3 channels
resized_image_array, scale_factor, offset_y, offset_x = resize_with_letterbox(image_path, target_shape)
#display_images([resized_image_array[0]], title="Resized Image with Letterboxing and Original Image")

model = dg.load_model(
    #model_name = 'tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2',
    model_name = 'yolov8n_relu6_coco--640x640_quant_hailort_hailo8_1',
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
print(f"Keys Available in First Result: {inference_result.results[0].keys()}")
print(json.dumps(inference_result.results, indent=2))
with open('output.json',"r") as json_file:
    label_dictionary = json.load(json_file)
detection_results = process_inference_results(inference_result.results, model.input_shape[0], 80, label_dictionary)
pprint(detection_results)
