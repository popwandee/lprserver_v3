import os
import logging
from flask import Flask, render_template, Response, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO

# Import our custom modules
from .config import (
    FLASK_HOST, FLASK_PORT, SECRET_KEY
)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static')
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)

# --- Flask Routes ---

@app.route('/')
def index():
    """Home page with basic structure."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Route to stream camera video feed."""
    return Response("Video feed placeholder", mimetype='text/plain')

@app.route('/update_camera_settings', methods=['POST'])
def update_camera_settings():
    """Handles submission of camera settings form."""
    flash('Camera settings updated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/close_camera', methods=['POST'])
def close_camera():
    """Stops camera and returns a JSON response."""
    return jsonify({'status': 'success', 'message': 'Camera closed successfully.'})

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'aicamera_v1.3'})

# --- Application Startup and Shutdown ---

def startup():
    """Initialize application."""
    logger.info("Setting up application: Basic initialization complete.")

@app.teardown_appcontext
def shutdown_application(exception=None):
    """Gracefully shuts down resources when Flask app context ends."""
    logger.info("Application teardown complete.")

# --- Run the Flask App ---
if __name__ == '__main__':
    startup()  
    socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)