# สำหรับทดลองรับข้อมูล
# server.py
import os
import asyncio
import websockets
import logging
from logging.handlers import TimedRotatingFileHandler
# Configure logging
if not os.path.exists("log/websocket_server.log"):
    logging.critical(f"Log file websocket_server.log does not exist or cannot be created.")
    # Define log directory and log file , create log file
    LOG_DIR = "log"
    LOG_FILE = os.path.join(LOG_DIR, "websocket_server.log")
    os.makedirs(LOG_DIR, exist_ok=True)
# Create a logger 
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Capture DEBUG for Detailed debugging information, INFO for General event, WARNING for possible issues, ERROR for serious issue, CRITICAL for severe problem
# File handler (logs to a file)
file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7) #Keep logs from the last 7 days.
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)  # Ensure all levels are logged

async def echo(websocket, path):
    async for message in websocket:
        print(f"Received: {message}")
        # Optional: Send a confirmation back
        await websocket.send(f"Server received: {message}")

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    print("WebSocket Server started on ws://localhost:8765")
    asyncio.run(main())