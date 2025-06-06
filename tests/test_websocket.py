import asyncio
import websockets
import logging
import os
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
async def test_connection():
    try:
        async with websockets.connect(SERVER_URL) as ws:
            await ws.send("ping")
            response = await ws.recv()
            print(f"Server response: {response}")
    except Exception as e:
        print(f"WebSocket test failed: {e}")

asyncio.run(test_connection())
