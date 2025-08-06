# WebSocket Server for AI Camera System

This directory contains all the files needed to deploy the WebSocket server on a separate machine.

## 📁 Files Included

- `websocket_server.py` - Main WebSocket server application
- `run_websocket_server.sh` - Service management script
- `install_all_services.sh` - Systemd service installation
- `requirements.txt` - Python dependencies
- `static/` - Static web assets
- `templates/` - HTML templates

## 🚀 Deployment Instructions

### 1. Copy to Target Server
```bash
# Copy this entire directory to your target server
scp -r websocket_server/ user@target-server:/path/to/deployment/
```

### 2. Install Dependencies
```bash
cd /path/to/deployment/websocket_server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Edit websocket_server.py to set the correct host and port
# Default: 0.0.0.0:8765 (listen on all interfaces, port 8765)
```

### 4. Install as Systemd Service (Optional)
```bash
sudo ./install_all_services.sh
sudo systemctl enable websocket-server
sudo systemctl start websocket-server
```

### 5. Manual Start (Alternative)
```bash
./run_websocket_server.sh start
```

## 🔧 Configuration

### WebSocket Server Settings
- **Host**: 0.0.0.0 (listen on all interfaces)
- **Port**: 8765 (default)
- **Database**: websocket_server.db (auto-created)

### Client Configuration
Update the client configuration to point to this server:
```bash
WEBSOCKET_SERVER_URL = "ws://your-server-ip:8765"
```

## 📊 Monitoring

### Check Status
```bash
./run_websocket_server.sh status
```

### View Logs
```bash
./run_websocket_server.sh logs
tail -f log/websocket_server.log
```

### Database Queries
```bash
sqlite3 websocket_server.db
.tables
SELECT COUNT(*) FROM lpr_detections;
SELECT COUNT(*) FROM health_monitors;
```

## 🔒 Security Considerations

1. **Firewall**: Configure firewall to allow port 8765
2. **SSL/TLS**: Consider using WSS (WebSocket Secure) for production
3. **Authentication**: Implement authentication if needed
4. **Rate Limiting**: Consider implementing rate limiting

## 📝 API Endpoints

The WebSocket server accepts the following message formats:

### LPR Detection Data
```json
{
  "table": "lpr_detection",
  "action": "insert",
  "data": {
    "license_plate": "ABC1234",
    "confidence": 95.5,
    "checkpoint_id": "1",
    "timestamp": "2024-08-06T10:30:00",
    "hostname": "aicamera",
    "image": "data:image/jpeg;base64,..."
  }
}
```

### Health Monitor Data
```json
{
  "table": "health_monitor",
  "action": "insert",
  "data": {
    "checkpoint_id": "1",
    "hostname": "aicamera",
    "timestamp": "2024-08-06T10:30:00",
    "component": "camera",
    "status": "PASS",
    "message": "Camera working normally"
  }
}
```

## 🚨 Troubleshooting

### Common Issues
1. **Port already in use**: Change port in websocket_server.py
2. **Permission denied**: Check file permissions and user access
3. **Database locked**: Ensure only one instance is running
4. **Connection refused**: Check firewall and network configuration

### Log Files
- `log/websocket_server.log` - Main application log
- `websocket_server.db` - SQLite database

## 📞 Support

For issues or questions, check the main AI Camera documentation or contact the development team. 