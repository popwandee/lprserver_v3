#!/bin/bash

# WebSocket Sender Startup Script for AI Camera
# This script starts the WebSocket sender service for sending detection and health data to LPR Server

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="/home/camuser/aicamera"
VENV_PATH="$PROJECT_ROOT/venv_hailo"
WORKING_DIR="$PROJECT_ROOT/v2"
SCRIPT_NAME="websocket_sender.py"
LOG_FILE="$WORKING_DIR/log/websocket_sender.log"
PID_FILE="$WORKING_DIR/websocket_sender.pid"

# Create log directory
mkdir -p "$WORKING_DIR/log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting WebSocket Sender for AI Camera${NC}"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $VENV_PATH${NC}"
    exit 1
fi

# Check if script exists
if [ ! -f "$WORKING_DIR/$SCRIPT_NAME" ]; then
    echo -e "${RED}❌ WebSocket sender script not found at: $WORKING_DIR/$SCRIPT_NAME${NC}"
    exit 1
fi

# Change to working directory
cd "$WORKING_DIR"

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  WebSocket sender is already running (PID: $OLD_PID)${NC}"
        echo "Use 'kill $OLD_PID' to stop it first, or use restart option"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Stale PID file found, removing...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Verify configuration
echo -e "${BLUE}🔍 Verifying configuration...${NC}"
if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ Configuration file .env.production not found${NC}"
    exit 1
fi

# Check WEBSOCKET_SERVER_URL
WEBSOCKET_URL=$(grep "WEBSOCKET_SERVER_URL" .env.production | cut -d'=' -f2 | tr -d ' "')
if [ -z "$WEBSOCKET_URL" ]; then
    echo -e "${RED}❌ WEBSOCKET_SERVER_URL not configured in .env.production${NC}"
    exit 1
fi

echo -e "${GREEN}✅ WebSocket Server URL: $WEBSOCKET_URL${NC}"

# Check database
DB_PATH=$(grep "DB_PATH" .env.production | cut -d'=' -f2 | tr -d ' "')
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}❌ Database not found at: $DB_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Database found: $DB_PATH${NC}"

# Start the service
echo -e "${BLUE}🎯 Starting WebSocket sender service...${NC}"
echo "Working directory: $WORKING_DIR"
echo "Log file: $LOG_FILE"
echo "Script: $SCRIPT_NAME"
echo ""

# Handle different startup modes
case "${1:-start}" in
    "start")
        echo -e "${GREEN}▶️  Starting in background mode...${NC}"
        nohup python "$SCRIPT_NAME" > "$LOG_FILE" 2>&1 &
        PID=$!
        echo $PID > "$PID_FILE"
        
        # Wait a moment and check if process is still running
        sleep 2
        if kill -0 $PID 2>/dev/null; then
            echo -e "${GREEN}✅ WebSocket sender started successfully!${NC}"
            echo -e "${GREEN}   PID: $PID${NC}"
            echo -e "${GREEN}   Log: $LOG_FILE${NC}"
            echo ""
            echo -e "${BLUE}📖 To monitor logs:${NC}"
            echo "   tail -f $LOG_FILE"
            echo ""
            echo -e "${BLUE}🛑 To stop service:${NC}"
            echo "   kill $PID"
            echo "   # or use: $0 stop"
        else
            echo -e "${RED}❌ WebSocket sender failed to start${NC}"
            echo -e "${YELLOW}Check logs: $LOG_FILE${NC}"
            rm -f "$PID_FILE"
            exit 1
        fi
        ;;
        
    "foreground"|"fg")
        echo -e "${GREEN}▶️  Starting in foreground mode...${NC}"
        echo -e "${YELLOW}   Press Ctrl+C to stop${NC}"
        echo ""
        python "$SCRIPT_NAME"
        ;;
        
    "stop")
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}🛑 Stopping WebSocket sender (PID: $PID)...${NC}"
                kill "$PID"
                sleep 2
                if kill -0 "$PID" 2>/dev/null; then
                    echo -e "${YELLOW}   Forcing stop...${NC}"
                    kill -9 "$PID"
                fi
                rm -f "$PID_FILE"
                echo -e "${GREEN}✅ WebSocket sender stopped${NC}"
            else
                echo -e "${YELLOW}⚠️  WebSocket sender not running${NC}"
                rm -f "$PID_FILE"
            fi
        else
            echo -e "${YELLOW}⚠️  PID file not found, WebSocket sender may not be running${NC}"
        fi
        ;;
        
    "restart")
        echo -e "${BLUE}🔄 Restarting WebSocket sender...${NC}"
        $0 stop
        sleep 2
        $0 start
        ;;
        
    "status")
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${GREEN}✅ WebSocket sender is running (PID: $PID)${NC}"
                echo -e "${BLUE}   Log file: $LOG_FILE${NC}"
            else
                echo -e "${RED}❌ WebSocket sender is not running (stale PID file)${NC}"
                rm -f "$PID_FILE"
            fi
        else
            echo -e "${RED}❌ WebSocket sender is not running${NC}"
        fi
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|foreground|fg}"
        echo ""
        echo "Commands:"
        echo "  start       - Start WebSocket sender in background"
        echo "  stop        - Stop WebSocket sender"
        echo "  restart     - Restart WebSocket sender"
        echo "  status      - Check WebSocket sender status"
        echo "  foreground  - Start WebSocket sender in foreground (fg)"
        echo ""
        exit 1
        ;;
esac

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}🎉 WebSocket Sender Management Complete${NC}"