#!/bin/bash

# Database Cleanup Script for AI Camera WebSocket System
# Removes old data from databases to manage disk space

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/venv_hailo"
MAIN_DB="$SCRIPT_DIR/db/lpr_data.db"
SERVER_DB="$SCRIPT_DIR/websocket_server.db"

# Default retention periods (days)
DEFAULT_DETECTION_RETENTION=30
DEFAULT_HEALTH_RETENTION=7
DEFAULT_SERVER_RETENTION=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

# Function to backup database
backup_database() {
    local db_file="$1"
    local backup_file="$2"
    
    if [ -f "$db_file" ]; then
        log "Creating backup: $backup_file"
        cp "$db_file" "$backup_file"
        return 0
    else
        warn "Database file not found: $db_file"
        return 1
    fi
}

# Function to cleanup main database
cleanup_main_database() {
    local detection_days="${1:-$DEFAULT_DETECTION_RETENTION}"
    local health_days="${2:-$DEFAULT_HEALTH_RETENTION}"
    
    if [ ! -f "$MAIN_DB" ]; then
        warn "Main database not found: $MAIN_DB"
        return 1
    fi
    
    log "Cleaning up main database: $MAIN_DB"
    
    # Activate virtual environment
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
    fi
    
    # Get initial counts
    local initial_detections=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM detection_results;" 2>/dev/null || echo "0")
    local initial_health=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM health_checks;" 2>/dev/null || echo "0")
    
    log "Initial counts - Detections: $initial_detections, Health: $initial_health"
    
    # Clean up old detection results (keep unsent data)
    log "Removing detection results older than $detection_days days (keeping unsent data)..."
    sqlite3 "$MAIN_DB" "
    DELETE FROM detection_results 
    WHERE sent_to_server = 1 
    AND datetime(substr(timestamp, 1, 19)) < datetime('now', '-${detection_days} days');
    " 2>/dev/null || error "Failed to cleanup detection results"
    
    # Clean up old health checks (keep unsent data)
    log "Removing health checks older than $health_days days (keeping unsent data)..."
    sqlite3 "$MAIN_DB" "
    DELETE FROM health_checks 
    WHERE sent_to_server = 1 
    AND datetime(timestamp) < datetime('now', '-${health_days} days');
    " 2>/dev/null || error "Failed to cleanup health checks"
    
    # Get final counts
    local final_detections=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM detection_results;" 2>/dev/null || echo "0")
    local final_health=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM health_checks;" 2>/dev/null || echo "0")
    
    local removed_detections=$((initial_detections - final_detections))
    local removed_health=$((initial_health - final_health))
    
    log "Cleanup complete - Removed: $removed_detections detections, $removed_health health records"
    log "Remaining - Detections: $final_detections, Health: $final_health"
    
    # Vacuum database to reclaim space
    log "Vacuuming main database..."
    sqlite3 "$MAIN_DB" "VACUUM;" 2>/dev/null || warn "Failed to vacuum main database"
}

# Function to cleanup server database
cleanup_server_database() {
    local retention_days="${1:-$DEFAULT_SERVER_RETENTION}"
    
    if [ ! -f "$SERVER_DB" ]; then
        warn "Server database not found: $SERVER_DB"
        return 1
    fi
    
    log "Cleaning up server database: $SERVER_DB"
    
    # Get initial counts
    local initial_lpr=$(sqlite3 "$SERVER_DB" "SELECT COUNT(*) FROM lpr_detections;" 2>/dev/null || echo "0")
    local initial_health=$(sqlite3 "$SERVER_DB" "SELECT COUNT(*) FROM health_monitors;" 2>/dev/null || echo "0")
    
    log "Initial server counts - LPR: $initial_lpr, Health: $initial_health"
    
    # Clean up old LPR detections
    log "Removing server LPR records older than $retention_days days..."
    sqlite3 "$SERVER_DB" "
    DELETE FROM lpr_detections 
    WHERE datetime(received_at) < datetime('now', '-${retention_days} days');
    " 2>/dev/null || error "Failed to cleanup server LPR records"
    
    # Clean up old health monitors
    log "Removing server health records older than $retention_days days..."
    sqlite3 "$SERVER_DB" "
    DELETE FROM health_monitors 
    WHERE datetime(received_at) < datetime('now', '-${retention_days} days');
    " 2>/dev/null || error "Failed to cleanup server health records"
    
    # Get final counts
    local final_lpr=$(sqlite3 "$SERVER_DB" "SELECT COUNT(*) FROM lpr_detections;" 2>/dev/null || echo "0")
    local final_health=$(sqlite3 "$SERVER_DB" "SELECT COUNT(*) FROM health_monitors;" 2>/dev/null || echo "0")
    
    local removed_lpr=$((initial_lpr - final_lpr))
    local removed_health_srv=$((initial_health - final_health))
    
    log "Server cleanup complete - Removed: $removed_lpr LPR, $removed_health_srv health records"
    log "Server remaining - LPR: $final_lpr, Health: $final_health"
    
    # Vacuum database to reclaim space
    log "Vacuuming server database..."
    sqlite3 "$SERVER_DB" "VACUUM;" 2>/dev/null || warn "Failed to vacuum server database"
}

