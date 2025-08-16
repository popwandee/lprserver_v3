#!/bin/bash

# Tailscale Fix Script for AI Camera Edge System
# This script fixes common Tailscale issues and sets up proper configuration

set -e

echo "=== Tailscale Fix Script for AI Camera Edge System ==="
echo ""

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
   print_error "This script should not be run as root. Please run as camuser."
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get user input
get_input() {
    local prompt="$1"
    local default="$2"
    local input
    
    if [[ -n "$default" ]]; then
        read -p "$prompt [$default]: " input
        echo "${input:-$default}"
    else
        read -p "$prompt: " input
        echo "$input"
    fi
}

print_status "Starting Tailscale configuration fix..."

# Step 1: Check current system status
print_status "Step 1: Checking current system status..."

# Check hostname
CURRENT_HOSTNAME=$(hostname)
print_status "Current hostname: $CURRENT_HOSTNAME"

if [[ "$CURRENT_HOSTNAME" != "aicamera1" ]]; then
    print_warning "Hostname is not set to 'aicamera1'. Fixing..."
    sudo hostnamectl set-hostname aicamera1
    echo "aicamera1" | sudo tee /etc/hostname
    
    # Update /etc/hosts
    if ! grep -q "127.0.1.1 aicamera1" /etc/hosts; then
        echo "127.0.1.1 aicamera1" | sudo tee -a /etc/hosts
    fi
    
    print_status "Hostname updated to aicamera1"
fi

# Check Tailscale installation
if ! command_exists tailscale; then
    print_error "Tailscale is not installed. Installing..."
    curl -fsSL https://tailscale.com/install.sh | sh
    print_status "Tailscale installed successfully"
fi

# Step 2: Stop and restart Tailscale services
print_status "Step 2: Restarting Tailscale services..."

# Stop current Tailscale connection
if tailscale status >/dev/null 2>&1; then
    print_status "Stopping current Tailscale connection..."
    tailscale down
fi

# Restart tailscaled service
print_status "Restarting tailscaled service..."
sudo systemctl restart tailscaled
sleep 3

# Check service status
if sudo systemctl is-active --quiet tailscaled; then
    print_status "tailscaled service is running"
else
    print_error "tailscaled service failed to start"
    sudo systemctl status tailscaled
    exit 1
fi

# Step 3: Get Tailscale auth key
print_status "Step 3: Setting up Tailscale authentication..."

# Check if auth key is provided as environment variable
if [[ -n "$TAILSCALE_AUTH_KEY" ]]; then
    AUTH_KEY="$TAILSCALE_AUTH_KEY"
    print_status "Using auth key from environment variable"
else
    print_warning "Please provide your Tailscale auth key"
    print_status "You can get this from: https://login.tailscale.com/admin/settings/keys"
    AUTH_KEY=$(get_input "Enter your Tailscale auth key")
fi

if [[ -z "$AUTH_KEY" ]]; then
    print_error "Auth key is required. Exiting..."
    exit 1
fi

# Step 4: Connect to Tailscale with proper configuration
print_status "Step 4: Connecting to Tailscale..."

# Connect with proper hostname and tags
tailscale up \
    --authkey="$AUTH_KEY" \
    --hostname=aicamera1 \
    --advertise-tags=tag:edge,tag:aicamera \
    --accept-dns=false

# Step 5: Verify connection
print_status "Step 5: Verifying connection..."

sleep 5

if tailscale status >/dev/null 2>&1; then
    print_status "Tailscale connection successful!"
    echo ""
    tailscale status
else
    print_error "Failed to connect to Tailscale"
    exit 1
fi

# Step 6: Create auto-connect service
print_status "Step 6: Creating auto-connect service..."

# Create the service file
sudo tee /etc/systemd/system/tailscale-autoconnect.service > /dev/null <<EOF
[Unit]
Description=Tailscale Auto-Connect for AI Camera
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/tailscale up --authkey=$AUTH_KEY --hostname=aicamera1 --advertise-tags=tag:edge,tag:aicamera --accept-dns=false
ExecStop=/usr/bin/tailscale down
User=camuser
Group=camuser

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable tailscale-autoconnect.service
sudo systemctl start tailscale-autoconnect.service

print_status "Auto-connect service created and enabled"

# Step 7: Create health check script
print_status "Step 7: Creating health check script..."

