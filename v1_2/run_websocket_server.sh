#!/bin/bash

# WebSocket Server Startup Script for AI Camera
# This script starts the WebSocket server for receiving detection and health data from clients

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="/home/camuser/aicamera"
VENV_PATH="$PROJECT_ROOT/venv_hailo"
WORKING_DIR="$PROJECT_ROOT/v2"
SCRIPT_NAME="websocket_server.py"
LOG_FILE="$WORKING_DIR/log/websocket_server.log"
PID_FILE="$WORKING_DIR/websocket_server.pid"

# Create log directory
mkdir -p "$WORKING_DIR/log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 WebSocket Server Management for AI Camera${NC}"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $VENV_PATH${NC}"
    exit 1
fi

# Check if script exists
if [ ! -f "$WORKING_DIR/$SCRIPT_NAME" ]; then
    echo -e "${RED}❌ WebSocket server script not found at: $WORKING_DIR/$SCRIPT_NAME${NC}"
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
        echo -e "${YELLOW}⚠️  WebSocket server is already running (PID: $OLD_PID)${NC}"
        echo "Use 'kill $OLD_PID' to stop it first, or use restart option"
        if [ "${1:-start}" != "status" ]; then
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  Stale PID file found, removing...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Verify configuration
echo -e "${BLUE}🔍 Verifying configuration...${NC}"

# Check port availability
PORT=8765
if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
    if [ "${1:-start}" = "start" ]; then
        echo -e "${RED}❌ Port $PORT is already in use${NC}"
        echo "Another WebSocket server may be running"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Port $PORT is available${NC}"

# Handle different startup modes
case "${1:-start}" in
    "start")
        echo -e "${GREEN}▶️  Starting WebSocket server in background mode...${NC}"
        echo "Server will listen on all interfaces (0.0.0.0:$PORT)"
        echo "Log file: $LOG_FILE"
        echo ""
        
        nohup python "$SCRIPT_NAME" > "$LOG_FILE" 2>&1 &
        PID=$!
        echo $PID > "$PID_FILE"
        
        # Wait a moment and check if process is still running
        sleep 3
        if kill -0 $PID 2>/dev/null; then
            echo -e "${GREEN}✅ WebSocket server started successfully!${NC}"
            echo -e "${GREEN}   PID: $PID${NC}"
            echo -e "${GREEN}   URL: ws://localhost:$PORT${NC}"
            echo -e "${GREEN}   Log: $LOG_FILE${NC}"
            echo ""
            echo -e "${BLUE}📖 To monitor logs:${NC}"
            echo "   tail -f $LOG_FILE"
            echo ""
            echo -e "${BLUE}🛑 To stop server:${NC}"
            echo "   kill $PID"
            echo "   # or use: $0 stop"
            echo ""
            echo -e "${BLUE}🔍 To check connections:${NC}"
            echo "   netstat -tlnp | grep $PORT"
        else
            echo -e "${RED}❌ WebSocket server failed to start${NC}"
            echo -e "${YELLOW}Check logs: $LOG_FILE${NC}"
            rm -f "$PID_FILE"
            exit 1
        fi
        ;;
        
    "foreground"|"fg")
        echo -e "${GREEN}▶️  Starting WebSocket server in foreground mode...${NC}"
        echo -e "${YELLOW}   Press Ctrl+C to stop${NC}"
        echo "Server will listen on all interfaces (0.0.0.0:$PORT)"
        echo ""
        python "$SCRIPT_NAME"
        ;;
        
    "stop")
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}🛑 Stopping WebSocket server (PID: $PID)...${NC}"
                kill "$PID"
                sleep 3
                if kill -0 "$PID" 2>/dev/null; then
                    echo -e "${YELLOW}   Forcing stop...${NC}"
                    kill -9 "$PID"
                fi
                rm -f "$PID_FILE"
                echo -e "${GREEN}✅ WebSocket server stopped${NC}"
            else
                echo -e "${YELLOW}⚠️  WebSocket server not running${NC}"
                rm -f "$PID_FILE"
            fi
        else
            echo -e "${YELLOW}⚠️  PID file not found, WebSocket server may not be running${NC}"
        fi
        ;;
        
    "restart")
        echo -e "${BLUE}🔄 Restarting WebSocket server...${NC}"
        $0 stop
        sleep 2
        $0 start
        ;;
        
    "status")
        echo -e "${BLUE}📊 WebSocket Server Status${NC}"
        echo "=========================="
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${GREEN}✅ WebSocket server is running (PID: $PID)${NC}"
                echo -e "${BLUE}   Process info:${NC}"
                ps aux | grep "$PID" | grep -v grep | head -1 | awk '{print "   CPU: "$3"%, Memory: "$4"%, Start: "$9}'
                
                # Check port listening
                if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
                    echo -e "${GREEN}   Listening on port $PORT${NC}"
                else
                    echo -e "${YELLOW}   Port $PORT not detected (server may be starting)${NC}"
                fi
                
                # Check database
                if [ -f "websocket_server.db" ]; then
                    echo -e "${BLUE}   Database:${NC}"
                    python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('websocket_server.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM lpr_detections')
    lpr_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM health_monitors')
    health_count = cursor.fetchone()[0]
    print(f'   LPR Records: {lpr_count}')
    print(f'   Health Records: {health_count}')
    conn.close()
