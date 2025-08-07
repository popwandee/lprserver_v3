#!/bin/bash

# AI Camera Production Startup Script
# Uses Nginx + Gunicorn for production deployment

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/venv_hailo"
APP_NAME="ai-camera-production"
LOG_DIR="$SCRIPT_DIR/log"
PID_FILE="$SCRIPT_DIR/gunicorn.pid"
NGINX_CONF="$SCRIPT_DIR/nginx.conf"
GUNICORN_CONF="$SCRIPT_DIR/gunicorn.conf.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Function to check if gunicorn is running
is_gunicorn_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Function to check if nginx is running
is_nginx_running() {
    if pgrep -x "nginx" > /dev/null; then
        return 0
    fi
    return 1
}

# Function to start gunicorn
start_gunicorn() {
    if is_gunicorn_running; then
        error "Gunicorn is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi

    log "Starting Gunicorn..."

    # Change to script directory
    cd "$SCRIPT_DIR"

    # Check virtual environment
    if [ ! -d "$VENV_PATH" ]; then
        error "Virtual environment not found at $VENV_PATH"
        return 1
    fi

    # Activate virtual environment
    source "$VENV_PATH/bin/activate"

    # Check if gunicorn is installed
    if ! python -c "import gunicorn" 2>/dev/null; then
        error "Gunicorn not found. Installing..."
        pip install gunicorn
    fi

    # Check if app.py exists
    if [ ! -f "app.py" ]; then
        error "app.py not found"
        return 1
    fi

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Set environment variables
    export FLASK_ENV=production
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export HEF_MODEL_PATH="@local"
    export MODEL_ZOO_URL="resources"

    # Start gunicorn
    gunicorn -c "$GUNICORN_CONF" wsgi:app &
    local gunicorn_pid=$!

    # Wait a moment to check if it started
    sleep 3
    if kill -0 $gunicorn_pid 2>/dev/null; then
        log "✅ Gunicorn started successfully (PID: $gunicorn_pid)"
        echo $gunicorn_pid > "$PID_FILE"
    else
        error "Gunicorn failed to start"
        return 1
    fi
}

# Function to start nginx
start_nginx() {
    if is_nginx_running; then
        warn "Nginx is already running"
        return 0
    fi

    log "Starting Nginx..."

    # Check if nginx is installed
    if ! command -v nginx &> /dev/null; then
        error "Nginx not found. Please install nginx first: sudo apt install nginx"
        return 1
    fi

    # Copy nginx config
    sudo cp "$NGINX_CONF" /etc/nginx/sites-available/ai-camera
    sudo ln -sf /etc/nginx/sites-available/ai-camera /etc/nginx/sites-enabled/
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default

    # Test nginx config
    if sudo nginx -t; then
        sudo systemctl start nginx
        sudo systemctl enable nginx
        log "✅ Nginx started successfully"
    else
        error "Nginx configuration test failed"
        return 1
    fi
}

# Function to stop gunicorn
stop_gunicorn() {
    if is_gunicorn_running; then
        local pid=$(cat "$PID_FILE")
        log "Stopping Gunicorn (PID: $pid)..."
        kill -TERM "$pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            warn "Force killing Gunicorn..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
        log "Gunicorn stopped"
    else
        log "Gunicorn is not running"
    fi
}

# Function to stop nginx
stop_nginx() {
    if is_nginx_running; then
        log "Stopping Nginx..."
        sudo systemctl stop nginx
        log "Nginx stopped"
    else
        log "Nginx is not running"
    fi
}

# Function to restart services
restart_services() {
    log "Restarting services..."
    stop_gunicorn
    stop_nginx
    sleep 2
    start_gunicorn
    start_nginx
}

# Function to show status
show_status() {
    echo "=== AI Camera Production Status ==="
    
    if is_gunicorn_running; then
        local pid=$(cat "$PID_FILE")
        log "Gunicorn: Running (PID: $pid)"
        
        # Check if port 8000 is listening
        if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
            log "Gunicorn is listening on port 8000"
        else
            warn "Gunicorn may not be ready yet"
        fi
    else
        log "Gunicorn: Not running"
    fi
    
    if is_nginx_running; then
        log "Nginx: Running"
        
        # Check if port 80 is listening
        if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
            log "Nginx is listening on port 80"
        else
            warn "Nginx may not be ready yet"
        fi
    else
        log "Nginx: Not running"
    fi
    
    # Show recent logs
    if [ -f "$LOG_DIR/gunicorn_error.log" ]; then
        log "Recent Gunicorn errors:"
        tail -3 "$LOG_DIR/gunicorn_error.log" | sed 's/^/  /'
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_DIR/gunicorn_error.log" ]; then
        tail -f "$LOG_DIR/gunicorn_error.log"
    else
        error "Gunicorn error log not found"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start Nginx and Gunicorn"
    echo "  stop    - Stop Nginx and Gunicorn"
    echo "  restart - Restart all services"
    echo "  status  - Show service status"
    echo "  logs    - Show Gunicorn error logs"
    echo "  help    - Show this help message"
    echo ""
    echo "Access:"
    echo "  Web Interface: http://localhost"
    echo "  API Endpoints: http://localhost/api/"
    echo ""
    echo "Files:"
    echo "  Nginx Config: $NGINX_CONF"
    echo "  Gunicorn Config: $GUNICORN_CONF"
    echo "  Log Directory: $LOG_DIR"
}

# Main script logic
case "${1:-start}" in
    start)
        log "Starting AI Camera Production Services..."
        start_gunicorn
        start_nginx
        log "✅ All services started successfully"
        log "Access the application at: http://localhost"
        ;;
    stop)
        log "Stopping AI Camera Production Services..."
        stop_gunicorn
        stop_nginx
        log "✅ All services stopped"
        ;;
    restart)
        restart_services
        log "✅ All services restarted successfully"
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 