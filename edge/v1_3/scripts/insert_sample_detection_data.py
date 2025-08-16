#!/usr/bin/env python3
"""
Sample Detection Data Insertion Script for AI Camera v1.3

This script inserts sample detection results data into the database
for testing the detection results web UI functionality.

Features:
- Creates 20 sample detection records
- Uses car1.jpg, car2.jpg, car3.jpg as sample images
- Generates realistic vehicle and license plate detection data
- Includes OCR results with Thai and English license plates
- Varies processing times and confidence scores

Usage:
    python3 insert_sample_detection_data.py

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sys
import os
from pathlib import Path
import json
import random
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'v1_3' / 'src'))

from v1_3.src.core.utils.import_helper import setup_import_paths
setup_import_paths()

from v1_3.src.core.utils.logging_config import setup_logging, get_logger
from v1_3.src.components.database_manager import DatabaseManager

# Setup logging
logger = setup_logging(level="INFO")

# Sample data configurations
SAMPLE_IMAGES = ['car1.jpg', 'car2.jpg', 'car3.jpg']

# Thai license plate patterns
THAI_PLATES = [
    'กก 1234 กรุงเทพมหานคร',
    'ขข 5678 กรุงเทพมหานคร', 
    'คค 9012 กรุงเทพมหานคร',
    'งง 3456 กรุงเทพมหานคร',
    'จจ 7890 กรุงเทพมหานคร',
    'ฉฉ 2468 กรุงเทพมหานคร',
    'ชช 1357 กรุงเทพมหานคร',
    'ซซ 9753 กรุงเทพมหานคร',
    'ฌฌ 8642 กรุงเทพมหานคร',
    'ญญ 1928 กรุงเทพมหานคร'
]

# English license plate patterns
ENGLISH_PLATES = [
    'ABC-123',
    'XYZ-789',
    'DEF-456',
    'GHI-012',
    'JKL-345',
    'MNO-678',
    'PQR-901',
    'STU-234',
    'VWX-567',
    'YZA-890'
]

# Vehicle types for detection
VEHICLE_TYPES = ['car', 'truck', 'motorcycle', 'bus', 'van']

def generate_bbox(image_width=1920, image_height=1080):
    """Generate realistic bounding box coordinates."""
    # Vehicle bounding box (larger)
    vehicle_width = random.randint(200, 600)
    vehicle_height = random.randint(150, 400)
    vehicle_x = random.randint(0, image_width - vehicle_width)
    vehicle_y = random.randint(0, image_height - vehicle_height)
    
    return [vehicle_x, vehicle_y, vehicle_x + vehicle_width, vehicle_y + vehicle_height]

def generate_plate_bbox(vehicle_bbox):
    """Generate license plate bounding box within vehicle bbox."""
    vx1, vy1, vx2, vy2 = vehicle_bbox
    
    # License plate is typically in lower portion of vehicle
    plate_width = random.randint(80, 150)
    plate_height = random.randint(30, 60)
    
    # Position plate within vehicle bounds
    plate_x = random.randint(vx1 + 20, max(vx1 + 21, vx2 - plate_width - 20))
    plate_y = random.randint(int(vy1 + (vy2 - vy1) * 0.6), max(int(vy1 + (vy2 - vy1) * 0.6) + 1, vy2 - plate_height - 10))
    
    return [plate_x, plate_y, plate_x + plate_width, plate_y + plate_height]

def generate_vehicle_detection():
    """Generate realistic vehicle detection data."""
    vehicle_type = random.choice(VEHICLE_TYPES)
    confidence = round(random.uniform(0.75, 0.98), 3)
    bbox = generate_bbox()
    
    return {
        'bbox': bbox,
        'confidence': confidence,
        'score': confidence,  # Alternative field name
        'class_name': vehicle_type,
        'label': vehicle_type,
        'category_id': VEHICLE_TYPES.index(vehicle_type)
    }

def generate_plate_detection(vehicle_bbox):
    """Generate realistic license plate detection data."""
    confidence = round(random.uniform(0.65, 0.95), 3)
    bbox = generate_plate_bbox(vehicle_bbox)
    
    return {
        'bbox': bbox,
        'confidence': confidence,
        'score': confidence,
        'class_name': 'license_plate',
        'label': 'license_plate',
        'category_id': 0
    }

def generate_ocr_result():
    """Generate realistic OCR result."""
    # Mix of Thai and English plates
    if random.random() < 0.6:  # 60% Thai plates
        plate_text = random.choice(THAI_PLATES)
        confidence = round(random.uniform(0.70, 0.95), 3)
    else:  # 40% English plates
        plate_text = random.choice(ENGLISH_PLATES)
        confidence = round(random.uniform(0.75, 0.98), 3)
    
    return {
        'text': plate_text,
        'confidence': confidence,
        'language': 'th' if any(char in 'กขคงจฉชซฌญ' for char in plate_text) else 'en'
    }

def generate_sample_detection_record(record_id):
    """Generate a complete sample detection record."""
    # Random timestamp within last 30 days
    base_time = datetime.now() - timedelta(days=random.randint(0, 30))
    timestamp = base_time - timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    
    # Random number of vehicles (1-3)
    num_vehicles = random.randint(1, 3)
    vehicles_count = num_vehicles
    
    # Generate vehicle detections
    vehicle_detections = []
    plate_detections = []
    ocr_results = []
    cropped_plates_paths = []
    
    plates_count = 0
    
    for i in range(num_vehicles):
        # Generate vehicle detection
        vehicle_detection = generate_vehicle_detection()
        vehicle_detections.append(vehicle_detection)
        
        # 70% chance each vehicle has a license plate
        if random.random() < 0.7:
            plates_count += 1
            
            # Generate plate detection
            plate_detection = generate_plate_detection(vehicle_detection['bbox'])
            plate_detections.append(plate_detection)
            
            # Generate OCR result
            ocr_result = generate_ocr_result()
            ocr_results.append(ocr_result)
            
            # Generate cropped plate path
            sample_image = random.choice(SAMPLE_IMAGES)
            cropped_path = f"detection_results/{timestamp.strftime('%Y%m%d')}/plate_{record_id}_{i}.jpg"
            cropped_plates_paths.append(cropped_path)
    
    # Generate processing time (20ms to 200ms)
    processing_time_ms = round(random.uniform(20.0, 200.0), 1)
    
    # Sample image path
    sample_image = random.choice(SAMPLE_IMAGES)
    annotated_image_path = f"detection_results/{timestamp.strftime('%Y%m%d')}/annotated_{record_id}.jpg"
    
    return {
        'timestamp': timestamp.isoformat(),
        'vehicles_count': vehicles_count,
        'plates_count': plates_count,
        'vehicle_detections': vehicle_detections,
        'plate_detections': plate_detections,
        'ocr_results': ocr_results,
        'annotated_image_path': annotated_image_path,
        'cropped_plates_paths': cropped_plates_paths,
        'processing_time_ms': processing_time_ms
    }

def insert_sample_data():
    """Insert sample detection data into database."""
    try:
        # Initialize database manager
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager()
        
        if not db_manager.initialize():
            logger.error("Failed to initialize database")
            return False
        
        logger.info("Database initialized successfully")
        
        # Generate and insert sample records
        logger.info("Generating 20 sample detection records...")
        
        inserted_count = 0
        for i in range(1, 21):  # Generate 20 records
            try:
                # Generate sample record
                record = generate_sample_detection_record(i)
                
                # Insert into database
                record_id = db_manager.insert_detection_result(record)
                
                if record_id:
                    inserted_count += 1
                    logger.info(f"Inserted record {i}/20 - ID: {record_id}, "
                              f"Vehicles: {record['vehicles_count']}, "
                              f"Plates: {record['plates_count']}, "
                              f"OCR: {len(record['ocr_results'])}")
                else:
                    logger.error(f"Failed to insert record {i}")
                    
            except Exception as e:
                logger.error(f"Error inserting record {i}: {e}")
        
        logger.info(f"Successfully inserted {inserted_count}/20 sample records")
        
        # Display statistics
        stats = db_manager.get_detection_statistics()
        logger.info("Database statistics after insertion:")
        logger.info(f"  Total detections: {stats.get('total_detections', 0)}")
        logger.info(f"  Total vehicles: {stats.get('total_vehicles', 0)}")
        logger.info(f"  Total plates: {stats.get('total_plates', 0)}")
        logger.info(f"  Average processing time: {stats.get('avg_processing_time_ms', 0):.1f}ms")
        
        # Cleanup
        db_manager.cleanup()
        logger.info("Sample data insertion completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during sample data insertion: {e}")
        return False

def clear_existing_data():
    """Clear existing detection data (optional)."""
    try:
        db_manager = DatabaseManager()
        if not db_manager.initialize():
            logger.error("Failed to initialize database for clearing data")
            return False
        
        # Get current count
        stats = db_manager.get_detection_statistics()
        current_count = stats.get('total_detections', 0)
        
        if current_count > 0:
            response = input(f"Found {current_count} existing detection records. Clear them? (y/N): ")
            if response.lower() == 'y':
                # Delete all records
                cursor = db_manager.connection.cursor()
                cursor.execute("DELETE FROM detection_results")
                db_manager.connection.commit()
                logger.info(f"Cleared {current_count} existing detection records")
        
        db_manager.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"Error clearing existing data: {e}")
        return False

def main():
    """Main function."""
    logger.info("AI Camera v1.3 - Sample Detection Data Insertion Script")
    logger.info("=" * 60)
    
    try:
        # Check if user wants to clear existing data
        clear_existing_data()
        
        # Insert sample data
        if insert_sample_data():
            logger.info("✅ Sample data insertion completed successfully!")
            logger.info("")
            logger.info("You can now test the detection results UI at:")
            logger.info("  http://localhost:5000/detection_results")
            logger.info("")
            logger.info("Sample data includes:")
            logger.info("  - 20 detection records")
            logger.info("  - Mixed Thai and English license plates")
            logger.info("  - Various vehicle types and counts")
            logger.info("  - Realistic confidence scores and processing times")
            logger.info("  - Timestamps spread over the last 30 days")
        else:
            logger.error("❌ Sample data insertion failed!")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
