# server_ws.py
import asyncio
import websockets
import json
import logging
import os
from datetime import datetime

SAVE_IMAGE_DIR = "received_images"
os.makedirs(SAVE_IMAGE_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

async def save_image_from_hex(hex_str, filename):
    if not hex_str:
        return
    with open(filename, "wb") as f:
        f.write(bytes.fromhex(hex_str))

async def handler(websocket):
    logging.info(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                logging.info(f"Received data: {data.keys()}")

                # Save images if present
                for key in ["original_image_b64", "processed_image_b64", "lp_image_b64"]:
                    if key in data and data[key]:
                        fname = f"{key}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                        fpath = os.path.join(SAVE_IMAGE_DIR, fname)
                        await save_image_from_hex(data[key], fpath)
                        logging.info(f"Saved image: {fpath}")

                # Save metadata as JSON
                meta_fname = f"meta_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
                with open(os.path.join(SAVE_IMAGE_DIR, meta_fname), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            except Exception as e:
                logging.error(f"Error processing message: {e}")

    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        logging.info("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())