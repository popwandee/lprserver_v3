import os
from dotenv import load_dotenv
import subprocess
import json
import csv
import cv2
from datetime import datetime
import easyocr
import degirum as dg
import numpy as np
from picamera2 import Picamera2
from libcamera import controls
# 🔧 Config
CSV_PATH = "experiment_results_imx708Wide_car_daytime_gopro.csv"
IMAGE_DIR = "experiment_results_imx708Wide_car_daytime_gopro"
METADATA_DIR = "experiment_results_imx708Wide_car_daytime_gopro"
os.makedirs(IMAGE_DIR, exist_ok=True)

# 🧠 Initialize
reader = easyocr.Reader(['th', 'en'])
env_path = os.path.join(os.path.dirname(__file__), '../src', '.env.production')
load_dotenv(env_path)
def safe_float(val):
    try:
        return f"{float(val):.2f}"
    except (ValueError, TypeError):
        return ""
def ensure_csv_exists():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "Distance(m)", "Image", "LicenseText","PlateWidth", "PlateHeight",
                "ExposureTime", "AnalogueGain", "DigitalGain",
                "LensPosition", "FocusFoM", "AfState", "SensorTemperature", "FrameDuration",
                "Lux"
            ])

def capture_image(distance):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = f"{timestamp}_{distance}m.jpg"
    image_path = os.path.join(IMAGE_DIR, image_name)

    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    picam2.start()
    request = picam2.capture_request()
    frame = request.make_array("main")
    metadata = request.get_metadata()
    request.release()
    picam2.close()

    # ✅ บันทึกภาพ
    cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    # ✅ จัด metadata ในรูปแบบ dict สำหรับ logging/CSV
    metadata_dict = {
        "AfPauseState": metadata.get("AfPauseState", "N/A"),
        "ExposureTime": metadata.get("ExposureTime", "N/A"),
        "FocusFoM": metadata.get("FocusFoM", "N/A"),
        "DigitalGain": metadata.get("DigitalGain", "N/A"),
        "SensorTemperature": metadata.get("SensorTemperature", "N/A"),
        "FrameDuration": metadata.get("FrameDuration", "N/A"),
        "LensPosition": metadata.get("LensPosition", "N/A"),
        "AfState": metadata.get("AfState", "N/A"),
        "AeState": metadata.get("AeState", "N/A"),
        "ColourTemperature": metadata.get("ColourTemperature", "N/A"),
        "Lux": metadata.get("Lux", "N/A"),
        "ColourGains": metadata.get("ColourGains", "N/A"),
        "SensorBlackLevels": metadata.get("SensorBlackLevels", "N/A"),
        "AnalogueGain": metadata.get("AnalogueGain", "N/A"),
        "ColourCorrectionMatrix": metadata.get("ColourCorrectionMatrix", "N/A"),
    }
    print(f"metadata_dict: {metadata_dict}")
    print(f"raw metadata: {metadata}")
    return image_path, metadata_dict, timestamp
def resize_with_letterbox(image, target_size=(640, 640), padding_value=(0, 0, 0)):
        """Resizes an image while maintaining aspect ratio and padding with letterbox."""
        if image is None or not isinstance(image, np.ndarray):
            print("resize_with_letterbox received Captured image is invalid input!")
            return None, None, None, None
        # Convert BGR to RGB (if needed) if it's BGR, as many models expect RGB
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        original_height, original_width, channels = image.shape
        target_height, target_width = target_size
        
        #original_aspect_ratio = original_width / original_height
        #target_aspect_ratio = target_width / target_height

        scale_factor = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)

        offset_y = (target_height - new_height) // 2 # Padding on the top 
        offset_x = (target_width - new_width) // 2 # Padding on the left 

        letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image

        return letterboxed_image, offset_x, offset_y, scale_factor

