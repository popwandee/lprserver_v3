# PostgreSQL Quick Setup Guide for LPR Server v3

## 🚀 Quick Setup (5 minutes)

### 1. Install PostgreSQL
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Configure Authentication
```bash
# Edit PostgreSQL authentication configuration
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Change this line:
# local   all             all                                     peer
# To:
# local   all             all                                     md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Create Database and User
```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE lprserver_v3;
CREATE USER lpruser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE lprserver_v3 TO lpruser;
ALTER DATABASE lprserver_v3 OWNER TO lpruser;
GRANT CREATE ON SCHEMA public TO lpruser;
GRANT USAGE ON SCHEMA public TO lpruser;

# Exit psql
\q
```

### 4. Run Database Schema
```bash
# Run the database schema
psql -U lpruser -d lprserver_v3 -h localhost -f database_schema.sql
```

### 5. Update Configuration
```bash
# Update config.py with your password
# Change: postgresql://lpruser:your_new_secure_password@localhost:5432/lprserver_v3
```

### 6. Test Connection
```bash
# Test database connection
psql -U lpruser -d lprserver_v3 -h localhost -c "SELECT version();"
```

## 🔧 Troubleshooting

### Peer Authentication Failed
```bash
# Error: FATAL: Peer authentication failed for user "lpruser"
# Solution: Change authentication method in pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Change 'peer' to 'md5' for local connections
sudo systemctl restart postgresql
```

### Permission Denied
```bash
# Error: permission denied for schema public
# Solution: Grant proper permissions
sudo -u postgres psql -c "ALTER DATABASE lprserver_v3 OWNER TO lpruser;"
sudo -u postgres psql -c "GRANT CREATE ON SCHEMA public TO lpruser;"
```

## 📊 Database Structure

### Tables Created
- `checkpoints` - จุดตรวจสอบต่างๆ
- `cameras` - กล้อง AI
- `detections` - ข้อมูลการตรวจจับ
- `vehicles` - ข้อมูลรถ
- `plates` - ข้อมูลป้ายทะเบียน
- `health_logs` - ข้อมูลสุขภาพกล้อง
- `blacklist` - รายชื่อป้ายทะเบียนที่ต้องเฝ้าระวัง
- `analytics` - ข้อมูลสถิติ
- `system_logs` - บันทึกการทำงานระบบ

### Views Created
- `daily_statistics` - สถิติรายวัน
- `recent_detections` - การตรวจจับล่าสุด
- `camera_health` - สถานะสุขภาพกล้อง

## 🔒 Security Best Practices

1. **Use strong passwords** for database users
2. **Set up environment variables** for database credentials
3. **Restrict network access** if needed
4. **Regular password rotation**
5. **Use SSL connections** in production

## 📝 Environment Variables

```bash
# Add to your .env file or environment
export DATABASE_URL="postgresql://lpruser:your_password@localhost:5432/lprserver_v3"
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=lpruser
export DB_PASSWORD=your_password
export DB_NAME=lprserver_v3
```

## ✅ Verification

After setup, verify everything works:

```bash
# Check tables
psql -U lpruser -d lprserver_v3 -h localhost -c "\dt"

# Check views
psql -U lpruser -d lprserver_v3 -h localhost -c "\dv"

# Test Flask connection
python -c "from config import get_config; print('Database URI:', get_config().SQLALCHEMY_DATABASE_URI)"
```

---

**Note**: This guide assumes Ubuntu/Debian system. For other distributions, adjust package manager commands accordingly.
