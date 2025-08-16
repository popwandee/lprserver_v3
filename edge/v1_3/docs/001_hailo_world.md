# Hailo World: Running Your First Inference on a Hailo Device Using DeGirum PySDK  

This guide is for ML developers who want to learn how to configure DeGirum PySDK to load a precompiled model and run inference on a Hailo device. Instead of a "just run this magic two line script" approach, we’ll focus on the essential details and steps involved. By the end of this guide, you’ll have a solid understanding of how to work with precompiled models and adapt the process to your needs.

---

## What You'll Need to Begin  

To follow this guide, you’ll need a machine equipped with a Hailo AI accelerator, either Hailo8 or Hailo8L. The host CPU can be an x86 system or an Arm based system (like Raspberry Pi). Before diving in, make sure the necessary drivers and software tools are installed correctly. You can find the setup instructions here: [Hailo + PySDK setup instructions](https://github.com/DeGirum/hailo_examples/blob/main/README.md).  

Here’s what else you’ll need:  

1. **A Model File (`.hef`)**: This is the compiled model for Hailo hardware. We’ll be using the `mobilenet_v2_1.0` classification model, available for Hailo8 devices at [Hailo8 Classification Models](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_classification.rst).  
2. **An Input Image**: The image you want to process using the model. For this guide, we’ll use a cat image, which you can download from [Cat Image](https://raw.githubusercontent.com/DeGirum/hailo_examples/refs/heads/main/assets/Cat.jpg).  
3. **A Labels File (`labels_ILSVRC2012_1000.json`)**: This file maps class indices to human-readable labels for ImageNet. You can download it from [Hugging Face](https://huggingface.co/datasets/huggingface/label-files/blob/main/imagenet-1k-id2label.json).  

Download these assets and keep them handy, as you’ll use them throughout this guide.

---  

## Summary  

In this guide, we’ll walk you through the steps to run inference on a Hailo device using DeGirum PySDK. Here’s what we’ll cover:  

- [Loading a Model with DeGirum PySDK](#loading-a-model-with-degirum-pysdk): Learn how to use the `load_model` function to configure and load a precompiled model in PySDK.  
- [Understanding the Model JSON File](#understanding-the-model-json-file): Explore how the model JSON file defines key configurations for pre-processing, model parameters, and post-processing.  
- [Preparing the Model Zoo](#preparing-the-model-zoo): Organize the model files (`.json`, `.hef`, and labels file) for seamless use with PySDK.  
- [Running Inference](#running-inference): Write Python code to load the model, preprocess the input, run inference, and process the output manually.  
- [Leveraging Built-in PySDK Features](#leveraging-built-in-pysdk-features): Replace manual pipelines with PySDK’s built-in pre-processing and post-processing features, simplifying your workflow.  

By the end of this guide, you’ll have a comprehensive understanding of how to configure, load, and run both manual and optimized pipelines using PySDK.  

## Loading a Model with DeGirum PySDK  

The starting point for running inference with DeGirum PySDK is the **`load_model`** function. This function loads an ML model and returns a model object, which you can use to run inferences. For this guide, the function takes three arguments:  

1. **`model_name`**: The name of the ML model to be used for inference. This is the name of the model's JSON file, without the `.json` extension (explained further under `zoo_url`).  
2. **`inference_host_address`**: Specifies where inference will run. PySDK supports three options:  
   - **`@local`**: Runs inference on a local machine with a connected device (e.g., Hailo8).  
   - **`ai_server_ip`**: Runs inference on an AI server.  
   - **`@cloud`**: Runs inference on devices hosted in the DeGirum AI Hub.  
   For this guide, we’ll use **`@local`** since we are working with a Hailo8 accelerator attached to our machine.  
3. **`zoo_url`**: Points to the model zoo containing model assets. For local inference, this is the path to the directory with all required assets. Each model in the zoo has a JSON file containing metadata like preprocessing steps, model parameters, and postprocessing details.  

---

## Understanding the Model JSON File  

The model JSON file defines key configurations for the model, such as supported devices, preprocessing requirements, model paths, and postprocessing steps. Below is a simple example of a model JSON file that directly passes the input to the model and outputs raw results without additional processing:  

### Example: Simple Model JSON  

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
            "InputType": "Tensor",
            "InputN": 1,
            "InputH": 224,
            "InputW": 224,
            "InputC": 3,                
            "InputRawDataType": "DG_UINT8"
        }
    ],
    "MODEL_PARAMETERS": [
        {
            "ModelPath": "mobilenet_v2_1.0.hef"
        }
    ],
    "POST_PROCESS": [
        {
            "OutputPostprocessType": "None"
        }
    ]
}
```

### Breaking Down the JSON  

#### **ConfigVersion**  
Specifies the JSON schema version. The current version is `10`.  

#### **DEVICE**  
Defines the supported hardware. For Hailo devices:  
- `DeviceType`: Use `HAILO8` for Hailo8 devices and `HAILO8L` for Hailo8L devices.  
- `RuntimeAgent`: Set to `HAILORT`.  

This ensures the model isn’t loaded onto incompatible hardware.  

#### **PRE_PROCESS**  
Describes how input data should be formatted before inference. In this guide, we’ve simplified preprocessing by configuring PySDK to pass the input directly to the model without alteration.  

- `InputType`: Set to `Tensor` to indicate the input is already preprocessed.  
- `InputN`, `InputH`, `InputW`, `InputC`: Define the input’s batch size, height, width, and channels.  
- `InputRawDataType`: Specifies the input’s data type (e.g., `DG_UINT8`).  

> **Note**: The input size (`InputH`, `InputW`, `InputC`) and type (`InputRawDataType`) are essential for validation purposes. PySDK uses these to check that the input data matches the model's requirements before running inference.  

#### **MODEL_PARAMETERS**  
Specifies the `ModelPath`, which is the path to the compiled `.hef` file required by Hailo devices.  

#### **POST_PROCESS**  
Defines how to handle the model’s raw output. In this guide, `OutputPostprocessType` is set to `None`, allowing you to work directly with raw model outputs. Advanced guides will explore PySDK’s built-in postprocessors, which can interpret outputs like bounding boxes, class labels, or keypoints.  

---

## Preparing the Model Zoo  

Now that you understand the structure of the model JSON file, it’s time to organize your model assets. Choose a directory where you want to store all the assets for your models.  

1. Copy the JSON configuration example above into a file named `mobilenet_v2_1.0.json`.  
2. Place the corresponding `mobilenet_v2_1.0.hef` file in the same directory.  
3. Place the labels file in the same directory

If you prefer to organize models into separate directories for easier maintenance, you can create a dedicated directory for each model and store its assets there. PySDK will automatically search for model JSON files in all sub-directories of the specified `zoo_url`.  

---

## Running Inference  

The `mobilenet_v2_1.0` model takes a **UINT8 array** of size `[1, 224, 224, 3]` as input and outputs a **UINT8 array** of size `[1, 1, 1, 1001]`. Let’s start with a utility function that prepares the input image in the required format:  

### Utility Function to Prepare Input  

```python
import cv2
import numpy as np

def resize_image_to_given_shape(image_path, input_shape=(1, 224, 224, 3)):
    """
    Reads an image using OpenCV, resizes it with INTER_LINEAR interpolation, and ensures it matches the specified size.

    Args:
        image_path (str): Path to the input image.
        input_shape (tuple): Desired shape of the output array (batch_size, height, width, channels).

    Returns:
        np.ndarray: Image array of shape matching the input shape.
    """
    if len(input_shape) != 4 or input_shape[0] != 1 or input_shape[3] != 3:
        raise ValueError("Input shape must be in the format (1, height, width, 3).")
    
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Image at path '{image_path}' could not be loaded.")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize the image using INTER_LINEAR interpolation
    resized_image = cv2.resize(image, (input_shape[2], input_shape[1]), interpolation=cv2.INTER_LINEAR)
    
    if resized_image.shape != (input_shape[1], input_shape[2], input_shape[3]):
        raise ValueError(f"Resized image has an unexpected shape: {resized_image.shape}")
    
    # Expand dimensions to match the batch size
    return np.expand_dims(resized_image, axis=0)
```

### Running Inference  

Now let’s load the model, prepare the input image, and run inference:  

```python
import degirum
from pprint import pprint

# Load the model
model = dg.load_model(
    model_name='mobilenet_v2_1.0',
    inference_host_address='@local',
    zoo_url='<path_to_model_zoo>'
)

# Prepare the input image
image_array = resize_image_to_given_shape('<path_to_cat_image>', model.input_shape[0])

# Run inference
inference_result = model(image_array)

# Pretty print the results
pprint(inference_result.results)
```

### Interpreting the Results  

The `inference_result` is of type `degirum.postprocessor.InferenceResults`. For now, we focus on `inference_result.results`, which is a list of dictionaries. Here’s how the output looks like:  

```bash
[{'data': array([[[[0, 0, 0, ..., 0, 0, 0]]]], dtype=uint8),
  'id': 0,
  'name': 'mobilenet_v2_1_0/softmax1',
  'quantization': {'axis': -1, 'scale': [0.003921568859368563], 'zero': [0]},
  'shape': [1, 1, 1, 1001],
  'size': 1001,
  'type': 'DG_UINT8'}]
```

The output is a **UINT8 array** of shape `[1, 1, 1, 1001]`, representing the probabilities of each of the 1001 ImageNet classes (1000 categories + 1 background class).  

---

### Post-Processing  

The raw output from the model contains probabilities for all 1001 classes in the ImageNet dataset. To make the results meaningful, we extract the top-5 predictions and map them to their corresponding class labels using a labels file.  

However, there’s a critical step to consider: **adjusting the class index**. Some models trained on datasets like ImageNet include an extra "background" class, which results in an off-by-one mismatch between the model's output and the labels file. This adjustment ensures the predictions are mapped correctly to their labels.  

Below is a function that performs the necessary post-processing, including dequantizing the raw output, extracting the top-k predictions, and mapping the adjusted class indices to labels:  

```python
import numpy as np
import json

def postprocess_classification_output(output, labels_file, topk=5):
    """
    Postprocesses the model output to extract top-k predictions, maps them to labels,
    and adjusts class indices based on label length compatibility.

    Args:
        output (list): The raw model output containing quantized data and metadata.
        labels_file (str): Path to the JSON file containing the list of labels.
        topk (int): Number of top predictions to extract.

    Returns:
        list of dict: List of dictionaries containing adjusted_class_id, class_id, labels, and probabilities.
    """
    # Load labels from the JSON file
    with open(labels_file, "r") as f:
        labels = json.load(f)  

    # Extract the first output (assuming only one output is present)
    output_data = output[0]

    # Extract relevant fields
    data = output_data['data']  # Quantized data
    scale = output_data['quantization']['scale'][0]  # Quantization scale
    zero = output_data['quantization']['zero'][0]  # Quantization zero point

    # Dequantize the data
    dequantized_data = (data.astype(np.float32) - zero) * scale

    # Flatten the data (assumes shape [1, 1, 1, N])
    dequantized_data = dequantized_data.flatten()

    # Get the top-k indices and probabilities
    top_k_indices = np.argsort(dequantized_data)[-topk:][::-1]  # Indices of top-k predictions
    top_k_probs = dequantized_data[top_k_indices]  # Probabilities of top-k predictions

    # Determine if class_index should be adjusted
    if len(labels) == len(dequantized_data):
        subtract_one = False
    elif len(labels) == len(dequantized_data) - 1:
        subtract_one = True
    else:
        print(f"Warning: Labels file is not compatible with output results. "
              f"Labels length: {len(labels)}, Output length: {len(dequantized_data)}")
        return []    

    # Process the results and map to labels
    processed_results = []
    for class_index, probability in zip(top_k_indices, top_k_probs):
        if subtract_one:
            # Adjust class_index if needed
            adjusted_class_index = class_index - 1
            if class_index == 0:
                label = "Background"  # Background class exists only when subtract_one is True
            elif 0 <= adjusted_class_index < len(labels):
                label = labels[str(adjusted_class_index)]
            else:
                label = "Unknown"
        else:
            # No adjustment needed for class_index
            adjusted_class_index = class_index
            if 0 <= adjusted_class_index < len(labels):
                label = labels[str(adjusted_class_index)]
            else:
                label = "Unknown"

        processed_results.append({
            "category_id": adjusted_class_index,
            "label": label,
            "score": probability
        })

    return processed_results
```

### Top-5 Predictions  

You can use the above function to get the top 5 predictions as follows:  

```python
top5_predictions = postprocess_classification_output(inference_result.results, '<path_to_labels_file>', topk=5)
pprint(top5_predictions)
```

### Example Output  

```bash
[{'category_id': 285, 'label': 'Egyptian cat', 'score': 0.20000002},
 {'category_id': 287, 'label': 'lynx, catamount', 'score': 0.16078432},
 {'category_id': 282, 'label': 'tiger cat', 'score': 0.14117648},
 {'category_id': 281, 'label': 'tabby, tabby cat', 'score': 0.121568635},
 {'category_id': 189, 'label': 'Lakeland terrier', 'score': 0.011764707}]
```
--- 

### Conclusion  

With this workflow, you can run inference on any compiled model using Hailo devices and DeGirum PySDK. While basic inference might be possible without PySDK, the real advantage of PySDK is its ability to simplify the development of complex AI applications. Future guides will explore advanced features, but this guide gives you a strong foundation to start experimenting!  

---

## Leveraging Built-in PySDK Features  

The code provided in this guide is instructive and easy to follow but not practical for production systems. Developers often write boilerplate code for tasks like pre-processing and post-processing for each model, leading to scattered snippets that must be carried along with the application code. Over time, this approach becomes cumbersome, and developers start building structured classes to avoid repetition, which can eventually balloon into a development effort of its own.  

At DeGirum, we’ve been down this road and recognized that managing pre-processing and post-processing code is a significant challenge when working with ML models. While we don’t claim to have a universal solution, PySDK provides a framework that simplifies this process. For common use cases and popular model architectures, PySDK integrates highly optimized C++ post-processors and built-in pre-processors, enabling developers to focus on solving real-world problems instead of writing repetitive code.

To illustrate the power of PySDK, here’s an example of a modified JSON configuration that leverages PySDK’s built-in pre-processors and post-processors. This configuration handles tasks like resizing, padding, quantization, and classification post-processing directly within PySDK, eliminating the need for custom Python code:  

### JSON with Built-in Pre-Processor and Post-Processor  

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
      "ImageBackend": "opencv",
      "InputPadMethod": "stretch",
      "InputResizeMethod": "bilinear",
      "InputN": 1,
      "InputH": 224,
      "InputW": 224,
      "InputC": 3,
      "InputQuantEn": true
    }
  ],
  "MODEL_PARAMETERS": [
    {
      "ModelPath": "mobilenet_v2_1.0.hef"
    }
  ],
  "POST_PROCESS": [
    {
      "OutputPostprocessType": "Classification",
      "OutputTopK": 5,
      "OutputNumClasses": 1000,
      "OutputClassIDAdjustment": 1,
      "LabelsPath": "labels_ILSVRC2012_1000.json"
    }
  ]
}
```
### Instructions  

1. Save this modified JSON file as `mobilenet_v2_1.0_optimized.json` in your model zoo directory.  

2. Ensure that the corresponding `.hef` file (`mobilenet_v2_1.0.hef`) and the labels file (`labels_ILSVRC2012_1000.json`) are also present in the same model zoo directory.  

3. Update your Python code to use this new JSON file by specifying the updated `model_name` and `zoo_url`.  

4. Simplify your Python code by removing the manual pre-processing and post-processing logic, as PySDK’s built-in handlers now take care of these steps. The simplified code looks like this:  

```python
import degirum
from pprint import pprint

# Load the optimized model JSON
model = dg.load_model(
    model_name='mobilenet_v2_1.0_optimized',
    inference_host_address='@local',
    zoo_url='<path_to_model_zoo>'
)

# Run inference directly on the image
inference_result = model('<path_to_cat_image>')

# Print the results directly
pprint(inference_result.results)
```

5. Run the updated code and observe the results. You’ll see that the output is similar to the manually implemented pipeline, but the code is significantly cleaner and easier to maintain.  

### Benefits of Using Built-in Features  

- **Simplified Code**: The JSON configuration handles pre-processing and post-processing tasks, reducing boilerplate code in your application.  
- **Optimized Performance**: Built-in features are implemented in highly optimized C++ for better speed and reliability.  
- **Ease of Maintenance**: Centralizing logic in the JSON file makes it easier to share and reuse configurations across projects.  

With PySDK, you can quickly get models up and running while leveraging its built-in tools to develop complex applications with minimal effort. This guide is just the starting point—explore our [PySDK Examples Repo](https://github.com/degirum/pysdkexamples), [Hailo Examples Repo](https://github.com/DeGirum/hailo_examples), and [official documentation](https://docs.degirum.com) to dive deeper into advanced capabilities.  

---

