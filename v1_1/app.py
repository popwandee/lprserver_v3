from flask import Flask, render_template, Response, request, jsonify
from picamera2 import Picamera2, Preview
from datetime import datetime
import threading, cv2, time, os
import numpy as np

app = Flask(__name__)
picam2 = Picamera2()
sharpness_score = 0

# Camera config
video_config = picam2.create_video_configuration(
    main={"size": (1280, 720)}, # Or (640, 480) for lower bandwidth
    lores={"size": (640, 640)}, # 640x640 สำหรับ AI model
    display="lores")
picam2.configure(video_config)
picam2.set_controls({"AfMode": 2})  # Continuous autofocus
picam2.start()

# Save folder
os.makedirs("img", exist_ok=True)

frame_lock = threading.Lock()
output_frame = None
bandwidth_kbps = 0

def capture_frames():
    global output_frame, bandwidth_kbps, sharpness_score
    prev_time = time.time()
    total_bytes = 0
    while True:
        frame = picam2.capture_array()
        # ---------- เพิ่ม timestamp ----------
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 255), 2)
                    
        # ---------- คำนวณ sharpness ----------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = round(laplacian_var, 2)
        
        # ---------- Autofocus simulation ----------
        metadata = picam2.capture_metadata()
        current_focus = metadata.get("FocusFoM", 0)
        
        # เช็คว่าภาพเบลอหรือไม่ แล้วค่อยปรับ gain/exposure
        #if laplacian_var < 80:  # ภาพเบลอมาก
        #    picam2.set_controls({"AnalogueGain": 3.0, "ExposureTime": 20000})
        #elif laplacian_var < 120:  # ปานกลาง
        #    picam2.set_controls({"AnalogueGain": 2.0, "ExposureTime": 15000})
        #else:  # ชัดแล้ว
        #    picam2.set_controls({"AnalogueGain": 1.0, "ExposureTime": 10000})
            
        # ---------- Encode JPEG + Bandwidth ----------
        _, jpeg = cv2.imencode('.jpg', frame)
        total_bytes += len(jpeg)
        now = time.time()
        if now - prev_time >= 1.0:
            bandwidth_kbps = int((total_bytes * 8) / 1024)
            total_bytes = 0
            prev_time = now
            
        with frame_lock:
            output_frame = jpeg.tobytes()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        global output_frame
        while True:
            with frame_lock:
                if output_frame is None:
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + output_frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_params')
def camera_params():
    metadata = picam2.capture_metadata()
    print(metadata)  # Debugging line to see metadata
    global sharpness_score, bandwidth_kbps
    return jsonify({
        "brightness": metadata.get("Lux", 0),
        "exposure": metadata.get("ExposureTime", 0),
        "analog_gain": metadata.get("AnalogueGain", 0),
        "fps": metadata.get("FrameDuration", 0),
        "focus": metadata.get("FocusFoM", 0),
        "sharpness_score": sharpness_score,
        "bandwidth_kbps": bandwidth_kbps
    })

@app.route('/set_params', methods=['POST'])
def set_params():
    data = request.json
    controls = {}
    if "exposure" in data:
        controls["ExposureTime"] = int(data["exposure"])
    if "gain" in data:
        controls["AnalogueGain"] = float(data["gain"])
    if controls:
        picam2.set_controls(controls)
    return jsonify({"status": "ok"})

@app.route('/capture')
def capture_image():
    frame = picam2.capture_array()
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"saved_images/capture_{now}.jpg"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2)
    cv2.imwrite(filename, frame)
    return jsonify({"status": "saved", "file": filename})

if __name__ == '__main__':
    t = threading.Thread(target=capture_frames)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=5000, threaded=True)