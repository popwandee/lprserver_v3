import os
import platform
import psutil

def get_cpu_info():
    return {
        "Model": platform.processor(),
        "Cores": psutil.cpu_count(logical=True), # Return the number of logical CPUs in the system (same as os.cpu_count) or None if undetermined. “logical CPUs” means the number of physical cores multiplied by the number of threads that can run on each core (this is known as Hyper Threading). If logical is False return the number of physical cores only
        "Frequency": f"{psutil.cpu_freq().current} MHz", # .current, .min, .max
    }

def get_ram_info():
    ram = psutil.virtual_memory()
    return {
        "Total": f"{ram.total / (1024 ** 3):.2f} GB",
        "Available": f"{ram.available / (1024 ** 3):.2f} GB",
        "Used": f"{ram.used / (1024 ** 3):.2f} GB"
    }

def get_disk_info():
    disk = psutil.disk_usage('/')
    return {
        "Total": f"{disk.total / (1024 ** 3):.2f} GB",
        "Used": f"{disk.used / (1024 ** 3):.2f} GB",
        "Free": f"{disk.free / (1024 ** 3):.2f} GB"
    }

def get_os_info():
    return {
        "Name": platform.system(),
        "Version": platform.version(),
        "Release": platform.release()
    }

def get_firmware_info():
    with open('/proc/version', 'r') as f:
        return f.read().strip()
    
def get_sensors_fans():
    """Get the sensors fans information."""
    try:
        sensors_fans = psutil.sensors_fans()
        return sensors_fans
    except Exception as e:
        return f"Error retrieving sensors fans information: {str(e)}"

def gather_system_info():
    """Gathers system information like CPU, RAM, Disk, OS version, and Firmware version."""
    cpu_info = get_cpu_info()
    #ram_info = f"{round(psutil.virtual_memory().total / (1024 * 1024))} MB"
    ram_info = get_ram_info()
    #disk_info = f"{round(psutil.disk_usage('/').total / (1024 * 1024 * 1024))} GB"
    disk_info = get_disk_info()
    os_version = platform.platform()
    os_info = get_os_info()
    firmware_info = os.popen("vcgencmd version").read().strip()
    temps = psutil.sensors_temperatures()
    battery = psutil.sensors_battery()
    # Use a dictionary to store the information
    system_info = {
        "CPU": cpu_info,
        "RAM": ram_info,
        "Disk": disk_info,
        "OS Version": os_version,
        "OS Info": os_info,
        "Firmware Version": firmware_info,
        "Sensors Fans (RPM-revolutions per minute)": get_sensors_fans(),
        "hardware temperatures": temps,
        "battery": battery,
    }
    
    # Format the output with newlines
    formatted_info = "\n".join([f"{key}: {value}" for key, value in system_info.items()])
    return formatted_info