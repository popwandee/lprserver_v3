import psutil
from datetime import datetime
import time
import os
import json
import edge_status.scripts.db_manager as db_manager
import websocket
import threading
import subprocess

# --- เซ็นเซอร์และความสามารถเฉพาะของ Pi ---
# สำหรับ CPU Temperature (ทดสอบกับ Raspberry Pi OS)
def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000.0
        return temp
    except FileNotFoundError:
        print("Warning: Could not read CPU temperature. /sys/class/thermal/thermal_zone0/temp not found.")
        return None
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return None

# ตรวจสอบสถานะกล้อง Camera Module 3
def check_camera_status():
    try:
        # วิธีที่ 1: ตรวจสอบผ่าน v4l2-ctl (ต้องติดตั้ง v4l-utils: sudo apt install v4l-utils)
        # ตรวจสอบว่ามีอุปกรณ์ video0 (มักจะเป็นกล้อง Pi)
        result = os.popen("v4l2-ctl --list-devices | grep -i 'camera'").read()
        if "camera" in result.lower() or "/dev/video0" in result.lower():
            return "OK"
        else:
            return "Not Detected"
    except Exception as e:
        print(f"Error checking camera status: {e}")
        return "Unknown"

# ตรวจสอบสถานะ Hailo-8 AI HAT (ตัวอย่าง - อาจต้องใช้ SDK ของ Hailo)
def check_hailo8_status():
    try:
        # นี่คือตัวอย่าง หากมี Hailo SDK คุณอาจจะรันคำสั่งเช่น:
        # result = os.popen("hailo-cli status").read()
        # if "Running" in result:
        #     return "OK"
        # else:
        #     return "Not Running"
        return "OK (Simulated)" # จำลองว่าใช้งานได้
    except Exception as e:
        print(f"Error checking Hailo-8 status: {e}")
        return "Unknown"

# ตรวจสอบสถานะการใช้ไฟฟ้า (จำลอง)
def check_power_status():
    # ในความเป็นจริง คุณอาจจะต้องใช้เซ็นเซอร์วัดแรงดัน/กระแส หรืออ่านจาก GPIO
    # สำหรับ Raspberry Pi มักจะบอกว่า undervoltage ผ่าน LED หรือ dmesg
    try:
        # ตรวจสอบ log kernel สำหรับ undervoltage (อาจจะต้องมีสิทธิ์ sudo)
        # result = os.popen("dmesg | grep -i 'voltage'").read()
        # if "undervoltage" in result.lower():
        #     return "Under-voltage detected"
        return "Stable (Simulated)"
    except Exception as e:
        print(f"Error checking power status: {e}")
        return "Unknown"

