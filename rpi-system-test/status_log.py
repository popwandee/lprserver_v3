import time
import subprocess
from datetime import datetime

# Log file path
log_file_path = "system_status.log"

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

def get_system_status():
    """ดึงสถานะของระบบ (Voltage, Temperature, CPU Status)
    Get the system status using 'vcgencmd' commands.
    ใช้คำสั่ง 'vcgencmd' เพื่อดึงข้อมูลแรงดันไฟฟ้า (Voltage), อุณหภูมิ (Temperature), 
    และสถานะของ CPU (CPU Status)

    Returns:
        tuple:
            - voltage (str): ข้อมูลแรงดันไฟฟ้า
            - temperature (float): อุณหภูมิในหน่วยองศาเซลเซียส
            - cpu_status_raw (str): สถานะ CPU ในรูปแบบ raw
            - cpu_status (str): สถานะ CPU ในรูปแบบ human-readable
            - temperature_warning (str): ข้อความแจ้งเตือนเกี่ยวกับอุณหภูมิ
    """
    try:
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

        # Check for temperature warnings
        if temperature > 80:
            temperature_warning = "WARNING: Over-temperature detected!"
        elif temperature < 0:
            temperature_warning = "WARNING: Under-temperature detected!"
        else:
            temperature_warning = "Temperature is normal."

    except subprocess.CalledProcessError as e:
        # Handle errors from vcgencmd commands
        voltage = "Error"
        temperature = "Error"
        cpu_status = f"Error: {e}"
        temperature_warning = "Error retrieving temperature."
    except Exception as e:
        # Handle any other unexpected errors
        voltage = "Error"
        temperature = "Error"
        cpu_status = f"Unexpected Error: {e}"
        temperature_warning = "Unexpected error occurred."

    return voltage, temperature, cpu_status_raw, cpu_status, temperature_warning

def log_status(start_datetime, elapsed_time, current_datetime, uptime_output, voltage, temperature, cpu_status_raw, cpu_status, temperature_warning):
    """บันทึกสถานะของระบบลงใน log file โดยจำกัดจำนวนบรรทัดไว้ที่ 100 บรรทัด
    Append the status to the log file, limiting it to 100 records.
    Args:
        start_datetime (datetime): เวลาที่ระบบเริ่มต้นทำงาน
        elapsed_time (tuple): เวลาที่ผ่านไปในรูปแบบ (days, hours, minutes, seconds)
        current_datetime (str): เวลาปัจจุบัน
        uptime_output (str): ข้อมูล uptime
        voltage (str): ข้อมูลแรงดันไฟฟ้า
        temperature (float): อุณหภูมิในหน่วยองศาเซลเซียส
        cpu_status_raw (str): สถานะ CPU ในรูปแบบ raw
        cpu_status (str): สถานะ CPU ในรูปแบบ human-readable
        temperature_warning (str): ข้อความแจ้งเตือนเกี่ยวกับอุณหภูมิ
    """
    elapsed_days, elapsed_hours, elapsed_minutes, elapsed_seconds = elapsed_time
    new_log_entry = (
        f"[Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}] "
        f"[Elapsed Time: {elapsed_days}d {elapsed_hours}h {elapsed_minutes}m {elapsed_seconds}s] "
        f"[Current Time: {current_datetime}] {uptime_output}\n"
        f"[Voltage: {voltage}] [Temperature: {temperature}°C] [CPU Status: {cpu_status_raw}-{cpu_status}]\n"
        f"{temperature_warning}\n"
    )

    try:
        # Read existing log file
        with open(log_file_path, "r") as log_file:
            log_lines = log_file.readlines()

        # Limit the log file to 100 records
        if len(log_lines) >= 100:
            log_lines = log_lines[len(log_lines) - 99:]

        # Add the new log entry
        log_lines.append(new_log_entry)

        # Write back to the log file
        with open(log_file_path, "w") as log_file:
            log_file.writelines(log_lines)

    except FileNotFoundError:
        # If the log file doesn't exist, create it and write the new log entry
        with open(log_file_path, "w") as log_file:
            log_file.write(new_log_entry)

def main():
    """ฟังก์ชันหลักสำหรับบันทึก uptime และสถานะของระบบ
    Main function to log uptime and system status.
    """
    start_datetime, start_time = get_system_start_time()

    while True:
        try:
            # Calculate elapsed time
            elapsed_time = calculate_elapsed_time(start_time)
            current_datetime = get_current_datetime()

            # Get uptime
            uptime_output = get_uptime()

            # Get uptimeime()

            # Get system status
            voltage, temperature, cpu_status_raw, cpu_status, temperature_warning = get_system_status()

            # Log the status
            log_status(start_datetime, elapsed_time, current_datetime, uptime_output, voltage, temperature, cpu_status_raw, cpu_status, temperature_warning)

            # Sleep for 60 seconds before logging again
            time.sleep(60)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()