#!/usr/bin/env python3
"""
WebSocket Server for LPR data reception
Runs on port 8765 as specified
Supports both SocketIO and REST API communication
"""

import os
import sys
import json
import logging
import uuid
from datetime import datetime, date
from collections import defaultdict

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import Config

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Data storage for statistics
connected_clients = {}
camera_data = {}
lpr_records = []
blacklist_items = []
health_records = []

# Simple route for testing
@app.route('/')
def index():
    """Simple index page"""
    return jsonify({
        'message': 'LPR WebSocket Server v3',
        'status': 'running',
        'port': 8765,
        'websocket_endpoint': '/websocket',
        'api_endpoints': {
            'test': '/api/test',
            'cameras_register': '/api/cameras/register',
            'detection': '/api/detection',
            'health': '/api/health',
            'statistics': '/api/statistics'
        }
    })

@app.route('/websocket')
def websocket_info():
    """WebSocket endpoint info"""
    return jsonify({
        'message': 'WebSocket endpoint is available',
        'connection_url': 'ws://localhost:8765',
        'events': [
            'connect', 'disconnect', 'error',
            'camera_register', 'lpr_data', 'health_status', 'ping',
            'pong', 'lpr_response', 'health_response'
        ]
    })

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/api/test', methods=['GET'])
def api_test():
    """Test connection endpoint"""
    return jsonify({
        'success': True,
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/cameras/register', methods=['POST'])
def api_cameras_register():
    """Camera registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        camera_id = data.get('camera_id')
        checkpoint_id = data.get('checkpoint_id')
        timestamp = data.get('timestamp')
        
        if not camera_id or not checkpoint_id:
            return jsonify({
                'success': False,
                'message': 'camera_id and checkpoint_id are required'
            }), 400
        
        # Store camera registration
        camera_key = f"{camera_id}_{checkpoint_id}"
        camera_data[camera_key] = {
            'camera_id': camera_id,
            'checkpoint_id': checkpoint_id,
            'registered_at': timestamp or datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'status': 'active'
        }
        
        logger.info(f"Camera registered via REST API: {camera_id} at checkpoint {checkpoint_id}")
        
        return jsonify({
            'success': True,
            'message': 'Camera registered successfully',
            'camera_id': camera_id,
            'checkpoint_id': checkpoint_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in camera registration: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@app.route('/api/detection', methods=['POST'])
def api_detection():
    """LPR detection data endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['type', 'camera_id', 'checkpoint_id', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Generate detection ID
        detection_id = str(uuid.uuid4())
        
        # Create detection record
        detection_record = {
            'detection_id': detection_id,
            'type': data.get('type'),
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'timestamp': data.get('timestamp'),
            'vehicles_count': data.get('vehicles_count', 0),
            'plates_count': data.get('plates_count', 0),
            'ocr_results': data.get('ocr_results', []),
            'vehicle_detections': data.get('vehicle_detections', []),
            'plate_detections': data.get('plate_detections', []),
            'processing_time_ms': data.get('processing_time_ms', 0),
            'annotated_image': data.get('annotated_image', ''),
            'cropped_plates': data.get('cropped_plates', []),
            'received_at': datetime.now().isoformat()
        }
        
        # Store detection record
        lpr_records.append(detection_record)
        
        # Update camera data
        camera_key = f"{data.get('camera_id')}_{data.get('checkpoint_id')}"
        if camera_key in camera_data:
            camera_data[camera_key]['last_seen'] = datetime.now().isoformat()
            camera_data[camera_key]['detection_count'] = camera_data[camera_key].get('detection_count', 0) + 1
        
        logger.info(f"Detection data received via REST API: {detection_id} from {data.get('camera_id')}")
        
        return jsonify({
            'success': True,
            'message': 'Detection data received',
            'detection_id': detection_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing detection data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing data: {str(e)}'
        }), 500

@app.route('/api/health', methods=['POST'])
def api_health():
    """Health check data endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['type', 'camera_id', 'checkpoint_id', 'timestamp', 'component', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Generate health ID
        health_id = str(uuid.uuid4())
        
        # Create health record
        health_record = {
            'health_id': health_id,
            'type': data.get('type'),
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'timestamp': data.get('timestamp'),
            'component': data.get('component'),
            'status': data.get('status'),
            'message': data.get('message', ''),
            'details': data.get('details', {}),
            'received_at': datetime.now().isoformat()
        }
        
        # Store health record
        health_records.append(health_record)
        
        # Update camera data
        camera_key = f"{data.get('camera_id')}_{data.get('checkpoint_id')}"
        if camera_key in camera_data:
            camera_data[camera_key]['last_seen'] = datetime.now().isoformat()
            camera_data[camera_key]['health_status'] = data.get('status')
        
        logger.info(f"Health data received via REST API: {health_id} from {data.get('camera_id')}")
        
        return jsonify({
            'success': True,
            'message': 'Health data received',
            'health_id': health_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing health data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing data: {str(e)}'
        }), 500

@app.route('/api/statistics')
def api_statistics():
    """API endpoint for statistics"""
    try:
        # Calculate today's records
        today = date.today()
        today_detections = [
            record for record in lpr_records 
            if datetime.fromisoformat(record['timestamp']).date() == today
        ]
        
        today_health = [
            record for record in health_records 
            if datetime.fromisoformat(record['timestamp']).date() == today
        ]
        
        # Get unique cameras
        unique_cameras = list(set(f"{record['camera_id']}_{record['checkpoint_id']}" for record in lpr_records))
        
        # Calculate statistics
        stats = {
            'success': True,
            'data': {
                'total_detections': len(lpr_records),
                'today_detections': len(today_detections),
                'total_health_checks': len(health_records),
                'today_health_checks': len(today_health),
                'unique_cameras': len(unique_cameras),
                'active_cameras': len(camera_data),
                'blacklist_count': len(blacklist_items),
                'connected_clients': len(connected_clients),
                'last_update': datetime.now().isoformat(),
                'server_status': 'running'
            }
        }
        
        logger.info(f"Statistics requested: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/records')
def api_records():
    """API endpoint for LPR records"""
    try:
        limit = request.args.get('limit', 20, type=int)
        camera_id = request.args.get('camera_id')
        checkpoint_id = request.args.get('checkpoint_id')
        
        # Filter records
        filtered_records = lpr_records
        
        if camera_id:
            filtered_records = [r for r in filtered_records if r['camera_id'] == camera_id]
        
        if checkpoint_id:
            filtered_records = [r for r in filtered_records if r['checkpoint_id'] == checkpoint_id]
        
        # Apply limit
        limited_records = filtered_records[-limit:] if limit > 0 else filtered_records
        
        response = {
            'success': True,
            'records': limited_records,
            'total_count': len(filtered_records),
            'returned_count': len(limited_records),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving records: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/cameras')
def api_cameras():
    """API endpoint for camera information"""
    try:
        cameras_info = []
        for camera_key, data in camera_data.items():
            camera_info = {
                'camera_id': data.get('camera_id'),
                'checkpoint_id': data.get('checkpoint_id'),
                'registered_at': data.get('registered_at'),
                'last_seen': data.get('last_seen'),
                'status': data.get('status'),
                'detection_count': data.get('detection_count', 0),
                'health_status': data.get('health_status', 'unknown')
            }
            cameras_info.append(camera_info)
        
        response = {
            'success': True,
            'cameras': cameras_info,
            'total_cameras': len(cameras_info),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving camera info: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# SOCKET.IO EVENT HANDLERS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients[client_id] = {
        'connected_at': datetime.now().isoformat(),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    logger.info(f"Client connected: {client_id} from {request.remote_addr}")
    emit('connect', {'message': 'Connected to LPR WebSocket Server', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    
    # Remove from camera rooms
    for camera_key in list(camera_data.keys()):
        if camera_key in camera_data and client_id in camera_data[camera_key].get('clients', []):
            camera_data[camera_key]['clients'].remove(client_id)
            if not camera_data[camera_key]['clients']:
                del camera_data[camera_key]
    
    logger.info(f"Client disconnected: {client_id}")

@socketio.on('camera_register')
def handle_camera_register(data):
    """Handle camera registration via SocketIO"""
    try:
        client_id = request.sid
        camera_id = data.get('camera_id')
        checkpoint_id = data.get('checkpoint_id')
        timestamp = data.get('timestamp')
        
        if not camera_id or not checkpoint_id:
            emit('error', {'message': 'camera_id and checkpoint_id are required'})
            return
        
        logger.info(f"Camera registered via SocketIO: {camera_id} at checkpoint {checkpoint_id}")
        
        # Join camera room
        room_name = f"camera_{camera_id}_{checkpoint_id}"
        join_room(room_name)
        
        # Store camera data
        camera_key = f"{camera_id}_{checkpoint_id}"
        if camera_key not in camera_data:
            camera_data[camera_key] = {
                'camera_id': camera_id,
                'checkpoint_id': checkpoint_id,
                'registered_at': timestamp or datetime.now().isoformat(),
                'clients': [],
                'detections': [],
                'last_seen': datetime.now().isoformat(),
                'status': 'active'
            }
        
        if client_id not in camera_data[camera_key]['clients']:
            camera_data[camera_key]['clients'].append(client_id)
        
        camera_data[camera_key]['last_seen'] = datetime.now().isoformat()
        
        emit('camera_register', {
            'success': True,
            'message': f'Camera {camera_id} registered successfully',
            'camera_id': camera_id,
            'checkpoint_id': checkpoint_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Broadcast to dashboard
        socketio.emit('camera_status', {
            'camera_id': camera_id,
            'checkpoint_id': checkpoint_id,
            'status': 'online',
            'timestamp': datetime.now().isoformat()
        }, room='dashboard')
        
    except Exception as e:
        logger.error(f"Error in camera registration: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('lpr_data')
def handle_lpr_data(data):
    """Handle LPR data from camera via SocketIO"""
    try:
        client_id = request.sid
        
        # Validate required fields
        required_fields = ['type', 'camera_id', 'checkpoint_id', 'timestamp']
        for field in required_fields:
            if field not in data:
                emit('error', {'message': f'Missing required field: {field}'})
                return
        
        # Generate detection ID
        detection_id = str(uuid.uuid4())
        
        # Create detection record
        detection_record = {
            'detection_id': detection_id,
            'type': data.get('type'),
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'timestamp': data.get('timestamp'),
            'vehicles_count': data.get('vehicles_count', 0),
            'plates_count': data.get('plates_count', 0),
            'ocr_results': data.get('ocr_results', []),
            'vehicle_detections': data.get('vehicle_detections', []),
            'plate_detections': data.get('plate_detections', []),
            'processing_time_ms': data.get('processing_time_ms', 0),
            'annotated_image': data.get('annotated_image', ''),
            'cropped_plates': data.get('cropped_plates', []),
            'received_at': datetime.now().isoformat(),
            'client_id': client_id
        }
        
        # Store detection record
        lpr_records.append(detection_record)
        
        # Update camera data
        camera_key = f"{data.get('camera_id')}_{data.get('checkpoint_id')}"
        if camera_key in camera_data:
            camera_data[camera_key]['detections'].append(detection_record)
            camera_data[camera_key]['last_seen'] = datetime.now().isoformat()
            camera_data[camera_key]['detection_count'] = camera_data[camera_key].get('detection_count', 0) + 1
        
        logger.info(f"LPR data received via SocketIO: {detection_id} from {data.get('camera_id')}")
        
        # Send response
        emit('lpr_response', {
            'success': True,
            'message': 'LPR data received successfully',
            'detection_id': detection_id,
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'timestamp': datetime.now().isoformat()
        })
        
        # Broadcast to dashboard
        socketio.emit('new_detection', {
            'detection_id': detection_id,
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'vehicles_count': data.get('vehicles_count', 0),
            'plates_count': data.get('plates_count', 0),
            'ocr_results': data.get('ocr_results', []),
            'timestamp': datetime.now().isoformat()
        }, room='dashboard')
        
    except Exception as e:
        logger.error(f"Error processing LPR data: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('health_status')
def handle_health_status(data):
    """Handle health status from camera via SocketIO"""
    try:
        client_id = request.sid
        
        # Validate required fields
        required_fields = ['type', 'camera_id', 'checkpoint_id', 'timestamp', 'component', 'status']
        for field in required_fields:
            if field not in data:
                emit('error', {'message': f'Missing required field: {field}'})
                return
        
        # Generate health ID
        health_id = str(uuid.uuid4())
        
        # Create health record
        health_record = {
            'health_id': health_id,
            'type': data.get('type'),
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'timestamp': data.get('timestamp'),
            'component': data.get('component'),
            'status': data.get('status'),
            'message': data.get('message', ''),
            'details': data.get('details', {}),
            'received_at': datetime.now().isoformat(),
            'client_id': client_id
        }
        
        # Store health record
        health_records.append(health_record)
        
        # Update camera data
        camera_key = f"{data.get('camera_id')}_{data.get('checkpoint_id')}"
        if camera_key in camera_data:
            camera_data[camera_key]['last_seen'] = datetime.now().isoformat()
            camera_data[camera_key]['health_status'] = data.get('status')
        
        logger.info(f"Health status received via SocketIO: {health_id} from {data.get('camera_id')}")
        
        # Send response
        emit('health_response', {
            'success': True,
            'message': 'Health status received successfully',
            'health_id': health_id,
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'timestamp': datetime.now().isoformat()
        })
        
        # Broadcast to health monitoring room
        socketio.emit('health_update', {
            'health_id': health_id,
            'camera_id': data.get('camera_id'),
            'checkpoint_id': data.get('checkpoint_id'),
            'component': data.get('component'),
            'status': data.get('status'),
            'message': data.get('message', ''),
            'timestamp': datetime.now().isoformat()
        }, room='health_monitoring')
        
    except Exception as e:
        logger.error(f"Error processing health status: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('ping')
def handle_ping(data):
    """Handle ping for connection testing"""
    try:
        message = data.get('message', 'Hello from AI Camera')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        logger.debug(f"Ping received: {message}")
        
        emit('pong', {
            'success': True,
            'message': 'pong',
            'original_message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error handling ping: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('join_dashboard')
def handle_join_dashboard():
    """Handle dashboard join request"""
    join_room('dashboard')
    emit('status', {
        'message': 'Joined dashboard room',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('join_health_room')
def handle_join_health_room():
    """Handle health monitoring room join request"""
    join_room('health_monitoring')
    emit('status', {
        'message': 'Joined health monitoring room',
        'timestamp': datetime.now().isoformat()
    })

def main():
    """Main WebSocket server entry point"""
    try:
        logger.info("Starting LPR WebSocket Server on port 8765")
        logger.info("WebSocket endpoint available at: ws://localhost:8765")
        logger.info("HTTP endpoint available at: http://localhost:8765")
        logger.info("API endpoints available at: http://localhost:8765/api/")
        logger.info("Supported SocketIO events: camera_register, lpr_data, health_status, ping")
        logger.info("Supported REST endpoints: /api/cameras/register, /api/detection, /api/health, /api/test")
        
        # Run SocketIO server
        socketio.run(
            app,
            host='0.0.0.0',
            port=8765,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        logger.error(f"Error starting WebSocket server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
