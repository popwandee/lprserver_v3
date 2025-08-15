-- LPR Server v3 Database Schema
-- PostgreSQL Database Schema for LPR Server v3
-- สร้างฐานข้อมูลสำหรับระบบ LPR Server v3

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLES
-- ============================================================================

-- Checkpoints table - จุดตรวจสอบต่างๆ ในระบบ
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
);

-- Cameras table - กล้อง AI ที่ติดตั้งในแต่ละจุด
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
);

-- Detections table - ข้อมูลการตรวจจับจาก AI Camera
CREATE TABLE IF NOT EXISTS detections (
    id SERIAL PRIMARY KEY,
    detection_id UUID UNIQUE DEFAULT uuid_generate_v4(),
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
);

-- Vehicles table - ข้อมูลรถที่ตรวจพบ
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
);

-- Plates table - ข้อมูลป้ายทะเบียนที่อ่านได้
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
);

-- Health logs table - ข้อมูลสุขภาพของกล้อง
CREATE TABLE IF NOT EXISTS health_logs (
    id SERIAL PRIMARY KEY,
    health_id UUID UNIQUE DEFAULT uuid_generate_v4(),
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
);

-- Blacklist table - รายชื่อป้ายทะเบียนที่ต้องเฝ้าระวัง
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
);

-- Analytics table - ข้อมูลสถิติและวิเคราะห์
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
);

-- System logs table - บันทึกการทำงานของระบบ
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
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Detections indexes
CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_detections_camera_id ON detections(camera_id);
CREATE INDEX IF NOT EXISTS idx_detections_checkpoint_id ON detections(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_detections_detection_type ON detections(detection_type);
CREATE INDEX IF NOT EXISTS idx_detections_created_at ON detections(created_at);

-- Plates indexes
CREATE INDEX IF NOT EXISTS idx_plates_plate_number ON plates(plate_number);
CREATE INDEX IF NOT EXISTS idx_plates_detection_id ON plates(detection_id);
CREATE INDEX IF NOT EXISTS idx_plates_confidence ON plates(confidence);
CREATE INDEX IF NOT EXISTS idx_plates_timestamp ON plates(created_at);
CREATE INDEX IF NOT EXISTS idx_plates_country ON plates(country);

-- Vehicles indexes
CREATE INDEX IF NOT EXISTS idx_vehicles_detection_id ON vehicles(detection_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_vehicle_class ON vehicles(vehicle_class);
CREATE INDEX IF NOT EXISTS idx_vehicles_confidence ON vehicles(confidence);
CREATE INDEX IF NOT EXISTS idx_vehicles_brand ON vehicles(brand);

-- Health logs indexes
CREATE INDEX IF NOT EXISTS idx_health_logs_timestamp ON health_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_health_logs_camera_id ON health_logs(camera_id);
CREATE INDEX IF NOT EXISTS idx_health_logs_status ON health_logs(status);
CREATE INDEX IF NOT EXISTS idx_health_logs_component ON health_logs(component);

-- Analytics indexes
CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date);
CREATE INDEX IF NOT EXISTS idx_analytics_checkpoint_id ON analytics(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_analytics_camera_id ON analytics(camera_id);

-- System logs indexes
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_component ON system_logs(component);

-- Blacklist indexes
CREATE INDEX IF NOT EXISTS idx_blacklist_plate_number ON blacklist(plate_number);
CREATE INDEX IF NOT EXISTS idx_blacklist_is_active ON blacklist(is_active);
CREATE INDEX IF NOT EXISTS idx_blacklist_alert_level ON blacklist(alert_level);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Daily statistics view
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
ORDER BY date DESC, checkpoint_id, camera_id;

-- Recent detections view
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
ORDER BY d.timestamp DESC;

-- Camera health view
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
ORDER BY c.checkpoint_id, c.camera_id;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_checkpoints_updated_at BEFORE UPDATE ON checkpoints FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cameras_updated_at BEFORE UPDATE ON cameras FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_blacklist_updated_at BEFORE UPDATE ON blacklist FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analytics_updated_at BEFORE UPDATE ON analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log system events
CREATE OR REPLACE FUNCTION log_system_event(
    p_level VARCHAR(10),
    p_component VARCHAR(50),
    p_message TEXT,
    p_details JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id VARCHAR(100) DEFAULT NULL,
    p_request_id VARCHAR(100) DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO system_logs (level, component, message, details, ip_address, user_agent, session_id, request_id)
    VALUES (p_level, p_component, p_message, p_details, p_ip_address, p_user_agent, p_session_id, p_request_id);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample checkpoints
INSERT INTO checkpoints (checkpoint_id, name, location, latitude, longitude, description) VALUES 
('CP001', 'Checkpoint A - Main Gate', 'Main Entrance', 13.7563, 100.5018, 'Main gate checkpoint'),
('CP002', 'Checkpoint B - Parking', 'Parking Area', 13.7565, 100.5020, 'Parking area checkpoint'),
('CP003', 'Checkpoint C - Exit', 'Exit Gate', 13.7567, 100.5022, 'Exit gate checkpoint')
ON CONFLICT (checkpoint_id) DO NOTHING;

-- Insert sample cameras
INSERT INTO cameras (camera_id, checkpoint_id, name, model, ip_address, status) VALUES 
('CAM001', 'CP001', 'Camera A1', 'Hikvision DS-2CD2347G2-LU', '192.168.1.100', 'active'),
('CAM002', 'CP001', 'Camera A2', 'Hikvision DS-2CD2347G2-LU', '192.168.1.101', 'active'),
('CAM003', 'CP002', 'Camera B1', 'Dahua IPC-HFW4431R-ZE', '192.168.1.102', 'active'),
('CAM004', 'CP003', 'Camera C1', 'Dahua IPC-HFW4431R-ZE', '192.168.1.103', 'active')
ON CONFLICT (camera_id) DO NOTHING;

-- Insert sample blacklist
INSERT INTO blacklist (plate_number, reason, alert_level, created_by) VALUES 
('ABC1234', 'Stolen vehicle', 'high', 'admin'),
('XYZ7890', 'Wanted person', 'medium', 'admin'),
('DEF5678', 'Expired registration', 'low', 'system')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE checkpoints IS 'จุดตรวจสอบต่างๆ ในระบบ LPR';
COMMENT ON TABLE cameras IS 'กล้อง AI ที่ติดตั้งในแต่ละจุดตรวจสอบ';
COMMENT ON TABLE detections IS 'ข้อมูลการตรวจจับจาก AI Camera';
COMMENT ON TABLE vehicles IS 'ข้อมูลรถที่ตรวจพบในแต่ละการตรวจจับ';
COMMENT ON TABLE plates IS 'ข้อมูลป้ายทะเบียนที่อ่านได้จากรถ';
COMMENT ON TABLE health_logs IS 'ข้อมูลสุขภาพของกล้อง AI';
COMMENT ON TABLE blacklist IS 'รายชื่อป้ายทะเบียนที่ต้องเฝ้าระวัง';
COMMENT ON TABLE analytics IS 'ข้อมูลสถิติและวิเคราะห์รายวัน';
COMMENT ON TABLE system_logs IS 'บันทึกการทำงานของระบบ';

COMMENT ON VIEW daily_statistics IS 'สถิติรายวันของแต่ละจุดตรวจสอบ';
COMMENT ON VIEW recent_detections IS 'การตรวจจับล่าสุดพร้อมข้อมูลป้ายทะเบียน';
COMMENT ON VIEW camera_health IS 'สถานะสุขภาพของกล้องทั้งหมด';


