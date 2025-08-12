"""
Report Manager Blueprint

This blueprint handles report generation and management including:
- Custom report generation
- Scheduled reports
- Report templates
- Export functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import logging
import io

# Create blueprint
report_bp = Blueprint('report', __name__, url_prefix='/report')

logger = logging.getLogger(__name__)

@report_bp.route('/')
def index():
    """Report Manager main page"""
    return render_template('report/index.html')

@report_bp.route('/generator')
def generator():
    """Report generator page"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        templates = report_service.get_report_templates()
        data_sources = report_service.get_data_sources()
        
        return render_template('report/generator.html', 
                             templates=templates,
                             data_sources=data_sources)
    except Exception as e:
        logger.error(f"Error loading report generator: {str(e)}")
        return render_template('report/generator.html', error=str(e))

@report_bp.route('/templates')
def templates():
    """Report templates page"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        templates = report_service.get_report_templates(page=page, per_page=per_page)
        
        return render_template('report/templates.html', templates=templates)
    except Exception as e:
        logger.error(f"Error loading report templates: {str(e)}")
        return render_template('report/templates.html', templates=[], error=str(e))

@report_bp.route('/scheduled')
def scheduled():
    """Scheduled reports page"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        scheduled_reports = report_service.get_scheduled_reports(page=page, per_page=per_page)
        
        return render_template('report/scheduled.html', scheduled_reports=scheduled_reports)
    except Exception as e:
        logger.error(f"Error loading scheduled reports: {str(e)}")
        return render_template('report/scheduled.html', scheduled_reports=[], error=str(e))

@report_bp.route('/history')
def history():
    """Report history page"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        report_type = request.args.get('report_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        history = report_service.get_report_history(
            page=page,
            per_page=per_page,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return render_template('report/history.html', history=history)
    except Exception as e:
        logger.error(f"Error loading report history: {str(e)}")
        return render_template('report/history.html', history=[], error=str(e))

@report_bp.route('/analytics')
def analytics():
    """Report analytics page"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        # Get analytics data
        usage_stats = report_service.get_report_usage_statistics()
        popular_reports = report_service.get_popular_reports()
        generation_times = report_service.get_report_generation_times()
        
        return render_template('report/analytics.html', 
                             usage_stats=usage_stats,
                             popular_reports=popular_reports,
                             generation_times=generation_times)
    except Exception as e:
        logger.error(f"Error loading report analytics: {str(e)}")
        return render_template('report/analytics.html', error=str(e))

