#!/usr/bin/env python3
"""
Experiments Blueprint for AI Camera v1.3

This blueprint provides experiment management and research functionality:
- Experiment dashboard and configuration
- Experiment execution and monitoring
- Results viewing and analysis
- Data collection and reporting
- Night mode lens comparison experiments

Author: AI Camera Team
Version: 1.3.2
Date: August 10, 2025
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_socketio import emit, join_room, leave_room

# Use absolute imports
from v1_3.src.core.dependency_container import get_service
from v1_3.src.core.utils.logging_config import get_logger

# Create blueprint
experiments_bp = Blueprint('experiments', __name__, url_prefix='/experiments')

logger = get_logger(__name__)


def get_experiment_service():
    """Get experiment service from dependency container."""
    try:
        from v1_3.src.core.dependency_container import get_service
        return get_service('experiment_service')
    except Exception as e:
        logger.error(f"Error getting experiment service: {e}")
        return None


@experiments_bp.route('/')
def dashboard():
    """
    Experiments dashboard page.
    
    Returns:
        str: Rendered HTML template
    """
    try:
        experiment_service = get_experiment_service()
        if not experiment_service:
            return render_template('experiments/dashboard.html',
                                 experiments=[],
                                 error="Experiment service not available",
                                 title="Experiments Dashboard")
        
        # Get available experiments
        available_experiments = experiment_service.get_available_experiments()
        
        # For now, return empty list of past experiments
        # In the future, this could load from database or CSV
        past_experiments = []
        
        return render_template('experiments/dashboard.html',
                             experiments=past_experiments,
                             available_experiments=available_experiments,
                             title="Experiments Dashboard")
    except Exception as e:
        logger.error(f"Error in experiments dashboard: {e}")
        return render_template('experiments/dashboard.html',
                             experiments=[],
                             available_experiments=[],
                             error=str(e),
                             title="Experiments Dashboard")


@experiments_bp.route('/new', methods=['GET', 'POST'])
def new_experiment():
    """
    Create new experiment page.
    
    Returns:
        str: Rendered HTML template or redirect
    """
    if request.method == 'POST':
        try:
            # Generate experiment ID
            exp_id = str(uuid.uuid4())
            
            # Get form data
            experiment_config = {
                "experiment_id": exp_id,
                "experiment_type": request.form.get("experiment_type"),
                "camera_type": request.form.getlist("camera_type"),
                "lens_cover": request.form.getlist("lens_cover"),
                "start_distance_m": int(request.form.get("start_distance_m", 1)),
                "end_distance_m": int(request.form.get("end_distance_m", 10)),
                "step_distance_m": int(request.form.get("step_distance_m", 1)),
                "is_night_mode": request.form.get("is_night_mode") == "on",
                "night_exposure_times": request.form.getlist("night_exposure_times"),
                "night_analog_gains": request.form.getlist("night_analog_gains"),
                "night_lens_positions": request.form.getlist("night_lens_positions"),
                "night_sharpness_values": request.form.getlist("night_sharpness_values"),
                "night_noise_reduction_modes": request.form.getlist("night_noise_reduction_modes"),
                "created_at": datetime.now().isoformat()
            }
            
            # Store experiment config in session or temporary storage
            # For now, store in current_app config (in production, use database)
            if 'experiment_configs' not in current_app.config:
                current_app.config['experiment_configs'] = {}
            current_app.config['experiment_configs'][exp_id] = experiment_config
            
            logger.info(f"Created new experiment: {exp_id}")
            
            return redirect(url_for('experiments.run_experiment', experiment_id=exp_id))
            
        except Exception as e:
            logger.error(f"Error creating new experiment: {e}")
            return render_template('experiments/new_experiment.html',
                                 error=str(e),
                                 title="New Experiment")
    
    # GET request - show form
    try:
        experiment_service = get_experiment_service()
        available_experiments = experiment_service.get_available_experiments() if experiment_service else []
        
        return render_template('experiments/new_experiment.html',
                             available_experiments=available_experiments,
                             title="New Experiment")
    except Exception as e:
        logger.error(f"Error loading new experiment form: {e}")
        return render_template('experiments/new_experiment.html',
                             available_experiments=[],
                             error=str(e),
                             title="New Experiment")


@experiments_bp.route('/run/<experiment_id>')
def run_experiment(experiment_id):
    """
    Run experiment page.
    
    Args:
        experiment_id: ID of the experiment to run
        
    Returns:
        str: Rendered HTML template
    """
    try:
        # Get experiment config
        experiment_configs = current_app.config.get('experiment_configs', {})
        experiment_config = experiment_configs.get(experiment_id)
        
        if not experiment_config:
            return render_template('experiments/error.html',
                                 error="Experiment not found",
                                 title="Experiment Error")
        
        return render_template('experiments/run_experiment.html',
                             experiment_id=experiment_id,
                             experiment_config=experiment_config,
                             title="Run Experiment")
    except Exception as e:
        logger.error(f"Error loading run experiment page: {e}")
        return render_template('experiments/error.html',
                             error=str(e),
                             title="Experiment Error")


@experiments_bp.route('/api/run_step/<experiment_id>', methods=['POST'])
def api_run_step(experiment_id):
    """
    API endpoint to run a single experiment step.
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        dict: JSON response with step results
    """
    try:
        experiment_service = get_experiment_service()
        if not experiment_service:
            return jsonify({
                'success': False,
                'error': 'Experiment service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Get experiment config
        experiment_configs = current_app.config.get('experiment_configs', {})
        experiment_config = experiment_configs.get(experiment_id)
        
        if not experiment_config:
            return jsonify({
                'success': False,
                'error': 'Experiment not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Create step config
        step_config = {
            "experiment_id": experiment_id,
            "distance_m": data.get('current_distance'),
            "camera_type": data.get('current_camera_type'),
            "lens_cover": data.get('current_lens_cover'),
            "is_night_mode": data.get('is_night_mode', False),
            "exposure_time_us": data.get("exposure_time_us"),
            "analog_gain": data.get("analog_gain"),
            "lens_position": data.get("lens_position"),
            "sharpness": data.get("sharpness"),
            "noise_reduction_mode": data.get("noise_reduction_mode"),
            "experiment_type": experiment_config.get("experiment_type", "Unknown")
        }
        
        # Run experiment step
        result = experiment_service.run_experiment_step(step_config)
        
        return jsonify({
            'success': result.get('status') == 'success',
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error running experiment step: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@experiments_bp.route('/results/<experiment_id>')
def view_results(experiment_id):
    """
    View experiment results page.
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        str: Rendered HTML template
    """
    try:
        experiment_service = get_experiment_service()
        if not experiment_service:
            return render_template('experiments/error.html',
                                 error="Experiment service not available",
                                 title="Experiment Error")
        
        # Get experiment summary
        summary = experiment_service.summarize_results(experiment_id)
        
        # Get experiment details
        experiment_details = experiment_service.get_experiment_details(experiment_id)
        
        # Get raw results from CSV (for detailed view)
        raw_results = []
        try:
            import csv
            csv_path = experiment_service.csv_path
            with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("ExperimentID") == experiment_id:
                        raw_results.append(row)
        except Exception as e:
            logger.warning(f"Could not load raw results: {e}")
        
        return render_template('experiments/results.html',
                             experiment_id=experiment_id,
                             summary=summary,
                             experiment_details=experiment_details,
                             raw_results=raw_results,
                             title="Experiment Results")
    except Exception as e:
        logger.error(f"Error loading experiment results: {e}")
        return render_template('experiments/error.html',
                             error=str(e),
                             title="Experiment Error")


@experiments_bp.route('/api/experiments')
def api_get_experiments():
    """
    API endpoint to get available experiments.
    
    Returns:
        dict: JSON response with available experiments
    """
    try:
        experiment_service = get_experiment_service()
        if not experiment_service:
            return jsonify({
                'success': False,
                'error': 'Experiment service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        available_experiments = experiment_service.get_available_experiments()
        
        return jsonify({
            'success': True,
            'data': available_experiments,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting experiments: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@experiments_bp.route('/api/experiment/<experiment_id>')
def api_get_experiment(experiment_id):
    """
    API endpoint to get experiment details.
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        dict: JSON response with experiment details
    """
    try:
        experiment_service = get_experiment_service()
        if not experiment_service:
            return jsonify({
                'success': False,
                'error': 'Experiment service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        experiment_details = experiment_service.get_experiment_details(experiment_id)
        
        return jsonify({
            'success': True,
            'data': experiment_details,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting experiment details: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@experiments_bp.route('/api/summary/<experiment_id>')
def api_get_summary(experiment_id):
    """
    API endpoint to get experiment summary.
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        dict: JSON response with experiment summary
    """
    try:
        experiment_service = get_experiment_service()
        if not experiment_service:
            return jsonify({
                'success': False,
                'error': 'Experiment service not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        summary = experiment_service.summarize_results(experiment_id)
        
        return jsonify({
            'success': True,
            'data': summary,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting experiment summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# WebSocket events for real-time updates
def register_experiment_events(socketio):
    """
    Register WebSocket events for experiment functionality.
    
    Args:
        socketio: Flask-SocketIO instance
    """
    
    @socketio.on('join_experiment')
    def handle_join_experiment(data):
        """Join experiment room for real-time updates."""
        experiment_id = data.get('experiment_id')
        if experiment_id:
            join_room(f'experiment_{experiment_id}')
            emit('joined_experiment', {'experiment_id': experiment_id})
    
    @socketio.on('leave_experiment')
    def handle_leave_experiment(data):
        """Leave experiment room."""
        experiment_id = data.get('experiment_id')
        if experiment_id:
            leave_room(f'experiment_{experiment_id}')
            emit('left_experiment', {'experiment_id': experiment_id})
    
    @socketio.on('experiment_step_complete')
    def handle_experiment_step_complete(data):
        """Handle experiment step completion."""
        experiment_id = data.get('experiment_id')
        step_result = data.get('result')
        
        if experiment_id and step_result:
            # Broadcast to all clients in the experiment room
            emit('step_result', step_result, room=f'experiment_{experiment_id}')
    
    @socketio.on('experiment_error')
    def handle_experiment_error(data):
        """Handle experiment errors."""
        experiment_id = data.get('experiment_id')
        error_message = data.get('error')
        
        if experiment_id and error_message:
            emit('experiment_error', {
                'experiment_id': experiment_id,
                'error': error_message,
                'timestamp': datetime.now().isoformat()
            }, room=f'experiment_{experiment_id}')
