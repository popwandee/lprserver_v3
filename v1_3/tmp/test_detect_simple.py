#!/usr/bin/env python3

"""Simple Hailo Detection Test with Post-processing."""

import argparse
import time
import json
import os

import cv2
import numpy as np

from picamera2 import Picamera2
from picamera2.devices import Hailo


def load_labels(labels_path):
    """Load labels from JSON or TXT file."""
    if labels_path.endswith('.json'):
        with open(labels_path, 'r') as f:
            labels_dict = json.load(f)
            # Convert to list if it's a dictionary
            if isinstance(labels_dict, dict):
                labels = [None] * len(labels_dict)
                for key, value in labels_dict.items():
                    labels[int(key)] = value
                return labels
            return labels_dict
    else:
        with open(labels_path, 'r', encoding="utf-8") as f:
            return f.read().splitlines()


def test_hailo_model(model_path, labels_path, num_frames=5):
    """Test Hailo model with camera input."""
    
    print(f"Testing Hailo model: {model_path}")
    print(f"Labels file: {labels_path}")
    print(f"Processing {num_frames} frames...")
    
    # Load labels
    labels = load_labels(labels_path)
    print(f"Loaded {len(labels)} labels")
    
    # Initialize Hailo
    with Hailo(model_path) as hailo:
        model_h, model_w, _ = hailo.get_input_shape()
        print(f"Model input shape: {model_w}x{model_h}")
        
        # Initialize camera
        with Picamera2() as picam2:
            # Configure camera
            main = {'size': (1280, 960), 'format': 'XRGB8888'}
            lores = {'size': (model_w, model_h), 'format': 'RGB888'}
            controls = {'FrameRate': 30}
            config = picam2.create_preview_configuration(main, lores=lores, controls=controls)
            picam2.configure(config)
            picam2.start()
            
            print("Camera started successfully")
            
            # Process frames
            frame_count = 0
            start_time = time.time()
            
            while frame_count < num_frames:
                # Capture frame
                frame = picam2.capture_array('lores')
                frame_count += 1
                
                print(f"\nFrame {frame_count}:")
                print(f"Frame shape: {frame.shape}")
                print(f"Frame dtype: {frame.dtype}")
                
                # Run inference
                try:
                    results = hailo.run(frame)
                    print(f"Inference successful")
                    print(f"Results type: {type(results)}")
                    
                    if isinstance(results, dict):
                        print(f"Output keys: {list(results.keys())}")
                        for key, value in results.items():
                            if isinstance(value, np.ndarray):
                                print(f"  {key}: shape={value.shape}, dtype={value.dtype}")
                            else:
                                print(f"  {key}: {type(value)}")
                    
                except Exception as e:
                    print(f"Inference error: {e}")
                
                # Small delay
                time.sleep(0.1)
            
            end_time = time.time()
            total_time = end_time - start_time
            fps = frame_count / total_time
            
            print(f"\nTest completed!")
            print(f"Processed {frame_count} frames in {total_time:.2f} seconds")
            print(f"Average FPS: {fps:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Hailo Detection Test")
    parser.add_argument("-m", "--model", required=True,
                        help="Path to the HEF model file")
    parser.add_argument("-l", "--labels", required=True,
                        help="Path to labels file (JSON or TXT)")
    parser.add_argument("-n", "--num_frames", type=int, default=5,
                        help="Number of frames to process")
    
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        exit(1)
    
    if not os.path.exists(args.labels):
        print(f"Error: Labels file not found: {args.labels}")
        exit(1)
    
    test_hailo_model(args.model, args.labels, args.num_frames)
