#!/bin/bash

# LPR Server v3 - Service Management Script
# ใช้สำหรับจัดการ systemd services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Service names
MAIN_SERVICE="lprserver.service"
WEBSOCKET_SERVICE="lprserver-websocket.service"
OLD_WEBSOCKET_SERVICE="websocket_server.service"

show_help() {
    echo "LPR Server v3 - Service Management"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     - Install and enable services"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  status      - Show status of all services"
    echo "  logs        - Show logs of services"
    echo "  enable      - Enable services to start on boot"
    echo "  disable     - Disable services from starting on boot"
    echo "  uninstall   - Stop and disable services"
    echo "  migrate     - Migrate from old websocket_server.service"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install    # Install and enable services"
    echo "  $0 status     # Check service status"
    echo "  $0 logs       # View service logs"
}

check_services_exist() {
    local services=("$MAIN_SERVICE" "$WEBSOCKET_SERVICE")
    local missing_services=()
    
    for service in "${services[@]}"; do
        if [ ! -f "/etc/systemd/system/$service" ]; then
            missing_services+=("$service")
        fi
    done
    
    if [ ${#missing_services[@]} -gt 0 ]; then
        print_error "Missing service files: ${missing_services[*]}"
        print_status "Run '$0 install' to install services"
        return 1
    fi
    
    return 0
}

install_services() {
    print_header "Installing LPR Server v3 Services"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    print_status "Copying service files..."
    sudo cp lprserver.service /etc/systemd/system/
    sudo cp lprserver-websocket.service /etc/systemd/system/
    
    # Check if old websocket service exists
    if [ -f "/etc/systemd/system/$OLD_WEBSOCKET_SERVICE" ]; then
        print_warning "Found existing $OLD_WEBSOCKET_SERVICE"
        read -p "Do you want to migrate from the old service? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            migrate_from_old_service
        fi
    fi
    
    print_status "Reloading systemd daemon..."
    sudo systemctl daemon-reload
    
    print_status "Enabling services..."
    sudo systemctl enable "$MAIN_SERVICE"
    sudo systemctl enable "$WEBSOCKET_SERVICE"
    
    print_status "Services installed and enabled successfully!"
    print_status "Run '$0 start' to start the services"
}

migrate_from_old_service() {
    print_status "Migrating from $OLD_WEBSOCKET_SERVICE..."
    
    # Stop old service
    sudo systemctl stop "$OLD_WEBSOCKET_SERVICE" 2>/dev/null || true
    
    # Disable old service
    sudo systemctl disable "$OLD_WEBSOCKET_SERVICE" 2>/dev/null || true
    
    # Backup old service file
    if [ -f "/etc/systemd/system/$OLD_WEBSOCKET_SERVICE" ]; then
        sudo cp "/etc/systemd/system/$OLD_WEBSOCKET_SERVICE" "/etc/systemd/system/$OLD_WEBSOCKET_SERVICE.backup"
        print_status "Old service file backed up to $OLD_WEBSOCKET_SERVICE.backup"
    fi
    
    print_status "Migration completed!"
}

start_services() {
    print_header "Starting LPR Server v3 Services"
    
    if ! check_services_exist; then
        exit 1
    fi
    
    print_status "Starting $MAIN_SERVICE..."
    sudo systemctl start "$MAIN_SERVICE"
    
    print_status "Starting $WEBSOCKET_SERVICE..."
    sudo systemctl start "$WEBSOCKET_SERVICE"
    
    sleep 2
    
    print_status "Checking service status..."
    show_service_status
}

stop_services() {
    print_header "Stopping LPR Server v3 Services"
    
    print_status "Stopping $MAIN_SERVICE..."
    sudo systemctl stop "$MAIN_SERVICE" 2>/dev/null || true
    
    print_status "Stopping $WEBSOCKET_SERVICE..."
    sudo systemctl stop "$WEBSOCKET_SERVICE" 2>/dev/null || true
    
    print_status "Services stopped!"
}

restart_services() {
    print_header "Restarting LPR Server v3 Services"
    
    if ! check_services_exist; then
        exit 1
    fi
    
    print_status "Restarting $MAIN_SERVICE..."
    sudo systemctl restart "$MAIN_SERVICE"
    
    print_status "Restarting $WEBSOCKET_SERVICE..."
    sudo systemctl restart "$WEBSOCKET_SERVICE"
    
    sleep 2
    
    print_status "Checking service status..."
    show_service_status
}

show_service_status() {
    print_header "LPR Server v3 Service Status"
    
    local services=("$MAIN_SERVICE" "$WEBSOCKET_SERVICE")
    
    for service in "${services[@]}"; do
        echo ""
        print_status "=== $service ==="
        
        if systemctl is-active --quiet "$service"; then
            echo -e "${GREEN}Status: Active${NC}"
        else
            echo -e "${RED}Status: Inactive${NC}"
        fi
        
        if systemctl is-enabled --quiet "$service"; then
            echo -e "${GREEN}Enabled: Yes${NC}"
        else
            echo -e "${YELLOW}Enabled: No${NC}"
        fi
        
        # Show recent logs
        echo "Recent logs:"
        sudo journalctl -u "$service" --no-pager -n 5 --no-hostname
    done
    
    # Check if old service is still running
    if systemctl is-active --quiet "$OLD_WEBSOCKET_SERVICE" 2>/dev/null; then
        echo ""
        print_warning "Old service $OLD_WEBSOCKET_SERVICE is still running!"
        print_status "Run '$0 migrate' to migrate from the old service"
    fi
}

show_logs() {
    print_header "LPR Server v3 Service Logs"
    
    echo ""
    print_status "=== $MAIN_SERVICE Logs ==="
    sudo journalctl -u "$MAIN_SERVICE" --no-pager -n 20 --no-hostname -f &
    MAIN_LOG_PID=$!
    
    echo ""
    print_status "=== $WEBSOCKET_SERVICE Logs ==="
    sudo journalctl -u "$WEBSOCKET_SERVICE" --no-pager -n 20 --no-hostname -f &
    WEBSOCKET_LOG_PID=$!
    
    echo ""
    print_status "Press Ctrl+C to stop viewing logs"
    
    # Wait for user to stop
    trap "kill $MAIN_LOG_PID $WEBSOCKET_LOG_PID 2>/dev/null; exit" INT
    wait
}

enable_services() {
    print_header "Enabling LPR Server v3 Services"
    
    if ! check_services_exist; then
        exit 1
    fi
    
    print_status "Enabling $MAIN_SERVICE..."
    sudo systemctl enable "$MAIN_SERVICE"
    
    print_status "Enabling $WEBSOCKET_SERVICE..."
    sudo systemctl enable "$WEBSOCKET_SERVICE"
    
    print_status "Services enabled! They will start automatically on boot."
}

disable_services() {
    print_header "Disabling LPR Server v3 Services"
    
    print_status "Disabling $MAIN_SERVICE..."
    sudo systemctl disable "$MAIN_SERVICE" 2>/dev/null || true
    
    print_status "Disabling $WEBSOCKET_SERVICE..."
    sudo systemctl disable "$WEBSOCKET_SERVICE" 2>/dev/null || true
    
    print_status "Services disabled! They will not start automatically on boot."
}

uninstall_services() {
    print_header "Uninstalling LPR Server v3 Services"
    
    print_warning "This will stop and disable all LPR Server services!"
    read -p "Are you sure you want to continue? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uninstall cancelled."
        exit 0
    fi
    
    # Stop and disable services
    stop_services
    disable_services
    
    # Remove service files
    print_status "Removing service files..."
    sudo rm -f "/etc/systemd/system/$MAIN_SERVICE"
    sudo rm -f "/etc/systemd/system/$WEBSOCKET_SERVICE"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    print_status "Services uninstalled successfully!"
}

# Main script logic
case "${1:-help}" in
    install)
        install_services
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_service_status
        ;;
    logs)
        show_logs
        ;;
    enable)
        enable_services
        ;;
    disable)
        disable_services
        ;;
    uninstall)
        uninstall_services
        ;;
    migrate)
        migrate_from_old_service
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
