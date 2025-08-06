#!/bin/bash

# Package WebSocket Server for Deployment
# This script creates a deployment package for the WebSocket server

set -e

# Configuration
PACKAGE_NAME="websocket_server_package"
PACKAGE_DIR="websocket_server"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="${PACKAGE_NAME}_${TIMESTAMP}.tar.gz"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if websocket_server directory exists
if [ ! -d "$PACKAGE_DIR" ]; then
    error "WebSocket server directory not found: $PACKAGE_DIR"
    exit 1
fi

log "Creating WebSocket server deployment package..."

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_PATH="$TEMP_DIR/$PACKAGE_NAME"

# Copy files to temporary directory
log "Copying files..."
cp -r "$PACKAGE_DIR" "$PACKAGE_PATH"

# Create deployment script
cat > "$PACKAGE_PATH/deploy.sh" << 'EOF'
#!/bin/bash

# WebSocket Server Deployment Script
# Run this script on the target server to deploy the WebSocket server

set -e

echo "🚀 Deploying WebSocket Server..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run as root. Use a regular user account."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create log directory
mkdir -p log

# Set permissions
chmod +x run_websocket_server.sh
chmod +x deploy.sh

echo "✅ WebSocket server deployment complete!"
echo ""
echo "To start the server:"
echo "  ./run_websocket_server.sh start"
echo ""
echo "To install as systemd service:"
echo "  sudo ./install_all_services.sh"
echo ""
echo "For more information, see README.md"
EOF

chmod +x "$PACKAGE_PATH/deploy.sh"

# Create archive
log "Creating archive: $ARCHIVE_NAME"
cd "$TEMP_DIR"
tar -czf "$ARCHIVE_NAME" "$PACKAGE_NAME"

# Move archive to current directory
mv "$ARCHIVE_NAME" "/home/camuser/aicamera/v2/"

# Cleanup
rm -rf "$TEMP_DIR"

log "✅ Package created successfully: $ARCHIVE_NAME"
log "📦 Package contents:"
echo "   - websocket_server.py (main server)"
echo "   - run_websocket_server.sh (service management)"
echo "   - install_all_services.sh (systemd installation)"
echo "   - requirements.txt (dependencies)"
echo "   - static/ and templates/ (web assets)"
echo "   - README.md (deployment instructions)"
echo "   - deploy.sh (deployment script)"
echo ""
log "🚀 To deploy on target server:"
echo "   1. Copy $ARCHIVE_NAME to target server"
echo "   2. Extract: tar -xzf $ARCHIVE_NAME"
echo "   3. Run: cd websocket_server_package && ./deploy.sh"
echo "   4. Start server: ./run_websocket_server.sh start" 