# Create health check script
sudo tee /usr/local/bin/tailscale-health-check.sh > /dev/null <<'EOF'
#!/bin/bash

# Tailscale Health Check Script
LOG_FILE="/var/log/tailscale-health.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if Tailscale is connected
if ! tailscale status > /dev/null 2>&1; then
    log_message "Tailscale is down, restarting..."
    sudo systemctl restart tailscaled
    sleep 5
    tailscale up --authkey=YOUR_AUTH_KEY --hostname=aicamera1 --advertise-tags=tag:edge,tag:aicamera
    log_message "Tailscale restarted"
fi

# Check connectivity to LPR server (if configured)
if [[ -n "$LPR_SERVER_HOST" ]]; then
    if ! tailscale ping -c 1 "$LPR_SERVER_HOST" > /dev/null 2>&1; then
        log_message "Cannot ping $LPR_SERVER_HOST"
    fi
fi
EOF

sudo chmod +x /usr/local/bin/tailscale-health-check.sh

# Add cron job for health check (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/tailscale-health-check.sh") | crontab -

print_status "Health check script created and cron job added"

# Step 8: Configure firewall
print_status "Step 8: Configuring firewall..."

# Allow Tailscale traffic
if command_exists ufw; then
    sudo ufw allow in on tailscale0
    sudo ufw allow out on tailscale0
    print_status "UFW rules added for Tailscale"
fi

# Step 9: Create environment file
print_status "Step 9: Creating environment configuration..."

# Create .env file for the application
cat > .env <<EOF
# Tailscale Configuration
TAILSCALE_HOSTNAME=aicamera1
TAILSCALE_AUTH_KEY=$AUTH_KEY
LPR_SERVER_HOST=lpr-server1

# Application Configuration
LOG_LEVEL=INFO
CAMERA_DEVICE=/dev/video0
AI_MODEL_PATH=resources/models/

# Network Configuration
WEBSOCKET_PORT=8765
HTTP_PORT=5000
EOF

print_status "Environment file created: .env"

# Step 10: Test connectivity
print_status "Step 10: Testing connectivity..."

# Test basic connectivity
if tailscale ping -c 1 100.100.100.100 > /dev/null 2>&1; then
    print_status "Basic Tailscale connectivity: OK"
else
    print_warning "Basic Tailscale connectivity: Failed"
fi

# Test DNS resolution
if nslookup aicamera1 > /dev/null 2>&1; then
    print_status "DNS resolution: OK"
else
    print_warning "DNS resolution: Failed"
fi

# Step 11: Create monitoring script
print_status "Step 11: Creating monitoring script..."

cat > monitor_tailscale.sh <<'EOF'
#!/bin/bash

# Tailscale Monitoring Script
echo "=== Tailscale Status ==="
tailscale status

echo ""
echo "=== Network Interfaces ==="
ip addr show tailscale0

echo ""
echo "=== Recent Logs ==="
sudo journalctl -u tailscaled -n 20 --no-pager

echo ""
echo "=== Connectivity Test ==="
if tailscale ping -c 1 100.100.100.100 > /dev/null 2>&1; then
    echo "✓ Basic connectivity: OK"
else
    echo "✗ Basic connectivity: Failed"
fi

if [[ -n "$LPR_SERVER_HOST" ]]; then
    if tailscale ping -c 1 "$LPR_SERVER_HOST" > /dev/null 2>&1; then
        echo "✓ LPR Server connectivity: OK"
    else
        echo "✗ LPR Server connectivity: Failed"
    fi
fi
EOF

chmod +x monitor_tailscale.sh

print_status "Monitoring script created: monitor_tailscale.sh"

# Final status
echo ""
echo "=== Configuration Complete ==="
print_status "Tailscale has been configured successfully!"
echo ""
echo "Next steps:"
echo "1. Update the auth key in /usr/local/bin/tailscale-health-check.sh"
echo "2. Test connectivity: ./monitor_tailscale.sh"
echo "3. Check Tailscale admin console for device registration"
echo "4. Configure ACLs in Tailscale admin console"
echo ""
echo "Useful commands:"
echo "- Check status: tailscale status"
echo "- Monitor logs: sudo journalctl -u tailscaled -f"
echo "- Test connectivity: tailscale ping lpr-server1"
echo "- View health logs: tail -f /var/log/tailscale-health.log"
echo ""

print_status "Configuration completed successfully!"
