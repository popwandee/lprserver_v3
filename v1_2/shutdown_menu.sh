#!/bin/bash

# AI Camera Shutdown Menu
# Provides safe shutdown options with proper resource cleanup

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Function to check if services are running
check_services() {
    echo -e "${CYAN}=== Current Service Status ===${NC}"
    
    # Check Gunicorn
    if pgrep -f "gunicorn.*wsgi:app" > /dev/null; then
        echo -e "🚀 ${GREEN}Gunicorn: Running${NC}"
    else
        echo -e "🚀 ${RED}Gunicorn: Not running${NC}"
    fi
    
    # Check Nginx
    if pgrep -x "nginx" > /dev/null; then
        echo -e "🌐 ${GREEN}Nginx: Running${NC}"
    else
        echo -e "🌐 ${RED}Nginx: Not running${NC}"
    fi
    
    # Check WebSocket Sender
    if pgrep -f "websocket_sender.py" > /dev/null; then
        echo -e "📤 ${GREEN}WebSocket Sender: Running${NC}"
    else
        echo -e "📤 ${RED}WebSocket Sender: Not running${NC}"
    fi
    
    # Check Camera/Detection processes
    if pgrep -f "detection_thread" > /dev/null; then
        echo -e "🎥 ${GREEN}Camera/Detection: Running${NC}"
    else
        echo -e "🎥 ${RED}Camera/Detection: Not running${NC}"
    fi
    
    echo ""
}

# Function to graceful shutdown
graceful_shutdown() {
    log "🛑 Starting graceful shutdown sequence..."
    
    # Step 1: Stop detection and camera first (most resource intensive)
    log "=== STEP 1: Stopping detection and camera ==="
    if pgrep -f "detection_thread" > /dev/null; then
        log "Stopping detection thread..."
        curl -s -X POST http://localhost:8000/api/stop_detection > /dev/null 2>&1 || true
        sleep 3
    fi
    
    if pgrep -f "camera" > /dev/null; then
        log "Stopping camera..."
        curl -s -X POST http://localhost:8000/api/stop_camera > /dev/null 2>&1 || true
        sleep 2
    fi
    
    # Step 2: Stop WebSocket sender
    log "=== STEP 2: Stopping WebSocket sender ==="
    if pgrep -f "websocket_sender.py" > /dev/null; then
        log "Stopping WebSocket sender..."
        curl -s -X POST http://localhost:8000/api/stop_websocket_sender > /dev/null 2>&1 || true
        sleep 2
    fi
    
    # Step 3: Stop main application services
    log "=== STEP 3: Stopping main application services ==="
    cd "$SCRIPT_DIR"
    ./run_production_extended.sh stop
    
    # Step 4: Force kill any remaining processes
    log "=== STEP 4: Cleaning up remaining processes ==="
    sudo pkill -f "gunicorn.*wsgi:app" 2>/dev/null || true
    sudo pkill -f "websocket_sender.py" 2>/dev/null || true
    sudo pkill -f "detection_thread" 2>/dev/null || true
    sudo pkill -f "camera" 2>/dev/null || true
    
    # Step 5: Clear system caches
    log "=== STEP 5: Clearing system caches ==="
    sudo sync  # Flush filesystem buffers
    echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true
    
    log "✅ Graceful shutdown complete"
}

# Function to force shutdown
force_shutdown() {
    log "💥 Starting force shutdown sequence..."
    
    # Kill all related processes
    sudo pkill -9 -f "gunicorn" 2>/dev/null || true
    sudo pkill -9 -f "websocket" 2>/dev/null || true
    sudo pkill -9 -f "detection" 2>/dev/null || true
    sudo pkill -9 -f "camera" 2>/dev/null || true
    sudo systemctl stop nginx 2>/dev/null || true
    
    # Clear caches
    sudo sync
    echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true
    
    log "✅ Force shutdown complete"
}

# Function to restart services
restart_services() {
    log "🔄 Restarting all services..."
    
    # Stop first
    graceful_shutdown
    
    # Wait a moment
    sleep 3
    
    # Start again
    cd "$SCRIPT_DIR"
    ./run_production_extended.sh start
    
    log "✅ Services restarted"
}

# Function to show shutdown menu
show_menu() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           AI Camera Shutdown Menu         ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║  1. Check Service Status                 ║${NC}"
    echo -e "${CYAN}║  2. Graceful Shutdown (Recommended)      ║${NC}"
    echo -e "${CYAN}║  3. Force Shutdown (Emergency)           ║${NC}"
    echo -e "${CYAN}║  4. Restart All Services                 ║${NC}"
    echo -e "${CYAN}║  5. Exit                                 ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show resource usage
show_resources() {
    echo -e "${CYAN}=== System Resource Usage ===${NC}"
    echo -e "Memory Usage:"
    free -h | grep -E "Mem|Swap"
    echo ""
    echo -e "Disk Usage:"
    df -h | grep -E "/dev/root|/dev/sda"
    echo ""
    echo -e "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
    echo ""
    echo -e "Active Processes:"
    ps aux | grep -E "(gunicorn|websocket|detection|camera)" | grep -v grep | wc -l
    echo " processes running"
}

# Main menu loop
while true; do
    show_menu
    read -p "Select option (1-5): " choice
    
    case $choice in
        1)
            check_services
            show_resources
            ;;
        2)
            echo -e "${YELLOW}Are you sure you want to perform graceful shutdown? (y/N):${NC} "
            read -r confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                graceful_shutdown
                check_services
            else
                log "Shutdown cancelled"
            fi
            ;;
        3)
            echo -e "${RED}⚠️  WARNING: Force shutdown will kill all processes immediately!${NC}"
            echo -e "${YELLOW}Are you absolutely sure? (y/N):${NC} "
            read -r confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                force_shutdown
                check_services
            else
                log "Force shutdown cancelled"
            fi
            ;;
        4)
            echo -e "${YELLOW}Are you sure you want to restart all services? (y/N):${NC} "
            read -r confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                restart_services
                check_services
            else
                log "Restart cancelled"
            fi
            ;;
        5)
            log "Exiting shutdown menu"
            exit 0
            ;;
        *)
            error "Invalid option. Please select 1-5."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done 