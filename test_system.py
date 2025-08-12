#!/usr/bin/env python3
"""
Test Script for LPR Server v3
ใช้สำหรับทดสอบระบบทั้งหมด
"""

import requests
import socketio
import time
import json
import base64
from datetime import datetime
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_web_interface():
    """Test web interface endpoints"""
    print("=== Testing Web Interface ===")
    
    base_url = "http://localhost"
    
    # Test main page
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Main page accessible")
        else:
            print(f"❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page error: {str(e)}")
    
    # Test dashboard
    try:
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard accessible")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
    
    # Test records page
    try:
        response = requests.get(f"{base_url}/records")
        if response.status_code == 200:
            print("✅ Records page accessible")
        else:
            print(f"❌ Records page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Records page error: {str(e)}")
    
    # Test blacklist page
    try:
        response = requests.get(f"{base_url}/blacklist")
        if response.status_code == 200:
            print("✅ Blacklist page accessible")
        else:
            print(f"❌ Blacklist page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Blacklist page error: {str(e)}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    base_url = "http://localhost/api"
    
    # Test statistics endpoint
    try:
        response = requests.get(f"{base_url}/statistics")
        if response.status_code == 200:
            data = response.json()
            print("✅ Statistics API working")
            print(f"   - Total records: {data.get('total_records', 0)}")
            print(f"   - Today records: {data.get('today_records', 0)}")
            print(f"   - Unique cameras: {data.get('unique_cameras', 0)}")
        else:
            print(f"❌ Statistics API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics API error: {str(e)}")
    
    # Test records endpoint
    try:
        response = requests.get(f"{base_url}/records")
        if response.status_code == 200:
            data = response.json()
            print("✅ Records API working")
            print(f"   - Records count: {len(data.get('records', []))}")
        else:
            print(f"❌ Records API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Records API error: {str(e)}")
    
    # Test blacklist endpoints
    try:
        response = requests.get(f"{base_url}/blacklist")
        if response.status_code == 200:
            data = response.json()
            print("✅ Blacklist API working")
            print(f"   - Blacklist entries: {len(data.get('blacklist', []))}")
        else:
            print(f"❌ Blacklist API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Blacklist API error: {str(e)}")
    
    # Test blacklist statistics
    try:
        response = requests.get(f"{base_url}/blacklist/statistics")
        if response.status_code == 200:
            data = response.json()
            print("✅ Blacklist statistics API working")
            print(f"   - Total blacklist entries: {data.get('total_blacklist_entries', 0)}")
            print(f"   - Total detections: {data.get('total_blacklist_detections', 0)}")
        else:
            print(f"❌ Blacklist statistics API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Blacklist statistics API error: {str(e)}")

def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n=== Testing WebSocket Connection ===")
    
    try:
        # Create SocketIO client
        sio = socketio.Client()
        
        # Connect to WebSocket server
        sio.connect('http://localhost:8765')
        print("✅ WebSocket connection established")
        
        # Test camera registration
        sio.emit('camera_register', {'camera_id': 'TEST_CAM'})
        time.sleep(1)
        
        # Check for response
        received = sio.get_received()
        if received:
            print("✅ Camera registration working")
        else:
            print("⚠️  No response from camera registration")
        
        # Test LPR data transmission
        test_image_data = base64.b64encode(b'test_image_data').decode('utf-8')
        lpr_data = {
            'camera_id': 'TEST_CAM',
            'plate_number': 'TEST123',
            'confidence': 85.5,
            'image_data': f'data:image/jpeg;base64,{test_image_data}',
            'location': 'Test Location',
            'location_lat': 13.7563,
            'location_lon': 100.5018
        }
        
        sio.emit('lpr_data', lpr_data)
        time.sleep(1)
        
        # Check for response
        received = sio.get_received()
        if received:
            print("✅ LPR data transmission working")
        else:
            print("⚠️  No response from LPR data transmission")
        
        # Disconnect
        sio.disconnect()
        print("✅ WebSocket connection closed")
        
    except Exception as e:
        print(f"❌ WebSocket test failed: {str(e)}")

def test_blacklist_functionality():
    """Test blacklist functionality"""
    print("\n=== Testing Blacklist Functionality ===")
    
    base_url = "http://localhost/api"
    
    # Test adding to blacklist
    try:
        blacklist_data = {
            'license_plate_text': 'TEST123',
            'reason': 'Test blacklist entry',
            'added_by': 'test_user',
            'notes': 'Test notes'
        }
        
        response = requests.post(f"{base_url}/blacklist", json=blacklist_data)
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print("✅ Add to blacklist working")
                blacklist_id = data.get('blacklist_id')
                
                # Test removing from blacklist
                response = requests.delete(f"{base_url}/blacklist/{blacklist_id}?removed_by=test_user")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print("✅ Remove from blacklist working")
                    else:
                        print(f"❌ Remove from blacklist failed: {data.get('message')}")
                else:
                    print(f"❌ Remove from blacklist failed: {response.status_code}")
            else:
                print(f"❌ Add to blacklist failed: {data.get('message')}")
        else:
            print(f"❌ Add to blacklist failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Blacklist functionality test failed: {str(e)}")

def test_database_operations():
    """Test database operations"""
    print("\n=== Testing Database Operations ===")
    
    try:
        from src.app import create_app, db
        from src.models.lpr_record import LPRRecord
        from src.models.camera import Camera
        from src.models.blacklist_plate import BlacklistPlate
        
        app = create_app()
        
        with app.app_context():
            # Test database connection
            db.session.execute('SELECT 1')
            print("✅ Database connection working")
            
            # Test table existence
            tables = ['lpr_records', 'cameras', 'blacklist_plates']
            for table in tables:
                try:
                    db.session.execute(f'SELECT COUNT(*) FROM {table}')
                    print(f"✅ Table {table} exists")
                except Exception as e:
                    print(f"❌ Table {table} error: {str(e)}")
            
            # Test record count
            record_count = LPRRecord.query.count()
            print(f"✅ LPR records count: {record_count}")
            
            camera_count = Camera.query.count()
            print(f"✅ Cameras count: {camera_count}")
            
            blacklist_count = BlacklistPlate.query.count()
            print(f"✅ Blacklist entries count: {blacklist_count}")
            
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")

def test_system_services():
    """Test system services"""
    print("\n=== Testing System Services ===")
    
    import subprocess
    
    # Test if services are running
    services = ['lprserver.service', 'lprserver-websocket.service', 'nginx']
    
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip() == 'active':
                print(f"✅ {service} is running")
            else:
                print(f"❌ {service} is not running")
        except Exception as e:
            print(f"❌ Error checking {service}: {str(e)}")

def main():
    """Main test function"""
    print("LPR Server v3 - System Test")
    print("=" * 50)
    
    # Test web interface
    test_web_interface()
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test WebSocket connection
    test_websocket_connection()
    
    # Test blacklist functionality
    test_blacklist_functionality()
    
    # Test database operations
    test_database_operations()
    
    # Test system services
    test_system_services()
    
    print("\n" + "=" * 50)
    print("System test completed!")

if __name__ == '__main__':
    main()
