#!/bin/bash

# Install WebSocket Sender as systemd service
# This script installs the WebSocket sender as a system service

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="/home/camuser/aicamera"
SERVICE_DIR="$PROJECT_ROOT/v2"
SERVICE_FILE="websocket_sender.service"
SYSTEMD_DIR="/etc/systemd/system"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Installing WebSocket Sender Service${NC}"
echo "========================================"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root or with sudo${NC}"
    echo "Usage: sudo $0"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_DIR/$SERVICE_FILE" ]; then
    echo -e "${RED}❌ Service file not found: $SERVICE_DIR/$SERVICE_FILE${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv_hailo" ]; then
    echo -e "${RED}❌ Virtual environment not found: $PROJECT_ROOT/venv_hailo${NC}"
    exit 1
fi

# Check if main script exists
if [ ! -f "$SERVICE_DIR/websocket_sender.py" ]; then
    echo -e "${RED}❌ WebSocket sender script not found: $SERVICE_DIR/websocket_sender.py${NC}"
    exit 1
fi

# Stop existing service if running
if systemctl is-active --quiet websocket-sender 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Stopping existing websocket-sender service...${NC}"
    systemctl stop websocket-sender
fi

# Copy service file to systemd directory
echo -e "${BLUE}📁 Installing service file...${NC}"
cp "$SERVICE_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/websocket-sender.service"

# Set proper permissions
chmod 644 "$SYSTEMD_DIR/websocket-sender.service"

# Reload systemd daemon
echo -e "${BLUE}🔄 Reloading systemd daemon...${NC}"
systemctl daemon-reload

# Enable service to start on boot
echo -e "${BLUE}✅ Enabling service to start on boot...${NC}"
systemctl enable websocket-sender

# Create log directory with proper permissions
echo -e "${BLUE}📝 Setting up log directory...${NC}"
mkdir -p "$SERVICE_DIR/log"
chown -R camuser:camuser "$SERVICE_DIR/log"

# Test configuration
echo -e "${BLUE}🔍 Testing configuration...${NC}"
if systemctl is-enabled websocket-sender >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Service enabled successfully${NC}"
else
    echo -e "${RED}❌ Failed to enable service${NC}"
    exit 1
fi

# Show service status
echo -e "${BLUE}📊 Service status:${NC}"
systemctl status websocket-sender --no-pager || true

echo ""
echo -e "${GREEN}🎉 WebSocket Sender Service Installation Complete!${NC}"
echo ""
echo -e "${BLUE}Available commands:${NC}"
echo "  sudo systemctl start websocket-sender    # Start the service"
echo "  sudo systemctl stop websocket-sender     # Stop the service"
echo "  sudo systemctl restart websocket-sender  # Restart the service"
echo "  sudo systemctl status websocket-sender   # Check status"
echo "  sudo systemctl disable websocket-sender  # Disable auto-start"
echo "  sudo journalctl -u websocket-sender -f   # View logs"
echo ""
echo -e "${YELLOW}📝 To start the service now:${NC}"
echo "  sudo systemctl start websocket-sender"
echo ""
echo -e "${BLUE}======================================${NC}"