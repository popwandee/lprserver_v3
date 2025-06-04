def perform_object_detection(command, duration):
    import subprocess
    import time
    from utils.logger import log_message

    log_message("Starting object detection...")

    try:
        # Start the object detection process
        process = subprocess.Popen(command, shell=True)
        log_message(f"Running command: {command}")

        # Let it run for the specified duration
        time.sleep(duration)

        # Terminate the process after the duration
        process.terminate()
        log_message("Object detection process terminated.")

    except Exception as e:
        log_message(f"Error during object detection: {str(e)}")

    log_message("Object detection completed.")