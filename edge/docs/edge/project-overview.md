# AI Camera Edge System - Project Documentation

**Version:** 1.3.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Status:** Active Development

## Project Overview

AI Camera Edge System เป็นระบบประมวลผลภาพแบบ Edge AI ที่ทำงานบน Raspberry Pi 5 พร้อม Hailo-8 AI accelerator สำหรับการตรวจจับและวิเคราะห์ภาพแบบ real-time

## System Architecture

### Edge Platform (Raspberry Pi 5)
- **Hardware:** Raspberry Pi 5 (ARM64)
- **OS:** Raspberry Pi OS (Brookwarm) - Debian-based
- **AI Acceleration:** Hailo-8 AI accelerator
- **Camera:** PiCamera2
- **Network:** Tailscale VPN

### Server Platform (Ubuntu)
- **Hardware:** Ubuntu Server
- **OS:** Ubuntu 22.04+/24.04 LTS
- **Database:** PostgreSQL
- **Web Framework:** Flask + Flask-SocketIO
- **Frontend:** Bootstrap 5 + Chart.js

## Key Features

- Real-time image processing with Hailo AI acceleration
- Distributed architecture with Edge-Server communication
- Secure VPN connectivity via Tailscale
- Web-based dashboard for monitoring and control
- RESTful API for system integration
- WebSocket for real-time data streaming

## Project Structure

```
aicamera/
├── v1_3/                    # Main application source
├── docs/                    # Documentation
│   ├── project/            # Project-specific docs
│   ├── guides/             # How-to guides
│   ├── reference/          # Technical references
│   ├── deployment/         # Deployment guides
│   └── monitoring/         # Monitoring and troubleshooting
├── systemd_service/        # Systemd service files
├── resources/              # AI models and resources
├── logs/                   # Application logs
└── venv_hailo/            # Python virtual environment
```

## Technology Stack

### Edge Platform
- **Python 3.10+**
- **Hailo TAPPAS** - AI framework
- **OpenCV** - Image processing
- **Picamera2** - Camera interface
- **Flask/Gunicorn** - Web server
- **WebSocket** - Real-time communication

### Server Platform
- **Python 3.10+**
- **Flask** - Web framework
- **Flask-SocketIO** - WebSocket support
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database
- **Nginx** - Reverse proxy

### Networking
- **Tailscale** - Mesh VPN
- **REST API** - HTTP communication
- **MQTT** - Lightweight messaging

## Development Guidelines

### Code Style
- **Python:** PEP 8 with Black formatter
- **Documentation:** Google-style docstrings
- **Testing:** 90%+ coverage requirement

### Version Control
- **Git** with Git LFS for large files
- **GitHub Actions** for CI/CD
- **Semantic versioning**

### Deployment
- **Edge:** Systemd service with auto-restart
- **Server:** Systemd service with health checks
- **Rollback:** Version tagging capability

## Quick Start

1. **Setup Environment:**
   ```bash
   source setup_env.sh
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Tailscale:**
   ```bash
   ./fix_tailscale.sh
   ```

4. **Start Application:**
   ```bash
   sudo systemctl start aicamera_v1.3
   ```

## Documentation Index

- [Installation Guide](../guides/installation.md)
- [Tailscale Setup](../guides/tailscale-setup.md)
- [Development Guide](../guides/development.md)
- [Deployment Guide](../deployment/deployment.md)
- [Monitoring Guide](../monitoring/monitoring.md)
- [API Reference](../reference/api-reference.md)

## Support

สำหรับคำถามหรือปัญหาทางเทคนิค กรุณาติดต่อทีมพัฒนา AI Camera
