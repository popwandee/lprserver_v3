# Simplifying Instance Segmentation on a Hailo Device Using DeGirum PySDK

This guide demonstrates how to leverage PySDK’s built-in segmentation postprocessing—integrated in C++—to run YOLOv8/YOLO11 segmentation models on Hailo devices. With minimal configuration, you can run inference and visualize segmentation outputs, including class labels. Although this example uses a model trained on the COCO dataset, the method works for any YOLOv8/YOLO11 segmentation model with appropriate modifications.

> **Tip:** If you are new to PySDK, consider reviewing the [object detection guide](./003_simplified_object_detection.md) before diving into segmentation.

---

## Overview of the Inference Pipeline

For segmentation models, the inference pipeline consists of:

1. **Pre-Processing**:  
   Resize and format the input image (e.g., letterbox padding, bilinear interpolation, quantization) to match model requirements.

2. **Inference**:  
   Run the YOLOv8/YOLO11 segmentation model (compiled into a `.hef` file) on the Hailo device.

3. **Post-Processing**:  
   The integrated C++ postprocessing converts the model’s raw outputs into a segmentation mask overlay. To enable this processing, specify `"OutputPostprocessType": "SegmentationYoloV8"` in the JSON configuration. In this guide, a COCO labels file is provided for human-readable output.

4. **Visualization**:  
   The processed segmentation overlay is provided as an image, which can be displayed using tools such as OpenCV.

A simple diagram of the pipeline:

```
Input Image
    │
    ▼
Pre-Processing (resize, letterbox, quantize)
    │
    ▼
Model Inference (.hef file on Hailo device)
    │
    ▼
Built-in Post-Processing (SegmentationYoloV8 in C++)
    │
    ▼
Segmentation Overlay (with COCO labels)
    │
    ▼
Visualization (e.g., via OpenCV)
```

---

## What You’ll Need

Ensure you have the following prerequisites:

1. **Hailo AI Accelerator**:  
   A Hailo8 or Hailo8L device. The host system can be x86 or an Arm-based system (e.g., Raspberry Pi).