# API Endpoints
@report_bp.route('/api/generate', methods=['POST'])
def api_generate_report():
    """Generate report API"""
    try:
        data = request.get_json()
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        report = report_service.generate_report(
            template_id=data.get('template_id'),
            parameters=data.get('parameters', {}),
            format_type=data.get('format', 'pdf'),
            include_charts=data.get('include_charts', True)
        )
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        logger.error(f"API Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/templates', methods=['GET'])
def api_get_templates():
    """Get report templates API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        templates = report_service.get_report_templates(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'templates': templates['templates'],
            'pagination': templates['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/templates', methods=['POST'])
def api_create_template():
    """Create report template API"""
    try:
        data = request.get_json()
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        template = report_service.create_report_template(
            name=data.get('name'),
            description=data.get('description'),
            template_type=data.get('template_type'),
            parameters=data.get('parameters', {}),
            query=data.get('query'),
            layout=data.get('layout', {})
        )
        
        return jsonify({
            'success': True,
            'template': template
        })
    except Exception as e:
        logger.error(f"API Error creating template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/templates/<template_id>', methods=['GET'])
def api_get_template(template_id):
    """Get report template by ID API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        template = report_service.get_report_template(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
        
        return jsonify({
            'success': True,
            'template': template
        })
    except Exception as e:
        logger.error(f"API Error getting template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/templates/<template_id>', methods=['PUT'])
def api_update_template(template_id):
    """Update report template API"""
    try:
        data = request.get_json()
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        template = report_service.update_report_template(template_id, data)
        
        return jsonify({
            'success': True,
            'template': template
        })
    except Exception as e:
        logger.error(f"API Error updating template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/templates/<template_id>', methods=['DELETE'])
def api_delete_template(template_id):
    """Delete report template API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        report_service.delete_report_template(template_id)
        
        return jsonify({
            'success': True,
            'message': 'Template deleted successfully'
        })
    except Exception as e:
        logger.error(f"API Error deleting template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/scheduled', methods=['GET'])
def api_get_scheduled_reports():
    """Get scheduled reports API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        scheduled_reports = report_service.get_scheduled_reports(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'scheduled_reports': scheduled_reports['scheduled_reports'],
            'pagination': scheduled_reports['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting scheduled reports: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/scheduled', methods=['POST'])
def api_schedule_report():
    """Schedule report API"""
    try:
        data = request.get_json()
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        scheduled_report = report_service.schedule_report(
            template_id=data.get('template_id'),
            schedule=data.get('schedule'),
            parameters=data.get('parameters', {}),
            recipients=data.get('recipients', []),
            format_type=data.get('format', 'pdf')
        )
        
        return jsonify({
            'success': True,
            'scheduled_report': scheduled_report
        })
    except Exception as e:
        logger.error(f"API Error scheduling report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/scheduled/<schedule_id>', methods=['DELETE'])
def api_delete_scheduled_report(schedule_id):
    """Delete scheduled report API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        report_service.delete_scheduled_report(schedule_id)
        
        return jsonify({
            'success': True,
            'message': 'Scheduled report deleted successfully'
        })
    except Exception as e:
        logger.error(f"API Error deleting scheduled report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/history', methods=['GET'])
def api_get_report_history():
    """Get report history API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        report_type = request.args.get('report_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        history = report_service.get_report_history(
            page=page,
            per_page=per_page,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'history': history['history'],
            'pagination': history['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting report history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/history/<report_id>', methods=['GET'])
def api_get_report(report_id):
    """Get report by ID API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        report = report_service.get_report(report_id)
        
        if not report:
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        logger.error(f"API Error getting report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/history/<report_id>/download', methods=['GET'])
def api_download_report(report_id):
    """Download report API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        report_data = report_service.get_report_file(report_id)
        
        if not report_data:
            return jsonify({
                'success': False,
                'error': 'Report file not found'
            }), 404
        
        # Create file-like object
        file_obj = io.BytesIO(report_data['content'])
        
        return send_file(
            file_obj,
            mimetype=report_data['mime_type'],
            as_attachment=True,
            download_name=report_data['filename']
        )
    except Exception as e:
        logger.error(f"API Error downloading report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/analytics/usage', methods=['GET'])
def api_get_usage_statistics():
    """Get report usage statistics API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        usage_stats = report_service.get_report_usage_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'usage_stats': usage_stats
        })
    except Exception as e:
        logger.error(f"API Error getting usage statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/analytics/popular', methods=['GET'])
def api_get_popular_reports():
    """Get popular reports API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        limit = request.args.get('limit', 10, type=int)
        
        popular_reports = report_service.get_popular_reports(limit=limit)
        
        return jsonify({
            'success': True,
            'popular_reports': popular_reports
        })
    except Exception as e:
        logger.error(f"API Error getting popular reports: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/analytics/generation-times', methods=['GET'])
def api_get_generation_times():
    """Get report generation times API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        generation_times = report_service.get_report_generation_times(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'generation_times': generation_times
        })
    except Exception as e:
        logger.error(f"API Error getting generation times: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/data-sources', methods=['GET'])
def api_get_data_sources():
    """Get data sources API"""
    try:
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        data_sources = report_service.get_data_sources()
        
        return jsonify({
            'success': True,
            'data_sources': data_sources
        })
    except Exception as e:
        logger.error(f"API Error getting data sources: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@report_bp.route('/socket/report-progress', methods=['POST'])
def socket_report_progress():
    """Handle report generation progress via WebSocket"""
    try:
        data = request.get_json()
        from src.services.report_service import get_report_service
        report_service = get_report_service()
        
        # Update report progress
        progress = report_service.update_report_progress(
            report_id=data.get('report_id'),
            progress=data.get('progress'),
            status=data.get('status'),
            message=data.get('message')
        )
        
        # Emit progress update to client
        emit('report_progress_update', progress, room=f"report_{data.get('report_id')}")
        
        return jsonify({
            'success': True,
            'progress': progress
        })
    except Exception as e:
        logger.error(f"Socket Error processing report progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
