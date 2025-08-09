#!/usr/bin/env python3
"""
Detection Results Blueprint for AI Camera v1.3

This blueprint handles the detection results web UI with pagination,
search, filter, sort, and detail view capabilities.

Features:
- Paginated table view of detection results
- Search functionality for OCR results and plate text
- Date range filtering
- Vehicle/plate presence filtering
- Sortable columns
- Detail view modal for individual results
- Export functionality

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from typing import Dict, Any

from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# Create blueprint
detection_results_bp = Blueprint('detection_results', __name__, url_prefix='/detection_results')

logger = get_logger(__name__)


@detection_results_bp.route('/')
def detection_results_dashboard():
    """
    Main detection results dashboard with table view.
    
    Returns:
        str: Rendered HTML template
    """
    try:
        # Get basic statistics for dashboard header
        database_manager = get_service('database_manager')
        stats = {}
        
        if database_manager:
            stats = database_manager.get_detection_statistics()
        
        return render_template('detection_results/dashboard.html', stats=stats)
        
    except Exception as e:
        logger.error(f"Error loading detection results dashboard: {e}")
        return render_template('detection_results/dashboard.html', stats={})


@detection_results_bp.route('/api/results')
def get_detection_results():
    """
    API endpoint to get paginated detection results with search and filters.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Results per page (default: 20)
        search: Search term for OCR/plate text
        sort_by: Column to sort by (default: created_at)
        sort_order: Sort order - asc/desc (default: desc)
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        has_vehicles: Filter by vehicle presence (true/false)
        has_plates: Filter by license plate presence (true/false)
    
    Returns:
        dict: JSON response with paginated results
    """
    try:
        database_manager = get_service('database_manager')
        if not database_manager:
            return jsonify({
                'success': False,
                'error': 'Database manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Max 100 per page
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Parse boolean filters
        has_vehicles = None
        if request.args.get('has_vehicles') in ['true', 'false']:
            has_vehicles = request.args.get('has_vehicles') == 'true'
        
        has_plates = None
        if request.args.get('has_plates') in ['true', 'false']:
            has_plates = request.args.get('has_plates') == 'true'
        
        # Get paginated results
        results = database_manager.get_detection_results_paginated(
            page=page,
            per_page=per_page,
            search=search if search else None,
            sort_by=sort_by,
            sort_order=sort_order,
            date_from=date_from,
            date_to=date_to,
            has_vehicles=has_vehicles,
            has_plates=has_plates
        )
        
        # Process results for frontend display
        processed_results = []
        for result in results['results']:
            processed_result = {
                'id': result['id'],
                'timestamp': result['timestamp'],
                'created_at': result['created_at'],
                'vehicles_count': result['vehicles_count'],
                'plates_count': result['plates_count'],
                'processing_time_ms': result['processing_time_ms'],
                'has_vehicles': result['vehicles_count'] > 0,
                'has_plates': result['plates_count'] > 0,
                'ocr_text': ', '.join([ocr.get('text', '') for ocr in result['ocr_results']]) if result['ocr_results'] else '',
                'confidence_avg': round(sum([ocr.get('confidence', 0) for ocr in result['ocr_results']]) / len(result['ocr_results']), 2) if result['ocr_results'] else 0
            }
            processed_results.append(processed_result)
        
        return jsonify({
            'success': True,
            'results': processed_results,
            'pagination': {
                'page': results['page'],
                'per_page': results['per_page'],
                'total': results['total'],
                'total_pages': results['total_pages'],
                'has_next': results['has_next'],
                'has_prev': results['has_prev']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        logger.warning(f"Invalid parameters in detection results request: {e}")
        return jsonify({
            'success': False,
            'error': 'Invalid parameters',
            'timestamp': datetime.now().isoformat()
        }), 400
        
    except Exception as e:
        logger.error(f"Error getting detection results: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_results_bp.route('/api/results/<int:result_id>')
def get_detection_result_detail(result_id):
    """
    API endpoint to get detailed information for a single detection result.
    
    Args:
        result_id: ID of the detection result
    
    Returns:
        dict: JSON response with detailed result information
    """
    try:
        database_manager = get_service('database_manager')
        if not database_manager:
            return jsonify({
                'success': False,
                'error': 'Database manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        result = database_manager.get_detection_result_by_id(result_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Detection result not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Process detailed result data
        detailed_result = {
            'id': result['id'],
            'timestamp': result['timestamp'],
            'created_at': result['created_at'],
            'vehicles_count': result['vehicles_count'],
            'plates_count': result['plates_count'],
            'processing_time_ms': result['processing_time_ms'],
            'annotated_image_path': result['annotated_image_path'],
            'cropped_plates_paths': result['cropped_plates_paths'],
            'vehicle_detections': result['vehicle_detections'],
            'plate_detections': result['plate_detections'],
            'ocr_results': result['ocr_results']
        }
        
        return jsonify({
            'success': True,
            'result': detailed_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting detection result detail for ID {result_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_results_bp.route('/api/statistics')
def get_detection_statistics():
    """
    API endpoint to get detection statistics for dashboard widgets.
    
    Returns:
        dict: JSON response with statistics
    """
    try:
        database_manager = get_service('database_manager')
        if not database_manager:
            return jsonify({
                'success': False,
                'error': 'Database manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        stats = database_manager.get_detection_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting detection statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@detection_results_bp.route('/api/export')
def export_detection_results():
    """
    API endpoint to export detection results as CSV.
    
    Query Parameters:
        Same as get_detection_results endpoint
        format: Export format (csv, json) - default: csv
    
    Returns:
        Response: CSV or JSON file download
    """
    try:
        database_manager = get_service('database_manager')
        if not database_manager:
            return jsonify({
                'success': False,
                'error': 'Database manager not available'
            }), 500
        
        # Parse parameters (similar to get_detection_results)
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        export_format = request.args.get('format', 'csv').lower()
        
        # Parse boolean filters
        has_vehicles = None
        if request.args.get('has_vehicles') in ['true', 'false']:
            has_vehicles = request.args.get('has_vehicles') == 'true'
        
        has_plates = None
        if request.args.get('has_plates') in ['true', 'false']:
            has_plates = request.args.get('has_plates') == 'true'
        
        # Get all results matching filters (no pagination for export)
        results = database_manager.get_detection_results_paginated(
            page=1,
            per_page=10000,  # Large number to get all results
            search=search if search else None,
            sort_by=sort_by,
            sort_order=sort_order,
            date_from=date_from,
            date_to=date_to,
            has_vehicles=has_vehicles,
            has_plates=has_plates
        )
        
        if export_format == 'json':
            from flask import make_response
            import json
            
            response = make_response(json.dumps(results['results'], indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=detection_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            return response
        
        else:  # CSV format
            import csv
            import io
            from flask import make_response
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # CSV headers
            headers = ['ID', 'Timestamp', 'Created At', 'Vehicles Count', 'Plates Count', 
                      'Processing Time (ms)', 'OCR Results', 'Vehicle Detections', 'Plate Detections']
            writer.writerow(headers)
            
            # CSV data
            for result in results['results']:
                ocr_text = ', '.join([f"{ocr.get('text', '')} ({ocr.get('confidence', 0):.2f})" 
                                    for ocr in result.get('ocr_results', [])])
                vehicle_info = f"{len(result.get('vehicle_detections', []))} vehicles"
                plate_info = f"{len(result.get('plate_detections', []))} plates"
                
                writer.writerow([
                    result['id'],
                    result['timestamp'],
                    result['created_at'],
                    result['vehicles_count'],
                    result['plates_count'],
                    result['processing_time_ms'],
                    ocr_text,
                    vehicle_info,
                    plate_info
                ])
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=detection_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            return response
        
    except Exception as e:
        logger.error(f"Error exporting detection results: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
