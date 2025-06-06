import logging
import os
import sqlite3
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '../src', '.env.production')
load_dotenv(env_path)
# Configure logging
LOG_FILE = os.getenv("LOG_FILE")
logging.basicConfig(filename=LOG_FILE,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger()

# ใช้ตัวแปรจาก .env.production
SERVER_URL = os.getenv("SERVER_URL")
print(f"LOG_FILE: {LOG_FILE}")
print(f"SERVER_URL: {SERVER_URL}")

"""เช็กข้อมูลใหม่ใน SQLite และส่งไปยังเซิร์ฟเวอร์"""
db_path = os.getenv("DB_PATH")

logging.debug(f"DB_PATH...{db_path}")
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    #cursor.execute("UPDATE lpr_data SET sent_to_server = 0 WHERE id = ?", (id,))
    cursor.execute("UPDATE lpr_data SET sent_to_server = 0 ")
    conn.commit()