# Function to cleanup log files
cleanup_log_files() {
    local log_retention_days="${1:-7}"
    local log_dir="$SCRIPT_DIR/log"
    
    if [ ! -d "$log_dir" ]; then
        warn "Log directory not found: $log_dir"
        return 1
    fi
    
    log "Cleaning up log files older than $log_retention_days days..."
    
    # Find and remove old log files
    local removed_files=0
    while IFS= read -r -d '' file; do
        rm -f "$file"
        removed_files=$((removed_files + 1))
        log "Removed old log file: $(basename "$file")"
    done < <(find "$log_dir" -name "*.log.*" -type f -mtime +$log_retention_days -print0 2>/dev/null)
    
    # Truncate current log files if they're too large (>10MB)
    for log_file in "$log_dir"/*.log; do
        if [ -f "$log_file" ]; then
            local size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
            if [ "$size" -gt 10485760 ]; then # 10MB
                log "Truncating large log file: $(basename "$log_file") (${size} bytes)"
                tail -1000 "$log_file" > "$log_file.tmp"
                mv "$log_file.tmp" "$log_file"
            fi
        fi
    done
    
    log "Log cleanup complete - Removed $removed_files old log files"
}

# Function to show database statistics
show_database_stats() {
    log "Database Statistics:"
    
    # Main database
    if [ -f "$MAIN_DB" ]; then
        echo -e "${BLUE}Main Database ($MAIN_DB):${NC}"
        local db_size=$(du -h "$MAIN_DB" | cut -f1)
        echo "  Size: $db_size"
        
        local total_detections=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM detection_results;" 2>/dev/null || echo "0")
        local unsent_detections=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM detection_results WHERE sent_to_server = 0;" 2>/dev/null || echo "0")
        local total_health=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM health_checks;" 2>/dev/null || echo "0")
        local unsent_health=$(sqlite3 "$MAIN_DB" "SELECT COUNT(*) FROM health_checks WHERE sent_to_server = 0;" 2>/dev/null || echo "0")
        
        echo "  Detection Results: $total_detections (Unsent: $unsent_detections)"
        echo "  Health Checks: $total_health (Unsent: $unsent_health)"
    else
        echo -e "${YELLOW}Main Database: Not found${NC}"
    fi
    
    # Server database
    if [ -f "$SERVER_DB" ]; then
        echo -e "${BLUE}Server Database ($SERVER_DB):${NC}"
        local db_size=$(du -h "$SERVER_DB" | cut -f1)
        echo "  Size: $db_size"
        
        local lpr_count=$(sqlite3 "$SERVER_DB" "SELECT COUNT(*) FROM lpr_detections;" 2>/dev/null || echo "0")
        local health_count=$(sqlite3 "$SERVER_DB" "SELECT COUNT(*) FROM health_monitors;" 2>/dev/null || echo "0")
        
        echo "  LPR Detections: $lpr_count"
        echo "  Health Monitors: $health_count"
    else
        echo -e "${YELLOW}Server Database: Not found${NC}"
    fi
    
    # Log files
    local log_dir="$SCRIPT_DIR/log"
    if [ -d "$log_dir" ]; then
        echo -e "${BLUE}Log Directory:${NC}"
        local log_size=$(du -sh "$log_dir" 2>/dev/null | cut -f1 || echo "0")
        local log_count=$(find "$log_dir" -name "*.log*" -type f | wc -l)
        echo "  Total Size: $log_size"
        echo "  Total Files: $log_count"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  cleanup-main      - Clean up main database (detection_results, health_checks)"
    echo "  cleanup-server    - Clean up server database (lpr_detections, health_monitors)"
    echo "  cleanup-logs      - Clean up old log files"
    echo "  cleanup-all       - Run all cleanup operations"
    echo "  stats             - Show database statistics"
    echo "  backup            - Create database backups"
    echo ""
    echo "Options:"
    echo "  --detection-days N    - Keep detection results for N days (default: $DEFAULT_DETECTION_RETENTION)"
    echo "  --health-days N       - Keep health checks for N days (default: $DEFAULT_HEALTH_RETENTION)"
    echo "  --server-days N       - Keep server records for N days (default: $DEFAULT_SERVER_RETENTION)"
    echo "  --log-days N          - Keep log files for N days (default: 7)"
    echo "  --dry-run             - Show what would be deleted without actually deleting"
    echo ""
    echo "Examples:"
    echo "  $0 stats                              # Show current statistics"
    echo "  $0 cleanup-all                        # Clean up everything with defaults"
    echo "  $0 cleanup-main --detection-days 60   # Keep detections for 60 days"
    echo "  $0 backup && $0 cleanup-all           # Backup first, then cleanup"
}

# Parse command line arguments
DETECTION_DAYS=$DEFAULT_DETECTION_RETENTION
HEALTH_DAYS=$DEFAULT_HEALTH_RETENTION
SERVER_DAYS=$DEFAULT_SERVER_RETENTION
LOG_DAYS=7
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --detection-days)
            DETECTION_DAYS="$2"
            shift 2
            ;;
        --health-days)
            HEALTH_DAYS="$2"
            shift 2
            ;;
        --server-days)
            SERVER_DAYS="$2"
            shift 2
            ;;
        --log-days)
            LOG_DAYS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Change to script directory
cd "$SCRIPT_DIR"

echo -e "${BLUE}🧹 AI Camera Database Cleanup Tool${NC}"
echo "=================================="

if [ "$DRY_RUN" = true ]; then
    warn "DRY RUN MODE - No actual changes will be made"
fi

# Execute command
case "${COMMAND:-help}" in
    cleanup-main)
        if [ "$DRY_RUN" = true ]; then
            log "Would cleanup main database with detection_days=$DETECTION_DAYS, health_days=$HEALTH_DAYS"
        else
            cleanup_main_database "$DETECTION_DAYS" "$HEALTH_DAYS"
        fi
        ;;
    cleanup-server)
        if [ "$DRY_RUN" = true ]; then
            log "Would cleanup server database with retention_days=$SERVER_DAYS"
        else
            cleanup_server_database "$SERVER_DAYS"
        fi
        ;;
    cleanup-logs)
        if [ "$DRY_RUN" = true ]; then
            log "Would cleanup log files older than $LOG_DAYS days"
        else
            cleanup_log_files "$LOG_DAYS"
        fi
        ;;
    cleanup-all)
        if [ "$DRY_RUN" = true ]; then
            log "Would run all cleanup operations:"
            log "  - Main DB: detection_days=$DETECTION_DAYS, health_days=$HEALTH_DAYS"
            log "  - Server DB: retention_days=$SERVER_DAYS"
            log "  - Log files: log_days=$LOG_DAYS"
        else
            cleanup_main_database "$DETECTION_DAYS" "$HEALTH_DAYS"
            cleanup_server_database "$SERVER_DAYS"
            cleanup_log_files "$LOG_DAYS"
            log "All cleanup operations completed"
        fi
        ;;
    backup)
        timestamp=$(date '+%Y%m%d_%H%M%S')
        backup_main="${MAIN_DB}.backup_${timestamp}"
        backup_server="${SERVER_DB}.backup_${timestamp}"
        
        backup_database "$MAIN_DB" "$backup_main"
        backup_database "$SERVER_DB" "$backup_server"
        log "Backup completed"
        ;;
    stats)
        show_database_stats
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: ${COMMAND}"
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Cleanup operations completed successfully${NC}"