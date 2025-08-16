# LPR Server - Project Documentation

**Version:** 1.0.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Status:** Planning

## Overview

LPR Server เป็นระบบประมวลผล License Plate Recognition ที่ทำงานบน Ubuntu Server สำหรับรับข้อมูลจาก Edge devices และประมวลผลผลลัพธ์

## System Architecture

### Server Platform (Ubuntu)
- **Hardware:** Ubuntu Server
- **OS:** Ubuntu 22.04+/24.04 LTS
- **Database:** PostgreSQL
- **Web Framework:** Flask + Flask-SocketIO
- **Frontend:** Bootstrap 5 + Chart.js

## Key Features

- License Plate Recognition processing
- Database storage and management
- Web-based dashboard
- RESTful API for Edge communication
- Real-time data streaming via WebSocket
- User authentication and authorization

## Project Structure

```
lpr_server/
├── api/                    # API endpoints
├── database/               # Database models and migrations
├── frontend/               # Web dashboard
├── processing/             # LPR processing logic
├── docs/                   # Documentation
└── deployment/             # Deployment scripts
```

## Technology Stack

### Backend
- **Python 3.10+**
- **Flask** - Web framework
- **Flask-SocketIO** - WebSocket support
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database

### Frontend
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **JavaScript** - Client-side logic

### Infrastructure
- **Nginx** - Reverse proxy
- **Gunicorn** - WSGI server
- **Docker** - Containerization (optional)

## Development Status

### Planned Features
- [ ] Database schema design
- [ ] API endpoints development
- [ ] LPR processing integration
- [ ] Web dashboard development
- [ ] User authentication system
- [ ] Real-time data streaming
- [ ] Performance monitoring
- [ ] Security implementation

### Documentation Needed
- [ ] Installation guide
- [ ] API documentation
- [ ] Database schema documentation
- [ ] Deployment guide
- [ ] Monitoring guide
- [ ] Security guide

## Integration with Edge Devices

### Communication Protocol
- **REST API** สำหรับการส่งข้อมูล
- **WebSocket** สำหรับ real-time updates
- **Tailscale VPN** สำหรับ secure communication

### Data Flow
1. Edge device captures image
2. AI processing on Edge
3. Results sent to LPR Server
4. Server processes and stores data
5. Dashboard updates in real-time

## Next Steps

1. **Database Design** - ออกแบบ schema สำหรับ LPR data
2. **API Development** - พัฒนา REST API endpoints
3. **Frontend Development** - สร้าง web dashboard
4. **Integration Testing** - ทดสอบการเชื่อมต่อกับ Edge devices
5. **Deployment** - Deploy ระบบไปยัง production

---

**Note:** เอกสารนี้จะได้รับการอัปเดตเมื่อเริ่มการพัฒนา LPR Server
