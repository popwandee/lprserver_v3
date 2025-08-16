#!/bin/bash

# LPR Server v3 Setup Script
# This script sets up the LPR Server with all necessary configurations

set -e

echo "=== LPR Server v3 Setup Script ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

print_status "Setting up LPR Server v3 in: $SCRIPT_DIR"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p storage/images
mkdir -p logs
mkdir -p database

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create database
print_status "Initializing database..."
python3 -c "
from src.app import create_app, db
from src.models.lpr_record import LPRRecord
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

# Set proper permissions
print_status "Setting proper permissions..."
chmod +x run.py
chmod +x websocket_server.py
chmod +x wsgi.py

# Create log directories with proper permissions
sudo mkdir -p /var/log/lprserver
sudo mkdir -p /var/log/nginx
sudo chown -R $USER:$USER /var/log/lprserver
sudo chown -R $USER:$USER /var/log/nginx

# Copy systemd service files
print_status "Setting up systemd services..."
sudo cp lprserver.service /etc/systemd/system/
sudo cp lprserver-websocket.service /etc/systemd/system/

# Check if existing websocket_server.service exists and disable it
if [ -f "/etc/systemd/system/websocket_server.service" ]; then
    print_status "Found existing websocket_server.service, disabling it..."
    sudo systemctl stop websocket_server.service 2>/dev/null || true
    sudo systemctl disable websocket_server.service 2>/dev/null || true
fi

# Copy nginx configuration
print_status "Setting up nginx configuration..."
sudo cp nginx/lprserver.conf /etc/nginx/sites-available/lprserver
sudo ln -sf /etc/nginx/sites-available/lprserver /etc/nginx/sites-enabled/

# Remove default nginx site if exists
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Reload systemd and enable services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable lprserver.service
sudo systemctl enable lprserver-websocket.service

# Test nginx configuration
print_status "Testing nginx configuration..."
sudo nginx -t

# Restart nginx
print_status "Restarting nginx..."
sudo systemctl restart nginx

# Start services
print_status "Starting LPR Server services..."
sudo systemctl start lprserver.service
sudo systemctl start lprserver-websocket.service

# Check service status
print_status "Checking service status..."
sleep 2

if sudo systemctl is-active --quiet lprserver.service; then
    print_status "LPR Server main service is running"
else
    print_error "LPR Server main service failed to start"
    sudo systemctl status lprserver.service
fi

if sudo systemctl is-active --quiet lprserver-websocket.service; then
    print_status "LPR Server WebSocket service is running"
else
    print_error "LPR Server WebSocket service failed to start"
    sudo systemctl status lprserver-websocket.service
fi

# Create test data (optional)
read -p "Do you want to create some test data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating test data..."
    python3 -c "
from src.app import create_app, db
from src.models.lpr_record import LPRRecord
from datetime import datetime, timedelta
import random

app = create_app()
with app.app_context():
    # Create test records
    cameras = ['CAM001', 'CAM002', 'CAM003']
    plate_numbers = ['กข1234', 'คง5678', 'จฉ9012', 'ชซ3456', 'ญฎ7890']
    locations = ['ประตูหน้า', 'ประตูหลัง', 'ลานจอดรถ']
    
    for i in range(20):
        record = LPRRecord(
            camera_id=random.choice(cameras),
            plate_number=random.choice(plate_numbers),
            confidence=random.uniform(60, 95),
            timestamp=datetime.now() - timedelta(hours=random.randint(0, 72)),
            location=random.choice(locations)
        )
        db.session.add(record)
    
    db.session.commit()
    print('Test data created successfully')
"
fi

print_status "Setup completed successfully!"
echo
echo "=== LPR Server v3 is now running ==="
echo "Web Interface: http://localhost"
echo "WebSocket Server: ws://localhost:8765"
echo "API Endpoints: http://localhost/api"
echo
echo "=== Service Management ==="
echo "Check status: sudo systemctl status lprserver.service"
echo "View logs: sudo journalctl -u lprserver.service -f"
echo "Restart: sudo systemctl restart lprserver.service"
echo
echo "=== WebSocket Service ==="
echo "Check status: sudo systemctl status lprserver-websocket.service"
echo "View logs: sudo journalctl -u lprserver-websocket.service -f"
echo "Restart: sudo systemctl restart lprserver-websocket.service"
echo
echo "=== Nginx ==="
echo "Check status: sudo systemctl status nginx"
echo "View logs: sudo tail -f /var/log/nginx/lprserver_access.log"
echo "Restart: sudo systemctl restart nginx"
