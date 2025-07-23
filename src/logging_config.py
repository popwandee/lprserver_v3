import os
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv

def setup_logging():
    """
    from src.logging_config import setup_logging
    setup_logging()
    import logging
    logging.info("เริ่มต้นโปรแกรม")
    """

    env_path = os.path.join(os.path.dirname(__file__), '.env.production')
    load_dotenv(env_path)

    LOG_FILE = os.getenv("DETECTION_LOG_FILE", "log/detection.log")
    LOG_DIR = os.path.dirname(LOG_FILE)
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # ป้องกันการเพิ่ม handler ซ้ำ
    if not logger.handlers:
        file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info("Logging setup complete.")

