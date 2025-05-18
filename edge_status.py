# edge_status.py
import socketio
import psutil

sio = socketio.Client()
SERVER_URL = "http://lprserver.tail605477.ts.net:1337/"

def check_and_send_status():
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    status = {"cpu": cpu_usage, "memory": memory}
    sio.emit("edge_status", status)
