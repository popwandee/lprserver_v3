import subprocess
import logging
from utils.logger import log_status

def test_hailo_hardware():
    try:
        # Check if Hailo-8 hardware is connected
        result = subprocess.run(['hailo-cli', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            log_status("Hailo-8 hardware detected:\n" + result.stdout)
        else:
            log_status("Hailo-8 hardware not detected. Error:\n" + result.stderr)

        # Check kernel logs for Hailo-related messages
        kernel_log = subprocess.run(['dmesg'], capture_output=True, text=True)
        hailo_logs = [line for line in kernel_log.stdout.splitlines() if 'hailo' in line.lower()]
        if hailo_logs:
            log_status("Hailo-related kernel logs:\n" + "\n".join(hailo_logs))
        else:
            log_status("No Hailo-related messages found in kernel logs.")

    except Exception as e:
        log_status(f"An error occurred while testing Hailo-8 hardware: {str(e)}")