2. **Drivers and Software Tools**:  
   Install the necessary drivers and follow the [Hailo + PySDK setup instructions](https://github.com/DeGirum/hailo_examples/blob/main/README.md).

3. **Segmentation Model File (`.hef`)**:  
   A YOLOv8/YOLO11 segmentation model trained on COCO, compiled into a `.hef` file. For example, you can use `yolov8n_seg.hef` available at [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_instance_segmentation.rst).

4. **Input Image**:  
   An image on which to run segmentation. For instance, download this [Cat Image](https://raw.githubusercontent.com/DeGirum/hailo_examples/refs/heads/main/assets/Cat.jpg). Feel free to experiment with your own images.

5. **COCO Labels File (`labels_coco.json`)**:  
   A file mapping the 80 COCO classes to human-readable labels. You can download this from [Hugging Face](https://huggingface.co/datasets/huggingface/label-files/blob/main/coco-detection-mmdet-id2label.json) or another trusted source.

---
## Summary

We’ll walk you through the key steps to run segmentation inference on a Hailo device using DeGirum PySDK:

- **Configuring the Model JSON File**:  
  Set up your JSON file to define pre-processing parameters, specify the segmentation model file, and enable the built-in C++ postprocessing (using `"OutputPostprocessType": "SegmentationYoloV8"`). This section also covers setting the number of classes, a confidence threshold, and the `"SigmoidOnCLS"` flag if required by your model.

- **Preparing the Model Zoo**:  
  Organize your model assets—including the JSON configuration file, the `.hef` model file, and the COCO labels file—into a structured directory for easy access and management by PySDK.

- **Running Inference**:  
  Load the segmentation model from the model zoo, execute inference on an input image, and obtain a segmentation overlay that visually represents the segmentation masks along with human-readable class labels.

- **Visualizing the Output**:  
  Use tools such as OpenCV to display the segmentation overlay, enabling you to review and analyze the segmented regions.

By following these steps, you can seamlessly deploy and visualize YOLOv8/YOLO11 segmentation models on Hailo devices using PySDK.

---
## Configuring the Model JSON File

Since the segmentation postprocessing is integrated in C++ with PySDK, the JSON configuration is straightforward. In addition to specifying pre-processing and the model file, you will also provide the COCO labels file, the number of classes, and a confidence threshold to filter low-probability detections.

### Example Model JSON (`yolov8n_seg.json`)

```json
{
    "ConfigVersion": 10,
    "DEVICE": [
        {
            "DeviceType": "HAILO8",
            "RuntimeAgent": "HAILORT",
            "SupportedDeviceTypes": "HAILORT/HAILO8"
        }
    ],
    "PRE_PROCESS": [
        {
            "InputType": "Image",
            "InputN": 1,
            "InputH": 640,
            "InputW": 640,
            "InputC": 3,
            "InputPadMethod": "letterbox",
            "InputResizeMethod": "bilinear",
            "InputQuantEn": true
        }
    ],
    "MODEL_PARAMETERS": [
        {
            "ModelPath": "yolov8n_seg.hef"
        }
    ],
    "POST_PROCESS": [
        {
            "OutputPostprocessType": "SegmentationYoloV8",
            "LabelsPath": "labels_coco.json",
            "OutputNumClasses": 80,
            "OutputConfThreshold": 0.3,
            "SigmoidOnCLS": true
        }
    ]
}
```

### Key Points

- **Pre-Processing Section**:  
  The input image is resized to **1 x 640 x 640 x 3** using letterbox padding and bilinear interpolation, with quantization enabled.

- **Model Parameters Section**:  
  Specifies the segmentation model file (`yolov8n_seg.hef`).

- **Post-Processing Section**:  
  - `"OutputPostprocessType": "SegmentationYoloV8"` activates the built-in C++ segmentation postprocessing. This setting works for both YOLOv8 and YOLO11 models.
  - `"LabelsPath": "labels_coco.json"` provides the COCO labels for human-readable output.
  - `"OutputNumClasses": 80` specifies the number of classes in the model.
  - `"OutputConfThreshold": 0.3` filters out detections below the confidence threshold.
  - **Understanding SigmoidOnCLS**:  
    The `"SigmoidOnCLS": true` flag indicates that a sigmoid activation is applied on certain output layers. This flag is necessary when models are compiled with vendor-specific settings that apply sigmoid activations; adjust this flag as needed for your model.

---

## Preparing the Model Zoo

A **model zoo** is a structured repository of model assets (configuration JSON files, model files, post-processor code, and labels) that simplifies model management. To organize your assets:
1. Save the JSON configuration as `yolov8n_seg.json`.
2. Place the segmentation model file (`yolov8n_seg.hef`) in the same directory.
3. Include the COCO labels file as `labels_coco.json`.

Your directory structure might look like:

```
/path/to/model_zoo/
├── yolov8n_seg.json
├── yolov8n_seg.hef
└── labels_coco.json
```

*Tip*: For easier maintenance, you can organize models into separate subdirectories. PySDK will automatically search for model JSON files in all subdirectories specified by the `zoo_url`. 

---

## Running Inference

Once your model zoo is set up, running inference is nearly identical to the process for detection models. The inference output includes an overlay image with segmentation masks and COCO labels.

### Python Code Example

```python
import degirum as dg
import cv2

# Load the segmentation model from the model zoo.
# Replace '<path_to_model_zoo>' with the directory path to your model assets.
model = dg.load_model(
    model_name='yolov8n_seg',
    inference_host_address='@local',
    zoo_url='<path_to_model_zoo>'
)

# Run inference on an input image.
# Replace '<path_to_input_image>' with the actual path to your image.
inference_result = model('<path_to_input_image>')

# The segmentation overlay (with masks and labels) is available via the image_overlay attribute.
cv2.imshow("Segmentation Output", inference_result.image_overlay)

# Wait until the user presses 'x' or 'q' to close the window.
while True:
    key = cv2.waitKey(0) & 0xFF
    if key == ord('x') or key == ord('q'):
        break

cv2.destroyAllWindows()
```

### Expected Output

The displayed window should show the input image with segmentation masks overlaid. Each segment will be highlighted with distinct colors, and the COCO class labels will be visible on the overlay.  

*Example output showing a cat image with segmented regions and labeled classes.*

![cat_seg_overlay](../assets/cat_overlay_seg.PNG)

---

## Troubleshooting and Debug Tips

- **Verify File Paths**:  
  Ensure that the JSON configuration file, model file, and labels file are in the correct locations, and that the paths specified in the JSON (e.g., `"ModelPath"` and `"LabelsPath"`) match the actual file names.

- **Input Dimensions**:  
  Confirm that the dimensions specified in the `PRE_PROCESS` section (e.g., 640×640) match your model's input requirements.

- **Number of Classes**:  
  Double-check that `"OutputNumClasses"` is correctly set to the number of classes your model detects.

- **SigmoidOnCLS Flag**:  
  If you experience unexpected behavior in the postprocessed output, verify that the `"SigmoidOnCLS"` flag is correctly configured for your model’s compiled settings.

---

## Conclusion

This guide has shown you how to run YOLOv8/YOLO11 segmentation models on Hailo devices using DeGirum PySDK. By simply specifying `"OutputPostprocessType": "SegmentationYoloV8"`, providing a COCO labels file (`labels_coco.json`), and correctly setting parameters such as `"OutputNumClasses"`, `"OutputConfThreshold"`, and `"SigmoidOnCLS"`, you enable the built-in C++ segmentation postprocessing. This converts raw model outputs into visually interpretable segmentation masks with human-readable labels.

The method outlined here also applies to any custom YOLOv8/YOLO11 segmentation model compiled for Hailo devices—simply adjust the JSON configuration (especially the labels file and number of classes) to match your model’s specifications.

