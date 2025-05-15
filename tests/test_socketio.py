import socketio
import time
import threading
import random
from datetime import datetime

sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)
keep_running = True  # shared flag to stop all threads
stop_event = threading.Event()

@sio.event
def connect():
    print("[✓] Socket.IO connected to server\n")

@sio.event
def disconnect():
    print("[x] Disconnected from server\n")
    
@sio.event
def connect_error(data):
    print("[x] Connection failed:", data)

@sio.on('debug_response')
def on_response(data):
    print(f">>> Received response from server: {data}\n")

def wait_for_quit():
    while True:
        user_input = input(">>> Press 'q' and Enter to quit: ")
        if user_input.lower() == 'q':
            print(">>> Quitting...\n")
            message = f"Client disconnecting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            sio.emit('disconnect', {'message': message}, namespace='/')
            # wait a little to ensure loop breaks before disconnect
            time.sleep(1)
            stop_event.set()
            if sio.connected:
                sio.disconnect()
            break
            
def send_periodic_messages():
    while not stop_event.is_set():
        time.sleep(5)
        if sio.connected:
            message = f"Random message {random.randint(1000, 9999)}"
            timestamp = time.time()
            print(f">>> Emitting new debug_event: {message}")
            sio.emit('debug_event', {'message': message, 'timestamp': timestamp}, namespace='/')

def main():
    try:
        sio.connect("http://lprserver.tail605477.ts.net:1337", namespaces=['/'])
        print(">>>Connected. Initial debug_event will be sent. Sending debug_event...")
        sio.on('connect', lambda: print("[✓] Connected to server"))
        sio.on('disconnect', lambda: print("[x] Disconnected from server"))
        sio.on('lpr_response', lambda data: print("Response:", data))
        sio.emit('debug_event', {'message': 'Hello from client!', 'timestamp': time.time()}, namespace='/')
        time.sleep(2)  # wait for response
        # Start thread to wait for 'q'
        # Start threads
        threading.Thread(target=wait_for_quit, daemon=True).start()
        threading.Thread(target=send_periodic_messages, daemon=True).start()

        # Keep main thread alive to listen for events
        sio.wait()
    except Exception as e:
        print(f">>> Error: {e}")

if __name__ == '__main__':
    main()