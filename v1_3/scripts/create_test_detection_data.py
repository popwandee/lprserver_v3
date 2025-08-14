#!/usr/bin/env python3
"""
Create test detection data with actual images
"""

import os
import cv2
import numpy as np
from datetime import datetime
from database_manager import DatabaseManager
import uuid

def create_test_image(text, filename, size=(640, 640)):
    """Create a test image with text"""
    # Create a blank image
    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img.fill(255)  # White background
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    color = (0, 0, 0)  # Black text
    thickness = 3
    
    # Get text size
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    # Center the text
    x = (size[0] - text_size[0]) // 2
    y = (size[1] + text_size[1]) // 2
    
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness)
    
    # Save image
    cv2.imwrite(filename, img)
    return filename

def create_test_data():
    """Create test detection data"""
    print("Creating test detection data...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Ensure directories exist
    os.makedirs('/home/camuser/aicamera/captured_images', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Test license plates
    test_plates = [
        "กข1234",
        "ABC123",
        "XYZ789", 
        "123กข456",
        "DEF456"
    ]
    
    for i, plate in enumerate(test_plates):
        try:
            # Create test images
            vehicle_img = f"test_vehicle_{i+1}.jpg"
            lp_img = f"test_lp_{i+1}.jpg"
            
            vehicle_path = os.path.join('/home/camuser/aicamera/captured_images', vehicle_img)
            lp_path = os.path.join('/home/camuser/aicamera/captured_images', lp_img)
            
            # Create images
            create_test_image(f"Vehicle {i+1}", vehicle_path)
            create_test_image(plate, lp_path, size=(256, 128))
            
            # Create symbolic links in static/images
            static_vehicle = os.path.join('static/images', vehicle_img)
            static_lp = os.path.join('static/images', lp_img)
            
            if os.path.exists(static_vehicle):
                os.remove(static_vehicle)
            if os.path.exists(static_lp):
                os.remove(static_lp)
                
            os.symlink(os.path.abspath(vehicle_path), static_vehicle)
            os.symlink(os.path.abspath(lp_path), static_lp)
            
            # Insert into database
            frame_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # Insert camera metadata
            db.cursor.execute('''
                INSERT INTO camera_metadata (
                    timestamp, frame_id, exposure_time, analog_gain, digital_gain,
                    lux, colour_temperature, lens_position, focus_state,
                    image_filename, processed_image_filename
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(), frame_id, 1.0/30, 2.0, 1.5, 
                100.0, 5000.0, 0.5, 1, vehicle_img, lp_img
            ))
            
            # Insert detection result
            db.cursor.execute('''
                INSERT INTO detection_results (
                    frame_id, license_plate_text, lp_confidence,
                    lp_box_x, lp_box_y, lp_box_w, lp_box_h, lp_image_filename
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                frame_id, plate, 0.95, 100, 200, 200, 100, lp_img
            ))
            
            db.conn.commit()
            print(f"Created test data for license plate: {plate}")
            
        except Exception as e:
            print(f"Error creating test data for {plate}: {e}")
    
    print("Test detection data created successfully!")
    
    # Show summary
    db.cursor.execute("SELECT COUNT(*) FROM detection_results WHERE license_plate_text != 'VEHICLE_ONLY'")
    real_plates = db.cursor.fetchone()[0]
    print(f"Total records with real license plates: {real_plates}")

if __name__ == "__main__":
    create_test_data()