# --- ฟังก์ชันหลักในการตรวจสอบสถานะ ---
def get_pi_status():
    timestamp = datetime.now().isoformat()
    voltage = subprocess.check_output(["vcgencmd", "measure_volts"], text=True).strip()
    temperature_raw = subprocess.check_output(["vcgencmd", "measure_temp"], text=True).strip()
    cpu_status_raw = subprocess.check_output(["vcgencmd", "get_throttled"], text=True).strip()

    # Extract temperature value (e.g., "temp=45.0'C" -> 45.0)
    temperature = float(temperature_raw.split('=')[1].replace("'C", ""))

    # Extract the CPU status code from the output
    if "=" in cpu_status_raw:
        cpu_status_raw = cpu_status_raw.split("=")[1].strip()
    else:
        cpu_status_raw = "Unknown"

    # Map CPU status codes to human-readable messages
    cpu_status_map = {
        "0x0": "OK",
        "0x1": "Throttled",
        "0x2": "Under-voltage",
        "0x4": "Over-temperature",
        "0x8": "Under-voltage and Throttled",
        "0x10": "Under-voltage and Over-temperature",
        "0x20": "Throttled and Over-temperature",
        "0x40": "Under-voltage, Throttled, and Over-temperature",
        "0x80": "Under-voltage, Throttled, Over-temperature, and Under-voltage",
    }

    # Get human-readable CPU status or default to "Unknown"
    cpu_status = cpu_status_map.get(cpu_status_raw, "Unknown")
    # CPU
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_temp = get_cpu_temperature()

    # RAM
    ram = psutil.virtual_memory()
    ram_total_mb = ram.total / (1024 * 1024)
    ram_used_mb = ram.used / (1024 * 1024)
    ram_percent = ram.percent

    # HDD/Disk
    disk = psutil.disk_usage('/')
    hdd_total_gb = disk.total / (1024 * 1024 * 1024)
    hdd_used_gb = disk.used / (1024 * 1024 * 1024)
    hdd_percent = disk.percent

    # Camera
    camera_status = check_camera_status()

    # Hailo-8 AI HAT
    hailo8_status = check_hailo8_status()

    # Power Status
    power_status = check_power_status()

    # Overall Status (ตัวอย่างการกำหนดสถานะโดยรวม)
    overall_status = "Normal"
    if cpu_usage > 80 or (cpu_temp is not None and cpu_temp > 75):
        overall_status = "High Load/Hot"
    elif ram_percent > 90 or hdd_percent > 90:
        overall_status = "Resource Critical"
    elif "Not Detected" in camera_status or  "Under-voltage" in power_status:
        overall_status = "Hardware Issue"

    status_data = {
        'timestamp': timestamp,
        'cpu_usage': cpu_usage,
        'cpu_temp': cpu_temp,
        'ram_total': round(ram_total_mb, 2),
        'ram_used': round(ram_used_mb, 2),
        'ram_percent': ram_percent,
        'hdd_total': round(hdd_total_gb, 2),
        'hdd_used': round(hdd_used_gb, 2),
        'hdd_percent': hdd_percent,
        'camera_status': camera_status,
        'power_status': power_status,
        'overall_status': overall_status
    }
    return status_data

def get_system_start_time():
    """ดึงเวลาที่ระบบเริ่มต้นทำงาน (System Start Time) 
    Get the system start time using 'uptime -s'.

    ใช้คำสั่ง 'uptime -s' เพื่อดึงเวลาที่ระบบเริ่มต้นทำงาน และแปลงเป็น timestamp

    Returns:
        tuple: 
            - start_datetime (datetime): เวลาที่ระบบเริ่มต้นในรูปแบบ datetime
            - start_time (float): เวลาที่ระบบเริ่มต้นในรูปแบบ timestamp
    """
    start_datetime_str = subprocess.check_output(["uptime", "-s"], text=True).strip()
    start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
    return start_datetime, time.mktime(start_datetime.timetuple())
def calculate_elapsed_time(start_time):
    """คำนวณเวลาที่ผ่านไปตั้งแต่ระบบเริ่มต้นทำงาน 
    Calculate elapsed time since the system started.
    Args:
        start_time (float): เวลาที่ระบบเริ่มต้นในรูปแบบ timestamp

    Returns:
        tuple:
            - elapsed_days (int): จำนวนวันที่ผ่านไป
            - elapsed_hours (int): จำนวนชั่วโมงที่ผ่านไป
            - elapsed_minutes (int): จำนวนนาทีที่ผ่านไป
            - elapsed_seconds (int): จำนวนวินาทีที่ผ่านไป
    """
    elapsed_time = int(time.time() - start_time)
    elapsed_days = elapsed_time // (24 * 3600)
    elapsed_time %= (24 * 3600)
    elapsed_hours = elapsed_time // 3600
    elapsed_time %= 3600
    elapsed_minutes = elapsed_time // 60
    elapsed_seconds = elapsed_time % 60
    return elapsed_days, elapsed_hours, elapsed_minutes, elapsed_seconds
