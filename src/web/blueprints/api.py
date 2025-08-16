"""
API Blueprint for LPR Server

This blueprint provides REST API endpoints for LPR data management,
statistics, and blacklist operations.
"""

from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os
from datetime import datetime, timedelta
import json
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.models.lpr_record import LPRRecord
from core.models.camera import Camera
from core.models.blacklist_plate import BlacklistPlate
from core.models import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/records', methods=['GET'])
def get_records():
    """Get LPR records with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    limit = request.args.get('limit', type=int)
    
    # Get filter parameters
    camera_id = request.args.get('camera_id')
    plate_number = request.args.get('plate_number')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = LPRRecord.query
    
    if camera_id:
        query = query.filter(LPRRecord.camera_id == camera_id)
    if plate_number:
        query = query.filter(LPRRecord.plate_number.like(f'%{plate_number}%'))
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(LPRRecord.timestamp >= date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(LPRRecord.timestamp < date_to_obj)
        except ValueError:
            pass
    
    # Order by timestamp descending
    query = query.order_by(LPRRecord.timestamp.desc())
    
    # Support limit param for simple recent lists
    if limit:
        per_page = limit
        page = 1

    # Paginate
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    records = []
    for record in pagination.items:
        records.append({
            'id': record.id,
            'camera_id': record.camera_id,
            'plate_number': record.plate_number,
            'confidence': record.confidence,
            'timestamp': record.timestamp.isoformat() if record.timestamp else None,
            'image_path': record.image_path,
            'location': record.location
        })
    
    return jsonify({
        'records': records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })

@api_bp.route('/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    """Get specific LPR record"""
    record = LPRRecord.query.get_or_404(record_id)
    
    return jsonify({
        'id': record.id,
        'camera_id': record.camera_id,
        'plate_number': record.plate_number,
        'confidence': record.confidence,
        'timestamp': record.timestamp.isoformat(),
        'image_path': record.image_path,
        'location': record.location
    })

@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    # Get today's records
    today = datetime.now().date()
    today_records = LPRRecord.query.filter(
        db.func.date(LPRRecord.timestamp) == today
    ).count()
    
    # Get total records
    total_records = LPRRecord.query.count()
    
    # Get unique cameras
    unique_cameras = db.session.query(LPRRecord.camera_id).distinct().count()
    
    # Get blacklist count (active)
    blacklist_count = db.session.query(BlacklistPlate).filter(
        BlacklistPlate.is_active == True
    ).count()

    # Get records by camera
    camera_stats = db.session.query(
        LPRRecord.camera_id,
        db.func.count(LPRRecord.id).label('count')
    ).group_by(LPRRecord.camera_id).all()
    
    camera_data = [{'camera_id': cam.camera_id, 'count': cam.count} for cam in camera_stats]
    
    return jsonify({
        'today_records': today_records,
        'total_records': total_records,
        'unique_cameras': unique_cameras,
        'camera_statistics': camera_data,
        'blacklist_count': blacklist_count
    })

@api_bp.route('/statistics/daily', methods=['GET'])
def get_daily_statistics():
    """Get daily statistics for the last N days"""
    days = request.args.get('days', 7, type=int)

    # Build a map of date -> count from DB
    date_counts = {
        row[0].isoformat(): row[1]
        for row in db.session.query(
            db.func.date(LPRRecord.timestamp).label('date'),
            db.func.count(LPRRecord.id)
        ).group_by(db.func.date(LPRRecord.timestamp)).all()
    }

    from datetime import timedelta, date as date_cls
    results = []
    for i in range(days - 1, -1, -1):
        d = (datetime.now().date() - timedelta(days=i))
        key = d.isoformat()
        results.append({'date': key, 'count': int(date_counts.get(key, 0))})

    return jsonify({'daily_stats': results})

@api_bp.route('/statistics/camera', methods=['GET'])
def get_camera_statistics():
    """Get record counts grouped by camera"""
    stats = db.session.query(
        LPRRecord.camera_id,
        db.func.count(LPRRecord.id).label('count')
    ).group_by(LPRRecord.camera_id).all()

    return jsonify({'camera_stats': [
        {'camera_id': s.camera_id, 'count': int(s.count)} for s in stats
    ]})

@api_bp.route('/records', methods=['POST'])
def create_record():
    """Create new LPR record (for WebSocket data)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Normalize confidence to percentage 0-100 for UI consistency
        confidence_val = data.get('confidence', 0.0)
        try:
            confidence_val = float(confidence_val)
            if confidence_val <= 1.0:
                confidence_val = confidence_val * 100.0
        except (TypeError, ValueError):
            confidence_val = 0.0

        record = LPRRecord(
            camera_id=data.get('camera_id'),
            plate_number=data.get('plate_number'),
            confidence=confidence_val,
            image_path=data.get('image_path'),
            location=data.get('location'),
            location_lat=data.get('location_lat'),
            location_lon=data.get('location_lon')
        )
        
        db.session.add(record)
        db.session.commit()
        
        # Check for blacklist
        from core.dependency_container import get_service
        
        blacklist_service = get_service('blacklist_service')
        blacklist_service.process_lpr_detection(record)
        
        return jsonify({
            'id': record.id,
            'message': 'Record created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Blacklist API endpoints
@api_bp.route('/blacklist', methods=['GET'])
def get_blacklist():
    """Get all active blacklist entries"""
    from src.services.blacklist_service import BlacklistService
    
    blacklist = BlacklistService.get_active_blacklist()
    # Map fields for UI expectations
    mapped = []
    for item in blacklist:
        item_copy = dict(item)
        if 'created_at' in item_copy:
            item_copy['added_timestamp'] = item_copy['created_at']
        mapped.append(item_copy)
    return jsonify({'blacklist': mapped})

@api_bp.route('/blacklist', methods=['POST'])
def add_to_blacklist():
    """Add license plate to blacklist"""
    from core.dependency_container import get_service
    
    data = request.get_json()
    
    if not data or not data.get('license_plate_text') or not data.get('reason'):
        return jsonify({'error': 'License plate and reason are required'}), 400
    
    # Parse expiry date if provided
    expiry_date = None
    if data.get('expiry_date'):
        try:
            expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid expiry date format'}), 400
    
    blacklist_service = get_service('blacklist_service')
    
    result = blacklist_service.add_to_blacklist(
        license_plate_text=data['license_plate_text'],
        reason=data['reason'],
        added_by=data.get('added_by', 'system'),
        expiry_date=expiry_date,
        notes=data.get('notes')
    )
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@api_bp.route('/blacklist/<int:blacklist_id>', methods=['DELETE'])
def remove_from_blacklist(blacklist_id):
    """Remove license plate from blacklist"""
    from core.dependency_container import get_service
    blacklist_service = get_service('blacklist_service')
    
    result = blacklist_service.remove_from_blacklist(
        blacklist_id=blacklist_id,
        removed_by=request.args.get('removed_by', 'system')
    )
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@api_bp.route('/blacklist/statistics', methods=['GET'])
def get_blacklist_statistics():
    """Get blacklist statistics aligned with UI needs"""
    try:
        # Total active blacklist entries
        total_blacklist_entries = db.session.query(BlacklistPlate).filter(
            BlacklistPlate.is_active == True
        ).count()

        # Total blacklist detections historically
        total_blacklist_detections = db.session.query(LPRRecord).filter(
            LPRRecord.is_blacklisted == True
        ).count()

        # Recent blacklist detections in last 24 hours
        from datetime import timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_detections_24h = db.session.query(LPRRecord).filter(
            LPRRecord.is_blacklisted == True,
            LPRRecord.timestamp >= recent_cutoff
        ).count()

        return jsonify({
            'total_blacklist_entries': int(total_blacklist_entries),
            'total_blacklist_detections': int(total_blacklist_detections),
            'recent_detections_24h': int(recent_detections_24h)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/blacklist/detections', methods=['GET'])
def get_blacklist_detections():
    """Get recent blacklist detections"""
    hours = request.args.get('hours', 24, type=int)
    
    detections = LPRRecord.get_blacklist_detections(hours=hours)
    return jsonify({
        'detections': [detection.to_dict() for detection in detections]
    })

@api_bp.route('/alerts/recent', methods=['GET'])
def get_recent_alerts():
    """Get recent alerts for dashboard. Currently derived from recent blacklist detections."""
    limit = request.args.get('limit', 5, type=int)
    recent_blacklisted = LPRRecord.query.filter(
        LPRRecord.is_blacklisted == True
    ).order_by(LPRRecord.timestamp.desc()).limit(limit).all()

    alerts = []
    for rec in recent_blacklisted:
        message = f"พบป้ายทะเบียนในบัญชีดำ {rec.plate_number} จากกล้อง {rec.camera_id}"
        alerts.append({
            'type': 'blacklist',
            'message': message,
            'timestamp': rec.timestamp.isoformat() if rec.timestamp else None
        })

    return jsonify({'alerts': alerts})

@api_bp.route('/cameras/status', methods=['GET'])
def get_cameras_status():
    """Get current camera connection status."""
    # Consider online if last_activity within 5 minutes and status is active
    threshold_minutes = request.args.get('threshold_minutes', 5, type=int)
    from datetime import timedelta
    now = datetime.now()

    cameras = db.session.query(Camera).all()
    results = []
    for cam in cameras:
        last_detection = cam.last_activity
        is_recent = False
        if last_detection:
            is_recent = (now - last_detection) <= timedelta(minutes=threshold_minutes)
        is_online = (cam.status == 'active') and is_recent
        results.append({
            'camera_id': cam.camera_id,
            'is_online': is_online,
            'ip_address': cam.ip_address,
            'last_detection': last_detection.isoformat() if last_detection else None,
            'status': 'online' if is_online else 'offline'
        })

    return jsonify({'cameras': results})

@api_bp.route('/records/<int:record_id>/image', methods=['GET'])
def get_record_image(record_id: int):
    """Serve image file for a given LPR record."""
    record = LPRRecord.query.get_or_404(record_id)
    if not record.image_path:
        return jsonify({'error': 'Image not available'}), 404

    # Build absolute path
    storage_root = current_app.config.get('IMAGE_STORAGE_PATH', 'storage/images')
    # If image_path is already absolute, split directory and filename for send_from_directory
    image_path = record.image_path
    if os.path.isabs(image_path):
        directory, filename = os.path.dirname(image_path), os.path.basename(image_path)
        if not os.path.exists(os.path.join(directory, filename)):
            return jsonify({'error': 'Image not found'}), 404
        return send_from_directory(directory, filename)
    else:
        directory = storage_root
        filename = image_path
        abs_path = os.path.join(directory, filename)
        if not os.path.exists(abs_path):
            return jsonify({'error': 'Image not found'}), 404
        return send_from_directory(directory, filename)
