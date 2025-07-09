import os
import cv2
import time
import csv
import numpy as np
import easyocr
import degirum as dg
from datetime import datetime
from picamera2 import Picamera2
from skimage import filters
from skimage.metrics import structural_similarity as ssim
import pandas as pd
import matplotlib.pyplot as plt
import json
import pandas as pd
import matplotlib.pyplot as plt

# 🧠 OCR ด้วย EasyOCR
reader = easyocr.Reader(['en','th'])

def rearrange_detections(ocr_results):
        """Rearranges OCR detection results into a single string for a readable format"""
        if not ocr_results:
            return "Unknown"
        extracted_text = []
        print(f"DEBUG: OCR results: {ocr_results}")
        # Sort results based on x-coordinate to get correct order for horizontal text
        sorted_results = sorted(ocr_results, key=lambda x: x.get("bbox", [0])[0] if isinstance(x, dict) and "bbox" in x else 0)
        for res in sorted_results:
            if isinstance(res, dict) and "label" in res:
                print(f"DEBUG: Extracting label: {res['label']}")
                extracted_text.append(res["label"])  # Extract text from label
        return " ".join(extracted_text)
def rearrange_detections_linewise(ocr_results, y_threshold=40):
    """
    เรียงข้อความ OCR ตามบรรทัด (Y) ก่อน แล้วค่อยเรียงในบรรทัดตาม X
    y_threshold: ค่าความสูงที่ถือว่าอยู่บรรทัดเดียวกัน (pixel)
    """
    if not ocr_results:
        return "Unknown"
    items = []
    extracted_text = []
    print(f"DEBUG: OCR results: {ocr_results}")
    for res in ocr_results:
        if isinstance(res, dict) and "label" in res and "bbox" in res:
            x = res["bbox"][0]
            y = res.get("bbox")[1] if len(res["bbox"]) > 1 else 0
            items.append({"label": res["label"], "x": x, "y": y})
    # จัดกลุ่มตาม y (บรรทัด)
    items = sorted(items, key=lambda k: k["y"])
    lines = []
    current_line = []
    last_y = None
    for item in items:
        if last_y is None or abs(item["y"] - last_y) < y_threshold:
            current_line.append(item)
        else:
            lines.append(current_line)
            current_line = [item]
        last_y = item["y"]
    if current_line:
        lines.append(current_line)
    # ในแต่ละบรรทัด เรียงตาม x
    texts = []
    for line in lines:
        line_sorted = sorted(line, key=lambda k: k["x"])
        texts.append("".join([k["label"] for k in line_sorted]))
    return " ".join(texts)
def ocr_text(image):
    if image is None or not isinstance(image, np.ndarray):
        return "No Plate Detected"
    results = reader.readtext(image)
    print(f"DEBUG: EasyOCR results: {results} (in read_text_with_easyocr)")
    ocr_results = []
    confidences = []
    for res in results:
        # ใช้ x ของจุดซ้ายบนเป็น key สำหรับเรียงลำดับ
        x_min = min([pt[0] for pt in res[0]])
        y_min = min([pt[1] for pt in res[0]])
        ocr_results.append({"bbox": [x_min, y_min, 0, 0], "label": res[1]})
        confidences.append(res[2])
    text = rearrange_detections_linewise(ocr_results) if ocr_results else "No Text"
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return text, avg_conf

def analyze_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = filters.gaussian(gray, sigma=1).std()
    return lap_var, blur_score, image.shape[1], image.shape[0]

def main():
    csv_path = "results_ocr_experiment.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "filename", "distance_m", "ocr_text", "confidence", 
            "sharpness", "blur_score"
        ])
        print("📊 Starting OCR experiment...")
        for filename in os.listdir("experiment_results"):
            if not filename.endswith(".jpg"):
                print("no image found")
                continue
            # Read the image from the experiment results directory
            print(f"Processing {filename}...")
            #image_path = os.path.join("experiment_results", filename)

            image_path = f"experiment_results/{filename}"
            
            distance = int(filename.split("_")[-1].replace("m.jpg", ""))
            print(f"Distance: {distance} m")

            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Failed to read {filename}")
                continue
            ocr_text_result, confidence = ocr_text(image)
            print(f"OCR Text: {ocr_text_result}, Confidence: {confidence:.2f}")
            sharpness, blur_score, width_px, height_px = analyze_image(image)
            print(f"Sharpness: {sharpness:.2f}, Blur Score: {blur_score:.2f}, Width: {width_px}px, Height: {height_px}px")
            writer.writerow([
                filename, distance, ocr_text_result, round(confidence, 3), 
                round(sharpness, 2), round(blur_score, 4)
            ])
    print("✅ Experiment complete. Results saved to:", csv_path)

def analyze():

    # 📥 Load data
    df = pd.read_csv("results_ocr_experiment.csv")

    # 🧹 กรองเฉพาะผลที่ OCR อ่านได้
    df_valid = df[df["ocr_text"].notna() & (df["ocr_text"].str.strip() != "")]

    # 🔍 วิเคราะห์: ค่าเฉลี่ยต่อระยะ
    grouped = df_valid.groupby("distance_m").agg({
        "confidence": "mean",
        "sharpness": "mean",
        "blur_score": "mean",
    }).reset_index()

    # 🏆 หาระยะที่ OCR Confidence สูงสุด
    best_row = grouped.loc[grouped["confidence"].idxmax()]
    best_distance = int(best_row["distance_m"])
    best_conf = round(best_row["confidence"], 3)
    best_sharp = round(best_row["sharpness"], 2)
    best_blur = round(best_row["blur_score"], 4)

    print(f"✅ Best distance for OCR is: {best_distance} m")
    print(f"OCR Confidence: {best_conf}")
    print(f"Sharpness: {best_sharp}, Blur Score: {best_blur}")

    # ✍️ วิเคราะห์เหตุผล
    if best_sharp > 100 and best_blur < 2.0:
        print("🧠 ความคมชัดสูง และเบลอต่ำ ช่วยให้ OCR ทำงานได้ดีที่สุดที่ระยะนี้")

    # 📈 Plot 1: OCR Confidence vs Distance
    plt.figure(figsize=(8,5))
    plt.plot(grouped["distance_m"], grouped["confidence"], marker='o', label="OCR Confidence", color='blue')
    plt.axvline(best_distance, color='gray', linestyle='--', label=f"Best at {best_distance}m")
    plt.title("OCR Confidence vs Distance")
    plt.xlabel("Distance (m)")
    plt.ylabel("OCR Confidence")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graph_ocr_confidence_vs_distance.png")
    plt.show()

    # 📈 Plot 2: Sharpness & Blur vs Distance
    plt.figure(figsize=(8,5))
    plt.plot(grouped["distance_m"], grouped["sharpness"], marker='s', label="Sharpness", color='green')
    plt.plot(grouped["distance_m"], grouped["blur_score"], marker='x', label="Blur Score", color='red')
    plt.title("Sharpness & Blur vs Distance")
    plt.xlabel("Distance (m)")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graph_sharpness_blur_vs_distance.png")
    plt.show()


if __name__ == "__main__":
    # capture_images()  # ← ถ้าอยากให้ถ่ายภาพอัตโนมัติ เปิดบรรทัดนี้
    main()
    analyze()