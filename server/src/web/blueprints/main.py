"""
Main Blueprint for LPR Server

This blueprint provides the main web interface including dashboard,
records view, and blacklist management.
"""

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from core.import_helper import setup_absolute_imports

# Setup absolute imports
setup_absolute_imports()

from core.models.lpr_record import LPRRecord
from core.models import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@main_bp.route('/records')
def records():
    """Records table view"""
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
    
    records = pagination.items
    
    return render_template('records.html', 
                         records=records, 
                         pagination=pagination,
                         camera_id=camera_id,
                         plate_number=plate_number,
                         date_from=date_from,
                         date_to=date_to)

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with statistics"""
    # Get today's records
    today = datetime.now().date()
    today_records = LPRRecord.query.filter(
        db.func.date(LPRRecord.timestamp) == today
    ).count()
    
    # Get total records
    total_records = LPRRecord.query.count()
    
    # Get unique cameras
    unique_cameras = db.session.query(LPRRecord.camera_id).distinct().count()
    
    # Get recent records for table
    recent_records = LPRRecord.query.order_by(
        LPRRecord.timestamp.desc()
    ).limit(10).all()
    
    return render_template('dashboard.html',
                         today_records=today_records,
                         total_records=total_records,
                         unique_cameras=unique_cameras,
                         recent_records=recent_records)

@main_bp.route('/blacklist')
def blacklist():
    """Blacklist management page"""
    return render_template('blacklist.html')
