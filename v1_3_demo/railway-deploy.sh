#!/bin/bash
"""
Railway Deployment Script for AI Camera v1.3 Demo

This script deploys the demo application to Railway platform.

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

log_header "Railway Deployment for AI Camera v1.3 Demo"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    log_error "Railway CLI not found"
    log_info "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    log_error "Not logged in to Railway"
    log_info "Please login to Railway:"
    railway login
fi

# Create new project if not exists
if [ ! -f ".railway" ]; then
    log_info "Creating new Railway project..."
    railway init
fi

# Set environment variables
log_info "Setting environment variables..."
railway variables set DEMO_MODE=true
railway variables set FLASK_ENV=production
railway variables set PYTHONUNBUFFERED=1

# Deploy the application
log_info "Deploying to Railway..."
railway up

# Get the deployment URL
log_info "Getting deployment URL..."
DEPLOY_URL=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

if [ -n "$DEPLOY_URL" ]; then
    log_info "✅ Deployment successful!"
    log_info "🌐 Demo URL: $DEPLOY_URL"
    log_info "📊 Status: $DEPLOY_URL/demo/status"
    log_info "📺 Video: $DEPLOY_URL/demo/video"
else
    log_warn "Could not get deployment URL"
    log_info "Check Railway dashboard for the URL"
fi

log_info "Deployment completed!"
