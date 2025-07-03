from picamera2 import Picamera2
import time, csv, os
import cv2
import numpy as np
from datetime import datetime

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(1)

results = []
output_dir = "img"
os.makedirs(output_dir, exist_ok=True)

# Loop ทดลอง
for gain in np.arange(1.0, 6.1, 0.5):
    for exposure in range(2000, 32000, 2000):
        for pos in range(5, 30, 2):  # Scan ค่าโฟกัสแต่ละตำแหน่ง
            # ตั้งค่ากล้อง
            picam2.set_controls({
                "AnalogueGain": float(gain),
                "ExposureTime": int(exposure),
                "LensPosition": pos,
                "AfMode": 0  # ปิดโหมดออโต้โฟกัส เพื่อใช้ค่าที่เรากำหนด
            })
            time.sleep(0.5)

            # อ่านค่าความคม (FocusFoM)
            meta = picam2.capture_metadata()
            focus_fom = meta.get("FocusFoM", 0)

            # จับภาพ
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

            # ชื่อไฟล์
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/img_g{gain:.1f}_e{exposure}_p{pos}_{int(sharpness)}.jpg"
            cv2.putText(frame, f"G:{gain:.1f} E:{exposure} P:{pos} S:{int(sharpness)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv2.imwrite(filename, frame)

            # บันทึกผล
            results.append((gain, exposure, pos, sharpness, focus_fom, filename))
            print(f"Gain={gain:.1f}, Exposure={exposure}, Position={pos} → Sharpness={int(sharpness)}, FocusFoM={focus_fom}")

# บันทึกลง CSV
with open("focus_results_v2.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Gain", "Exposure", "LensPosition", "Sharpness", "FocusFoM", "Filename"])
    writer.writerows(results)

print("✅ เสร็จสิ้นการเก็บข้อมูล พร้อมบันทึกใน focus_results.csv")
