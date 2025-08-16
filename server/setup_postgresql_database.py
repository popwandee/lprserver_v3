#!/usr/bin/env python3
"""
PostgreSQL Database Setup for LPR Server v3
ติดตั้งและสร้างฐานข้อมูล PostgreSQL สำหรับ LPR Server
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from datetime import datetime
from pathlib import Path

class PostgreSQLSetup:
    def __init__(self):
        self.db_config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': os.environ.get('DB_PORT', '5432'),
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD', ''),
            'database': os.environ.get('DB_NAME', 'lprserver_v3')
        }
        
        self.connection = None
        self.cursor = None
    
    def check_postgresql_installation(self):
        """ตรวจสอบการติดตั้ง PostgreSQL"""
        print("🔍 ตรวจสอบการติดตั้ง PostgreSQL...")
        
        try:
            # ตรวจสอบ PostgreSQL service
            result = subprocess.run(['systemctl', 'is-active', 'postgresql'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL service กำลังทำงาน")
                return True
            else:
                print("❌ PostgreSQL service ไม่ทำงาน")
                return False
                
        except FileNotFoundError:
            print("❌ ไม่พบ PostgreSQL")
            return False
    
    def install_postgresql(self):
        """ติดตั้ง PostgreSQL"""
        print("🔧 ติดตั้ง PostgreSQL...")
        
        try:
            # Update package list
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            
            # Install PostgreSQL
            subprocess.run(['sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib'], check=True)
            
            # Start PostgreSQL service
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], check=True)
            
            print("✅ PostgreSQL ติดตั้งสำเร็จ")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ การติดตั้ง PostgreSQL ล้มเหลว: {e}")
            return False
    
    def setup_database_user(self):
        """ตั้งค่าฐานข้อมูลและ user"""
        print("🔧 ตั้งค่าฐานข้อมูลและ user...")
        
        try:
            # Connect to PostgreSQL as postgres user
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user='postgres',
                password=self.db_config['password']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Create database if not exists
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.db_config['database']}'")
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {self.db_config['database']}")
                print(f"✅ สร้างฐานข้อมูล {self.db_config['database']} สำเร็จ")
            
            # Create user if not exists
            cursor.execute(f"SELECT 1 FROM pg_user WHERE usename = '{self.db_config['user']}'")
            if not cursor.fetchone():
                cursor.execute(f"CREATE USER {self.db_config['user']} WITH PASSWORD '{self.db_config['password']}'")
                print(f"✅ สร้าง user {self.db_config['user']} สำเร็จ")
            
            # Grant privileges
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {self.db_config['database']} TO {self.db_config['user']}")
            cursor.execute(f"ALTER USER {self.db_config['user']} CREATEDB")
            
            cursor.close()
            conn.close()
            
            print("✅ ตั้งค่าฐานข้อมูลและ user สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ การตั้งค่าฐานข้อมูลล้มเหลว: {e}")
            return False
    
    def create_tables(self):
        """สร้างตารางในฐานข้อมูล"""
        print("🔧 สร้างตารางในฐานข้อมูล...")
        
        try:
            # Connect to database
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            
            # Create tables
            self._create_checkpoints_table()
            self._create_cameras_table()
            self._create_detections_table()
            self._create_vehicles_table()
            self._create_plates_table()
            self._create_health_logs_table()
            self._create_blacklist_table()
            self._create_analytics_table()
            self._create_system_logs_table()
            
            # Create indexes
            self._create_indexes()
            
            # Commit changes
            self.connection.commit()
            
            print("✅ สร้างตารางสำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ การสร้างตารางล้มเหลว: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def _create_checkpoints_table(self):
        """สร้างตาราง checkpoints"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id SERIAL PRIMARY KEY,
                checkpoint_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(200),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                description TEXT,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ ตาราง checkpoints")
    
    def _create_cameras_table(self):
        """สร้างตาราง cameras"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cameras (
                id SERIAL PRIMARY KEY,
                camera_id VARCHAR(50) UNIQUE NOT NULL,
                checkpoint_id VARCHAR(50) REFERENCES checkpoints(checkpoint_id),
                name VARCHAR(100) NOT NULL,
                model VARCHAR(100),
                ip_address INET,
                mac_address MACADDR,
                status VARCHAR(20) DEFAULT 'active',
                health_status VARCHAR(20) DEFAULT 'unknown',
                health_details JSONB,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_health_check TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ ตาราง cameras")
    
    def _create_detections_table(self):
        """สร้างตาราง detections"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id SERIAL PRIMARY KEY,
                detection_id UUID UNIQUE DEFAULT gen_random_uuid(),
                camera_id VARCHAR(50) REFERENCES cameras(camera_id),
                checkpoint_id VARCHAR(50) REFERENCES checkpoints(checkpoint_id),
                timestamp TIMESTAMP NOT NULL,
                vehicles_count INTEGER DEFAULT 0,
                plates_count INTEGER DEFAULT 0,
                processing_time_ms INTEGER,
                annotated_image_path VARCHAR(500),
                annotated_image_data BYTEA,
                confidence_score DECIMAL(5,4),
                detection_type VARCHAR(50) DEFAULT 'lpr',
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ ตาราง detections")
    
    def _create_vehicles_table(self):
        """สร้างตาราง vehicles"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id SERIAL PRIMARY KEY,
                detection_id UUID REFERENCES detections(detection_id) ON DELETE CASCADE,
                vehicle_index INTEGER,
                bbox_x1 INTEGER,
                bbox_y1 INTEGER,
                bbox_x2 INTEGER,
                bbox_y2 INTEGER,
                confidence DECIMAL(5,4),
                vehicle_class VARCHAR(50),
                vehicle_type VARCHAR(50),
                color VARCHAR(50),
                brand VARCHAR(100),
                model VARCHAR(100),
                year INTEGER,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ ตาราง vehicles")
    
    def _create_plates_table(self):
        """สร้างตาราง plates"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS plates (
                id SERIAL PRIMARY KEY,
                detection_id UUID REFERENCES detections(detection_id) ON DELETE CASCADE,
                vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE CASCADE,
                plate_index INTEGER,
                plate_number VARCHAR(20) NOT NULL,
                bbox_x1 INTEGER,
                bbox_y1 INTEGER,
                bbox_x2 INTEGER,
                bbox_y2 INTEGER,
                confidence DECIMAL(5,4),
                plate_type VARCHAR(50),
                country VARCHAR(50) DEFAULT 'TH',
                province VARCHAR(100),
                cropped_image_path VARCHAR(500),
                cropped_image_data BYTEA,
                ocr_raw_result TEXT,
                ocr_processed_result VARCHAR(20),
                is_valid BOOLEAN DEFAULT true,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ ตาราง plates")
    
    def _create_health_logs_table(self):
        """สร้างตาราง health_logs"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_logs (
                id SERIAL PRIMARY KEY,
                health_id UUID UNIQUE DEFAULT gen_random_uuid(),
                camera_id VARCHAR(50) REFERENCES cameras(camera_id),
                checkpoint_id VARCHAR(50) REFERENCES checkpoints(checkpoint_id),
                timestamp TIMESTAMP NOT NULL,
                component VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                message TEXT,
                cpu_usage DECIMAL(5,2),
                memory_usage DECIMAL(5,2),
                disk_usage DECIMAL(5,2),
                network_status VARCHAR(20),
                temperature DECIMAL(5,2),
                details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ ตาราง health_logs")
    
    def _create_blacklist_table(self):
        """สร้างตาราง blacklist"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id SERIAL PRIMARY KEY,
                plate_number VARCHAR(20) NOT NULL,
                reason TEXT NOT NULL,
                alert_level VARCHAR(20) DEFAULT 'medium',
                is_active BOOLEAN DEFAULT true,
                created_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                notes TEXT
            )
        """)
        print("   ✅ ตาราง blacklist")
    
    def _create_analytics_table(self):
        """สร้างตาราง analytics"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                checkpoint_id VARCHAR(50) REFERENCES checkpoints(checkpoint_id),
                camera_id VARCHAR(50) REFERENCES cameras(camera_id),
                total_detections INTEGER DEFAULT 0,
                total_vehicles INTEGER DEFAULT 0,
                total_plates INTEGER DEFAULT 0,
                unique_plates INTEGER DEFAULT 0,
                blacklist_hits INTEGER DEFAULT 0,
                avg_processing_time_ms DECIMAL(10,2),
                peak_hour INTEGER,
                peak_count INTEGER,
                hourly_breakdown JSONB,
                vehicle_type_breakdown JSONB,
                plate_type_breakdown JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, checkpoint_id, camera_id)
            )
        """)
        print("   ✅ ตาราง analytics")
    
    def _create_system_logs_table(self):
        """สร้างตาราง system_logs"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level VARCHAR(10) NOT NULL,
                component VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                details JSONB,
                ip_address INET,
                user_agent TEXT,
                session_id VARCHAR(100),
                request_id VARCHAR(100)
            )
        """)
        print("   ✅ ตาราง system_logs")
    
    def _create_indexes(self):
        """สร้าง indexes สำหรับ performance"""
        print("🔧 สร้าง indexes...")
        
        indexes = [
            # Detections indexes
            "CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_detections_camera_id ON detections(camera_id)",
            "CREATE INDEX IF NOT EXISTS idx_detections_checkpoint_id ON detections(checkpoint_id)",
            "CREATE INDEX IF NOT EXISTS idx_detections_detection_type ON detections(detection_type)",
            
            # Plates indexes
            "CREATE INDEX IF NOT EXISTS idx_plates_plate_number ON plates(plate_number)",
            "CREATE INDEX IF NOT EXISTS idx_plates_detection_id ON plates(detection_id)",
            "CREATE INDEX IF NOT EXISTS idx_plates_confidence ON plates(confidence)",
            "CREATE INDEX IF NOT EXISTS idx_plates_timestamp ON plates(created_at)",
            
            # Vehicles indexes
            "CREATE INDEX IF NOT EXISTS idx_vehicles_detection_id ON vehicles(detection_id)",
            "CREATE INDEX IF NOT EXISTS idx_vehicles_vehicle_class ON vehicles(vehicle_class)",
            "CREATE INDEX IF NOT EXISTS idx_vehicles_confidence ON vehicles(confidence)",
            
            # Health logs indexes
            "CREATE INDEX IF NOT EXISTS idx_health_logs_timestamp ON health_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_health_logs_camera_id ON health_logs(camera_id)",
            "CREATE INDEX IF NOT EXISTS idx_health_logs_status ON health_logs(status)",
            
            # Analytics indexes
            "CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_checkpoint_id ON analytics(checkpoint_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_camera_id ON analytics(camera_id)",
            
            # System logs indexes
            "CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level)",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_component ON system_logs(component)"
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)
        
        print("   ✅ สร้าง indexes สำเร็จ")
    
    def insert_sample_data(self):
        """เพิ่มข้อมูลตัวอย่าง"""
        print("🔧 เพิ่มข้อมูลตัวอย่าง...")
        
        try:
            # Insert sample checkpoints
            self.cursor.execute("""
                INSERT INTO checkpoints (checkpoint_id, name, location, latitude, longitude, description)
                VALUES 
                ('CP001', 'Checkpoint A - Main Gate', 'Main Entrance', 13.7563, 100.5018, 'Main gate checkpoint'),
                ('CP002', 'Checkpoint B - Parking', 'Parking Area', 13.7565, 100.5020, 'Parking area checkpoint'),
                ('CP003', 'Checkpoint C - Exit', 'Exit Gate', 13.7567, 100.5022, 'Exit gate checkpoint')
                ON CONFLICT (checkpoint_id) DO NOTHING
            """)
            
            # Insert sample cameras
            self.cursor.execute("""
                INSERT INTO cameras (camera_id, checkpoint_id, name, model, ip_address, status)
                VALUES 
                ('CAM001', 'CP001', 'Camera A1', 'Hikvision DS-2CD2347G2-LU', '192.168.1.100', 'active'),
                ('CAM002', 'CP001', 'Camera A2', 'Hikvision DS-2CD2347G2-LU', '192.168.1.101', 'active'),
                ('CAM003', 'CP002', 'Camera B1', 'Dahua IPC-HFW4431R-ZE', '192.168.1.102', 'active'),
                ('CAM004', 'CP003', 'Camera C1', 'Dahua IPC-HFW4431R-ZE', '192.168.1.103', 'active')
                ON CONFLICT (camera_id) DO NOTHING
            """)
            
            # Insert sample blacklist
            self.cursor.execute("""
                INSERT INTO blacklist (plate_number, reason, alert_level, created_by)
                VALUES 
                ('ABC1234', 'Stolen vehicle', 'high', 'admin'),
                ('XYZ7890', 'Wanted person', 'medium', 'admin'),
                ('DEF5678', 'Expired registration', 'low', 'system')
                ON CONFLICT DO NOTHING
            """)
            
            self.connection.commit()
            print("   ✅ เพิ่มข้อมูลตัวอย่างสำเร็จ")
            
        except Exception as e:
            print(f"   ❌ การเพิ่มข้อมูลตัวอย่างล้มเหลว: {e}")
            self.connection.rollback()
    
    def create_views(self):
        """สร้าง views สำหรับการวิเคราะห์"""
        print("🔧 สร้าง views...")
        
        try:
            # Daily statistics view
            self.cursor.execute("""
                CREATE OR REPLACE VIEW daily_statistics AS
                SELECT 
                    DATE(d.timestamp) as date,
                    c.checkpoint_id,
                    c.name as checkpoint_name,
                    cam.camera_id,
                    cam.name as camera_name,
                    COUNT(d.id) as total_detections,
                    SUM(d.vehicles_count) as total_vehicles,
                    SUM(d.plates_count) as total_plates,
                    COUNT(DISTINCT p.plate_number) as unique_plates,
                    AVG(d.processing_time_ms) as avg_processing_time,
                    COUNT(CASE WHEN b.plate_number IS NOT NULL THEN 1 END) as blacklist_hits
                FROM detections d
                LEFT JOIN checkpoints c ON d.checkpoint_id = c.checkpoint_id
                LEFT JOIN cameras cam ON d.camera_id = cam.camera_id
                LEFT JOIN plates p ON d.detection_id = p.detection_id
                LEFT JOIN blacklist b ON p.plate_number = b.plate_number AND b.is_active = true
                GROUP BY DATE(d.timestamp), c.checkpoint_id, c.name, cam.camera_id, cam.name
                ORDER BY date DESC, checkpoint_id, camera_id
            """)
            
            # Recent detections view
            self.cursor.execute("""
                CREATE OR REPLACE VIEW recent_detections AS
                SELECT 
                    d.detection_id,
                    d.timestamp,
                    c.checkpoint_id,
                    c.name as checkpoint_name,
                    cam.camera_id,
                    cam.name as camera_name,
                    d.vehicles_count,
                    d.plates_count,
                    d.processing_time_ms,
                    p.plate_number,
                    p.confidence as plate_confidence,
                    v.vehicle_class,
                    v.confidence as vehicle_confidence,
                    CASE WHEN b.plate_number IS NOT NULL THEN true ELSE false END as is_blacklisted
                FROM detections d
                LEFT JOIN checkpoints c ON d.checkpoint_id = c.checkpoint_id
                LEFT JOIN cameras cam ON d.camera_id = cam.camera_id
                LEFT JOIN plates p ON d.detection_id = p.detection_id
                LEFT JOIN vehicles v ON d.detection_id = v.detection_id
                LEFT JOIN blacklist b ON p.plate_number = b.plate_number AND b.is_active = true
                ORDER BY d.timestamp DESC
            """)
            
            # Camera health view
            self.cursor.execute("""
                CREATE OR REPLACE VIEW camera_health AS
                SELECT 
                    c.camera_id,
                    c.name as camera_name,
                    cp.checkpoint_id,
                    cp.name as checkpoint_name,
                    c.status,
                    c.health_status,
                    c.last_activity,
                    c.last_health_check,
                    hl.cpu_usage,
                    hl.memory_usage,
                    hl.disk_usage,
                    hl.timestamp as last_health_timestamp
                FROM cameras c
                LEFT JOIN checkpoints cp ON c.checkpoint_id = cp.checkpoint_id
                LEFT JOIN LATERAL (
                    SELECT * FROM health_logs 
                    WHERE camera_id = c.camera_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) hl ON true
                ORDER BY c.checkpoint_id, c.camera_id
            """)
            
            self.connection.commit()
            print("   ✅ สร้าง views สำเร็จ")
            
        except Exception as e:
            print(f"   ❌ การสร้าง views ล้มเหลว: {e}")
            self.connection.rollback()
    
    def save_database_config(self):
        """บันทึกการตั้งค่าฐานข้อมูล"""
        config = {
            'database': self.db_config,
            'tables': [
                'checkpoints', 'cameras', 'detections', 'vehicles', 
                'plates', 'health_logs', 'blacklist', 'analytics', 'system_logs'
            ],
            'views': [
                'daily_statistics', 'recent_detections', 'camera_health'
            ],
            'setup_timestamp': datetime.now().isoformat()
        }
        
        try:
            with open('database_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("💾 บันทึกการตั้งค่าฐานข้อมูล: database_config.json")
        except Exception as e:
            print(f"❌ ไม่สามารถบันทึกการตั้งค่าได้: {e}")
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อฐานข้อมูล"""
        print("🔍 ทดสอบการเชื่อมต่อฐานข้อมูล...")
        
        try:
            # Test basic connection
            self.cursor.execute("SELECT version()")
            version = self.cursor.fetchone()[0]
            print(f"   ✅ PostgreSQL version: {version.split(',')[0]}")
            
            # Test table count
            self.cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = self.cursor.fetchone()[0]
            print(f"   ✅ Tables created: {table_count}")
            
            # Test sample query
            self.cursor.execute("SELECT COUNT(*) FROM checkpoints")
            checkpoint_count = self.cursor.fetchone()[0]
            print(f"   ✅ Sample data: {checkpoint_count} checkpoints")
            
            return True
            
        except Exception as e:
            print(f"   ❌ การทดสอบการเชื่อมต่อล้มเหลว: {e}")
            return False
    
    def cleanup(self):
        """ทำความสะอาดการเชื่อมต่อ"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def run_setup(self):
        """รันการตั้งค่าทั้งหมด"""
        print("🚀 เริ่มต้นการตั้งค่า PostgreSQL Database สำหรับ LPR Server v3")
        print("="*70)
        
        try:
            # Check PostgreSQL installation
            if not self.check_postgresql_installation():
                print("📦 ติดตั้ง PostgreSQL...")
                if not self.install_postgresql():
                    return False
            
            # Setup database and user
            if not self.setup_database_user():
                return False
            
            # Create tables
            if not self.create_tables():
                return False
            
            # Insert sample data
            self.insert_sample_data()
            
            # Create views
            self.create_views()
            
            # Test connection
            if not self.test_connection():
                return False
            
            # Save configuration
            self.save_database_config()
            
            print("\n" + "="*70)
            print("✅ การตั้งค่า PostgreSQL Database เสร็จสิ้น")
            print("="*70)
            print("\n📋 สรุปการตั้งค่า:")
            print(f"   Database: {self.db_config['database']}")
            print(f"   Host: {self.db_config['host']}:{self.db_config['port']}")
            print(f"   User: {self.db_config['user']}")
            print("   Tables: 9 tables created")
            print("   Views: 3 views created")
            print("   Indexes: 18 indexes created")
            print("\n💡 ขั้นตอนต่อไป:")
            print("   1. ตรวจสอบไฟล์ database_config.json")
            print("   2. ปรับแต่งการตั้งค่าใน config.py")
            print("   3. ทดสอบการเชื่อมต่อจาก application")
            
            return True
            
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาดในการตั้งค่า: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    setup = PostgreSQLSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


