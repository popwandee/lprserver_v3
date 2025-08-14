#!/usr/bin/env python3

"""Example module for Hailo Detection."""

import argparse
import time

import cv2

from picamera2 import MappedArray, Picamera2
from picamera2.devices import Hailo


def extract_detections(hailo_output, w, h, class_names, threshold=0.5):
    """Extract detections from the HailoRT-postprocess output."""
    results = []
    
    # Debug: print the structure of hailo_output
    print(f"Debug: hailo_output type: {type(hailo_output)}")
    print(f"Debug: hailo_output length: {len(hailo_output) if hasattr(hailo_output, '__len__') else 'N/A'}")
    
    try:
        # Handle different output formats
        if isinstance(hailo_output, list):
            for class_id, detections in enumerate(hailo_output):
                if isinstance(detections, list):
                    for detection in detections:
                        if len(detection) >= 5:
                            score = detection[4]
                            if score >= threshold:
                                y0, x0, y1, x1 = detection[:4]
                                bbox = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
                                class_name = class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
                                results.append([class_name, bbox, score])
        elif hasattr(hailo_output, 'detections'):
            # Handle structured output
            for detection in hailo_output.detections:
                if hasattr(detection, 'score') and detection.score >= threshold:
                    bbox = (int(detection.bbox.x0 * w), int(detection.bbox.y0 * h), 
                           int(detection.bbox.x1 * w), int(detection.bbox.y1 * h))
                    class_name = class_names[detection.class_id] if detection.class_id < len(class_names) else f"class_{detection.class_id}"
                    results.append([class_name, bbox, detection.score])
        else:
            print(f"Debug: Unexpected output format: {type(hailo_output)}")
            print(f"Debug: Output content: {hailo_output}")
            
    except Exception as e:
        print(f"Error processing detections: {e}")
        print(f"Output structure: {hailo_output}")
    
    return results


def print_detections(detections):
    """Print detections to console."""
    if detections:
        print(f"Found {len(detections)} objects:")
        for class_name, bbox, score in detections:
            x0, y0, x1, y1 = bbox
            print(f"  - {class_name}: {score:.2f} at ({x0},{y0},{x1},{y1})")
    else:
        print("No objects detected")


if __name__ == "__main__":
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(description="Detection Example")
    parser.add_argument("-m", "--model", help="Path for the HEF model.",
                        default="/usr/share/hailo-models/yolov8s_h8l.hef")
    parser.add_argument("-l", "--labels", default="coco.txt",
                        help="Path to a text file containing labels.")
    parser.add_argument("-s", "--score_thresh", type=float, default=0.5,
                        help="Score threshold, must be a float between 0 and 1.")
    parser.add_argument("-n", "--num_frames", type=int, default=10,
                        help="Number of frames to process.")
    args = parser.parse_args()

    print(f"Loading model: {args.model}")
    print(f"Using labels: {args.labels}")
    print(f"Score threshold: {args.score_thresh}")
    print(f"Processing {args.num_frames} frames...")

    # Get the Hailo model, the input size it wants, and the size of our preview stream.
    with Hailo(args.model) as hailo:
        model_h, model_w, _ = hailo.get_input_shape()
        video_w, video_h = 1280, 960

        print(f"Model input shape: {model_w}x{model_h}")
        print(f"Video resolution: {video_w}x{video_h}")

        # Load class names from the labels file
        with open(args.labels, 'r', encoding="utf-8") as f:
            class_names = f.read().splitlines()

        print(f"Loaded {len(class_names)} class names")

        # Configure and start Picamera2.
        with Picamera2() as picam2:
            main = {'size': (video_w, video_h), 'format': 'XRGB8888'}
            lores = {'size': (model_w, model_h), 'format': 'RGB888'}
            controls = {'FrameRate': 30}
            config = picam2.create_preview_configuration(main, lores=lores, controls=controls)
            picam2.configure(config)

            picam2.start()
            print("Camera started successfully")

            # Process frames
            frame_count = 0
            start_time = time.time()
            
            while frame_count < args.num_frames:
                frame = picam2.capture_array('lores')
                frame_count += 1

                # Run inference on the preprocessed frame
                results = hailo.run(frame)

                # Extract detections from the inference results
                detections = extract_detections(results, video_w, video_h, class_names, args.score_thresh)
                
                print(f"\nFrame {frame_count}:")
                print_detections(detections)

            end_time = time.time()
            total_time = end_time - start_time
            fps = frame_count / total_time
            
            print(f"\nProcessing complete!")
            print(f"Processed {frame_count} frames in {total_time:.2f} seconds")
            print(f"Average FPS: {fps:.2f}")