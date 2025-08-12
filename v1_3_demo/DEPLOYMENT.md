# AI Camera v1.3 Demo - Deployment Guide

## 🚀 Quick Start

### Local Development
```bash
cd v1_3_demo
python3 demo_app.py
```

### Docker Deployment
```bash
cd v1_3_demo
docker-compose up -d
```

## 🌐 Cloud Deployment Options

### 1. AWS EC2

#### Launch EC2 Instance
```bash
# Launch Ubuntu 22.04 LTS instance
# Minimum: t2.micro (free tier)
# Recommended: t2.small or t3.small
```

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install OpenCV dependencies
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev -y
```

#### Deploy Application
```bash
# Clone or upload demo files
cd /home/ubuntu
mkdir aicamera-demo
cd aicamera-demo

# Upload demo files to this directory
# Then run:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 demo_app.py
```

#### Configure Security Group
- **Port 5000**: Open for web access
- **Port 22**: Open for SSH access

### 2. Google Cloud Platform

#### Create VM Instance
```bash
# Create Compute Engine instance
gcloud compute instances create aicamera-demo \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud
```

#### Deploy with Docker
```bash
# SSH to instance
gcloud compute ssh aicamera-demo --zone=us-central1-a

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER

# Upload and run demo
docker-compose up -d
```

### 3. Azure

#### Create App Service
```bash
# Create resource group
az group create --name aicamera-demo-rg --location eastus

# Create app service plan
az appservice plan create --name aicamera-demo-plan --resource-group aicamera-demo-rg --sku B1

# Create web app
az webapp create --name aicamera-demo --resource-group aicamera-demo-rg --plan aicamera-demo-plan --runtime "PYTHON:3.11"
```

#### Deploy Application
```bash
# Deploy using Azure CLI
az webapp deployment source config-zip --resource-group aicamera-demo-rg --name aicamera-demo --src demo.zip
```

### 4. Heroku

#### Create Heroku App
```bash
# Install Heroku CLI
# Create app
heroku create aicamera-demo

# Set environment variables
heroku config:set DEMO_MODE=true
heroku config:set FLASK_ENV=production
```

#### Deploy
```bash
# Deploy to Heroku
git push heroku main
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t aicamera-demo .

# Run container
docker run -d -p 5000:5000 --name aicamera-demo aicamera-demo

# Or use docker-compose
docker-compose up -d
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Configuration

### Environment Variables
```bash
# Demo mode (always true for demo)
DEMO_MODE=true

# Flask environment
FLASK_ENV=development  # or production

# Python path
PYTHONPATH=/app

# Logging
LOG_LEVEL=INFO
```

### Port Configuration
- **Default Port**: 5000
- **Change Port**: Modify `demo_app.py` line 371
- **Docker Port**: Modify `docker-compose.yml` ports section

### Video File
- **Default**: `example.mp4`
- **Change**: Modify `DEMO_VIDEO_FILE` in `demo_app.py`
- **Supported Formats**: MP4, AVI, MOV (OpenCV supported)

## 📊 Monitoring

### Health Check
```bash
# Check application status
curl http://localhost:5000/demo/status

# Expected response:
{
  "success": true,
  "data": {
    "demo_mode": true,
    "camera": {...},
    "detection": {...},
    "health": {...}
  }
}
```

### Logs
```bash
# View application logs
tail -f logs/aicamera.log

# Docker logs
docker logs aicamera-demo

# Docker compose logs
docker-compose logs -f
```

### Performance Monitoring
```bash
# Check resource usage
docker stats aicamera-demo

# Check port usage
netstat -tlnp | grep 5000
```

## 🔒 Security Considerations

### Network Security
- **Firewall**: Only open port 5000
- **HTTPS**: Use reverse proxy (nginx) for production
- **Access Control**: Limit access to trusted IPs

### Application Security
- **Demo Mode**: Always enabled (no hardware access)
- **Local Access**: Default to localhost only
- **No External Calls**: No data sent to external servers

### Container Security
```bash
# Run as non-root user
docker run -u 1000:1000 -p 5000:5000 aicamera-demo

# Use read-only filesystem
docker run --read-only -p 5000:5000 aicamera-demo
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 5000
lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or use different port
export FLASK_RUN_PORT=5001
```

#### Video File Not Found
```bash
# Check if video file exists
ls -la example.mp4

# Check video file format
file example.mp4

# Re-encode if needed
ffmpeg -i input.mp4 -c:v libx264 -preset fast example.mp4
```

#### Docker Issues
```bash
# Clean up containers
docker system prune -a

# Rebuild image
docker build --no-cache -t aicamera-demo .

# Check container logs
docker logs aicamera-demo
```

#### Memory Issues
```bash
# Check memory usage
free -h

# Increase swap if needed
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Performance Optimization

#### For High Traffic
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 demo_app:app

# Use nginx as reverse proxy
sudo apt install nginx
# Configure nginx to proxy to gunicorn
```

#### For Low Resources
```bash
# Reduce video quality
# Modify demo_app.py line 281
cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])

# Reduce frame rate
# Modify demo_app.py line 285
time.sleep(1.0 / 15)  # 15 FPS instead of 30
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Run multiple instances
docker run -d -p 5001:5000 aicamera-demo
docker run -d -p 5002:5000 aicamera-demo
docker run -d -p 5003:5000 aicamera-demo

# Use load balancer
# Configure nginx or HAProxy
```

### Vertical Scaling
```bash
# Increase container resources
docker run -d -p 5000:5000 \
  --memory=2g \
  --cpus=2 \
  aicamera-demo
```

## 🔄 Updates

### Application Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker
sudo apt install docker.io docker-compose -y
```

## 📞 Support

### Logs Location
- **Local**: `logs/aicamera.log`
- **Docker**: `docker logs aicamera-demo`
- **System**: `/var/log/syslog`

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 demo_app.py

# Or modify demo_app.py
logger.setLevel(logging.DEBUG)
```

### Contact
- Check README.md for detailed documentation
- Review logs for error messages
- Verify network connectivity
- Test video file accessibility

---

**Note**: This demo application is designed for demonstration purposes only and should not be used in production environments.
