# AI Camera Edge System - Project Documentation

**Version:** 1.3.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Status:** Active

## Overview

เอกสารเฉพาะโปรเจคสำหรับระบบ AI Camera Edge ที่ประกอบด้วย Edge Device (Raspberry Pi + Hailo) และ LPR Server (Ubuntu)

## 📁 Documentation Structure

```
docs/
├── edge/                    # เอกสารเฉพาะ Edge Device
│   ├── project-overview.md  # ภาพรวมโปรเจค AI Camera Edge
│   ├── api-reference.md     # API เฉพาะของ Edge device
│   ├── metadata-debugging.md # การ debug metadata
│   ├── dashboard-improvements.md # การปรับปรุง dashboard
│   └── picamera2-reference.md # อ้างอิง PiCamera2
├── server/                  # เอกสารเฉพาะ Server
│   └── README.md           # LPR Server Documentation
├── shared/                  # เอกสารที่แชร์ระหว่าง Edge และ Server
│   ├── tailscale-setup.md  # การตั้งค่า Tailscale เฉพาะโปรเจค
│   ├── tailscale-acls.json # ACLs configuration
│   └── tailscale-acls-fixed.json # ACLs ที่แก้ไขแล้ว
└── README.md               # This file
```

## 🚀 Quick Start

### For Edge Device Development
1. **[Project Overview](edge/project-overview.md)** - ภาพรวมระบบ Edge AI
2. **[API Reference](edge/api-reference.md)** - API endpoints และ WebSocket
3. **[PiCamera2 Reference](edge/picamera2-reference.md)** - การใช้งาน PiCamera2
4. **[Metadata Debugging](edge/metadata-debugging.md)** - การ debug metadata
5. **[Dashboard Improvements](edge/dashboard-improvements.md)** - การปรับปรุง dashboard

### For Server Development
1. **[LPR Server Documentation](server/README.md)** - เอกสารสำหรับ LPR Server

### For Shared Configuration
1. **[Tailscale Setup](shared/tailscale-setup.md)** - การตั้งค่า Tailscale เฉพาะโปรเจค
2. **[Tailscale ACLs](shared/tailscale-acls.json)** - ACLs configuration
3. **[Fixed ACLs](shared/tailscale-acls-fixed.json)** - ACLs ที่แก้ไขแล้ว
4. **[Unified Communication Architecture](shared/unified-communication-architecture.md)** - สถาปัตยกรรมการสื่อสารแบบรวม
5. **[GitHub Issue Guidelines](GITHUB_ISSUE_GUIDELINES.md)** - แนวทางการจัดการ GitHub Issues

## 🔗 Cross-References

### Installation and Setup
- **[Installation Guides](../../pwd_library/docs/installation/README.md)** - คู่มือการติดตั้งทุก platform
- **[Setup Guides](../../pwd_library/docs/setup/README.md)** - คู่มือการตั้งค่าทุกเทคโนโลยี

### General Knowledge
- **[General Guides](../../pwd_library/docs/guides/)** - คู่มือทั่วไป
- **[References](../../pwd_library/docs/reference/)** - เอกสารอ้างอิงทั่วไป
- **[Monitoring](../../pwd_library/docs/monitoring/)** - การติดตามระบบ
- **[Deployment](../../pwd_library/docs/deployment/)** - การ deploy

## 📊 System Architecture

### Edge Device (Raspberry Pi 5 + Hailo-8)
- **Hardware:** Raspberry Pi 5 (ARM64)
- **OS:** Raspberry Pi OS (Brookwarm)
- **AI Accelerator:** Hailo-8
- **Camera:** PiCamera2
- **Communication:** REST API, WebSocket, MQTT

### LPR Server (Ubuntu)
- **Hardware:** Ubuntu Server
- **OS:** Ubuntu 22.04+/24.04 LTS
- **Database:** PostgreSQL
- **Web Framework:** Flask + Flask-SocketIO
- **Frontend:** Bootstrap 5 + Chart.js

### Development Environment
- **Platforms:** Windows, macOS, Linux
- **Tools:** VS Code, PyCharm, Cursor
- **Version Control:** Git
- **VPN:** Tailscale

