#!/bin/bash

# Install All AI Camera Services as systemd services
# This script installs all components as system services for production deployment

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="/home/camuser/aicamera"
SERVICE_DIR="$PROJECT_ROOT/v2"
SYSTEMD_DIR="/etc/systemd/system"

# Service files
WEBSOCKET_SENDER_SERVICE="websocket_sender.service"
WEBSOCKET_SERVER_SERVICE="websocket_server.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Installing All AI Camera Services${NC}"
echo "===================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root or with sudo${NC}"
    echo "Usage: sudo $0"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv_hailo" ]; then
    echo -e "${RED}❌ Virtual environment not found: $PROJECT_ROOT/venv_hailo${NC}"
    exit 1
fi

# Function to install a service
install_service() {
    local service_name="$1"
    local service_file="$2"
    local script_file="$3"
    
    echo -e "${BLUE}📁 Installing $service_name...${NC}"
    
    # Check if service file exists
    if [ ! -f "$SERVICE_DIR/$service_file" ]; then
        echo -e "${RED}❌ Service file not found: $SERVICE_DIR/$service_file${NC}"
        return 1
    fi
    
    # Check if main script exists
    if [ ! -f "$SERVICE_DIR/$script_file" ]; then
        echo -e "${RED}❌ Script file not found: $SERVICE_DIR/$script_file${NC}"
        return 1
    fi
    
    # Stop existing service if running
    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Stopping existing $service_name service...${NC}"
        systemctl stop "$service_name"
    fi
    
    # Copy service file to systemd directory
    cp "$SERVICE_DIR/$service_file" "$SYSTEMD_DIR/$service_name.service"
    
    # Set proper permissions
    chmod 644 "$SYSTEMD_DIR/$service_name.service"
    
    # Enable service to start on boot
    systemctl enable "$service_name"
    
    echo -e "${GREEN}✅ $service_name service installed successfully${NC}"
    return 0
}

# Install WebSocket Sender Service
echo -e "${BLUE}🔗 Installing WebSocket Sender Service...${NC}"
if install_service "websocket-sender" "$WEBSOCKET_SENDER_SERVICE" "websocket_sender.py"; then
    echo -e "${GREEN}✅ WebSocket Sender service ready${NC}"
else
    echo -e "${RED}❌ Failed to install WebSocket Sender service${NC}"
    exit 1
fi

# Install WebSocket Server Service
echo -e "${BLUE}🌐 Installing WebSocket Server Service...${NC}"
if install_service "websocket-server" "$WEBSOCKET_SERVER_SERVICE" "websocket_server.py"; then
    echo -e "${GREEN}✅ WebSocket Server service ready${NC}"
else
    echo -e "${RED}❌ Failed to install WebSocket Server service${NC}"
    exit 1
fi

# Reload systemd daemon
echo -e "${BLUE}🔄 Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Create log directory with proper permissions
echo -e "${BLUE}📝 Setting up log directory...${NC}"
mkdir -p "$SERVICE_DIR/log"
chown -R camuser:camuser "$SERVICE_DIR/log"

# Create data directory for WebSocket server
mkdir -p "$SERVICE_DIR/data"
chown -R camuser:camuser "$SERVICE_DIR/data"

# Test configurations
echo -e "${BLUE}🔍 Testing service configurations...${NC}"

services=("websocket-sender" "websocket-server")
for service in "${services[@]}"; do
    if systemctl is-enabled "$service" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service enabled successfully${NC}"
    else
        echo -e "${RED}❌ Failed to enable $service${NC}"
        exit 1
    fi
done

# Show service status
echo -e "${BLUE}📊 Service status:${NC}"
for service in "${services[@]}"; do
    echo ""
    echo -e "${YELLOW}$service:${NC}"
    systemctl status "$service" --no-pager -l || true
done

echo ""
echo -e "${GREEN}🎉 All AI Camera Services Installation Complete!${NC}"
echo ""
echo -e "${BLUE}Installed Services:${NC}"
echo "  🔗 websocket-sender  - Sends detection/health data to server"
echo "  🌐 websocket-server  - Receives and processes data from clients"
echo ""
echo -e "${BLUE}Available Commands:${NC}"
echo ""
echo -e "${YELLOW}WebSocket Sender:${NC}"
echo "  sudo systemctl start websocket-sender     # Start the sender"
echo "  sudo systemctl stop websocket-sender      # Stop the sender"
echo "  sudo systemctl status websocket-sender    # Check status"
echo "  sudo journalctl -u websocket-sender -f    # View logs"
echo ""
echo -e "${YELLOW}WebSocket Server:${NC}"
echo "  sudo systemctl start websocket-server     # Start the server"
echo "  sudo systemctl stop websocket-server      # Stop the server"
echo "  sudo systemctl status websocket-server    # Check status"
echo "  sudo journalctl -u websocket-server -f    # View logs"
echo ""
echo -e "${YELLOW}All Services:${NC}"
echo "  sudo systemctl start websocket-server websocket-sender    # Start all"
echo "  sudo systemctl stop websocket-sender websocket-server     # Stop all"
echo ""
echo -e "${BLUE}Standalone Scripts (for development/testing):${NC}"
echo "  ./run_websocket_sender.sh {start|stop|status}"
echo "  ./run_websocket_server.sh {start|stop|status}"
echo ""
echo -e "${YELLOW}📝 Quick Start Guide:${NC}"
echo "1. Start WebSocket Server first:"
echo "   sudo systemctl start websocket-server"
echo ""
echo "2. Start main AI Camera application:"
echo "   ./run_production.sh start"
echo ""
echo "3. Start WebSocket Sender to send data:"
echo "   sudo systemctl start websocket-sender"
echo ""
echo "4. Monitor everything:"
echo "   ./run_production.sh status"
echo "   sudo systemctl status websocket-server websocket-sender"
echo ""
echo -e "${BLUE}====================================${NC}"