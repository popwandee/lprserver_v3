"""
API Blueprint for LPR Server

This blueprint provides REST API endpoints for LPR data management,
statistics, and blacklist operations.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.models.lpr_record import LPRRecord
from core.models import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/records', methods=['GET'])
def get_records():
    """Get LPR records with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
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
            'timestamp': record.timestamp.isoformat(),
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
        'camera_statistics': camera_data
    })

@api_bp.route('/records', methods=['POST'])
def create_record():
    """Create new LPR record (for WebSocket data)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        record = LPRRecord(
            camera_id=data.get('camera_id'),
            plate_number=data.get('plate_number'),
            confidence=data.get('confidence', 0.0),
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
    return jsonify({
        'blacklist': blacklist
    })

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
    """Get blacklist statistics"""
    from core.dependency_container import get_service
    
    blacklist_service = get_service('blacklist_service')
    stats = blacklist_service.get_blacklist_statistics()
    return jsonify(stats)

@api_bp.route('/blacklist/detections', methods=['GET'])
def get_blacklist_detections():
    """Get recent blacklist detections"""
    hours = request.args.get('hours', 24, type=int)
    
    detections = LPRRecord.get_blacklist_detections(hours=hours)
    return jsonify({
        'detections': [detection.to_dict() for detection in detections]
    })
