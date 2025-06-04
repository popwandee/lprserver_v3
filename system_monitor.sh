#!/bin/bash
# This script is intended to be run as a cron job to monitor system status
# and log the results to a file.
echo "Running as $(whoami)" > /tmp/system_monitor_user.log
echo "PATH=$PATH" > /tmp/system_monitor_path.log

# Navigate to the directory containing the main.py script
cd /home/camuser/hailo/rpi-system-test || exit

# Execute the main.py script using Python
/home/camuser/hailo/venv_hailo/bin/python main.py
#nohup /home/camuser/hailo/venv_hailo/bin/python status_log.py &