## 🔧 Development Workflow

### Edge Device Development
1. **Setup Environment** - ติดตั้ง Hailo TAPPAS และ dependencies
2. **Camera Configuration** - ตั้งค่า PiCamera2
3. **AI Model Integration** - เชื่อมต่อ Hailo-8 models
4. **API Development** - พัฒนา REST API และ WebSocket
5. **Testing** - ทดสอบบน Edge device

### Server Development
1. **Database Design** - ออกแบบ PostgreSQL schema
2. **API Development** - พัฒนา REST API endpoints
3. **WebSocket Integration** - เชื่อมต่อ real-time communication
4. **Frontend Development** - พัฒนา web dashboard
5. **Integration Testing** - ทดสอบการเชื่อมต่อกับ Edge devices

### Shared Development
1. **Network Setup** - ตั้งค่า Tailscale VPN
2. **Communication Protocol** - กำหนด REST API และ WebSocket
3. **Security Configuration** - ตั้งค่าความปลอดภัย
4. **Monitoring Setup** - ตั้งค่าการติดตามระบบ

## 📝 API Documentation

### REST API Endpoints
- **Health Check:** `GET /health`
- **Camera Control:** `POST /api/camera/start`, `POST /api/camera/stop`
- **AI Processing:** `POST /api/ai/process`
- **System Information:** `GET /api/system/info`

### WebSocket Events
- **Connection:** `connect`, `disconnect`
- **Camera Events:** `camera_started`, `camera_stopped`, `frame_captured`
- **AI Events:** `ai_processing_started`, `ai_processing_completed`, `detection_result`
- **System Events:** `system_status`, `error_occurred`

## 🔒 Security Configuration

### Network Security
- **Tailscale VPN** - เชื่อมต่อทุกเครื่องอย่างปลอดภัย
- **ACLs Configuration** - ควบคุมการเข้าถึงระหว่างเครื่อง
- **Firewall Rules** - ตั้งค่าความปลอดภัย

### Application Security
- **Authentication** - JWT-based authentication
- **Authorization** - Role-based access control
- **Data Encryption** - เข้ารหัสข้อมูลที่สำคัญ
- **Input Validation** - ตรวจสอบข้อมูล input

## 📊 Monitoring and Logging

### System Monitoring
- **CPU Usage** - ตรวจสอบ CPU utilization
- **Memory Usage** - ตรวจสอบ memory consumption
- **Temperature** - ตรวจสอบ system temperature
- **Network** - ตรวจสอบ network connectivity

### Application Monitoring
- **Service Status** - ตรวจสอบ service health
- **AI Processing** - ตรวจสอบ AI inference performance
- **Camera Status** - ตรวจสอบ camera operation
- **Error Logging** - บันทึก errors และ exceptions

## 🛠️ Troubleshooting

### Common Issues
- **Camera Detection** - ตรวจสอบ camera interface และ permissions
- **Hailo Device** - ตรวจสอบ Hailo-8 connection และ firmware
- **Network Connectivity** - ตรวจสอบ Tailscale status และ ACLs
- **Service Startup** - ตรวจสอบ systemd services และ logs

### Diagnostic Commands
```bash
# System information
uname -a
vcgencmd get_mem gpu
vcgencmd measure_temp

# Service status
sudo systemctl status aicamera_v1.3
sudo journalctl -u aicamera_v1.3 -f

# Network connectivity
tailscale status
tailscale ping lprserver

# Camera status
vcgencmd get_camera
ls -la /dev/video*
```

## 📚 References

### Official Documentation
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [Hailo TAPPAS Documentation](https://hailo.ai/developer-zone/)
- [PiCamera2 Documentation](https://picamera2.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Tailscale Documentation](https://tailscale.com/kb/)

### Project Resources
- [Installation Guides](../../pwd_library/docs/installation/) - คู่มือการติดตั้ง
- [Setup Guides](../../pwd_library/docs/setup/) - คู่มือการตั้งค่า
- [General Knowledge](../../pwd_library/docs/) - ความรู้ทั่วไป

---

**Note:** เอกสารนี้เป็นเอกสารเฉพาะโปรเจค AI Camera Edge System
