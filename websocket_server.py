#!/usr/bin/env python3
"""
WebSocket Server for LPR data reception
Runs on port 8765 as specified
"""

import os
import sys
import json
import logging
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

# Simple route for testing
@app.route('/')
def index():
    """Simple index page"""
    return jsonify({
        'message': 'LPR WebSocket Server v3',
        'status': 'running',
        'port': 8765,
        'websocket_endpoint': '/websocket'
    })

@app.route('/websocket')
def websocket_info():
    """WebSocket endpoint info"""
    return jsonify({
        'message': 'WebSocket endpoint is available',
        'connection_url': 'ws://localhost:8765',
        'events': ['connect', 'disconnect', 'camera_register', 'lpr_data', 'status']
    })

@app.route('/api/statistics')
def api_statistics():
    """API endpoint for statistics"""
    try:
        # Calculate today's records
        today = date.today()
        today_records = [
            record for record in lpr_records 
            if datetime.fromisoformat(record['timestamp']).date() == today
        ]
        
        # Get unique cameras
        unique_cameras = list(set(record['camera_id'] for record in lpr_records))
        
        # Calculate statistics
        stats = {
            'total_records': len(lpr_records),
            'today_records': len(today_records),
            'unique_cameras': len(unique_cameras),
            'active_cameras': len(camera_data),
            'blacklist_count': len(blacklist_items),
            'connected_clients': len(connected_clients),
            'timestamp': datetime.now().isoformat(),
            'server_status': 'running'
        }
        
        logger.info(f"Statistics requested: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/records')
def api_records():
    """API endpoint for LPR records"""
    try:
        limit = request.args.get('limit', 20, type=int)
        camera_id = request.args.get('camera_id')
        plate_number = request.args.get('plate_number')
        
        # Filter records
        filtered_records = lpr_records
        
        if camera_id:
            filtered_records = [r for r in filtered_records if r['camera_id'] == camera_id]
        
        if plate_number:
            filtered_records = [r for r in filtered_records if plate_number.lower() in r['plate_number'].lower()]
        
        # Apply limit
        limited_records = filtered_records[-limit:] if limit > 0 else filtered_records
        
        response = {
            'records': limited_records,
            'total_count': len(filtered_records),
            'returned_count': len(limited_records),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving records: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/cameras')
def api_cameras():
    """API endpoint for camera information"""
    try:
        cameras_info = []
        for camera_id, data in camera_data.items():
            camera_info = {
                'camera_id': camera_id,
                'registered_at': data.get('registered_at'),
                'last_seen': data.get('last_seen'),
                'detection_count': len(data.get('detections', [])),
                'connected_clients': len(data.get('clients', []))
            }
            cameras_info.append(camera_info)
        
        response = {
            'cameras': cameras_info,
            'total_cameras': len(cameras_info),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving camera info: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# WebSocket event handlers
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
    emit('status', {'message': 'Connected to LPR WebSocket Server', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    
    # Remove from camera rooms
    for camera_id in list(camera_data.keys()):
        if camera_id in camera_data and client_id in camera_data[camera_id].get('clients', []):
            camera_data[camera_id]['clients'].remove(client_id)
            if not camera_data[camera_id]['clients']:
                del camera_data[camera_id]
    
    logger.info(f"Client disconnected: {client_id}")

@socketio.on('camera_register')
def handle_camera_register(data):
    """Handle camera registration"""
    try:
        client_id = request.sid
        camera_id = data.get('camera_id', 'unknown')
        logger.info(f"Camera registered: {camera_id}")
        
        # Join camera room
        join_room(f"camera_{camera_id}")
        
        # Store camera data
        if camera_id not in camera_data:
            camera_data[camera_id] = {
                'registered_at': datetime.now().isoformat(),
                'clients': [],
                'detections': [],
                'last_seen': datetime.now().isoformat()
            }
        
        if client_id not in camera_data[camera_id]['clients']:
            camera_data[camera_id]['clients'].append(client_id)
        
        camera_data[camera_id]['last_seen'] = datetime.now().isoformat()
        
        emit('status', {
            'message': f'Camera {camera_id} registered successfully',
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Broadcast to dashboard
        socketio.emit('camera_status', {
            'camera_id': camera_id,
            'status': 'online',
            'timestamp': datetime.now().isoformat()
        }, room='dashboard')
        
    except Exception as e:
        logger.error(f"Error in camera registration: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('lpr_data')
def handle_lpr_data(data):
    """Handle LPR data from camera"""
    try:
        client_id = request.sid
        camera_id = data.get('camera_id', 'unknown')
        plate_number = data.get('plate_number', 'unknown')
        confidence = data.get('confidence', 0)
        image_data = data.get('image_data', '')
        location = data.get('location', 'unknown')
        
        logger.info(f"LPR data received: {plate_number} from {camera_id} (confidence: {confidence}%)")
        
        # Create record
        record = {
            'plate_number': plate_number,
            'camera_id': camera_id,
            'confidence': confidence,
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'client_id': client_id,
            'image_data': image_data[:100] + '...' if len(image_data) > 100 else image_data  # Truncate for storage
        }
        
        # Store record
        lpr_records.append(record)
        
        # Update camera data
        if camera_id in camera_data:
            camera_data[camera_id]['detections'].append(record)
            camera_data[camera_id]['last_seen'] = datetime.now().isoformat()
        
        # Process the data (simple demo - just log and acknowledge)
        response = {
            'message': 'LPR data received successfully',
            'plate_number': plate_number,
            'camera_id': camera_id,
            'confidence': confidence,
            'detection_id': len(lpr_records),
            'timestamp': datetime.now().isoformat()
        }
        
        emit('lpr_response', response)
        
        # Broadcast to dashboard
        socketio.emit('new_detection', {
            'plate_number': plate_number,
            'camera_id': camera_id,
            'confidence': confidence,
            'location': location,
            'timestamp': datetime.now().isoformat()
        }, room='dashboard')
        
    except Exception as e:
        logger.error(f"Error processing LPR data: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('join_dashboard')
def handle_join_dashboard():
    """Handle dashboard join request"""
    join_room('dashboard')
    emit('status', {
        'message': 'Joined dashboard room',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing"""
    emit('pong', {
        'message': 'pong',
        'timestamp': datetime.now().isoformat()
    })

def main():
    """Main WebSocket server entry point"""
    try:
        logger.info("Starting LPR WebSocket Server on port 8765")
        logger.info("WebSocket endpoint available at: ws://localhost:8765")
        logger.info("HTTP endpoint available at: http://localhost:8765")
        logger.info("API endpoints available at: http://localhost:8765/api/")
        
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
