"""
Detection Manager Blueprint

This blueprint handles LPR detection management including:
- Detection records management
- Detection settings and configuration
- Detection statistics and analytics
- Detection alerts and notifications
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import logging

# Create blueprint
detection_bp = Blueprint('detection', __name__, url_prefix='/detection')

logger = logging.getLogger(__name__)

@detection_bp.route('/')
def index():
    """Detection Manager main page"""
    return render_template('detection/index.html')

@detection_bp.route('/records')
def records():
    """Detection records page"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        camera_id = request.args.get('camera_id')
        plate_number = request.args.get('plate_number')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        records = detection_service.get_detection_records(
            page=page,
            per_page=per_page,
            camera_id=camera_id,
            plate_number=plate_number,
            start_date=start_date,
            end_date=end_date
        )
        
        return render_template('detection/records.html', records=records)
    except Exception as e:
        logger.error(f"Error loading detection records: {str(e)}")
        return render_template('detection/records.html', records=[], error=str(e))

@detection_bp.route('/records/<record_id>')
def record_detail(record_id):
    """Detection record detail page"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        record = detection_service.get_detection_record(record_id)
        
        if not record:
            return render_template('error.html', message="Record not found"), 404
        
        return render_template('detection/record_detail.html', record=record)
    except Exception as e:
        logger.error(f"Error loading detection record: {str(e)}")
        return render_template('error.html', message=str(e)), 500

@detection_bp.route('/statistics')
def statistics():
    """Detection statistics page"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        # Get statistics for different time periods
        today_stats = detection_service.get_detection_statistics(period='today')
        week_stats = detection_service.get_detection_statistics(period='week')
        month_stats = detection_service.get_detection_statistics(period='month')
        
        return render_template('detection/statistics.html', 
                             today_stats=today_stats,
                             week_stats=week_stats,
                             month_stats=month_stats)
    except Exception as e:
        logger.error(f"Error loading detection statistics: {str(e)}")
        return render_template('detection/statistics.html', error=str(e))

@detection_bp.route('/settings')
def settings():
    """Detection settings page"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        settings = detection_service.get_detection_settings()
        
        return render_template('detection/settings.html', settings=settings)
    except Exception as e:
        logger.error(f"Error loading detection settings: {str(e)}")
        return render_template('detection/settings.html', error=str(e))

@detection_bp.route('/alerts')
def alerts():
    """Detection alerts page"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        alerts = detection_service.get_detection_alerts(page=page, per_page=per_page)
        
        return render_template('detection/alerts.html', alerts=alerts)
    except Exception as e:
        logger.error(f"Error loading detection alerts: {str(e)}")
        return render_template('detection/alerts.html', alerts=[], error=str(e))

# API Endpoints
@detection_bp.route('/api/records', methods=['GET'])
def api_get_records():
    """Get detection records API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        camera_id = request.args.get('camera_id')
        plate_number = request.args.get('plate_number')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        records = detection_service.get_detection_records(
            page=page,
            per_page=per_page,
            camera_id=camera_id,
            plate_number=plate_number,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'records': records['records'],
            'pagination': records['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting detection records: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/records/<record_id>', methods=['GET'])
def api_get_record(record_id):
    """Get detection record by ID API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        record = detection_service.get_detection_record(record_id)
        
        if not record:
            return jsonify({
                'success': False,
                'error': 'Record not found'
            }), 404
        
        return jsonify({
            'success': True,
            'record': record
        })
    except Exception as e:
        logger.error(f"API Error getting detection record: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/records/<record_id>', methods=['DELETE'])
def api_delete_record(record_id):
    """Delete detection record API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        detection_service.delete_detection_record(record_id)
        
        return jsonify({
            'success': True,
            'message': 'Record deleted successfully'
        })
    except Exception as e:
        logger.error(f"API Error deleting detection record: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/statistics', methods=['GET'])
def api_get_statistics():
    """Get detection statistics API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        period = request.args.get('period', 'today')
        stats = detection_service.get_detection_statistics(period=period)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"API Error getting detection statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/statistics/daily', methods=['GET'])
def api_get_daily_statistics():
    """Get daily detection statistics API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        days = request.args.get('days', 7, type=int)
        stats = detection_service.get_daily_statistics(days=days)
        
        return jsonify({
            'success': True,
            'daily_stats': stats
        })
    except Exception as e:
        logger.error(f"API Error getting daily statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/statistics/camera', methods=['GET'])
def api_get_camera_statistics():
    """Get camera detection statistics API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        stats = detection_service.get_camera_statistics()
        
        return jsonify({
            'success': True,
            'camera_stats': stats
        })
    except Exception as e:
        logger.error(f"API Error getting camera statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/settings', methods=['GET'])
def api_get_settings():
    """Get detection settings API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        settings = detection_service.get_detection_settings()
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"API Error getting detection settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/settings', methods=['PUT'])
def api_update_settings():
    """Update detection settings API"""
    try:
        data = request.get_json()
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        settings = detection_service.update_detection_settings(data)
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"API Error updating detection settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/alerts', methods=['GET'])
def api_get_alerts():
    """Get detection alerts API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        alerts = detection_service.get_detection_alerts(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'alerts': alerts['alerts'],
            'pagination': alerts['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting detection alerts: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@detection_bp.route('/api/alerts/<alert_id>', methods=['PUT'])
def api_mark_alert_read(alert_id):
    """Mark alert as read API"""
    try:
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        detection_service.mark_alert_read(alert_id)
        
        return jsonify({
            'success': True,
            'message': 'Alert marked as read'
        })
    except Exception as e:
        logger.error(f"API Error marking alert as read: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@detection_bp.route('/socket/new-detection', methods=['POST'])
def socket_new_detection():
    """Handle new detection via WebSocket"""
    try:
        data = request.get_json()
        from src.services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        record = detection_service.create_detection_record(
            camera_id=data.get('camera_id'),
            plate_number=data.get('plate_number'),
            confidence=data.get('confidence'),
            image_data=data.get('image_data'),
            location=data.get('location'),
            location_lat=data.get('location_lat'),
            location_lon=data.get('location_lon')
        )
        
        # Emit new detection to dashboard
        emit('new_lpr_record', record, broadcast=True)
        
        # Check for blacklist alerts
        if detection_service.check_blacklist_alert(record['plate_number']):
            alert = detection_service.create_blacklist_alert(record)
            emit('blacklist_alert', alert, broadcast=True)
        
        return jsonify({
            'success': True,
            'record': record
        })
    except Exception as e:
        logger.error(f"Socket Error processing new detection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
