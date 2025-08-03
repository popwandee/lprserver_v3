from app import app, socketio
import logging

logger = logging.getLogger(__name__)
logger.info("WSGI started: Initializing Flask app for Gunicorn.")

# Gunicorn expects an 'app' callable.
# Flask-SocketIO's 'socketio.run' starts its own server and event loop.
# When using Gunicorn, you typically run Gunicorn with eventlet/gevent workers
# and let SocketIO handle its own WebSocket connections within that context.
# We'll expose the Flask app directly for Gunicorn.
# The SocketIO setup in app.py remains relevant for handling WebSocket logic
# when Gunicorn uses gevent or eventlet workers.
if __name__ == '__main__':
    # This block is for direct execution of wsgi.py if you ever needed it,
    # but Gunicorn will typically import and run the 'app' variable directly.
    logger.warning("wsgi.py is typically run by a WSGI server like Gunicorn, not directly.")
    socketio.run(app, host='0.0.0.0', port=5000) # Fallback for direct run