from picamera2 import Picamera2
import time
import cv2
import numpy as np
import os
output_dir = "img"
os.makedirs(output_dir, exist_ok=True)
def wait_until_focus_stable(picam2, timeout=5.0, stable_threshold=2, fom_window=5):
    """
    รอจนกว่า FocusFoM จะนิ่งในช่วงเวลาหนึ่งก่อนถ่ายภาพ
    """
    start_time = time.time()
    prev_foms = []

    while time.time() - start_time < timeout:
        meta = picam2.capture_metadata()
        fom = meta.get("FocusFoM", 0)
        prev_foms.append(fom)

        if len(prev_foms) > fom_window:
            prev_foms.pop(0)
            if np.std(prev_foms) < stable_threshold:
                print(f"✅ FocusFoM stable at ~{int(np.mean(prev_foms))}")
                return True

        time.sleep(0.1)

    print("⚠️ FocusFoM did not stabilize in time.")
    return False

# ตั้งค่ากล้อง
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 720)})
picam2.configure(config)
picam2.start()
time.sleep(1)

# ตั้งค่าให้กล้องเข้าสู่โหมด autofocus-on-capture
picam2.set_controls({"AfMode": 2})  # continuous mode
time.sleep(0.5)

# Trigger autofocus scan แบบ manual (เหมือนกดปุ่มโฟกัสก่อนถ่าย)
picam2.set_controls({"AfTrigger": 1})
print("🔍 Scanning focus...")

# รอจน FocusFoM คงที่
focus_ready = wait_until_focus_stable(picam2)

if focus_ready:
    frame = picam2.capture_array()
    meta = picam2.capture_metadata()
    lens_position = round(meta.get("LensPosition", 0.0),2)
    focus_fom = meta.get("FocusFoM", 0)
    exposure = meta.get("ExposureTime", 0)
    analogue_gain = round(meta.get("AnalogueGain", 0.0),2)
    digital_gain = round(meta.get("DigitalGain", 0.0),2)
    lux = round(meta.get("Lux", 0.0),2)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    filename = f"{output_dir}/pos{lens_position}_sharp{int(sharpness)}_ag{analogue_gain}_dg{digital_gain}.jpg"
    cv2.putText(frame, f"Pos:{lens_position} Sharp:{int(sharpness)} FoM:{focus_fom}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.imwrite(filename, frame)
    print(f"[Lens={lens_position}] Sharpness={int(sharpness)}, FocusFoM={focus_fom}, Lux={int(lux)}")
    print(f"📸 บันทึกภาพแล้ว: {filename}")
else:
    print("❌ ไม่สามารถโฟกัสได้ในเวลาที่กำหนด")
