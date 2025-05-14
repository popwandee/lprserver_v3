import logging
import os

# Configure logging
logging.basicConfig(
    filename="system_check.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_status(message):
    """Logs a status message to the log file."""
    logging.info(message)
    print(message)  # Also print to console for real-time feedback

class Logger:
    def __init__(self, log_file='system_test.log'):
        self.log_file = log_file

    def log_info(self, message):
        logging.info(message)

    def log_warning(self, message):
        logging.warning(message)

    def log_error(self, message):
        logging.error(message)

    def log_debug(self, message):
        logging.debug(message)

    def log_status(self, test_name, status):
        message = f'Test: {test_name}, Status: {status}'
        self.log_info(message)

    def clear_log(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            self.log_info('Log file cleared.')