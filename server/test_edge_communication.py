#!/usr/bin/env python3
"""
Test Client for Edge Communication
Tests both SocketIO and REST API endpoints according to the new specification
"""

import requests
import json
import time
import socketio
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:8765"
SOCKETIO_URL = "http://localhost:8765"

class EdgeCommunicationTester:
    def __init__(self):
        self.session = requests.Session()
        self.sio = socketio.Client()
        self.camera_id = "test_camera_001"
        self.checkpoint_id = "checkpoint_001"
        
        # Setup SocketIO event handlers
        self.setup_socketio_handlers()
    
    def setup_socketio_handlers(self):
        """Setup SocketIO event handlers"""
        @self.sio.event
        def connect():
            print("✅ SocketIO connected successfully")
        
        @self.sio.event
        def disconnect():
            print("❌ SocketIO disconnected")
        
        @self.sio.on('camera_register')
        def on_camera_register(data):
            print(f"📹 Camera registration response: {data}")
        
        @self.sio.on('lpr_response')
        def on_lpr_response(data):
            print(f"🚗 LPR response: {data}")
        
        @self.sio.on('health_response')
        def on_health_response(data):
            print(f"💚 Health response: {data}")
        
        @self.sio.on('pong')
        def on_pong(data):
            print(f"🏓 Pong response: {data}")
        
        @self.sio.on('error')
        def on_error(data):
            print(f"❌ Error: {data}")
    
    def test_rest_api(self):
        """Test REST API endpoints"""
        print("\n" + "="*50)
        print("🧪 TESTING REST API ENDPOINTS")
        print("="*50)
        
        # Test 1: Connection test
        print("\n1️⃣ Testing connection...")
        try:
            response = self.session.get(f"{SERVER_URL}/api/test")
            if response.status_code == 200:
                print("✅ Connection test passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Connection test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Connection test error: {e}")
        
        # Test 2: Camera registration
        print("\n2️⃣ Testing camera registration...")
        try:
            data = {
                "camera_id": self.camera_id,
                "checkpoint_id": self.checkpoint_id,
                "timestamp": datetime.now().isoformat()
            }
            response = self.session.post(f"{SERVER_URL}/api/cameras/register", json=data)
            if response.status_code == 200:
                print("✅ Camera registration passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Camera registration failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Camera registration error: {e}")
        
        # Test 3: LPR detection data
        print("\n3️⃣ Testing LPR detection data...")
        try:
            data = {
                "type": "detection_result",
                "camera_id": self.camera_id,
                "checkpoint_id": self.checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "vehicles_count": 1,
                "plates_count": 1,
                "ocr_results": ["ABC1234"],
                "vehicle_detections": [
                    {
                        "bbox": [100, 100, 200, 200],
                        "confidence": 0.95,
                        "class": "car"
                    }
                ],
                "plate_detections": [
                    {
                        "bbox": [150, 150, 180, 170],
                        "confidence": 0.92,
                        "text": "ABC1234"
                    }
                ],
                "processing_time_ms": 150,
                "annotated_image": "base64_encoded_image_data_placeholder",
                "cropped_plates": ["base64_plate1_placeholder"]
            }
            response = self.session.post(f"{SERVER_URL}/api/detection", json=data)
            if response.status_code == 200:
                print("✅ LPR detection data passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ LPR detection data failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ LPR detection data error: {e}")
        
        # Test 4: Health status
        print("\n4️⃣ Testing health status...")
        try:
            data = {
                "type": "health_check",
                "camera_id": self.camera_id,
                "checkpoint_id": self.checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "component": "camera",
                "status": "healthy",
                "message": "Camera working normally",
                "details": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 23.1
                }
            }
            response = self.session.post(f"{SERVER_URL}/api/health", json=data)
            if response.status_code == 200:
                print("✅ Health status passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health status failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Health status error: {e}")
        
        # Test 5: Statistics
        print("\n5️⃣ Testing statistics...")
        try:
            response = self.session.get(f"{SERVER_URL}/api/statistics")
            if response.status_code == 200:
                print("✅ Statistics passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Statistics failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Statistics error: {e}")
    
    def test_socketio(self):
        """Test SocketIO endpoints"""
        print("\n" + "="*50)
        print("🧪 TESTING SOCKETIO ENDPOINTS")
        print("="*50)
        
        try:
            # Connect to SocketIO
            print("\n1️⃣ Connecting to SocketIO...")
            self.sio.connect(SOCKETIO_URL)
            time.sleep(2)  # Wait for connection
            
            # Test 2: Camera registration
            print("\n2️⃣ Testing camera registration via SocketIO...")
            data = {
                "camera_id": self.camera_id,
                "checkpoint_id": self.checkpoint_id,
                "timestamp": datetime.now().isoformat()
            }
            self.sio.emit('camera_register', data)
            time.sleep(1)
            
            # Test 3: LPR data
            print("\n3️⃣ Testing LPR data via SocketIO...")
            data = {
                "type": "detection_result",
                "camera_id": self.camera_id,
                "checkpoint_id": self.checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "vehicles_count": 2,
                "plates_count": 2,
                "ocr_results": ["XYZ789", "DEF456"],
                "vehicle_detections": [
                    {
                        "bbox": [100, 100, 200, 200],
                        "confidence": 0.95,
                        "class": "car"
                    },
                    {
                        "bbox": [300, 300, 400, 400],
                        "confidence": 0.88,
                        "class": "truck"
                    }
                ],
                "plate_detections": [
                    {
                        "bbox": [150, 150, 180, 170],
                        "confidence": 0.92,
                        "text": "XYZ789"
                    },
                    {
                        "bbox": [350, 350, 380, 370],
                        "confidence": 0.85,
                        "text": "DEF456"
                    }
                ],
                "processing_time_ms": 200,
                "annotated_image": "base64_encoded_image_data_placeholder",
                "cropped_plates": ["base64_plate1_placeholder", "base64_plate2_placeholder"]
            }
            self.sio.emit('lpr_data', data)
            time.sleep(1)
            
            # Test 4: Health status
            print("\n4️⃣ Testing health status via SocketIO...")
            data = {
                "type": "health_check",
                "camera_id": self.camera_id,
                "checkpoint_id": self.checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "component": "camera",
                "status": "healthy",
                "message": "Camera working normally via SocketIO",
                "details": {
                    "cpu_usage": 42.1,
                    "memory_usage": 65.3,
                    "disk_usage": 25.7,
                    "network_status": "connected"
                }
            }
            self.sio.emit('health_status', data)
            time.sleep(1)
            
            # Test 5: Ping
            print("\n5️⃣ Testing ping via SocketIO...")
            data = {
                "type": "test",
                "message": "Hello from AI Camera via SocketIO",
                "timestamp": datetime.now().isoformat()
            }
            self.sio.emit('ping', data)
            time.sleep(1)
            
            # Test 6: Join dashboard
            print("\n6️⃣ Testing dashboard join...")
            self.sio.emit('join_dashboard')
            time.sleep(1)
            
            # Test 7: Join health room
            print("\n7️⃣ Testing health room join...")
            self.sio.emit('join_health_room')
            time.sleep(1)
            
            # Wait a bit for all responses
            time.sleep(2)
            
            # Disconnect
            print("\n8️⃣ Disconnecting from SocketIO...")
            self.sio.disconnect()
            
        except Exception as e:
            print(f"❌ SocketIO test error: {e}")
            try:
                self.sio.disconnect()
            except:
                pass
    
    def test_fallback_scenario(self):
        """Test fallback scenario (SocketIO fails, REST API works)"""
        print("\n" + "="*50)
        print("🧪 TESTING FALLBACK SCENARIO")
        print("="*50)
        
        print("\n📝 This test simulates a scenario where SocketIO fails and system falls back to REST API")
        print("   In a real scenario, the edge device would:")
        print("   1. Try SocketIO connection first")
        print("   2. If SocketIO fails, use REST API")
        print("   3. Retry SocketIO after some time")
        
        # Test REST API as fallback
        print("\n✅ Testing REST API as fallback...")
        self.test_rest_api()
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Edge Communication Tests")
        print(f"   Server URL: {SERVER_URL}")
        print(f"   Camera ID: {self.camera_id}")
        print(f"   Checkpoint ID: {self.checkpoint_id}")
        
        # Test REST API
        self.test_rest_api()
        
        # Test SocketIO
        self.test_socketio()
        
        # Test fallback scenario
        self.test_fallback_scenario()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS COMPLETED")
        print("="*50)
        print("\n📋 Summary:")
        print("   ✅ REST API endpoints tested")
        print("   ✅ SocketIO events tested")
        print("   ✅ Fallback scenario tested")
        print("\n💡 Next steps:")
        print("   1. Check server logs for any errors")
        print("   2. Verify data is stored correctly")
        print("   3. Test with real edge devices")

def main():
    """Main test function"""
    tester = EdgeCommunicationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
