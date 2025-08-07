#!/bin/bash

# AI Camera Extended Production Startup Script
# Manages Nginx + Gunicorn + WebSocket Services for complete production deployment

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

# WebSocket Services
WEBSOCKET_SENDER_SERVICE="websocket-sender"
WEBSOCKET_SERVER_SERVICE="websocket-server"

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

# Function to check systemd service status
is_service_running() {
    local service_name=$1
    systemctl is-active --quiet "$service_name" 2>/dev/null
}

# Function to start WebSocket services
start_websocket_services() {
    log "Starting WebSocket services..."
    
    # Note: WebSocket Server should be running on a separate machine
    log "ℹ️  WebSocket Server should be running on a separate machine"
    log "ℹ️  Server files are available in: websocket_server/ directory"
    
    # Start WebSocket Sender
    if is_service_running "$WEBSOCKET_SENDER_SERVICE"; then
        warn "WebSocket Sender is already running"
    else
        log "Starting WebSocket Sender..."
        if sudo systemctl start "$WEBSOCKET_SENDER_SERVICE" 2>/dev/null; then
            log "✅ WebSocket Sender started"
        else
            warn "Could not start WebSocket Sender as systemd service, trying standalone..."
            # Try standalone version
            if [ -f "run_websocket_sender.sh" ]; then
                ./run_websocket_sender.sh start
            else
                error "WebSocket Sender startup failed"
            fi
        fi
    fi
}

# Function to stop WebSocket services (Sender only)
stop_websocket_services() {
    log "Stopping WebSocket services (Sender only)..."
    
    # Stop WebSocket Sender only
    if is_service_running "$WEBSOCKET_SENDER_SERVICE"; then
        log "Stopping WebSocket Sender..."
        sudo systemctl stop "$WEBSOCKET_SENDER_SERVICE" 2>/dev/null || true
    else
        # Try standalone version
        if [ -f "run_websocket_sender.sh" ]; then
            ./run_websocket_sender.sh stop 2>/dev/null || true
        fi
    fi
    
    log "WebSocket services stopped"
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
    sleep 5
    if kill -0 $gunicorn_pid 2>/dev/null; then
        log "✅ Gunicorn started successfully (PID: $gunicorn_pid)"
        echo $gunicorn_pid > "$PID_FILE"
        
        # Wait for Flask app to fully initialize
        log "Waiting for Flask application to initialize..."
        local max_attempts=30
        local attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if curl -s http://localhost:8000/api/camera_status > /dev/null 2>&1; then
                log "✅ Flask application is ready"
                break
            fi
            sleep 2
            attempt=$((attempt + 1))
            if [ $((attempt % 5)) -eq 0 ]; then
                log "Still waiting for Flask app... (attempt $attempt/$max_attempts)"
            fi
        done
        
        if [ $attempt -eq $max_attempts ]; then
            warn "Flask app may not be fully ready, but continuing..."
        fi
    else
        error "Gunicorn failed to start"
        return 1
    fi
}

