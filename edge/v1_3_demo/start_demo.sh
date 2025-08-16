#!/bin/bash
"""
AI Camera v1.3 Demo Startup Script

This script starts the demo application with proper environment setup.

Author: AI Camera Team
Version: 1.3 Demo
Date: August 8, 2025
"""

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/venv_hailo"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if we're in the right directory
if [ ! -f "$SCRIPT_DIR/demo_app.py" ]; then
    log_error "Demo application not found. Please run this script from the v1_3_demo directory."
    exit 1
fi

log_header "AI Camera v1.3 Demo Startup"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    log_error "Virtual environment not found at $VENV_PATH"
    log_info "Please run setup_env.sh first or activate your virtual environment manually"
    exit 1
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Check if demo video file exists
if [ ! -f "$SCRIPT_DIR/example.mp4" ]; then
    log_error "Demo video file not found: example.mp4"
    log_info "Please ensure the video file is in the v1_3_demo directory"
    exit 1
fi

# Check required Python packages
log_info "Checking dependencies..."
python3 -c "import flask, flask_socketio, cv2, numpy" 2>/dev/null || {
    log_error "Required Python packages not found"
    log_info "Please install dependencies: pip install flask flask-socketio opencv-python numpy"
    exit 1
}

# Check if demo app dependencies are available
log_info "Checking demo application dependencies..."
cd "$SCRIPT_DIR"

# Create logs directory if it doesn't exist
mkdir -p logs

# Set environment variables
export FLASK_ENV=development
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export DEMO_MODE=true

log_info "Starting AI Camera v1.3 Demo Application..."
log_info "Demo video: example.mp4"
log_info "Web interface: http://localhost:5000"
log_info "Video stream: http://localhost:5000/demo/video"
log_info "Demo interface: http://localhost:5000/demo"
echo ""

# Start the demo application
python3 demo_app.py
