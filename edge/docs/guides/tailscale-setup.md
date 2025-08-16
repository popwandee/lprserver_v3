# Tailscale Setup Guide for AI Camera Edge System

**Version:** 1.0.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Category:** Networking & Security  
**Status:** Active

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [ACLs Setup](#acls-setup)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Overview

Tailscale เป็น mesh VPN ที่ใช้สำหรับเชื่อมต่อ Edge devices (Raspberry Pi) กับ LPR Server (Ubuntu) อย่างปลอดภัยและเสถียร

### Key Benefits
- **Zero-config VPN** - ไม่ต้องตั้งค่า firewall rules
- **Mesh networking** - ทุก device เชื่อมต่อกันโดยตรง
- **Secure by default** - ใช้ WireGuard protocol
- **Easy management** - จัดการผ่าน web dashboard

## Prerequisites

- Tailscale account (https://login.tailscale.com)
- Admin access to Tailscale organization
- Root/sudo access on all devices
- Stable internet connection

## Installation

### Edge Device (Raspberry Pi 5)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale daemon
sudo systemctl enable tailscaled
sudo systemctl start tailscaled
```

### LPR Server (Ubuntu)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale daemon
sudo systemctl enable tailscaled
sudo systemctl start tailscaled
```

### Development Machines

#### Windows
```powershell
winget install Tailscale.Tailscale
```

#### macOS
```bash
brew install tailscale
```

#### Linux
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

## Configuration

### 1. Hostname Configuration

```bash
# Set stable hostname for Edge device
sudo hostnamectl set-hostname aicamera1
echo "aicamera1" | sudo tee /etc/hostname

# Set hostname for LPR server
sudo hostnamectl set-hostname lprserver
echo "lprserver" | sudo tee /etc/hostname

# Update /etc/hosts
echo "127.0.1.1 aicamera1" | sudo tee -a /etc/hosts
echo "127.0.1.1 lprserver" | sudo tee -a /etc/hosts
```

### 2. Auto-Connect Service

สร้างไฟล์ systemd service สำหรับ auto-connect:

```bash
# Create auto-connect service
sudo tee /etc/systemd/system/tailscale-autoconnect.service > /dev/null <<EOF
[Unit]
Description=Tailscale Auto-Connect for AI Camera
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/tailscale up --authkey=YOUR_AUTH_KEY --hostname=aicamera1 --advertise-tags=tag:edge,tag:aicamera --accept-dns=false
ExecStop=/usr/bin/tailscale down
User=camuser
Group=camuser

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tailscale-autoconnect.service
sudo systemctl start tailscale-autoconnect.service
```

### 3. Health Check Script

```bash
# Create health check script
sudo tee /usr/local/bin/tailscale-health-check.sh > /dev/null <<'EOF'
#!/bin/bash

LOG_FILE="/var/log/tailscale-health.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if Tailscale is connected
if ! tailscale status > /dev/null 2>&1; then
    log_message "Tailscale is down, restarting..."
    sudo systemctl restart tailscaled
    sleep 5
    tailscale up --authkey=YOUR_AUTH_KEY --hostname=aicamera1 --advertise-tags=tag:edge,tag:aicamera
    log_message "Tailscale restarted"
fi

# Check connectivity to LPR server
if ! tailscale ping -c 1 lprserver > /dev/null 2>&1; then
    log_message "Cannot ping lprserver"
fi
EOF

sudo chmod +x /usr/local/bin/tailscale-health-check.sh

# Add cron job (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/tailscale-health-check.sh") | crontab -
```

## ACLs Setup

### Basic ACLs Configuration

```json
{
  "tagOwners": {
    "tag:edge": ["email@gmail.com"],
    "tag:server": ["email@gmail.com"],
    "tag:dev": ["email@gmail.com"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:edge"],
      "dst": ["tag:server:*"]
    },
    {
      "action": "accept", 
      "src": ["tag:server"],
      "dst": ["tag:edge:*"]
    },
    {
      "action": "accept", 
      "src": ["tag:dev"],
      "dst": ["tag:server:*", "tag:edge:*"]
    },
    {
      "action": "accept", 
      "src": ["tag:server", "tag:edge"],
      "dst": ["tag:dev:*"]
    }
  ],
  "ssh": [
    {
      "action": "accept",
      "src": ["tag:dev"],
      "dst": ["aicamera1:22"],
      "users": ["camuser"]
    },
    {
      "action": "accept",
      "src": ["tag:dev"],
      "dst": ["lprserver:22"],
      "users": ["ubuntu", "root"]
    }
  ],
  "hosts": {
    "aicamera1": "100.xx.xx.xx",
    "lprserver": "100.xx.xx.xx"
  }
}
```

### Advanced ACLs with Groups

```json
{
  "tagOwners": {
    "tag:edge": ["email@gmail.com"],
    "tag:server": ["email@gmail.com"],
    "tag:dev": ["email@gmail.com"]
  },
  "groups": {
    "group:ai-camera-team": ["email1@gmail.com", "email2@gmail.com"],
    "group:admins": ["admin@gmail.com"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["group:ai-camera-team"],
      "dst": ["tag:edge:*", "tag:server:*"]
    },
    {
      "action": "accept",
      "src": ["group:admins"],
      "dst": ["*:*"]
    }
  ],
  "ssh": [
    {
      "action": "accept",
      "src": ["group:ai-camera-team"],
      "dst": ["aicamera1:22", "lprserver:22"],
      "users": ["camuser", "ubuntu", "root"]
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. Tailscale Connection Issues

```bash
# Check service status
sudo systemctl status tailscaled

# Check logs
sudo journalctl -u tailscaled -f

# Restart service
sudo systemctl restart tailscaled

# Manual connection
tailscale up --authkey=YOUR_AUTH_KEY --hostname=aicamera1
```

#### 2. Hostname Resolution Issues

```bash
# Check hostname
hostname

# Check /etc/hosts
cat /etc/hosts

# Test DNS resolution
nslookup aicamera1
nslookup lprserver
```

#### 3. ACLs Issues

```bash
# Check current status
tailscale status

# Test connectivity
tailscale ping lprserver
tailscale ping aicamera1

# Check ACLs in admin console
# https://login.tailscale.com/admin/acls
```

### Diagnostic Commands

```bash
# Comprehensive status check
tailscale status --json

# Network interface info
ip addr show tailscale0

# Route information
ip route show

# Connectivity test
tailscale ping -c 3 lprserver
```

## Best Practices

### 1. Security
- ใช้ unique hostnames สำหรับแต่ละ device
- ตั้งค่า ACLs ที่จำกัดสิทธิ์ตามความจำเป็น
- ใช้ groups สำหรับการจัดการสิทธิ์
- เปิดใช้งาน SSH access control

### 2. Reliability
- ตั้งค่า auto-connect service
- ใช้ health check scripts
- ตั้งค่า cron jobs สำหรับ monitoring
- เก็บ logs สำหรับ troubleshooting

### 3. Performance
- ใช้ hostnames แทน IP addresses
- ตั้งค่า proper DNS resolution
- ใช้ subnet routes เมื่อจำเป็น
- Monitor network performance

### 4. Management
- ใช้ tags สำหรับ categorization
- ตั้งค่า proper naming convention
- เก็บ documentation ไว้เป็นปัจจุบัน
- ใช้ version control สำหรับ configuration

## Monitoring

### Health Check Script

```bash
#!/bin/bash
# monitor_tailscale.sh

echo "=== Tailscale Status ==="
tailscale status

echo ""
echo "=== Network Interfaces ==="
ip addr show tailscale0

echo ""
echo "=== Recent Logs ==="
sudo journalctl -u tailscaled -n 20 --no-pager

echo ""
echo "=== Connectivity Test ==="
if tailscale ping -c 1 100.100.100.100 > /dev/null 2>&1; then
    echo "✓ Basic connectivity: OK"
else
    echo "✗ Basic connectivity: Failed"
fi

if tailscale ping -c 1 lprserver > /dev/null 2>&1; then
    echo "✓ LPR Server connectivity: OK"
else
    echo "✗ LPR Server connectivity: Failed"
fi
```

### Log Monitoring

```bash
# Monitor health logs
tail -f /var/log/tailscale-health.log

# Monitor systemd logs
sudo journalctl -u tailscaled -f

# Monitor cron logs
tail -f /var/log/cron
```

## References

- [Tailscale Documentation](https://tailscale.com/kb/)
- [ACLs Reference](https://tailscale.com/kb/1068/acl-tags/)
- [SSH Configuration](https://tailscale.com/kb/1193/tailscale-ssh/)
- [Troubleshooting Guide](https://tailscale.com/kb/1019/troubleshooting/)

---

**Note:** เอกสารนี้จะได้รับการอัปเดตเมื่อมีการเปลี่ยนแปลงในระบบหรือ Tailscale configuration
