"""
User Manager Blueprint

This blueprint handles user management including:
- User authentication and authorization
- User profile management
- Role and permission management
- User activity tracking
"""

from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import logging
from functools import wraps

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

logger = logging.getLogger(__name__)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        if 'role' not in session or session['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/')
@login_required
def index():
    """User Manager main page"""
    return render_template('user/index.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        try:
            from src.services.user_service import get_user_service
            user_service = get_user_service()
            
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = user_service.authenticate_user(username, password)
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                
                # Log login activity
                user_service.log_user_activity(user['id'], 'login', 'User logged in')
                
                return redirect(url_for('main.index'))
            else:
                return render_template('user/login.html', error='Invalid credentials')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render_template('user/login.html', error='Login failed')
    
    return render_template('user/login.html')

@user_bp.route('/logout')
def logout():
    """User logout"""
    try:
        if 'user_id' in session:
            from src.services.user_service import get_user_service
            user_service = get_user_service()
            
            # Log logout activity
            user_service.log_user_activity(session['user_id'], 'logout', 'User logged out')
        
        session.clear()
        return redirect(url_for('user.login'))
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        session.clear()
        return redirect(url_for('user.login'))

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        user = user_service.get_user_by_id(session['user_id'])
        activities = user_service.get_user_activities(session['user_id'], limit=10)
        
        return render_template('user/profile.html', user=user, activities=activities)
    except Exception as e:
        logger.error(f"Error loading user profile: {str(e)}")
        return render_template('user/profile.html', error=str(e))

@user_bp.route('/users')
@admin_required
def users():
    """User management page (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = user_service.get_users(page=page, per_page=per_page)
        
        return render_template('user/users.html', users=users)
    except Exception as e:
        logger.error(f"Error loading users: {str(e)}")
        return render_template('user/users.html', users=[], error=str(e))

@user_bp.route('/roles')
@admin_required
def roles():
    """Role management page (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        roles = user_service.get_roles()
        permissions = user_service.get_permissions()
        
        return render_template('user/roles.html', roles=roles, permissions=permissions)
    except Exception as e:
        logger.error(f"Error loading roles: {str(e)}")
        return render_template('user/roles.html', error=str(e))

@user_bp.route('/activities')
@admin_required
def activities():
    """User activities page (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user_id')
        activity_type = request.args.get('activity_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        activities = user_service.get_activities(
            page=page,
            per_page=per_page,
            user_id=user_id,
            activity_type=activity_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return render_template('user/activities.html', activities=activities)
    except Exception as e:
        logger.error(f"Error loading activities: {str(e)}")
        return render_template('user/activities.html', activities=[], error=str(e))

# API Endpoints
@user_bp.route('/api/login', methods=['POST'])
def api_login():
    """User login API"""
    try:
        data = request.get_json()
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        username = data.get('username')
        password = data.get('password')
        
        user = user_service.authenticate_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            # Log login activity
            user_service.log_user_activity(user['id'], 'login', 'User logged in via API')
            
            return jsonify({
                'success': True,
                'user': user
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
    except Exception as e:
        logger.error(f"API Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """User logout API"""
    try:
        if 'user_id' in session:
            from src.services.user_service import get_user_service
            user_service = get_user_service()
            
            # Log logout activity
            user_service.log_user_activity(session['user_id'], 'logout', 'User logged out via API')
        
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        logger.error(f"API Logout error: {str(e)}")
        session.clear()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/profile', methods=['GET'])
@login_required
def api_get_profile():
    """Get user profile API"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        user = user_service.get_user_by_id(session['user_id'])
        
        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        logger.error(f"API Error getting profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    """Update user profile API"""
    try:
        data = request.get_json()
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        user = user_service.update_user_profile(session['user_id'], data)
        
        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        logger.error(f"API Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/profile/password', methods=['PUT'])
@login_required
def api_change_password():
    """Change password API"""
    try:
        data = request.get_json()
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        result = user_service.change_password(
            session['user_id'],
            current_password,
            new_password
        )
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    except Exception as e:
        logger.error(f"API Error changing password: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/users', methods=['GET'])
@admin_required
def api_get_users():
    """Get users API (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = user_service.get_users(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'users': users['users'],
            'pagination': users['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting users: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    """Create user API (admin only)"""
    try:
        data = request.get_json()
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        user = user_service.create_user(
            username=data.get('username'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            email=data.get('email'),
            role=data.get('role', 'user')
        )
        
        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        logger.error(f"API Error creating user: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/users/<user_id>', methods=['GET'])
@admin_required
def api_get_user(user_id):
    """Get user by ID API (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        logger.error(f"API Error getting user: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/users/<user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    """Update user API (admin only)"""
    try:
        data = request.get_json()
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        user = user_service.update_user(user_id, data)
        
        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        logger.error(f"API Error updating user: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/users/<user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    """Delete user API (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        user_service.delete_user(user_id)
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
    except Exception as e:
        logger.error(f"API Error deleting user: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/roles', methods=['GET'])
@admin_required
def api_get_roles():
    """Get roles API (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        roles = user_service.get_roles()
        
        return jsonify({
            'success': True,
            'roles': roles
        })
    except Exception as e:
        logger.error(f"API Error getting roles: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/roles', methods=['POST'])
@admin_required
def api_create_role():
    """Create role API (admin only)"""
    try:
        data = request.get_json()
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        role = user_service.create_role(
            name=data.get('name'),
            description=data.get('description'),
            permissions=data.get('permissions', [])
        )
        
        return jsonify({
            'success': True,
            'role': role
        })
    except Exception as e:
        logger.error(f"API Error creating role: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/activities', methods=['GET'])
@admin_required
def api_get_activities():
    """Get user activities API (admin only)"""
    try:
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user_id')
        activity_type = request.args.get('activity_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        activities = user_service.get_activities(
            page=page,
            per_page=per_page,
            user_id=user_id,
            activity_type=activity_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'activities': activities['activities'],
            'pagination': activities['pagination']
        })
    except Exception as e:
        logger.error(f"API Error getting activities: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@user_bp.route('/socket/user-activity', methods=['POST'])
def socket_user_activity():
    """Handle user activity via WebSocket"""
    try:
        data = request.get_json()
        from src.services.user_service import get_user_service
        user_service = get_user_service()
        
        # Log user activity
        activity = user_service.log_user_activity(
            user_id=data.get('user_id'),
            activity_type=data.get('activity_type'),
            description=data.get('description'),
            metadata=data.get('metadata', {})
        )
        
        # Emit activity to admin dashboard
        emit('user_activity_update', activity, broadcast=True)
        
        return jsonify({
            'success': True,
            'activity': activity
        })
    except Exception as e:
        logger.error(f"Socket Error processing user activity: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
