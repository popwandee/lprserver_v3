#!/usr/bin/env python3
"""
Database Schema Update Script for AI Camera v1.3

This script updates the database schema to support WebSocket sender functionality
by adding missing columns and tables.

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from v1_3.src.core.config import DATABASE_PATH

def update_database_schema():
    """Update database schema for WebSocket sender support."""
    
    print("🔧 Updating database schema for WebSocket sender support...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print(f"📁 Database: {DATABASE_PATH}")
        
        # Check if sent_to_server column exists in detection_results
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'sent_to_server' not in columns:
            print("➕ Adding sent_to_server column to detection_results table...")
            cursor.execute("ALTER TABLE detection_results ADD COLUMN sent_to_server BOOLEAN DEFAULT 0")
            cursor.execute("ALTER TABLE detection_results ADD COLUMN sent_at DATETIME")
            cursor.execute("ALTER TABLE detection_results ADD COLUMN server_response TEXT")
            print("✅ Added sent_to_server columns to detection_results")
        else:
            print("✅ sent_to_server column already exists in detection_results")
        
        # Check if sent_to_server column exists in health_checks
        cursor.execute("PRAGMA table_info(health_checks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'sent_to_server' not in columns:
            print("➕ Adding sent_to_server column to health_checks table...")
            cursor.execute("ALTER TABLE health_checks ADD COLUMN sent_to_server BOOLEAN DEFAULT 0")
            cursor.execute("ALTER TABLE health_checks ADD COLUMN sent_at DATETIME")
            cursor.execute("ALTER TABLE health_checks ADD COLUMN server_response TEXT")
            print("✅ Added sent_to_server columns to health_checks")
        else:
            print("✅ sent_to_server column already exists in health_checks")
        
        # Create websocket_sender_logs table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS websocket_sender_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                data_type TEXT,
                record_count INTEGER DEFAULT 0,
                server_response TEXT,
                aicamera_id TEXT,
                checkpoint_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ websocket_sender_logs table created/verified")
        
        # Add AI Camera ID and Checkpoint ID columns if they don't exist
        cursor.execute("PRAGMA table_info(websocket_sender_logs)")
        websocket_columns = [col[1] for col in cursor.fetchall()]
        
        if 'aicamera_id' not in websocket_columns:
            print("➕ Adding aicamera_id column to websocket_sender_logs table...")
            cursor.execute("ALTER TABLE websocket_sender_logs ADD COLUMN aicamera_id TEXT")
            print("✅ Added aicamera_id column to websocket_sender_logs")
        
        if 'checkpoint_id' not in websocket_columns:
            print("➕ Adding checkpoint_id column to websocket_sender_logs table...")
            cursor.execute("ALTER TABLE websocket_sender_logs ADD COLUMN checkpoint_id TEXT")
            print("✅ Added checkpoint_id column to websocket_sender_logs")
        
        # Create indexes for better performance
        print("🔍 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_detection_sent_to_server ON detection_results(sent_to_server)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_health_sent_to_server ON health_checks(sent_to_server)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_websocket_logs_timestamp ON websocket_sender_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_websocket_logs_action ON websocket_sender_logs(action)")
        print("✅ Indexes created/verified")
        
        # Commit changes
        conn.commit()
        
        # Verify the updates
        print("\n🔍 Verifying database schema...")
        
        # Check detection_results schema
        cursor.execute("PRAGMA table_info(detection_results)")
        detection_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 detection_results columns: {detection_columns}")
        
        # Check health_checks schema
        cursor.execute("PRAGMA table_info(health_checks)")
        health_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 health_checks columns: {health_columns}")
        
        # Check websocket_sender_logs schema
        cursor.execute("PRAGMA table_info(websocket_sender_logs)")
        websocket_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 websocket_sender_logs columns: {websocket_columns}")
        
        # Check table counts
        cursor.execute("SELECT COUNT(*) FROM detection_results")
        detection_count = cursor.fetchone()[0]
        print(f"📊 detection_results count: {detection_count}")
        
        cursor.execute("SELECT COUNT(*) FROM health_checks")
        health_count = cursor.fetchone()[0]
        print(f"📊 health_checks count: {health_count}")
        
        cursor.execute("SELECT COUNT(*) FROM websocket_sender_logs")
        websocket_count = cursor.fetchone()[0]
        print(f"📊 websocket_sender_logs count: {websocket_count}")
        
        conn.close()
        
        print("\n✅ Database schema update completed successfully!")
        print("🚀 WebSocket sender functionality is now ready to use.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🔧 AI Camera v1.3 - Database Schema Update")
    print("=" * 60)
    
    if update_database_schema():
        print("\n🎉 Database update completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Database update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
