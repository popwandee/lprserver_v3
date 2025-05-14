import time
import subprocess
from datetime import datetime

# Log the uptime every minute
log_file_path = "uptime.log"

# Get the system start time using 'uptime -s'
start_datetime_str = subprocess.check_output(["uptime", "-s"], text=True).strip()
start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
start_time = time.mktime(start_datetime.timetuple())  # Convert to timestamp

while True:
    try:
        # Calculate elapsed time since the system started
        elapsed_time = int(time.time() - start_time)
        elapsed_days = elapsed_time // (24 * 3600)
        elapsed_time %= (24 * 3600)
        elapsed_hours = elapsed_time // 3600
        elapsed_time %= 3600
        elapsed_minutes = elapsed_time // 60
        elapsed_seconds = elapsed_time % 60

        # Get the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Execute the 'uptime -p' command
        uptime_output = subprocess.check_output(["uptime", "-p"], text=True).strip()
        
        # Append the output, elapsed time, and current date/time to the log file
        with open(log_file_path, "a") as log_file:
            log_file.write(
                f"[Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[Elapsed Time: {elapsed_days}d {elapsed_hours}h {elapsed_minutes}m {elapsed_seconds}s] "
                f"[Current Time: {current_datetime}] {uptime_output}\n"
            )
        
        # Sleep for 60 seconds before logging again
        time.sleep(60)
    except Exception as e:
        print(f"An error occurred: {e}")
        break