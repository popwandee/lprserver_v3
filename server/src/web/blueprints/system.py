"""
System Log Manager Blueprint

This blueprint handles system logging and monitoring including:
- System logs management
- Performance monitoring
- System health checks
- Log analysis and reporting
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import logging

# Create blueprint
system_bp = Blueprint('system', __name__, url_prefix='/system')

logger = logging.getLogger(__name__)

@system_bp.route('/')
def index():
    """System Log Manager main page"""
    return render_template('system/index.html')

@system_bp.route('/logs')
def logs():
    """System logs page"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        
        logs = system_service.get_system_logs(
            page=page,
            per_page=per_page,
            level=level,
            start_date=start_date,
            end_date=end_date,
            search=search
        )
        
        return render_template('system/logs.html', logs=logs)
    except Exception as e:
        logger.error(f"Error loading system logs: {str(e)}")
        return render_template('system/logs.html', logs=[], error=str(e))

@system_bp.route('/monitoring')
def monitoring():
    """System monitoring page"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        # Get monitoring data
        performance_data = system_service.get_performance_data()
        health_status = system_service.get_system_health()
        resource_usage = system_service.get_resource_usage()
        
        return render_template('system/monitoring.html', 
                             performance_data=performance_data,
                             health_status=health_status,
                             resource_usage=resource_usage)
    except Exception as e:
        logger.error(f"Error loading system monitoring: {str(e)}")
        return render_template('system/monitoring.html', error=str(e))

@system_bp.route('/health')
def health():
    """System health page"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        health_checks = system_service.run_health_checks()
        
        return render_template('system/health.html', health_checks=health_checks)
    except Exception as e:
        logger.error(f"Error loading system health: {str(e)}")
        return render_template('system/health.html', error=str(e))

@system_bp.route('/settings')
def settings():
    """System settings page"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        settings = system_service.get_system_settings()
        
        return render_template('system/settings.html', settings=settings)
    except Exception as e:
        logger.error(f"Error loading system settings: {str(e)}")
        return render_template('system/settings.html', error=str(e))

@system_bp.route('/maintenance')
def maintenance():
    """System maintenance page"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        maintenance_tasks = system_service.get_maintenance_tasks()
        scheduled_tasks = system_service.get_scheduled_tasks()
        
        return render_template('system/maintenance.html', 
                             maintenance_tasks=maintenance_tasks,
                             scheduled_tasks=scheduled_tasks)
    except Exception as e:
        logger.error(f"Error loading system maintenance: {str(e)}")
        return render_template('system/maintenance.html', error=str(e))

# API Endpoints
@system_bp.route('/api/logs', methods=['GET'])
def api_get_logs():
    """Get system logs API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        
        logs = system_service.get_system_logs(
            page=page,
            per_page=per_page,
            level=level,
            start_date=start_date,
            end_date=end_date,
            search=search
        )
        
        return jsonify({
            'success': True,
            'logs': logs['logs'],
            'pagination': logs['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting system logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/logs/clear', methods=['POST'])
def api_clear_logs():
    """Clear system logs API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        data = request.get_json()
        days = data.get('days', 30)
        
        result = system_service.clear_old_logs(days=days)
        
        return jsonify({
            'success': True,
            'message': f'Cleared logs older than {days} days',
            'result': result
        })
    except Exception as e:
        logger.error(f"API Error clearing system logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/logs/export', methods=['POST'])
def api_export_logs():
    """Export system logs API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        format_type = data.get('format', 'csv')
        
        export_data = system_service.export_logs(
            start_date=start_date,
            end_date=end_date,
            format_type=format_type
        )
        
        return jsonify({
            'success': True,
            'export_data': export_data
        })
    except Exception as e:
        logger.error(f"API Error exporting system logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/monitoring/performance', methods=['GET'])
def api_get_performance():
    """Get performance data API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        hours = request.args.get('hours', 24, type=int)
        performance_data = system_service.get_performance_data(hours=hours)
        
        return jsonify({
            'success': True,
            'performance_data': performance_data
        })
    except Exception as e:
        logger.error(f"API Error getting performance data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/monitoring/health', methods=['GET'])
def api_get_health():
    """Get system health API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        health_status = system_service.get_system_health()
        
        return jsonify({
            'success': True,
            'health_status': health_status
        })
    except Exception as e:
        logger.error(f"API Error getting system health: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/monitoring/resources', methods=['GET'])
def api_get_resources():
    """Get resource usage API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        resource_usage = system_service.get_resource_usage()
        
        return jsonify({
            'success': True,
            'resource_usage': resource_usage
        })
    except Exception as e:
        logger.error(f"API Error getting resource usage: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/health/check', methods=['POST'])
def api_run_health_check():
    """Run health check API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        data = request.get_json()
        check_type = data.get('check_type', 'all')
        
        health_checks = system_service.run_health_checks(check_type=check_type)
        
        return jsonify({
            'success': True,
            'health_checks': health_checks
        })
    except Exception as e:
        logger.error(f"API Error running health check: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/settings', methods=['GET'])
def api_get_settings():
    """Get system settings API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        settings = system_service.get_system_settings()
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"API Error getting system settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/settings', methods=['PUT'])
def api_update_settings():
    """Update system settings API"""
    try:
        data = request.get_json()
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        settings = system_service.update_system_settings(data)
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"API Error updating system settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/maintenance/tasks', methods=['GET'])
def api_get_maintenance_tasks():
    """Get maintenance tasks API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        maintenance_tasks = system_service.get_maintenance_tasks()
        
        return jsonify({
            'success': True,
            'maintenance_tasks': maintenance_tasks
        })
    except Exception as e:
        logger.error(f"API Error getting maintenance tasks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/maintenance/tasks/<task_id>', methods=['POST'])
def api_run_maintenance_task(task_id):
    """Run maintenance task API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        result = system_service.run_maintenance_task(task_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"API Error running maintenance task: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/maintenance/schedule', methods=['GET'])
def api_get_scheduled_tasks():
    """Get scheduled tasks API"""
    try:
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        scheduled_tasks = system_service.get_scheduled_tasks()
        
        return jsonify({
            'success': True,
            'scheduled_tasks': scheduled_tasks
        })
    except Exception as e:
        logger.error(f"API Error getting scheduled tasks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/api/maintenance/schedule', methods=['POST'])
def api_schedule_task():
    """Schedule maintenance task API"""
    try:
        data = request.get_json()
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        scheduled_task = system_service.schedule_maintenance_task(
            task_type=data.get('task_type'),
            schedule=data.get('schedule'),
            parameters=data.get('parameters', {})
        )
        
        return jsonify({
            'success': True,
            'scheduled_task': scheduled_task
        })
    except Exception as e:
        logger.error(f"API Error scheduling maintenance task: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@system_bp.route('/socket/system-status', methods=['POST'])
def socket_system_status():
    """Handle system status update via WebSocket"""
    try:
        data = request.get_json()
        from src.services.system_service import get_system_service
        system_service = get_system_service()
        
        # Update system status
        status_update = system_service.update_system_status(
            cpu_usage=data.get('cpu_usage'),
            memory_usage=data.get('memory_usage'),
            disk_usage=data.get('disk_usage'),
            network_usage=data.get('network_usage')
        )
        
        # Emit status update to monitoring page
        emit('system_status_update', status_update, broadcast=True)
        
        return jsonify({
            'success': True,
            'status_update': status_update
        })
    except Exception as e:
        logger.error(f"Socket Error processing system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
