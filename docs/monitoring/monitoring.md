# AI Camera Edge System - Monitoring Guide

**Version:** 1.0.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Category:** Operations & Monitoring  
**Status:** Active

## Table of Contents

1. [Overview](#overview)
2. [System Monitoring](#system-monitoring)
3. [Application Monitoring](#application-monitoring)
4. [Network Monitoring](#network-monitoring)
5. [Log Management](#log-management)
6. [Alerting](#alerting)
7. [Troubleshooting](#troubleshooting)

## Overview

Monitoring guide สำหรับ AI Camera Edge System ครอบคลุมการติดตามประสิทธิภาพของระบบ การตรวจสอบสถานะ และการแก้ไขปัญหา

### Monitoring Objectives
- **System Health:** CPU, Memory, Storage, Temperature
- **Application Performance:** Response time, Throughput, Error rates
- **Network Connectivity:** Tailscale, Internet, Local network
- **AI Processing:** Inference latency, Model performance
- **Camera Operations:** Frame rate, Image quality, Device status

## System Monitoring

### Hardware Monitoring

#### CPU Monitoring
```bash
# CPU usage
htop
top -p $(pgrep -d',' python)

# CPU temperature
vcgencmd measure_temp

# CPU frequency
vcgencmd measure_clock arm
vcgencmd measure_clock gpu

# CPU load average
uptime
cat /proc/loadavg
```

#### Memory Monitoring
```bash
# Memory usage
free -h
cat /proc/meminfo

# Memory allocation
vcgencmd get_mem arm
vcgencmd get_mem gpu

# Memory pressure
cat /proc/pressure/memory
```

#### Storage Monitoring
```bash
# Disk usage
df -h
du -sh /home/camuser/aicamera/*

# Disk I/O
iotop
iostat -x 1

# Storage health
sudo smartctl -a /dev/mmcblk0
```

#### Temperature Monitoring
```bash
# System temperature
vcgencmd measure_temp

# Thermal throttling
vcgencmd get_throttled

# Temperature monitoring script
cat > /usr/local/bin/temp_monitor.sh <<'EOF'
#!/bin/bash
while true; do
    temp=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
    echo "$(date): CPU Temperature: ${temp}°C"
    
    if (( $(echo "$temp > 80" | bc -l) )); then
        echo "WARNING: High temperature detected!"
    fi
    
    sleep 30
done
EOF

chmod +x /usr/local/bin/temp_monitor.sh
```

### Performance Monitoring

#### System Performance Script
```bash
#!/bin/bash
# system_monitor.sh

echo "=== System Performance Report ==="
echo "Date: $(date)"
echo ""

echo "=== CPU Information ==="
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo "CPU Temperature: $(vcgencmd measure_temp | cut -d'=' -f2)"
echo "CPU Frequency: $(vcgencmd measure_clock arm | cut -d'=' -f2) Hz"
echo ""

echo "=== Memory Information ==="
free -h | grep -E "(Mem|Swap)"
echo ""

echo "=== Storage Information ==="
df -h | grep -E "(Filesystem|/dev/root)"
echo ""

echo "=== Process Information ==="
ps aux | grep -E "(python|hailo)" | grep -v grep
echo ""

echo "=== Network Information ==="
ip addr show | grep -E "(inet|UP)"
echo ""
```

## Application Monitoring

### Service Status Monitoring

#### Systemd Service Monitoring
```bash
# Check service status
sudo systemctl status aicamera_v1.3

# Monitor service logs
sudo journalctl -u aicamera_v1.3 -f

# Service health check
sudo systemctl is-active aicamera_v1.3
sudo systemctl is-enabled aicamera_v1.3
```

#### Application Health Check
```bash
# Health check endpoint
curl -f http://localhost:5000/health

# Application metrics
curl http://localhost:5000/metrics

# WebSocket connectivity
python3 -c "
import websocket
try:
    ws = websocket.create_connection('ws://localhost:8765', timeout=5)
    print('WebSocket: OK')
    ws.close()
except Exception as e:
    print(f'WebSocket: ERROR - {e}')
"
```

### AI Processing Monitoring

#### Hailo Device Monitoring
```bash
# Hailo device status
hailortcli fw-control identify

# Hailo device temperature
hailortcli fw-control get-temperature

# Hailo device utilization
hailortcli fw-control get-utilization

# Hailo logs
tail -f /var/log/hailort.log
```

#### Model Performance Monitoring
```python
# model_performance_monitor.py
import time
import logging
from datetime import datetime

class ModelPerformanceMonitor:
    def __init__(self):
        self.inference_times = []
        self.error_count = 0
        self.total_inferences = 0
        
    def record_inference(self, inference_time, success=True):
        self.inference_times.append(inference_time)
        self.total_inferences += 1
        
        if not success:
            self.error_count += 1
            
    def get_metrics(self):
        if not self.inference_times:
            return {}
            
        avg_time = sum(self.inference_times) / len(self.inference_times)
        max_time = max(self.inference_times)
        min_time = min(self.inference_times)
        error_rate = self.error_count / self.total_inferences if self.total_inferences > 0 else 0
        
        return {
            'avg_inference_time': avg_time,
            'max_inference_time': max_time,
            'min_inference_time': min_time,
            'error_rate': error_rate,
            'total_inferences': self.total_inferences
        }
        
    def log_metrics(self):
        metrics = self.get_metrics()
        logging.info(f"Model Performance: {metrics}")
```

### Camera Monitoring

#### Camera Status Monitoring
```bash
# Camera device status
ls -la /dev/video*

# Camera capabilities
v4l2-ctl --device=/dev/video0 --list-formats-ext

# Camera frame rate
v4l2-ctl --device=/dev/video0 --get-fmt-video

# Camera temperature (if supported)
v4l2-ctl --device=/dev/video0 --get-ctrl=temperature
```

#### Camera Performance Script
```python
# camera_monitor.py
import cv2
import time
from picamera2 import Picamera2

class CameraMonitor:
    def __init__(self):
        self.picam2 = Picamera2()
        self.frame_count = 0
        self.start_time = time.time()
        
    def check_camera_health(self):
        try:
            # Configure camera
            self.picam2.configure(self.picam2.create_preview_configuration())
            self.picam2.start()
            
            # Capture test frame
            frame = self.picam2.capture_array()
            
            # Check frame properties
            height, width, channels = frame.shape
            frame_size = frame.nbytes
            
            self.picam2.stop()
            
            return {
                'status': 'healthy',
                'resolution': f"{width}x{height}",
                'channels': channels,
                'frame_size': frame_size
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def monitor_frame_rate(self, duration=10):
        try:
            self.picam2.configure(self.picam2.create_preview_configuration())
            self.picam2.start()
            
            start_time = time.time()
            frame_count = 0
            
            while time.time() - start_time < duration:
                self.picam2.capture_array()
                frame_count += 1
                
            self.picam2.stop()
            
            fps = frame_count / duration
            return {
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
```

## Network Monitoring

### Tailscale Monitoring

#### Tailscale Status Monitoring
```bash
# Tailscale status
tailscale status

# Tailscale connectivity
tailscale ping lprserver

# Tailscale logs
sudo journalctl -u tailscaled -f

# Tailscale health check
tailscale status --json
```

#### Network Performance Monitoring
```bash
# Network interface status
ip addr show tailscale0
ip route show

# Network performance
ping -c 5 lprserver
iperf3 -c lprserver

# Network bandwidth
nethogs
iftop
```

### Connectivity Monitoring Script
```bash
#!/bin/bash
# network_monitor.sh

echo "=== Network Connectivity Report ==="
echo "Date: $(date)"
echo ""

echo "=== Tailscale Status ==="
tailscale status
echo ""

echo "=== Network Interfaces ==="
ip addr show | grep -E "(inet|UP)"
echo ""

echo "=== Connectivity Tests ==="
echo "Testing connection to LPR server..."
if tailscale ping -c 3 lprserver > /dev/null 2>&1; then
    echo "✓ LPR Server: Connected"
else
    echo "✗ LPR Server: Disconnected"
fi

echo "Testing internet connectivity..."
if ping -c 3 8.8.8.8 > /dev/null 2>&1; then
    echo "✓ Internet: Connected"
else
    echo "✗ Internet: Disconnected"
fi

echo "Testing DNS resolution..."
if nslookup google.com > /dev/null 2>&1; then
    echo "✓ DNS: Working"
else
    echo "✗ DNS: Not working"
fi
echo ""
```

## Log Management

### Log Configuration

#### Application Logging
```python
# logging_config.py
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/aicamera.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Create specific loggers
    ai_logger = logging.getLogger('ai_processing')
    ai_logger.setLevel(logging.INFO)
    
    camera_logger = logging.getLogger('camera')
    camera_logger.setLevel(logging.INFO)
    
    network_logger = logging.getLogger('network')
    network_logger.setLevel(logging.INFO)
    
    return ai_logger, camera_logger, network_logger
```

#### System Log Monitoring
```bash
# Monitor system logs
sudo journalctl -f

# Monitor application logs
tail -f logs/aicamera.log

# Monitor Tailscale logs
sudo journalctl -u tailscaled -f

# Monitor Hailo logs
tail -f /var/log/hailort.log
```

### Log Rotation Configuration
```bash
# /etc/logrotate.d/aicamera
/home/camuser/aicamera/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 camuser camuser
    postrotate
        systemctl reload aicamera_v1.3
    endscript
}
```

## Alerting

### Alert Configuration

#### System Alert Script
```bash
#!/bin/bash
# alert_monitor.sh

# Configuration
ALERT_EMAIL="admin@example.com"
LOG_FILE="/var/log/aicamera_alerts.log"

# Alert functions
send_alert() {
    local message="$1"
    local level="$2"
    
    echo "$(date) - $level: $message" >> "$LOG_FILE"
    
    # Send email alert
    echo "$message" | mail -s "AI Camera Alert: $level" "$ALERT_EMAIL"
    
    # Log to system journal
    logger -t aicamera_alert "$level: $message"
}

# Check CPU temperature
check_temperature() {
    local temp=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
    if (( $(echo "$temp > 80" | bc -l) )); then
        send_alert "High CPU temperature: ${temp}°C" "WARNING"
    fi
}

# Check memory usage
check_memory() {
    local mem_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
    if (( $(echo "$mem_usage > 90" | bc -l) )); then
        send_alert "High memory usage: ${mem_usage}%" "WARNING"
    fi
}

# Check disk usage
check_disk() {
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        send_alert "High disk usage: ${disk_usage}%" "WARNING"
    fi
}

# Check service status
check_service() {
    if ! systemctl is-active --quiet aicamera_v1.3; then
        send_alert "AI Camera service is not running" "CRITICAL"
    fi
}

# Check network connectivity
check_network() {
    if ! tailscale ping -c 1 lprserver > /dev/null 2>&1; then
        send_alert "Cannot connect to LPR server" "WARNING"
    fi
}

# Main monitoring loop
while true; do
    check_temperature
    check_memory
    check_disk
    check_service
    check_network
    
    sleep 300  # Check every 5 minutes
done
```

#### Alert Integration with Monitoring Tools
```bash
# Install monitoring tools
sudo apt install -y prometheus-node-exporter

# Configure Prometheus alerts
cat > /etc/prometheus/alerts.yml <<EOF
groups:
  - name: aicamera_alerts
    rules:
      - alert: HighTemperature
        expr: node_hwmon_temp_celsius > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU temperature detected"
          
      - alert: ServiceDown
        expr: up{job="aicamera"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AI Camera service is down"
          
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
EOF
```

## Troubleshooting

### Common Issues and Solutions

#### 1. High CPU Temperature
```bash
# Check temperature
vcgencmd measure_temp

# Check thermal throttling
vcgencmd get_throttled

# Solutions:
# - Improve ventilation
# - Reduce CPU load
# - Add cooling fan
# - Optimize application performance
```

#### 2. Memory Issues
```bash
# Check memory usage
free -h

# Check memory pressure
cat /proc/pressure/memory

# Solutions:
# - Restart application
# - Optimize memory usage
# - Increase swap space
# - Reduce concurrent processes
```

#### 3. Network Connectivity Issues
```bash
# Check Tailscale status
tailscale status

# Check network interfaces
ip addr show

# Solutions:
# - Restart Tailscale service
# - Check ACLs configuration
# - Verify network cables
# - Check firewall settings
```

#### 4. Camera Issues
```bash
# Check camera devices
ls -la /dev/video*

# Check camera permissions
groups camuser

# Solutions:
# - Restart camera service
# - Check camera connections
# - Update camera drivers
# - Check camera permissions
```

### Diagnostic Commands

#### Comprehensive System Check
```bash
#!/bin/bash
# system_diagnostic.sh

echo "=== AI Camera System Diagnostic ==="
echo "Date: $(date)"
echo ""

echo "=== System Information ==="
uname -a
cat /etc/os-release
echo ""

echo "=== Hardware Information ==="
vcgencmd get_mem arm
vcgencmd get_mem gpu
vcgencmd measure_temp
echo ""

echo "=== Service Status ==="
systemctl status aicamera_v1.3 --no-pager
systemctl status tailscaled --no-pager
echo ""

echo "=== Network Status ==="
tailscale status
ip addr show tailscale0
echo ""

echo "=== Process Information ==="
ps aux | grep -E "(python|hailo)" | grep -v grep
echo ""

echo "=== Log Information ==="
tail -20 logs/aicamera.log
echo ""

echo "=== Storage Information ==="
df -h
echo ""

echo "=== Memory Information ==="
free -h
echo ""
```

## References

- [Raspberry Pi Monitoring](https://www.raspberrypi.org/documentation/usage/terminal/)
- [Systemd Journal](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [Tailscale Monitoring](https://tailscale.com/kb/1019/troubleshooting/)
- [Hailo Monitoring](https://hailo.ai/developer-zone/)

---

**Note:** เอกสารนี้จะได้รับการอัปเดตเมื่อมีการเปลี่ยนแปลงในระบบหรือ monitoring requirements
