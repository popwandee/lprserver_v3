import os
import cv2
import degirum as dg
from dotenv import load_dotenv

# Load .env
env_path = os.path.join(os.path.dirname(__file__), 'src', '.env.production')
load_dotenv(env_path)

# Load vehicle detection model
vehicle_model = dg.load_model(
    model_name=os.getenv("VEHICLE_DETECTION_MODEL"),
    inference_host_address=os.getenv("HEF_MODEL_PATH"),
    zoo_url=os.getenv("MODEL_ZOO_URL")
)

# Ensure output directory
input_folder = "img/vehicle"
output_folder = "output/vehicle_crop"
os.makedirs(output_folder, exist_ok=True)

# Process each image in input folder
for fname in os.listdir(input_folder):
    if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    img_path = os.path.join(input_folder, fname)
    img = cv2.imread(img_path)
    if img is None:
        print(f"[ERROR] Cannot read image: {img_path}")
        continue

    orig_h, orig_w = img.shape[:2]
    input_h, input_w = vehicle_model.input_shape[0][1], vehicle_model.input_shape[0][2]

    # Resize and predict
    resized = cv2.resize(img, (input_w, input_h))

    # Keep track of scale
    orig_h, orig_w = img.shape[:2]
    input_h, input_w = resized.shape[:2]
    # Scale factors
    scale_x = orig_w / input_w
    scale_y = orig_h / input_h

    results = vehicle_model(resized)
    vehicle_boxes = getattr(results, "results", [])
    

    if not vehicle_boxes:
        print(f"[INFO] No vehicles found in: {fname}")
        continue
    else:
        print(f"[RAW DETECTION] {fname}: {vehicle_boxes}")

    

    # Process first vehicle only
    for box in vehicle_boxes:
        if isinstance(box, dict):
            x1 = int(box.get("bbox", [0, 0, 0, 0])[0] * scale_x)
            y1 = int(box.get("bbox", [0, 0, 0, 0])[1] * scale_y)
            x2 = int(box.get("bbox", [0, 0, 0, 0])[2] * scale_x)
            y2 = int(box.get("bbox", [0, 0, 0, 0])[3] * scale_y)
        else:
            x1 = int(box[0] * scale_x)
            y1 = int(box[1] * scale_y)
            x2 = int(box[2] * scale_x)
            y2 = int(box[3] * scale_y)
        # Clamp to image bounds
        x1 = max(0, min(orig_w - 1, x1))
        x2 = max(0, min(orig_w, x2))
        y1 = max(0, min(orig_h - 1, y1))
        y2 = max(0, min(orig_h, y2))

        # Draw box on original image for debug
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{box.get('label', '')} {box.get('confidence', 0):.2f}"
        cv2.putText(img, label, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        # Show or save for review
        debug_output_path = os.path.join("output/debug", fname)
        os.makedirs("output/debug", exist_ok=True)
        cv2.imwrite(debug_output_path, img)
        print(f"[DEBUG] Saved debug image: {debug_output_path}")

        # Crop the vehicle from the original image
        crop = img[y1:y2, x1:x2]
        print(f"[INFO] Cropped vehicle from: {fname} at [CROP] [x1:{x1}, y1:{y1}, x2:{x2}, y2:{y2}],orig size={orig_w}x{orig_h}")
        if crop.size == 0:
            print(f"[WARNING] Empty crop for: {fname}→ size: {crop.shape}")
        else:
            print(f"[INFO] Crop size: {crop.shape[1]}x{crop.shape[0]} for {fname}")
            output_path = os.path.join(output_folder, fname)
            cv2.imwrite(output_path, crop)
            print(f"[OK] Cropped and saved: {output_path}")
        break  # Only process first vehicle