def get_current_datetime():
    """ดึงเวลาปัจจุบันในรูปแบบ string 
    Get the current date and time.
    Returns:
        str: เวลาปัจจุบันในรูปแบบ 'YYYY-MM-DD HH:MM:SS'
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_uptime():
    """ดึงข้อมูล uptime ของระบบ 
    Execute the 'uptime -p' command to get the system uptime.
    ใช้คำสั่ง 'uptime -p' เพื่อดึงข้อมูล uptime

    Returns:
        str: ข้อมูล uptime ในรูปแบบ human-readable
    """
    return subprocess.check_output(["uptime", "-p"], text=True).strip()
# --- WebSocket Client ---
WEBSOCKET_SERVER_URL = "ws://localhost:8765" # เปลี่ยนเป็น URL ของ WebSocket Server ของคุณ

def send_data_via_websocket(data):
    try:
        ws = websocket.create_connection(WEBSOCKET_SERVER_URL)
        ws.send(json.dumps(data))
        ws.close()
        return True
    except ConnectionRefusedError:
        print(f"WebSocket connection refused. Server not running at {WEBSOCKET_SERVER_URL}?")
        return False
    except Exception as e:
        print(f"Error sending data via WebSocket: {e}")
        return False

def check_and_send_unsent_data():
    while True:
        unsent_rows = db_manager.get_unsent_data()
        if unsent_rows:
            print(f"Found {len(unsent_rows)} unsent data entries. Attempting to send...")
            sent_ids = []
            for row in unsent_rows:
                # แปลง tuple จาก SQLite เป็น dictionary เพื่อความสะดวกในการส่ง
                # (id, timestamp, cpu_usage, cpu_temp, ..., sent_to_server)
                data_to_send = {
                    'id': row[0],
                    'timestamp': row[1],
                    'cpu_usage': row[2],
                    'cpu_temp': row[3],
                    'ram_total': row[4],
                    'ram_used': row[5],
                    'ram_percent': row[6],
                    'hdd_total': row[7],
                    'hdd_used': row[8],
                    'hdd_percent': row[9],
                    'camera_status': row[10],
                    'power_status': row[11],
                    'overall_status': row[12]
                }
                if send_data_via_websocket(data_to_send):
                    sent_ids.append(row[0])
                else:
                    print(f"Failed to send data for ID: {row[0]}. Will retry later.")
                    break # หยุดส่งหากส่งไม่ได้ เพื่อไม่ให้เกิดปัญหาต่อเนื่อง
            if sent_ids:
                db_manager.mark_as_sent(sent_ids)
                print(f"Marked {len(sent_ids)} entries as sent.")
        else:
            print("No unsent data found in SQLite.")
        time.sleep(10) # ตรวจสอบทุก 10 วินาทีว่ามีข้อมูลที่ยังไม่ส่งหรือไม่

# --- Main loop ---
def main():
    db_manager.init_db() # ตรวจสอบและสร้างฐานข้อมูลหากยังไม่มี

    # เริ่ม thread สำหรับตรวจสอบและส่งข้อมูลที่ยังไม่ส่ง
    #websocket_sender_thread = threading.Thread(target=check_and_send_unsent_data, daemon=True)
    #websocket_sender_thread.start()
    start_datetime, start_time = get_system_start_time()
    while True:
        # Calculate elapsed time
        elapsed_time = calculate_elapsed_time(start_time)
        current_datetime = get_current_datetime()

        # Get uptime
        uptime_output = get_uptime()

        # Get uptimeime()

        # Get system status
        #voltage, temperature, cpu_status_raw, cpu_status, temperature_warning 

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collecting Pi status...")
        status_data = get_pi_status()
        print(json.dumps(status_data, indent=2))

        db_manager.insert_status(status_data)
        print("Status saved to SQLite.")

        # พยายามส่งข้อมูลทันทีหลังจากบันทึก (ถ้า WebSocket server พร้อม)
        # ไม่ต้องตั้งค่า sent_to_server เป็น 1 ทันที เพราะ check_and_send_unsent_data จะจัดการเอง
        # และเพื่อให้แน่ใจว่าข้อมูลจะถูกส่งจริง ไม่ใช่แค่พยายามส่ง
        # if send_data_via_websocket(status_data):
        #     db_manager.mark_as_sent([status_data['id_after_insert']]) # ต้องแก้ db_manager ให้ return id
        #     print("Data sent via WebSocket and marked as sent.")
        # else:
        #     print("Failed to send data via WebSocket. It will be sent later by background thread.")


        print("Waiting for 1 hour...")
        time.sleep(3600) # รอ 1 ชั่วโมง

if __name__ == "__main__":
    main()