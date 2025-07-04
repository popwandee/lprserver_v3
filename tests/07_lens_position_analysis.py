from picamera2 import Picamera2
import time, csv, os
import cv2
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

results = []
output_dir = "lens_scan"
os.makedirs(output_dir, exist_ok=True)
positions = np.arange(0.0, 10.05, 0.05)
#for pos in range(30, 50):  # ทดลองตั้งแต่ 0 ถึง 30
for pos in positions:  # ทดลองตั้งแต่ 0 ถึง 10.0
    picam2.set_controls({
        "LensPosition": float(pos),
        "AfMode": 0  # ปิด AF
    })
    time.sleep(2)

    frame = picam2.capture_array()
    meta = picam2.capture_metadata()
    focus_fom = meta.get("FocusFoM", 0)
    exposure = meta.get("ExposureTime", 0)
    analogue_gain = meta.get("AnalogueGain", 0.0)
    digital_gain = meta.get("DigitalGain", 0.0)
    lux = meta.get("Lux", 0.0)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    filename = f"{output_dir}/{timestamp}lens_{pos:.2f}_sharp{int(sharpness)}.jpg"
    cv2.putText(frame, f"Pos:{pos} Sharp:{int(sharpness)} FoM:{focus_fom}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.imwrite(filename, frame)

    results.append((round(pos, 2), sharpness, focus_fom, exposure, analogue_gain, digital_gain, lux, filename))
    print(f"[Lens={pos:.2f}] Sharpness={int(sharpness)}, FocusFoM={focus_fom}, Lux={int(lux)}")
filename = f"lens_scan_results{timestamp}.csv"
            
# 🔽 บันทึกลง CSV
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["LensPosition", "Sharpness", "FocusFoM", "ExposureTime", "AnalogueGain", "DigitalGain", "Lux", "Filename"])
    writer.writerows(results)
print(f"✅ เสร็จสิ้นการเก็บข้อมูล พร้อมบันทึกใน {filename}")

print("Plot Graph...")

df = pd.read_csv(filename)

plt.figure(figsize=(12, 6))

# Plot Sharpness
plt.subplot(1, 2, 1)
plt.plot(df["LensPosition"], df["Sharpness"], marker='o', label="Sharpness")
plt.title("Sharpness vs LensPosition")
plt.xlabel("LensPosition")
plt.ylabel("Sharpness (Laplacian)")
plt.grid(True)
plt.legend()

# Plot FocusFoM
plt.subplot(1, 2, 2)
plt.plot(df["LensPosition"], df["FocusFoM"], marker='x', color='orange', label="FocusFoM")
plt.title("FocusFoM vs LensPosition")
plt.xlabel("LensPosition")
plt.ylabel("FocusFoM")
plt.grid(True)
plt.legend()
graph_filename = f"lens_scan_graph_{timestamp}.png"
plt.tight_layout()
plt.savefig(graph_filename)
plt.show()