except Exception as e:
    print(f'   Database check failed: {e}')
" 2>/dev/null || echo "   Database check failed"
                fi
                
            else
                echo -e "${RED}❌ WebSocket server is not running (stale PID file)${NC}"
                rm -f "$PID_FILE"
            fi
        else
            echo -e "${RED}❌ WebSocket server is not running${NC}"
        fi
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo -e "${BLUE}📝 Recent logs (last 5 lines):${NC}"
            tail -5 "$LOG_FILE" | sed 's/^/   /'
        fi
        ;;
        
    "logs")
        if [ -f "$LOG_FILE" ]; then
            echo -e "${BLUE}📝 WebSocket Server Logs (press Ctrl+C to exit)${NC}"
            echo "================================================"
            tail -f "$LOG_FILE"
        else
            echo -e "${RED}❌ Log file not found: $LOG_FILE${NC}"
            exit 1
        fi
        ;;
        
    "test")
        echo -e "${BLUE}🧪 Testing WebSocket server connection...${NC}"
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${GREEN}✅ Server is running, testing connection...${NC}"
                
                # Test with Python websockets client
                python3 -c "
import asyncio
import websockets
import json

async def test_connection():
    try:
        uri = 'ws://localhost:$PORT'
        async with websockets.connect(uri, timeout=5) as websocket:
            # Send test message
            test_message = {
                'table': 'health_monitor',
                'action': 'insert',
                'data': {
                    'checkpoint_id': 'test',
                    'hostname': 'test-client',
                    'timestamp': '$(date -Iseconds)',
                    'component': 'connection_test',
                    'status': 'PASS',
                    'message': 'Connection test successful'
                }
            }
            
            await websocket.send(json.dumps(test_message))
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get('status') == 'success':
                print('✅ Connection test successful!')
                print(f'   Response: {response_data[\"message\"]}')
            else:
                print('❌ Connection test failed!')
                print(f'   Response: {response_data}')
                
    except Exception as e:
        print(f'❌ Connection test failed: {e}')

asyncio.run(test_connection())
" 2>/dev/null || echo -e "${RED}❌ Connection test failed${NC}"
            else
                echo -e "${RED}❌ Server is not running${NC}"
            fi
        else
            echo -e "${RED}❌ Server is not running${NC}"
        fi
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test|foreground|fg}"
        echo ""
        echo "Commands:"
        echo "  start       - Start WebSocket server in background"
        echo "  stop        - Stop WebSocket server"
        echo "  restart     - Restart WebSocket server"
        echo "  status      - Check WebSocket server status and stats"
        echo "  logs        - Show WebSocket server logs (follow mode)"
        echo "  test        - Test WebSocket server connection"
        echo "  foreground  - Start WebSocket server in foreground (fg)"
        echo ""
        echo "WebSocket Server Details:"
        echo "  🌐 Listen Address: 0.0.0.0:$PORT (all interfaces)"
        echo "  🔗 Connection URL: ws://localhost:$PORT"
        echo "  📁 Database: websocket_server.db"
        echo "  📝 Log File: $LOG_FILE"
        echo ""
        exit 1
        ;;
esac

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}🎉 WebSocket Server Management Complete${NC}"