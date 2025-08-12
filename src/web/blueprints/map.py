"""
Map Manager Blueprint

This blueprint handles map and location management including:
- Vehicle tracking and route visualization
- Location-based analytics
- Map configuration and settings
- Geographic data management
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import logging

# Create blueprint
map_bp = Blueprint('map', __name__, url_prefix='/map')

logger = logging.getLogger(__name__)

@map_bp.route('/')
def index():
    """Map Manager main page"""
    return render_template('map/index.html')

@map_bp.route('/tracking')
def tracking():
    """Vehicle tracking page"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        # Get query parameters
        plate_number = request.args.get('plate_number')
        camera_id = request.args.get('camera_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        tracking_data = map_service.get_vehicle_tracking(
            plate_number=plate_number,
            camera_id=camera_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return render_template('map/tracking.html', tracking_data=tracking_data)
    except Exception as e:
        logger.error(f"Error loading vehicle tracking: {str(e)}")
        return render_template('map/tracking.html', tracking_data=[], error=str(e))

@map_bp.route('/analytics')
def analytics():
    """Map analytics page"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        # Get analytics data
        heatmap_data = map_service.get_heatmap_data()
        route_analytics = map_service.get_route_analytics()
        location_stats = map_service.get_location_statistics()
        
        return render_template('map/analytics.html', 
                             heatmap_data=heatmap_data,
                             route_analytics=route_analytics,
                             location_stats=location_stats)
    except Exception as e:
        logger.error(f"Error loading map analytics: {str(e)}")
        return render_template('map/analytics.html', error=str(e))

@map_bp.route('/locations')
def locations():
    """Location management page"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        locations = map_service.get_locations(page=page, per_page=per_page)
        
        return render_template('map/locations.html', locations=locations)
    except Exception as e:
        logger.error(f"Error loading locations: {str(e)}")
        return render_template('map/locations.html', locations=[], error=str(e))

@map_bp.route('/settings')
def settings():
    """Map settings page"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        settings = map_service.get_map_settings()
        
        return render_template('map/settings.html', settings=settings)
    except Exception as e:
        logger.error(f"Error loading map settings: {str(e)}")
        return render_template('map/settings.html', error=str(e))

# API Endpoints
@map_bp.route('/api/tracking', methods=['GET'])
def api_get_tracking():
    """Get vehicle tracking data API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        plate_number = request.args.get('plate_number')
        camera_id = request.args.get('camera_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        tracking_data = map_service.get_vehicle_tracking(
            plate_number=plate_number,
            camera_id=camera_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'tracking_data': tracking_data
        })
    except Exception as e:
        logger.error(f"API Error getting tracking data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/tracking/<plate_number>', methods=['GET'])
def api_get_vehicle_tracking(plate_number):
    """Get specific vehicle tracking API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        tracking_data = map_service.get_vehicle_tracking(
            plate_number=plate_number,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'tracking_data': tracking_data
        })
    except Exception as e:
        logger.error(f"API Error getting vehicle tracking: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/analytics/heatmap', methods=['GET'])
def api_get_heatmap():
    """Get heatmap data API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        heatmap_data = map_service.get_heatmap_data(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'heatmap_data': heatmap_data
        })
    except Exception as e:
        logger.error(f"API Error getting heatmap data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/analytics/routes', methods=['GET'])
def api_get_route_analytics():
    """Get route analytics API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        route_analytics = map_service.get_route_analytics(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'route_analytics': route_analytics
        })
    except Exception as e:
        logger.error(f"API Error getting route analytics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/analytics/locations', methods=['GET'])
def api_get_location_statistics():
    """Get location statistics API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        location_stats = map_service.get_location_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'location_stats': location_stats
        })
    except Exception as e:
        logger.error(f"API Error getting location statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/locations', methods=['GET'])
def api_get_locations():
    """Get locations API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        locations = map_service.get_locations(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'locations': locations['locations'],
            'pagination': locations['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting locations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/locations', methods=['POST'])
def api_create_location():
    """Create new location API"""
    try:
        data = request.get_json()
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        location = map_service.create_location(
            name=data.get('name'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            description=data.get('description'),
            location_type=data.get('location_type')
        )
        
        return jsonify({
            'success': True,
            'location': location
        })
    except Exception as e:
        logger.error(f"API Error creating location: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/locations/<location_id>', methods=['GET'])
def api_get_location(location_id):
    """Get location by ID API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        location = map_service.get_location(location_id)
        
        if not location:
            return jsonify({
                'success': False,
                'error': 'Location not found'
            }), 404
        
        return jsonify({
            'success': True,
            'location': location
        })
    except Exception as e:
        logger.error(f"API Error getting location: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/locations/<location_id>', methods=['PUT'])
def api_update_location(location_id):
    """Update location API"""
    try:
        data = request.get_json()
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        location = map_service.update_location(location_id, data)
        
        return jsonify({
            'success': True,
            'location': location
        })
    except Exception as e:
        logger.error(f"API Error updating location: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/locations/<location_id>', methods=['DELETE'])
def api_delete_location(location_id):
    """Delete location API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        map_service.delete_location(location_id)
        
        return jsonify({
            'success': True,
            'message': 'Location deleted successfully'
        })
    except Exception as e:
        logger.error(f"API Error deleting location: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/settings', methods=['GET'])
def api_get_settings():
    """Get map settings API"""
    try:
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        settings = map_service.get_map_settings()
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"API Error getting map settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@map_bp.route('/api/settings', methods=['PUT'])
def api_update_settings():
    """Update map settings API"""
    try:
        data = request.get_json()
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        settings = map_service.update_map_settings(data)
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"API Error updating map settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@map_bp.route('/socket/location-update', methods=['POST'])
def socket_location_update():
    """Handle location update via WebSocket"""
    try:
        data = request.get_json()
        from src.services.map_service import get_map_service
        map_service = get_map_service()
        
        # Update vehicle location
        location_update = map_service.update_vehicle_location(
            plate_number=data.get('plate_number'),
            camera_id=data.get('camera_id'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            timestamp=data.get('timestamp')
        )
        
        # Emit location update to tracking page
        emit('vehicle_location_update', location_update, broadcast=True)
        
        return jsonify({
            'success': True,
            'location_update': location_update
        })
    except Exception as e:
        logger.error(f"Socket Error processing location update: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