def crop_license_plates(image, results):
        """Extract license plate regions from detected bounding boxes"""
        cropped_images = []

        for result in results:
            bbox = result.get("bbox")
            if not bbox or len(bbox) != 4:
                continue

            x_min, y_min, x_max, y_max = map(int, bbox)

            if x_min >= x_max or y_min >= y_max:
                print(f"Warning: Invalid bounding box coordinates: {bbox}")
                continue

            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(image.shape[1], x_max)
            y_max = min(image.shape[0], y_max)

            cropped_images.append(image[y_min:y_max, x_min:x_max])

        return cropped_images
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
def detect_license_plate(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None
    vehicle_model = dg.load_model(
        model_name=os.getenv("VEHICLE_DETECTION_MODEL"),
        inference_host_address=os.getenv("HEF_MODEL_PATH"),
        zoo_url=os.getenv("MODEL_ZOO_URL"),
    )
    lp_detection_model = dg.load_model(
        model_name=os.getenv("LICENSE_PLACE_DETECTION_MODEL"),
        inference_host_address=os.getenv("HEF_MODEL_PATH"),
        zoo_url=os.getenv("MODEL_ZOO_URL"),
        overlay_color=[(255, 255, 0), (0, 255, 0)]
    )
    print(f"DEBUG: image_path={image_path}, image={type(image)}, shape={getattr(image, 'shape', None)}")
    resized_image_array, offset_x, offset_y, scale_factor = resize_with_letterbox(
        image, (vehicle_model.input_shape[0][1], vehicle_model.input_shape[0][2])
        )
    if resized_image_array is None:
        print("Resized image is None. Skipping further processing.")
        return None, None, None, None
        
    detected_license_plates = lp_detection_model(resized_image_array)

    if detected_license_plates and detected_license_plates.results:
        for result in detected_license_plates.results:
            bbox = result.get("bbox")
            if bbox and len(bbox) == 4:
                # "Unletterbox" กลับไปยังภาพต้นฉบับ
                x_min = int((bbox[0] - offset_x) / scale_factor)
                y_min = int((bbox[1] - offset_y) / scale_factor)
                x_max = int((bbox[2] - offset_x) / scale_factor)
                y_max = int((bbox[3] - offset_y) / scale_factor)
                # ตรวจสอบขอบเขต
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(image.shape[1], x_max)
                y_max = min(image.shape[0], y_max)
                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
        # Save image with bounding box
        boxed_path = image_path.replace(".jpg", "_boxed.jpg")
        cv2.imwrite(boxed_path, image)
        cropped_license_plates = crop_license_plates(image, [{"bbox": [x_min, y_min, x_max, y_max]}])
        for index, cropped_plate in enumerate(cropped_license_plates):
            if cropped_plate is not None and cropped_plate.size > 0:
                print(f"Found cropped plate at index {index}")
                cropped_path = image_path.replace(".jpg", "_lp.jpg")
                cv2.imwrite(cropped_path, cropped_plate)
                return cropped_plate 
    return None

def read_text_with_easyocr(cropped_image):
    if cropped_image is None or not isinstance(cropped_image, np.ndarray):
        return "No Plate Detected"
    results = reader.readtext(cropped_image)
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

def save_csv_row(timestamp, distance, image_path, license_text, plate_width, plate_height,metadata):
    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp, distance, image_path, license_text, plate_width, plate_height,
            safe_float(metadata.get("ExposureTime")), safe_float(metadata.get("AnalogueGain")),
            safe_float(metadata.get("DigitalGain")), safe_float(metadata.get("LensPosition")),
            safe_float(metadata.get("FocusFoM")), metadata.get("AfState"), 
            safe_float(metadata.get("SensorTemperature")), safe_float(metadata.get("FrameDuration")), 
            safe_float(metadata.get("Lux"))
        ])

def run_interactive_experiment():
    ensure_csv_exists()
    while True:
        user_input = input("🔢 ระบุระยะห่าง (เมตร) หรือพิมพ์ 'q' เพื่อออก: ")
        if user_input.lower() == 'q':
            print("🛑 จบการทดลอง")
            break
        if not user_input.isdigit():
            print("⚠️ กรุณาใส่ตัวเลขหรือ 'q' เพื่อออก")
            continue
        distance = int(user_input)
        print(f"📸 เริ่มถ่ายภาพที่ระยะ {distance} เมตร...")
        image_path, metadata_dict, timestamp = capture_image(distance)
        print(f"📷 บันทึกภาพที่: {image_path}")
        print(f"📝 บันทึกข้อมูลเมตาดาต้า: {metadata_dict}")
        print(f"⏰ เวลาที่บันทึก: {timestamp}")
        if not os.path.exists(image_path):
            print(f"❌ ไม่พบไฟล์ภาพ: {image_path}")
            continue
        cropped = detect_license_plate(image_path)
        if isinstance(cropped, tuple):
            cropped = cropped[0]
        if cropped is not None and isinstance(cropped, np.ndarray):
            plate_height, plate_width = cropped.shape[:2]
        else:
            plate_height, plate_width = None, None
        license_text = read_text_with_easyocr(cropped)
        save_csv_row(timestamp, distance, image_path, license_text, plate_width, plate_height,metadata_dict )
        print(f"✅ อ่านป้ายทะเบียน: {license_text}\n")

if __name__ == "__main__":
    run_interactive_experiment()