# Function to verify all services are running
verify_services() {
    log "Verifying all services are running..."
    
    # Wait for Flask app to fully initialize
    sleep 5
    
    # Check basic services first (non-blocking)
    log "Checking basic services..."
    local health_status=$(timeout 5 curl -s http://localhost:8000/api/health_status 2>/dev/null || echo "{}")
    if echo "$health_status" | grep -q '"monitoring": true'; then
        log "✅ Health monitoring confirmed"
    else
        warn "Health monitoring may not be running properly (will start automatically)"
    fi
    
    # Check WebSocket sender status (non-blocking)
    log "Checking WebSocket sender status..."
    local websocket_status=$(timeout 5 curl -s http://localhost:8000/api/websocket_status 2>/dev/null || echo "{}")
    if echo "$websocket_status" | grep -q '"running": true'; then
        log "✅ WebSocket sender confirmed"
    else
        warn "WebSocket sender may not be running properly (ignoring if server unreachable)"
    fi
    
    # Camera and detection are now auto-started by Flask app
    log "✅ All services verified - Camera and detection auto-starting internally"
}

# Function to initialize camera and detection externally
initialize_camera_and_detection() {
    log "Starting external camera and detection initialization..."
    
    # Wait for Flask app to be fully ready
    sleep 5
    
    # STEP 1: Start camera
    log "=== STEP 1: Starting camera ==="
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Camera start attempt $attempt/$max_attempts..."
        local camera_response=$(curl -s -X POST http://localhost:8000/api/start_camera 2>/dev/null || echo "{}")
        
        if echo "$camera_response" | grep -q "success"; then
            log "✅ Camera started successfully"
            break
        else
            warn "Camera start attempt $attempt failed: $camera_response"
            if [ $attempt -eq $max_attempts ]; then
                error "❌ Failed to start camera after $max_attempts attempts"
                return 1
            fi
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    # Wait for camera to initialize
    sleep 5
    
    # STEP 2: Verify camera status
    log "=== STEP 2: Verifying camera status ==="
    local camera_status=$(curl -s http://localhost:8000/api/camera_status 2>/dev/null || echo "{}")
    if echo "$camera_status" | grep -q '"streaming": true'; then
        log "✅ Camera streaming confirmed"
    else
        warn "⚠️ Camera may not be streaming properly"
        log "Camera status: $camera_status"
    fi
    
    # STEP 3: Start detection
    log "=== STEP 3: Starting detection ==="
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        log "Detection start attempt $attempt/$max_attempts..."
        local detection_response=$(curl -s -X POST http://localhost:8000/api/start_detection 2>/dev/null || echo "{}")
        
        if echo "$detection_response" | grep -q "success"; then
            log "✅ Detection started successfully"
            break
        else
            warn "Detection start attempt $attempt failed: $detection_response"
            if [ $attempt -eq $max_attempts ]; then
                error "❌ Failed to start detection after $max_attempts attempts"
                return 1
            fi
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    # Wait for detection to initialize
    sleep 5
    
    # STEP 4: Verify detection status
    log "=== STEP 4: Verifying detection status ==="
    local detection_status=$(curl -s http://localhost:8000/api/detection_status 2>/dev/null || echo "{}")
    if echo "$detection_status" | grep -q '"running": true'; then
        log "✅ Detection running confirmed"
    else
        warn "⚠️ Detection may not be running properly"
        log "Detection status: $detection_status"
    fi
    
    log "🎉 Camera and detection initialization complete!"
    return 0
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

# Function to restart all services
restart_all_services() {
    log "Restarting all services..."
    stop_websocket_services
    stop_gunicorn
    stop_nginx
    sleep 3
    start_websocket_services
    start_gunicorn
    start_nginx
}

# Function to show comprehensive status
show_status() {
    echo "=== AI Camera Extended Production Status ==="
    echo ""
    
    # WebSocket Services Status
    echo -e "${BLUE}🔗 WebSocket Services:${NC}"
    
    echo -e "${YELLOW}ℹ️  WebSocket Server: Should be running on separate machine${NC}"
    echo -e "${YELLOW}ℹ️  Server files available in: websocket_server/ directory${NC}"
    
    if is_service_running "$WEBSOCKET_SENDER_SERVICE"; then
        log "WebSocket Sender: Running (systemd)"
    elif pgrep -f "websocket_sender.py" > /dev/null; then
        log "WebSocket Sender: Running (standalone)"
    else
        warn "WebSocket Sender: Not running"
    fi
    
    echo ""
    
    # Main Application Status
    echo -e "${BLUE}🚀 Main Application:${NC}"
    
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
        warn "Gunicorn: Not running"
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
        warn "Nginx: Not running"
    fi
    
    echo ""
    
    # Database and Statistics
    echo -e "${BLUE}📊 System Statistics:${NC}"
    
    # Check main database
    if [ -f "db/lpr_data.db" ]; then
        cd "$SCRIPT_DIR"
        source "$VENV_PATH/bin/activate" 2>/dev/null || true
        python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('db/lpr_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM detection_results')
    total_detections = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM detection_results WHERE sent_to_server = 0')
    unsent_detections = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM health_checks')
    total_health = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM health_checks WHERE sent_to_server = 0')
    unsent_health = cursor.fetchone()[0]
    print(f'📈 Total Detection Records: {total_detections}')
    print(f'📤 Unsent Detection Records: {unsent_detections}')
    print(f'🏥 Total Health Records: {total_health}')
    print(f'📤 Unsent Health Records: {unsent_health}')
    conn.close()
except Exception as e:
    print(f'⚠️  Could not check main database: {e}')
" 2>/dev/null || warn "Could not check main database"
    fi
    
    # Check WebSocket server database
    if [ -f "websocket_server.db" ]; then
        python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('websocket_server.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM lpr_detections')
    server_lpr = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM health_monitors')
    server_health = cursor.fetchone()[0]
    print(f'📨 Server Received LPR: {server_lpr}')
    print(f'📨 Server Received Health: {server_health}')
    conn.close()
except Exception as e:
    print(f'⚠️  Could not check server database: {e}')
" 2>/dev/null || warn "Could not check server database"
    fi
    
    echo ""
    
    # Network Status
    echo -e "${BLUE}🌐 Network Status:${NC}"
    netstat -tlnp 2>/dev/null | grep -E ":(80|8000|8765) " | while read line; do
        echo "   $line"
    done || warn "Could not check network status"
    
    echo ""
    
    # Show recent logs
    log "Recent logs:"
    
    if [ -f "$LOG_DIR/gunicorn_error.log" ]; then
        echo -e "${YELLOW}🚀 Gunicorn (last 2 lines):${NC}"
        tail -2 "$LOG_DIR/gunicorn_error.log" | sed 's/^/   /'
    fi
    
    if [ -f "$LOG_DIR/websocket_sender.log" ]; then
        echo -e "${YELLOW}📤 WebSocket Sender (last 2 lines):${NC}"
        tail -2 "$LOG_DIR/websocket_sender.log" | sed 's/^/   /'
    fi
    
    if [ -f "$LOG_DIR/websocket_server.log" ]; then
        echo -e "${YELLOW}📥 WebSocket Server (last 2 lines):${NC}"
        tail -2 "$LOG_DIR/websocket_server.log" | sed 's/^/   /'
    fi
}

# Function to show logs
show_logs() {
    echo "Select logs to view:"
    echo "  1) Gunicorn error logs"
    echo "  2) WebSocket Sender logs"
    echo "  3) WebSocket Server logs"
    echo "  4) All logs (systemd services)"
    echo "  5) All logs (split screen)"
    read -p "Choice (1-5): " choice
    
    case $choice in
        1)
            if [ -f "$LOG_DIR/gunicorn_error.log" ]; then
                tail -f "$LOG_DIR/gunicorn_error.log"
            else
                error "Gunicorn error log not found"
            fi
            ;;
        2)
            if [ -f "$LOG_DIR/websocket_sender.log" ]; then
                tail -f "$LOG_DIR/websocket_sender.log"
            else
                error "WebSocket Sender log not found"
            fi
            ;;
        3)
            if [ -f "$LOG_DIR/websocket_server.log" ]; then
                tail -f "$LOG_DIR/websocket_server.log"
            else
                error "WebSocket Server log not found"
            fi
            ;;
        4)
            echo "Following systemd service logs (Ctrl+C to exit)..."
            sudo journalctl -u "$WEBSOCKET_SERVER_SERVICE" -u "$WEBSOCKET_SENDER_SERVICE" -f
            ;;
        5)
            # Use multitail if available
            if command -v multitail &> /dev/null; then
                log_files=()
                [ -f "$LOG_DIR/gunicorn_error.log" ] && log_files+=("$LOG_DIR/gunicorn_error.log")
                [ -f "$LOG_DIR/websocket_sender.log" ] && log_files+=("$LOG_DIR/websocket_sender.log")
                [ -f "$LOG_DIR/websocket_server.log" ] && log_files+=("$LOG_DIR/websocket_server.log")
                
                if [ ${#log_files[@]} -gt 0 ]; then
                    multitail "${log_files[@]}"
                else
                    error "No log files found"
                fi
            else
                warn "Install multitail for better log viewing: sudo apt install multitail"
                tail -f "$LOG_DIR"/*.log 2>/dev/null || error "No log files found"
            fi
            ;;
        *)
            error "Invalid choice"
            ;;
    esac
}

# Function to show help
show_help() {
    echo "Usage: $0 {start|stop|restart|restart-websocket|status|logs|install-services|help}"
    echo ""
    echo "Commands:"
    echo "  start             - Start all services (WebSocket + Nginx + Gunicorn)"
    echo "  stop              - Stop all services"
    echo "  restart           - Restart all services"
    echo "  restart-websocket - Restart only WebSocket services"
    echo "  status            - Show comprehensive service status and statistics"
    echo "  logs              - Show service logs (interactive menu)"
    echo "  install-services  - Install systemd services"
    echo "  help              - Show this help message"
    echo ""
    echo "Services Architecture:"
    echo "  🌐 Nginx           - Reverse proxy and web server (port 80)"
    echo "  🚀 Gunicorn        - Python WSGI HTTP Server (port 8000)"
    echo "  🔗 WebSocket Sender - Sends detection/health data to remote server"
    echo "  📥 WebSocket Server - Should run on separate machine "
    echo ""
    echo "Access Points:"
    echo "  Web Interface: http://localhost"
    echo "  WebSocket Management: http://localhost/websocket"
    echo "  API Endpoints: http://localhost/api/"
    echo "  WebSocket Server: ws://localhost:8765"
    echo ""
    echo "Files:"
    echo "  Nginx Config: $NGINX_CONF"
    echo "  Gunicorn Config: $GUNICORN_CONF"
    echo "  Log Directory: $LOG_DIR"
    echo ""
    echo "Service Management:"
    echo "  sudo systemctl {start|stop|status} websocket-sender"
    echo ""
    echo "WebSocket Server Deployment:"
    echo "  Copy websocket_server/ directory to target server"
    echo "  Follow instructions in websocket_server/README.md"
}

# Main script logic
case "${1:-start}" in
    start)
        log "🚀 Starting AI Camera Extended Production Services..."
        start_websocket_services
        start_gunicorn
        start_nginx
        verify_services
        log "✅ All services started successfully"
        log "Access the application at: http://localhost"
        log "WebSocket management: http://localhost/websocket"
        log "WebSocket server: ws://localhost:8765"
        ;;
    stop)
        log "🛑 Stopping AI Camera Extended Production Services..."
        stop_websocket_services
        stop_gunicorn
        stop_nginx
        log "✅ All services stopped"
        ;;
    restart)
        restart_all_services
        log "✅ All services restarted successfully"
        ;;
    restart-websocket)
        log "🔄 Restarting WebSocket services only..."
        stop_websocket_services
        sleep 2
        start_websocket_services
        log "✅ WebSocket services restarted successfully"
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    install-services)
        if [ -f "install_all_services.sh" ]; then
            log "Installing systemd services..."
            sudo ./install_all_services.sh
        else
            error "install_all_services.sh not found"
            exit 1
        fi
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