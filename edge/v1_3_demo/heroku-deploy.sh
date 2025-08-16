#!/bin/bash
"""
Heroku Deployment Script for AI Camera v1.3 Demo

This script deploys the demo application to Heroku platform.

Author: AI Camera Team
Version: 1.3 Demo
Date: August 8, 2025
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
if [ ! -f "demo_app.py" ]; then
    log_error "Please run this script from the v1_3_demo directory"
    exit 1
fi

log_header "Heroku Deployment for AI Camera v1.3 Demo"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    log_error "Heroku CLI not found"
    log_info "Installing Heroku CLI..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Check if user is logged in
if ! heroku auth:whoami &> /dev/null; then
    log_error "Not logged in to Heroku"
    log_info "Please login to Heroku:"
    heroku login
fi

# Create new app if not exists
if [ ! -f ".git" ]; then
    log_info "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Create Heroku app
APP_NAME="aicamera-demo-$(date +%s)"
log_info "Creating Heroku app: $APP_NAME"
heroku create $APP_NAME

# Set environment variables
log_info "Setting environment variables..."
heroku config:set DEMO_MODE=true
heroku config:set FLASK_ENV=production
heroku config:set PYTHONUNBUFFERED=1

# Add buildpacks
log_info "Adding buildpacks..."
heroku buildpacks:add heroku/python

# Deploy the application
log_info "Deploying to Heroku..."
git push heroku main

# Open the application
log_info "Opening application..."
heroku open

# Get the app URL
APP_URL=$(heroku info -s | grep web_url | cut -d= -f2)
if [ -n "$APP_URL" ]; then
    log_info "✅ Deployment successful!"
    log_info "🌐 Demo URL: $APP_URL"
    log_info "📊 Status: $APP_URL/demo/status"
    log_info "📺 Video: $APP_URL/demo/video"
else
    log_warn "Could not get app URL"
    log_info "Check Heroku dashboard for the URL"
fi

log_info "Deployment completed!"
