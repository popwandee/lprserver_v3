# Tailscale ACLs Reference Guide

**Version:** 1.0.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Category:** Networking & Security  
**Status:** Active

## Table of Contents

1. [Overview](#overview)
2. [ACLs Structure](#acls-structure)
3. [Tags and Groups](#tags-and-groups)
4. [SSH Configuration](#ssh-configuration)
5. [Hosts Mapping](#hosts-mapping)
6. [Examples](#examples)
7. [Best Practices](#best-practices)

## Overview

Tailscale ACLs (Access Control Lists) ใช้สำหรับควบคุมการเข้าถึงระหว่าง devices ใน Tailscale network

### Key Concepts
- **Tags:** สำหรับ categorizing devices
- **Groups:** สำหรับ grouping users
- **Hosts:** สำหรับ mapping hostnames to IPs
- **SSH:** สำหรับ controlling SSH access

## ACLs Structure

### Basic Structure
```json
{
  "tagOwners": {},
  "groups": {},
  "acls": [],
  "ssh": [],
  "hosts": {}
}
```

### Required Sections
- `tagOwners`: กำหนดใครสามารถ assign tags ได้
- `acls`: กำหนด network access rules
- `ssh`: กำหนด SSH access rules (optional)
- `hosts`: กำหนด hostname mapping (optional)
- `groups`: กำหนด user groups (optional)

## Tags and Groups

### TagOwners
```json
{
  "tagOwners": {
    "tag:edge": ["email@gmail.com"],
    "tag:server": ["email@gmail.com"],
    "tag:dev": ["email@gmail.com"]
  }
}
```

### Groups
```json
{
  "groups": {
    "group:ai-camera-team": ["email1@gmail.com", "email2@gmail.com"],
    "group:admins": ["admin@gmail.com"],
    "group:developers": ["dev1@gmail.com", "dev2@gmail.com"]
  }
}
```

## ACLs Rules

### Basic ACL Rule
```json
{
  "action": "accept",
  "src": ["tag:edge"],
  "dst": ["tag:server:*"]
}
```

### ACL Rule with Ports
```json
{
  "action": "accept",
  "src": ["tag:dev"],
  "dst": ["tag:server:5000", "tag:server:8000"]
}
```

### ACL Rule with Rate Limiting
```json
{
  "action": "accept",
  "src": ["tag:edge"],
  "dst": ["tag:server:*"],
  "rate": "1000/min"
}
```

### Actions Available
- `accept`: อนุญาตการเชื่อมต่อ
- `reject`: ปฏิเสธการเชื่อมต่อ
- `drop`: ละทิ้งการเชื่อมต่อ (ไม่ส่ง response)

## SSH Configuration

### Basic SSH Rule
```json
{
  "action": "accept",
  "src": ["tag:dev"],
  "dst": ["aicamera1:22"],
  "users": ["camuser"]
}
```

### SSH Rule with Multiple Users
```json
{
  "action": "accept",
  "src": ["group:developers"],
  "dst": ["aicamera1:22", "lprserver:22"],
  "users": ["camuser", "ubuntu", "root"]
}
```

### SSH Rule with Groups
```json
{
  "action": "accept",
  "src": ["group:admins"],
  "dst": ["*:22"],
  "users": ["*"]
}
```

## Hosts Mapping

### Basic Hosts Mapping
```json
{
  "hosts": {
    "aicamera1": "100.64.0.1",
    "lprserver": "100.64.0.2",
    "dev-windows": "100.64.0.3"
  }
}
```

### Hosts with Comments
```json
{
  "hosts": {
    "aicamera1": "100.64.0.1",      // Edge device
    "lprserver": "100.64.0.2",       // LPR server
    "dev-windows": "100.64.0.3",     // Windows dev machine
    "dev-mac": "100.64.0.4",         // macOS dev machine
    "dev-linux": "100.64.0.5"        // Linux dev machine
  }
}
```

## Examples

### Example 1: Basic Edge-Server Communication
```json
{
  "tagOwners": {
    "tag:edge": ["email@gmail.com"],
    "tag:server": ["email@gmail.com"]
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
    }
  ]
}
```

### Example 2: Multi-Environment Setup
```json
{
  "tagOwners": {
    "tag:edge": ["email@gmail.com"],
    "tag:server": ["email@gmail.com"],
    "tag:dev": ["email@gmail.com"],
    "tag:prod": ["email@gmail.com"]
  },
  "groups": {
    "group:developers": ["dev1@gmail.com", "dev2@gmail.com"],
    "group:admins": ["admin@gmail.com"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:edge"],
      "dst": ["tag:server:*"]
    },
    {
      "action": "accept",
      "src": ["group:developers"],
      "dst": ["tag:dev:*", "tag:edge:*"]
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
      "src": ["group:developers"],
      "dst": ["tag:edge:22", "tag:dev:22"],
      "users": ["camuser", "ubuntu"]
    },
    {
      "action": "accept",
      "src": ["group:admins"],
      "dst": ["*:22"],
      "users": ["*"]
    }
  ]
}
```

### Example 3: Production Environment
```json
{
  "tagOwners": {
    "tag:edge": ["admin@gmail.com"],
    "tag:server": ["admin@gmail.com"],
    "tag:prod": ["admin@gmail.com"]
  },
  "groups": {
    "group:ai-camera-team": ["team1@gmail.com", "team2@gmail.com"],
    "group:ops": ["ops@gmail.com"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:edge"],
      "dst": ["tag:server:5000", "tag:server:8000"]
    },
    {
      "action": "accept",
      "src": ["tag:server"],
      "dst": ["tag:edge:*"]
    },
    {
      "action": "accept",
      "src": ["group:ai-camera-team"],
      "dst": ["tag:edge:*", "tag:server:*"]
    },
    {
      "action": "accept",
      "src": ["group:ops"],
      "dst": ["*:*"]
    }
  ],
  "ssh": [
    {
      "action": "accept",
      "src": ["group:ai-camera-team"],
      "dst": ["aicamera1:22", "lprserver:22"],
      "users": ["camuser", "ubuntu"]
    },
    {
      "action": "accept",
      "src": ["group:ops"],
      "dst": ["*:22"],
      "users": ["*"]
    }
  ],
  "hosts": {
    "aicamera1": "100.64.0.1",
    "lprserver": "100.64.0.2"
  }
}
```

## Best Practices

### 1. Security
- ใช้ least privilege principle
- จำกัดการเข้าถึงตามความจำเป็น
- ใช้ groups แทน individual users
- เปิดใช้งาน SSH access control

### 2. Organization
- ใช้ consistent naming convention
- แยก tags ตาม environment (dev, staging, prod)
- ใช้ groups สำหรับ team management
- เก็บ documentation ไว้เป็นปัจจุบัน

### 3. Maintenance
- ตรวจสอบ ACLs เป็นประจำ
- ลบ unused tags และ groups
- อัปเดต hostnames เมื่อมีการเปลี่ยนแปลง
- ใช้ version control สำหรับ ACLs

### 4. Troubleshooting
- ใช้ `tailscale status` เพื่อตรวจสอบ connectivity
- ตรวจสอบ logs เมื่อมีปัญหา
- ใช้ `tailscale ping` เพื่อทดสอบ connectivity
- ตรวจสอบ ACLs ใน admin console

## Common Patterns

### Pattern 1: Edge to Server Communication
```json
{
  "action": "accept",
  "src": ["tag:edge"],
  "dst": ["tag:server:*"]
}
```

### Pattern 2: Development Access
```json
{
  "action": "accept",
  "src": ["group:developers"],
  "dst": ["tag:dev:*", "tag:edge:*"]
}
```

### Pattern 3: Admin Access
```json
{
  "action": "accept",
  "src": ["group:admins"],
  "dst": ["*:*"]
}
```

### Pattern 4: Service-Specific Access
```json
{
  "action": "accept",
  "src": ["tag:edge"],
  "dst": ["tag:server:5000", "tag:server:8000"]
}
```

## Validation

### ACLs Validation Commands
```bash
# Validate ACLs syntax
tailscale status --json

# Test connectivity
tailscale ping <hostname>

# Check SSH access
tailscale ssh <hostname>
```

### Common Validation Errors
- `tag not found`: ตรวจสอบ tagOwners และ tags ที่ใช้
- `host not found`: ตรวจสอบ hosts mapping
- `permission denied`: ตรวจสอบ ACLs rules

## References

- [Tailscale ACLs Documentation](https://tailscale.com/kb/1068/acl-tags/)
- [SSH Configuration](https://tailscale.com/kb/1193/tailscale-ssh/)
- [ACLs Examples](https://tailscale.com/kb/1068/acl-tags/#examples)
- [Troubleshooting ACLs](https://tailscale.com/kb/1019/troubleshooting/)

---

**Note:** เอกสารนี้จะได้รับการอัปเดตเมื่อมีการเปลี่ยนแปลงใน Tailscale ACLs specification
