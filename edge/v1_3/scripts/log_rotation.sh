#!/bin/bash
"""
Log Rotation Script for AI Camera v1.3

This script manages log files to prevent them from growing too large.
It should be run periodically (e.g., daily) via cron.

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

# Configuration
LOG_DIR="/home/camuser/aicamera/v1_3/logs"
MAX_LOG_SIZE="100M"  # Maximum log file size
MAX_LOG_FILES=5      # Maximum number of backup files
LOG_FILE="aicamera.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if log directory exists
if [ ! -d "$LOG_DIR" ]; then
    log_error "Log directory does not exist: $LOG_DIR"
    exit 1
fi

# Check if log file exists
if [ ! -f "$LOG_DIR/$LOG_FILE" ]; then
    log_info "Log file does not exist: $LOG_DIR/$LOG_FILE"
    exit 0
fi

# Get current log file size
current_size=$(du -h "$LOG_DIR/$LOG_FILE" | cut -f1)
log_info "Current log file size: $current_size"

# Check if rotation is needed
if [ -f "$LOG_DIR/$LOG_FILE" ]; then
    # Get file size in bytes
    size_bytes=$(stat -c%s "$LOG_DIR/$LOG_FILE")
    max_size_bytes=$(numfmt --from=iec $MAX_LOG_SIZE)
    
    if [ $size_bytes -gt $max_size_bytes ]; then
        log_info "Log file exceeds maximum size ($MAX_LOG_SIZE), rotating..."
        
        # Remove oldest backup if we have too many
        if [ -f "$LOG_DIR/$LOG_FILE.$MAX_LOG_FILES" ]; then
            rm "$LOG_DIR/$LOG_FILE.$MAX_LOG_FILES"
            log_info "Removed oldest backup: $LOG_FILE.$MAX_LOG_FILES"
        fi
        
        # Shift existing backups
        for i in $(seq $((MAX_LOG_FILES-1)) -1 1); do
            if [ -f "$LOG_DIR/$LOG_FILE.$i" ]; then
                mv "$LOG_DIR/$LOG_FILE.$i" "$LOG_DIR/$LOG_FILE.$((i+1))"
            fi
        done
        
        # Rotate current log file
        mv "$LOG_DIR/$LOG_FILE" "$LOG_DIR/$LOG_FILE.1"
        touch "$LOG_DIR/$LOG_FILE"
        
        # Set proper permissions
        chown camuser:camuser "$LOG_DIR/$LOG_FILE"
        chmod 644 "$LOG_DIR/$LOG_FILE"
        
        log_info "Log rotation completed successfully"
        
        # Show new file sizes
        log_info "Current log files:"
        ls -lh "$LOG_DIR/$LOG_FILE"*
    else
        log_info "Log file size is within limits, no rotation needed"
    fi
else
    log_info "No log file to rotate"
fi

# Cleanup old log files (older than 30 days)
log_info "Cleaning up old log files..."
find "$LOG_DIR" -name "$LOG_FILE.*" -type f -mtime +30 -delete
log_info "Cleanup completed"

log_info "Log rotation script completed"
