# gunicorn_config.py
import os
import multiprocessing

# Server socket
bind = "unix:/tmp/aicamera.sock"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/home/camuser/aicamera/log/gunicorn_access.log"
errorlog = "/home/camuser/aicamera/log/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "aicamera_v1.3"

# Timeout settings
timeout = 30
keepalive = 2

# The app path - using the renamed directory
app = "v1_3.src.app:app"

# Preload app for better performance
preload_app = True

# User and group (will be set by systemd)
# user = "camuser"
# group = "camuser"

# Environment variables
raw_env = [
    "FLASK_ENV=production",
    "FLASK_APP=v1_3.src.app:app"
]