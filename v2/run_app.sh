#!/bin/bash

# AI Camera Application Startup Script
# Optimized for systemd service deployment
# This script starts the AI camera application with proper environment setup

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/venv_hailo"
APP_NAME="ai-camera-v2"
LOG_DIR="$SCRIPT_DIR/log"
PID_FILE="$SCRIPT_DIR/ai_camera.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Function to check if application is already running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
        fi
    fi
    return 1  # Not running
}

# Function to stop application
stop_app() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        log "Stopping $APP_NAME (PID: $pid)..."
        kill -TERM "$pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            warn "Process still running, force killing..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
        log "$APP_NAME stopped"
    else
        log "$APP_NAME is not running"
    fi
}

# Function to start application
start_app() {
    if is_running; then
        error "$APP_NAME is already running (PID: $(cat "$PID_FILE"))"
        exit 1
    fi

    log "Starting $APP_NAME..."

    # Change to the script directory
    cd "$SCRIPT_DIR"

    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        error "Virtual environment not found at $VENV_PATH"
        error "Please run setup_env.sh first or activate your virtual environment manually"
        exit 1
    fi

    # Activate virtual environment
    log "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"

    # Check if app.py exists
    if [ ! -f "app.py" ]; then
        error "app.py not found in current directory"
        exit 1
    fi

    # Check required Python packages
    log "Checking dependencies..."
    python3 -c "import flask, picamera2, cv2, numpy, degirum" 2>/dev/null || {
        error "Required Python packages not found"
        error "Please install dependencies: pip install flask picamera2 opencv-python numpy degirum"
        exit 1
    }

    # Create necessary directories
    mkdir -p static/images
    mkdir -p captured_images
    mkdir -p log
    mkdir -p tests

    # Set environment variables
    export FLASK_ENV=production
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export HEF_MODEL_PATH="@local"
    export MODEL_ZOO_URL="resources"

    # Check Hailo environment
    if python3 -c "import degirum" 2>/dev/null; then
        log "✅ Degirum is available"
    else
        warn "Degirum not found in virtual environment"
    fi

    if python3 -c "import easyocr" 2>/dev/null; then
        log "✅ EasyOCR is available"
    else
        warn "EasyOCR not found in virtual environment"
    fi

    # Start the application in background
    log "Starting Flask application..."
    nohup python3 app.py > "$LOG_DIR/app.log" 2>&1 &
    local app_pid=$!

    # Save PID
    echo $app_pid > "$PID_FILE"

    # Wait a moment to check if it started successfully
    sleep 3
    if kill -0 $app_pid 2>/dev/null; then
        log "✅ $APP_NAME started successfully (PID: $app_pid)"
        log "Access the application at: http://localhost:5000"
        log "Log file: $LOG_DIR/app.log"
        log "PID file: $PID_FILE"
    else
        error "$APP_NAME failed to start"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        log "$APP_NAME is running (PID: $pid)"
        
        # Check if port 5000 is listening
        if netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
            log "Web interface is accessible at http://localhost:5000"
        else
            warn "Web interface may not be ready yet"
        fi
        
        # Show recent logs
        if [ -f "$LOG_DIR/app.log" ]; then
            log "Recent logs:"
            tail -5 "$LOG_DIR/app.log" | sed 's/^/  /'
        fi
    else
        log "$APP_NAME is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_DIR/app.log" ]; then
        tail -f "$LOG_DIR/app.log"
    else
        error "Log file not found: $LOG_DIR/app.log"
        exit 1
    fi
}

# Function to restart application
restart_app() {
    log "Restarting $APP_NAME..."
    stop_app
    sleep 2
    start_app
}

# Function to show help
show_help() {
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the AI Camera application"
    echo "  stop    - Stop the AI Camera application"
    echo "  restart - Restart the AI Camera application"
    echo "  status  - Show application status"
    echo "  logs    - Show application logs (follow mode)"
    echo "  help    - Show this help message"
    echo ""
    echo "Environment:"
    echo "  Virtual Environment: $VENV_PATH"
    echo "  Application Directory: $SCRIPT_DIR"
    echo "  Log Directory: $LOG_DIR"
    echo "  PID File: $PID_FILE"
}

# Main script logic
case "${1:-start}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
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