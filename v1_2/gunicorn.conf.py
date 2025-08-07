# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes - Use only 1 worker for camera access
workers = 1
worker_class = "gthread"
threads = 4
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "log/gunicorn_access.log"
errorlog = "log/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "ai-camera-gunicorn"

# User/group
user = "camuser"
group = "camuser"

# Preload app
preload_app = True

# Daemon mode
daemon = False

# PID file
pidfile = "gunicorn.pid"

# SSL (if needed)
# keyfile = "ssl/private.key"
# certfile = "ssl/certificate.crt" 