แผนการพัฒนาส่วนการทดลองและวิจัยสำหรับ Flask web app 
--------------------------------------------------------------------------------
1. การใช้ Flask Web App Framework พร้อม Component และ Service ที่มีอยู่
ปัจจุบันคุณมี Flask web app Framework ที่มี Component และ Service พื้นฐานคือ Camera, Detection, และ Health Monitor ซึ่งทำงานได้อยู่แล้ว การพัฒนาส่วนการทดลองนี้จะถูกออกแบบให้ ทำงานร่วมกับ Component ที่มีอยู่ได้อย่างราบรื่น  โดยเฉพาะการใช้ Camera สำหรับการจับภาพ, Detection สำหรับการตรวจจับป้ายทะเบียน (ใช้โมเดล YOLO บน Hailo) และ Health Monitor สำหรับการตรวจสอบสถานะระบบในระหว่างการทดลอง.
2. Script สำหรับการทดลอง (สร้าง Component และ Service พร้อม Blueprint, Template)
เราจะสร้าง Component ใหม่ชื่อ Experiment ซึ่งจะประกอบด้วย Blueprint และ Service เพื่อจัดการขั้นตอนการทดลองทั้งหมด ตั้งแต่การเตรียมการ การทดลอง การเก็บรวบรวมข้อมูล และการสรุปผลเพื่อจัดทำรายงาน
2.1 โครงสร้าง Service Experiment (ตัวอย่าง)
# app/experiments/services.py

import os
import json
import csv
import cv2
from datetime import datetime
import numpy as np
import easyocr
import degirum as dg
import subprocess

# สมมติว่ามี Camera Service และ Detection Service อยู่แล้ว
# from app.camera.services import CameraService
# from app.detection.services import DetectionService

class ExperimentService:
    def __init__(self, app_config):
        self.app_config = app_config
        self.reader = easyocr.Reader(['th', 'en'])
        self.results_dir = app_config.get("EXPERIMENT_RESULTS_DIR", "experiment_results")
        os.makedirs(self.results_dir, exist_ok=True)
        self.csv_path = os.path.join(self.results_dir, "experiment_log.csv")
        self._ensure_csv_exists()

        # โหลดโมเดลสำหรับตรวจจับป้ายทะเบียน (อิงจากแหล่งข้อมูล 20, 61)
        self.lp_detection_model = dg.load_model(
            model_name=os.getenv("LICENSE_PLACE_DETECTION_MODEL"),
            inference_host_address=os.getenv("HEF_MODEL_PATH"),
            zoo_url=os.getenv("MODEL_ZOO_URL")
        )

    def _ensure_csv_exists(self):
        """ตรวจสอบและสร้างไฟล์ CSV สำหรับบันทึกผลการทดลองหากยังไม่มี"""
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "ExperimentType", "CameraType", "LensCover", "Distance(m)",
                    "LicenseTextCropped", "LicenseTextFull", "ConfidenceCrop", "ConfidenceFull",
                    "SharpnessLaplacian", "BlurGaussian",
                    "ExposureTime", "AnalogueGain", "DigitalGain",
                    "LensPosition", "FocusFoM", "AfState", "SensorTemperature", "FrameDuration", "Lux"
                ])
        print(f"CSV log file ensured at: {self.csv_path}") # สำหรับ Debug

    def run_experiment_step(self, experiment_config):
        """
        ดำเนินการทดลองในแต่ละ Step ตาม Config ที่ระบุ
        :param experiment_config: Dictionary ที่มี parameters สำหรับการทดลองปัจจุบัน
        """
        distance = experiment_config.get("distance_m")
        camera_type = experiment_config.get("camera_type")
        lens_cover = experiment_config.get("lens_cover")
        is_night_mode = experiment_config.get("is_night_mode", False)
        
        print(f"เริ่มถ่ายภาพที่ระยะ {distance} เมตร ด้วย {camera_type} และ Lens Cover {lens_cover} (กลางคืน: {is_night_mode})...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"{timestamp}_{camera_type}_{lens_cover}_{distance}m.jpg"
        metadata_name = f"{timestamp}_{camera_type}_{lens_cover}_{distance}m.json"
        image_path = os.path.join(self.results_dir, image_name)
        metadata_path = os.path.join(self.results_dir, metadata_name)

        # 1. Capture Image with rpicam-still (รวม metadata)
        # สำหรับการ capture และ สำหรับ metadata
        cmd = [
            "rpicam-still", "-o", image_path,
            "--metadata", metadata_path, "--metadata-format", "json",
            "--timeout", "1000", "--autofocus-on-capture" # ใช้ autofocus ก่อนจับภาพ 
        ]
        
        # ปรับค่าพารามิเตอร์กล้องตามโหมดกลางวัน/กลางคืน
        if is_night_mode:
            # สำหรับ Night Mode Parameters
            # ในการทดลองจริง อาจจะต้องวนลูปหรือเลือกค่าที่เหมาะสมจาก NIGHT_EXPOSURE_TIMES_US, NIGHT_ANALOG_GAINS
            # สำหรับตัวอย่างนี้ ผมจะสมมติว่ามีการส่งค่าที่ต้องการมาใน config หรือใช้ค่าเริ่มต้นที่ดีที่สุด
            exposure_time = experiment_config.get("exposure_time_us", 499989) # ค่าที่ดีที่สุดจาก 
            analog_gain = experiment_config.get("analog_gain", 16.0) # ค่าที่ดีที่สุด
            manual_lens_pos = experiment_config.get("lens_position", 0.07) # ค่าที่ดีที่สุด
            sharpness_val = experiment_config.get("sharpness", 2.0) # ค่าที่ดีที่สุด
            noise_red_mode = experiment_config.get("noise_reduction_mode", 0) # ค่าที่ดีที่สุด

            cmd.extend([
                "--exposure", str(exposure_time),
                "--gain", str(analog_gain),
                "--manual-focus", str(manual_lens_pos),
                "--sharpness", str(sharpness_val),
                "--denoise", str(noise_red_mode)
            ])
            # For simplicity, AwbModeEnum.Off and ae_enable=False are not directly passed to rpicam-still via cli here.
            # These would need to be set via picamera2 API if integrating directly, or via advanced rpicam-still options.
            # The current setup uses `--autofocus-on-capture` which might override some manual focus settings if not carefully handled.
            # For manual focus only, one might omit --autofocus-on-capture and control lens position directly.
            
        else: # Day mode
            # สำหรับ Day Mode Parameters
            # สามารถเพิ่มการปรับค่า sharpness, noise reduction ได้เช่นกัน 
            # --autofocus-on-capture ใช้ได้ดีในเวลากลางวัน
            pass # ใช้ค่าเริ่มต้นของ rpicam-still หรือกำหนดใน config

        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # 2. Extract Metadata
        metadata = self._extract_metadata(metadata_path)

        # 3. Detect License Plate and Crop
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image at {image_path}")
            return None

        # ปรับขนาดภาพให้เข้ากับโมเดล YOLO 
        resized_image_array = self._resize_with_letterbox(image, (self.lp_detection_model.input_shape, self.lp_detection_model.input_shape))
        
        cropped_plate_image = None
        license_plate_detected = "Failed"
        if resized_image_array is not None:
            try:
                # การตรวจจับป้ายทะเบียน
                detected_license_plates = self.lp_detection_model(resized_image_array) [14]
                if detected_license_plates and detected_license_plates.results:
                    # ครอบตัดป้ายทะเบียน 
                    cropped_plates = self._crop_license_plates(image, detected_license_plates.results)
                    if cropped_plates:
                        cropped_plate_image = cropped_plates # เลือกป้ายแรกที่เจอ
                        license_plate_detected = "Good"
            except Exception as e:
                print(f"Error during license plate detection: {e}")

        # 4. OCR on Cropped Image (เน้นความแม่นยำของข้อความ)
        license_text_cropped = self._read_text_with_easyocr(cropped_plate_image) if cropped_plate_image is not None else "No Plate Detected"
        confidence_cropped = self._calculate_ocr_confidence(license_text_cropped, "กก 6014 อุบลราชธานี") # คำนวณความแม่นยำเทียบกับป้ายจริง

        # 5. OCR on Full Image (เพื่อเก็บ Confidence Score)
        license_text_full = self._read_text_with_easyocr(image)
        confidence_full = self._calculate_ocr_confidence_from_easyocr_results(self.reader.readtext(image)) # อ่าน confidence จากผลลัพธ์ OCR

        # 6. Analyze Image Quality (Sharpness and Blur)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sharpness_laplacian = cv2.Laplacian(gray_image, cv2.CV_64F).var() 
        blur_gaussian = filters.gaussian(gray_image, sigma=1).std()     (ต้อง import skimage.filters as filters)

        # 7. Save Results to CSV
        self._save_csv_row(
            timestamp, experiment_config.get("experiment_type", "Unknown"), camera_type, lens_cover, distance,
            license_text_cropped, license_text_full, confidence_cropped, confidence_full,
            sharpness_laplacian, blur_gaussian,
            metadata.get("ExposureTime"), metadata.get("AnalogueGain"), metadata.get("DigitalGain"),
            metadata.get("LensPosition"), metadata.get("FocusFoM"), metadata.get("AfState"),
            metadata.get("SensorTemperature"), metadata.get("FrameDuration"), metadata.get("Lux")
        )

        return {
            "status": "success",
            "image_path": image_path,
            "license_text_cropped": license_text_cropped,
            "confidence_cropped": confidence_cropped,
            "sharpness_laplacian": sharpness_laplacian,
            "blur_gaussian": blur_gaussian,
            "metadata": metadata,
            "license_plate_detected": license_plate_detected
        }

    # Helper methods 
    def _resize_with_letterbox(self, image, target_size=(640, 640), padding_value=(0, 0, 0)):

        if image is None or not isinstance(image, np.ndarray):
            print("resize_with_letterbox received Captured image is invalid input!")
            return None
        if len(image.shape) == 3 and image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_height, original_width, channels = image.shape
        target_height, target_width = target_size
        scale_factor = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        letterboxed_image = np.full((target_height, target_width, channels), padding_value, dtype=np.uint8)
        offset_y = (target_height - new_height) // 2
        offset_x = (target_width - new_width) // 2
        letterboxed_image[offset_y:offset_y + new_height, offset_x:offset_x + new_width] = resized_image
        return letterboxed_image

    def _crop_license_plates(self, image, results):
        cropped_images = []
        for result in results:
            bbox = result.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            x_min, y_min, x_max, y_max = map(int, bbox)
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(image.shape[15], x_max)
            y_max = min(image.shape, y_max)
            if x_min >= x_max or y_min >= y_max: # ตรวจสอบ bounding box ที่ไม่ถูกต้อง
                print(f"Warning: Invalid bounding box coordinates: {bbox}")
                continue
            cropped_images.append(image[y_min:y_max, x_min:x_max])
        return cropped_images

    def _extract_metadata(self, metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            return {
                "ExposureTime": metadata.get("ExposureTime"),
                "AnalogueGain": metadata.get("AnalogueGain"),
                "DigitalGain": metadata.get("DigitalGain"),
                "LensPosition": metadata.get("LensPosition"),
                "FocusFoM": metadata.get("FocusFoM"),
                "AfState": metadata.get("AfState"),
                "SensorTemperature": metadata.get("SensorTemperature"),
                "FrameDuration": metadata.get("FrameDuration"),
                "Lux": metadata.get("Lux")
            }
        except FileNotFoundError:
            print(f"Metadata file not found: {metadata_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from metadata file: {metadata_path}")
            return {}

    def _read_text_with_easyocr(self, img):
        if img is None or img.size == 0:
            return "No Plate Detected"
        try:
            results = self.reader.readtext(img)
            return " ".join([res for res in results]) if results else "No Text"
        except Exception as e:
            print(f"Error during EasyOCR processing: {e}")
            return "OCR Error"

    def _calculate_ocr_confidence(self, ocr_text, target_text="กก 6014 อุบลราชธานี"):
        """คำนวณความแม่นยำของ OCR Text เทียบกับ Target Text """
        if ocr_text == target_text:
            return 1.0 # อ่านได้ถูกต้อง 100%
        # สามารถเพิ่ม logic fuzzy matching หรือ regex ได้ที่นี่
        # เช่น หากมี "กก 6014" ตรงกัน แต่จังหวัดไม่ตรง
        # สำหรับตัวอย่างนี้ ให้ 0.0 ถ้าไม่ตรงเป๊ะ หรือมีข้อผิดพลาด
        return 0.0 # ถ้าไม่ตรงเป๊ะ
    
    def _calculate_ocr_confidence_from_easyocr_results(self, ocr_results):
        """ดึงค่า confidence เฉลี่ยจากผลลัพธ์ EasyOCR"""
        if not ocr_results:
            return 0.0
        total_confidence = sum(res for res in ocr_results)
        return total_confidence / len(ocr_results)


    def summarize_results(self, experiment_id):
        """
        อ่านและสรุปผลการทดลองจาก CSV
        :param experiment_id: ID ของการทดลองที่จะสรุป
        :return: ข้อมูลสรุปผล (เช่น ตาราง, กราฟ)
        """
        # ควรมี logic กรองข้อมูลจาก CSV ตาม experiment_id
        # และสร้างรายงาน สถิติ, กราฟ 
        # เช่น อัตราความสำเร็จในการตรวจจับ, ความแม่นยำของ OCR, แนวโน้ม Sharpness/Blur
        
        # ตัวอย่างการอ่าน CSV และกรองข้อมูล
        results = []
        with open(self.csv_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # ตัวอย่างการกรองตาม experiment_id (ต้องเพิ่ม experiment_id ใน CSV ด้วย)
                # if row.get("ExperimentID") == experiment_id:
                results.append(row)
        
        # สำหรับการทดลอง Night Mode Lens Comparison:
        # เปรียบเทียบ Sharpness, OCR Confidence, และความถูกต้องของข้อความที่อ่านได้
        # ระหว่าง IMX708, IMX708 Wide, IMX708 NoIR ที่แต่ละระยะในเวลากลางคืน
        # และอาจจะต้องพิจารณาค่า Exposure Time, Analog Gain ที่ใช้ด้วย 
        
        summary_data = {
            "total_records": len(results),
            "summary_by_camera_type": {},
            # สามารถเพิ่มกราฟข้อมูลได้ที่นี่
        }
        
        # ตัวอย่างการสรุปผล (สามารถขยายได้ตามต้องการ)
        for row in results:
            cam_type = row.get("CameraType", "N/A")
            if cam_type not in summary_data["summary_by_camera_type"]:
                summary_data["summary_by_camera_type"][cam_type] = {
                    "correct_ocr_count": 0,
                    "total_ocr_attempts": 0,
                    "avg_sharpness": [],
                    "avg_confidence_cropped": []
                }
            
            if row.get("LicenseTextCropped") == "กก 6014 อุบลราชธานี":
                summary_data["summary_by_camera_type"][cam_type]["correct_ocr_count"] += 1
            if row.get("LicenseTextCropped") != "No Plate Detected":
                 summary_data["summary_by_camera_type"][cam_type]["total_ocr_attempts"] += 1

            try:
                summary_data["summary_by_camera_type"][cam_type]["avg_sharpness"].append(float(row.get("SharpnessLaplacian", 0)))
                summary_data["summary_by_camera_type"][cam_type]["avg_confidence_cropped"].append(float(row.get("ConfidenceCrop", 0)))
            except ValueError:
                pass # จัดการค่าที่แปลงไม่ได้

        for cam_type, data in summary_data["summary_by_camera_type"].items():
            data["avg_sharpness"] = np.mean(data["avg_sharpness"]) if data["avg_sharpness"] else 0
            data["avg_confidence_cropped"] = np.mean(data["avg_confidence_cropped"]) if data["avg_confidence_cropped"] else 0
            data["accuracy_rate"] = (data["correct_ocr_count"] / data["total_ocr_attempts"]) if data["total_ocr_attempts"] > 0 else 0


        return summary_data

    def get_experiment_details(self, experiment_id):
        """ดึงรายละเอียดของ experiment ID นั้นๆ"""
        # อ่านจากไฟล์ config หรือ database
        pass
2.2 การทดลองเพิ่มเติม: เปรียบเทียบสภาพแสงในเวลากลางคืน (เลนส์ Normal, Wide, NoIR ที่ระยะ 1 ถึง 10 เมตร)
การทดลองนี้จะใช้แนวทางเดียวกับการทดลองเปรียบเทียบเลนส์ในเวลากลางวัน แต่ปรับเปลี่ยนเงื่อนไขเป็นเวลากลางคืน โดยอ้างอิงค่าพารามิเตอร์สำหรับกลางคืนที่ระบุไว้ในการค้นหาค่าพารามิเตอร์กล้อง:
• อุปกรณ์: Raspberry Pi 5, Hailo 8 AI Accelerator.
• กล้อง: Camera Module 3 (Sony IMX708 - Standard), IMX708 Wide FoV, IMX708 NoIR.
• ป้ายทะเบียน: "กก 6014 อุบลราชธานี" (ติดบนยานพาหนะ).
• ระยะการทดสอบ: 1 ถึง 10 เมตร (เพิ่มขึ้นทีละ 1 เมตร).
• การตั้งค่าสำหรับกลางคืน:
    ◦ ae_enable = False (ปิด Auto Exposure)
    ◦ awb_mode = controls.AwbModeEnum.Off.value (ปิด Auto White Balance)
    ◦ exposure_time_values = NIGHT_EXPOSURE_TIMES_US (100000, 200000, 300000, 400000, 500000 ไมโครวินาที)
    ◦ analog_gain_values = NIGHT_ANALOG_GAINS (1.0, 2.0, 4.0, 8.0, 16.0)
    ◦ Focus mode: Manual, Lens Position (อาจใช้ 0.07 ซึ่งเป็นค่าที่ชัดที่สุดในการทดลองกลางคืนก่อนหน้า)
    ◦ Sharpness: 2, Noise reduction: Off (ค่าที่ดีที่สุดในการทดลองกลางคืนก่อนหน้า)
    ◦ ควรมีการทดลองหาค่า Exposure/Gain/Lens Position ที่เหมาะสมที่สุดสำหรับแต่ละเลนส์ในเวลากลางคืนด้วย (Grid Search) หรือใช้ค่าที่ได้จาก "การค้นหาค่าพารามิเตอร์กล้อง"
• ขั้นตอนการทดลอง:
    1. ติดตั้งกล้อง/เลนส์ และเลนส์ครอบ (อาจทดสอบทั้ง Curve และ Flat เหมือนเดิม).
    2. กำหนดป้ายทะเบียนที่ระยะต่าง ๆ (1-10 เมตร).
    3. จับภาพและดึงข้อมูล metadata.
    4. ประมวลผลภาพ: ตรวจจับป้ายทะเบียนด้วย YOLO บน Hailo, ครอบตัด ROI.
    5. อ่านป้ายทะเบียนด้วย EasyOCR (ทั้งภาพที่ครอบตัดและทั้งภาพ), บันทึกค่า confidence.
    6. วิเคราะห์ความคมชัด (Laplacian Variance) และความเบลอ (Gaussian Blur Score).
    7. บันทึกผลทั้งหมดลงใน CSV.
• เกณฑ์การประเมิน: ความถูกต้องของข้อความที่อ่านได้ ("กก 6014 อุบลราชธานี") มีความสำคัญที่สุด. รองลงมาคือ OCR Confidence, Sharpness และ Blur Score.
• ข้อควรพิจารณา: กล้อง IMX708 NoIR คาดว่าจะแสดงประสิทธิภาพได้ดีกว่าในสภาพแสงน้อย/กลางคืน. ต้องระวังปัญหาการตรวจจับป้ายทะเบียนที่ระยะ 1-2 เมตรเนื่องจากมุมกล้องเช่นเดียวกับการทดลองกลางวัน.
3. Flowchart ลำดับการทำงานของ Service (PlantUML)
@startuml
skinparam handwritten true
skinparam style strict

actor User
participant "Flask Web App" as FlaskApp
boundary "Experiment Dashboard" as Dashboard
control "Experiment Blueprint" as ExperimentBP
entity "Experiment Service" as ExperimentSvc
entity "Camera Service" as CameraSvc
entity "Detection Service" as DetectionSvc
database "Experiment Data (CSV/DB)" as DataStorage
cloud "Hailo-8 AI Accel." as HailoAI
external_system "EasyOCR API" as EasyOCR

User -> FlaskApp : Access /experiments
FlaskApp -> ExperimentBP : Route request
ExperimentBP -> Dashboard : Display Experiment Dashboard (list, new experiment)

User -> Dashboard : Select "Create New Experiment"
Dashboard -> ExperimentBP : POST /experiments/new (Experiment Config)

ExperimentBP -> ExperimentSvc : Create Experiment Configuration (config_id)
ExperimentSvc -> DataStorage : Save Experiment Config
ExperimentSvc --> ExperimentBP : Return config_id

User -> Dashboard : Select "Run Experiment" (config_id)
Dashboard -> ExperimentBP : GET /experiments/run/<config_id>

loop For Each Distance (1 to 10m)
    ExperimentBP -> ExperimentBP : Display "Run Experiment" Page (live view, controls)
    User -> ExperimentBP : Click "Next Step" or "Start Automatic Run"
    ExperimentBP -> ExperimentSvc : run_experiment_step(current_config)

    ExperimentSvc -> CameraSvc : Capture Image (rpicam-still) with requested params (e.g., night mode settings)
    CameraSvc --> ExperimentSvc : Return Image Path & Metadata Path

    ExperimentSvc -> DetectionSvc : Load LP Detection Model (YOLO)
    DetectionSvc -> HailoAI : Infer License Plate Detection
    HailoAI --> DetectionSvc : Return Bounding Boxes

    DetectionSvc --> ExperimentSvc : Return Detection Results

    ExperimentSvc -> ExperimentSvc : Crop License Plate Image
    ExperimentSvc -> EasyOCR : Send Cropped Image for OCR
    EasyOCR --> ExperimentSvc : Return OCR Text & Confidence (Cropped)

    ExperimentSvc -> EasyOCR : Send Full Image for OCR
    EasyOCR --> ExperimentSvc : Return OCR Text & Confidence (Full)

    ExperimentSvc -> ExperimentSvc : Calculate Sharpness (Laplacian) & Blur (Gaussian)
    ExperimentSvc -> DataStorage : Save Step Results (Image, Metadata, OCR, Metrics)
    DataStorage --> ExperimentSvc : Confirm Save
    ExperimentSvc --> ExperimentBP : Return Step Status & Latest Data
    ExperimentBP -> ExperimentBP : Update "Run Experiment" Page
end

User -> ExperimentBP : Click "Stop Experiment" or All steps completed
ExperimentBP -> ExperimentSvc : summarize_results(config_id)
ExperimentSvc -> DataStorage : Retrieve all results for config_id
DataStorage --> ExperimentSvc : Return Raw Results
ExperimentSvc -> ExperimentSvc : Aggregate & Analyze Results (e.g., accuracy, trends)
ExperimentSvc --> ExperimentBP : Return Summary Data
ExperimentBP -> ExperimentBP : Display "Experiment Results" Page (tables, graphs)
User -> ExperimentBP : View/Download Report

@enduml
4. ออกแบบ Blueprint และ Template สำหรับผู้ใช้
4.1 Blueprint (app/experiments/routes.py)
# app/experiments/routes.py

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from .services import ExperimentService
import uuid

experiment_bp = Blueprint('experiments', __name__, url_prefix='/experiments',
                          template_folder='templates', static_folder='static')

# initialize service
def get_experiment_service():
    if 'experiment_service' not in current_app.extensions:
        current_app.extensions['experiment_service'] = ExperimentService(current_app.config)
    return current_app.extensions['experiment_service']

@experiment_bp.route('/')
def dashboard():
    # แสดงรายการการทดลองที่ผ่านมา
    # สามารถดึงข้อมูลสรุปสั้นๆ มาแสดงได้
    return render_template('experiments/dashboard.html', active_page='experiments')

@experiment_bp.route('/new', methods=['GET', 'POST'])
def new_experiment():
    if request.method == 'POST':
        # รับค่าจาก Form และสร้าง experiment_config
        exp_id = str(uuid.uuid4()) # สร้าง ID เฉพาะสำหรับการทดลองนี้
        experiment_config = {
            "experiment_id": exp_id,
            "experiment_type": request.form.get("experiment_type"), # เช่น "Night Mode Lens Comparison"
            "camera_type": request.form.getlist("camera_type"), # เลือกได้หลายตัว: IMX708, IMX708Wide, IMX708NoIR
            "lens_cover": request.form.getlist("lens_cover"), # เลือกได้หลายตัว: Curve, Flat
            "start_distance_m": int(request.form.get("start_distance_m", 1)),
            "end_distance_m": int(request.form.get("end_distance_m", 10)),
            "step_distance_m": int(request.form.get("step_distance_m", 1)),
            "is_night_mode": request.form.get("is_night_mode") == "on",
            "night_exposure_times": request.form.getlist("night_exposure_times"), # ถ้าเป็น Night mode
            "night_analog_gains": request.form.getlist("night_analog_gains"),   # ถ้าเป็น Night mode
            # เพิ่ม parameter อื่นๆ 
        }
        # ควรมี logic บันทึก experiment_config นี้ไว้
        current_app.config['current_experiment_config'] = experiment_config # สำหรับตัวอย่างแบบง่ายๆ
        
        return redirect(url_for('experiments.run_experiment', experiment_id=exp_id))
    
    # สำหรับ GET request: แสดง Form สำหรับสร้างการทดลองใหม่
    return render_template('experiments/new_experiment.html', active_page='experiments')

@experiment_bp.route('/run/<experiment_id>')
def run_experiment(experiment_id):
    # ดึง config ของการทดลอง
    # สำหรับการนำเสนอ ให้ใช้ config ที่เก็บไว้ชั่วคราว
    experiment_config = current_app.config.get('current_experiment_config')
    if not experiment_config or experiment_config['experiment_id'] != experiment_id:
        # ควรโหลดจาก DB หรือไฟล์ config จริงๆ
        return "Experiment not found or invalid config.", 404

    # แสดงหน้าจอสำหรับ run การทดลองทีละ step
    # แสดง live view, ปุ่มควบคุม
    return render_template('experiments/run_experiment.html', 
                           experiment_id=experiment_id, 
                           experiment_config=experiment_config,
                           active_page='experiments')

@experiment_bp.route('/api/run_step/<experiment_id>', methods=['POST'])
def api_run_step(experiment_id):
    exp_service = get_experiment_service()
    data = request.json
    current_distance = data.get('current_distance')
    current_camera_type = data.get('current_camera_type')
    current_lens_cover = data.get('current_lens_cover')
    is_night_mode = data.get('is_night_mode', False)

    # สร้าง config ย่อยสำหรับ step นี้
    step_config = {
        "experiment_id": experiment_id,
        "distance_m": current_distance,
        "camera_type": current_camera_type,
        "lens_cover": current_lens_cover,
        "is_night_mode": is_night_mode,
        # ส่งค่า parameter กลางคืนที่เลือกไปให้ service
        "exposure_time_us": data.get("exposure_time_us"),
        "analog_gain": data.get("analog_gain"),
        "lens_position": data.get("lens_position"),
        "sharpness": data.get("sharpness"),
        "noise_reduction_mode": data.get("noise_reduction_mode")
    }

    result = exp_service.run_experiment_step(step_config)
    return jsonify(result)

@experiment_bp.route('/results/<experiment_id>')
def view_results(experiment_id):
    exp_service = get_experiment_service()
    summary = exp_service.summarize_results(experiment_id) # สรุปผลการทดลอง
    # ดึงข้อมูลดิบจาก CSV หรือ DB เพื่อแสดงในตาราง
    
    return render_template('experiments/results.html', 
                           experiment_id=experiment_id, 
                           summary=summary, 
                           active_page='experiments')
4.2 Templates (ภายใต้ app/experiments/templates/experiments/)
• dashboard.html:
    ◦ แสดงภาพรวมของการทดลองที่เคยทำ
    ◦ ปุ่ม "สร้างการทดลองใหม่" (link ไปที่ /new)
    ◦ ตารางรายชื่อการทดลองที่ผ่านมา พร้อมสถานะ (Finished, Running) และลิงก์ไปยังหน้าผลลัพธ์ (/results/<id>) หรือหน้า Run (/run/<id>)
• new_experiment.html:
    ◦ Form สำหรับกำหนดค่าการทดลอง:
        ▪ ชื่อการทดลอง: Text input
        ▪ ประเภทการทดลอง: Dropdown/Radio (เช่น "ค้นหาพารามิเตอร์กล้อง", "ทดสอบระยะการอ่านป้ายทะเบียน", "เปรียบเทียบเลนส์กลางวัน", "เปรียบเทียบเลนส์กลางคืน")
        ▪ ประเภทกล้อง: Checkbox/Multi-select (IMX708, IMX708 Wide, IMX708 NoIR)
        ▪ ประเภทเลนส์ครอบ: Checkbox/Multi-select (Curve, Flat)
        ▪ ช่วงระยะการทดลอง (เมตร): Start, End, Step (Input numbers)
        ▪ โหมดแสง: Radio (กลางวัน, กลางคืน)
        ▪ Parameter สำหรับกลางคืน (ถ้าเลือก): Dropdowns/Checkboxes สำหรับ Exposure Times, Analog Gains, Manual Lens Positions, Sharpness, Noise Reduction.
        ▪ ปุ่ม "เริ่มการทดลอง" (Submit form)
• run_experiment.html:
    ◦ ส่วนแสดงภาพสด/ภาพที่บันทึก: แสดงภาพล่าสุดที่ถ่าย (พร้อม Bounding Box)
    ◦ ส่วนแสดงผลลัพธ์ Real-time:
        ▪ ระยะปัจจุบัน
        ▪ ข้อความ OCR ที่อ่านได้ (จากภาพที่ครอบตัด) และ Confidence Score
        ▪ ค่า Sharpness (Laplacian), Blur Score
        ▪ Metadata กล้อง (Exposure, Gain, FocusFoM, Lens Position)
    ◦ ส่วนควบคุม:
        ▪ ปุ่ม "Next Distance" (ปรับระยะห่างอัตโนมัติ)
        ▪ ปุ่ม "Stop Experiment"
        ▪ แสดงสถานะการทดลอง (กำลังดำเนินการ, รอผู้ใช้)
    ◦ ใช้ JavaScript/AJAX เพื่อเรียก api/run_step และอัปเดต UI
• results.html:
    ◦ ส่วนสรุปผล: ตารางสรุปภาพรวม เช่น อัตราความสำเร็จของ OCR, ค่า Sharpness เฉลี่ย, เลนส์/ระยะที่ดีที่สุด (อิงจาก)
    ◦ กราฟ:
        ▪ OCR Confidence vs Distance (แยกตามประเภทกล้อง/เลนส์ครอบ)
        ▪ Sharpness & Blur vs Distance (แยกตามประเภทกล้อง/เลนส์ครอบ)
        ▪ สามารถสร้างกราฟอื่นๆ เช่น Exposure/Gain vs Distance ได้
    ◦ ตารางข้อมูลดิบ: แสดงผลลัพธ์ของแต่ละ Step จาก CSV พร้อมรายละเอียดทั้งหมด เพื่อให้ผู้ใช้สามารถวิเคราะห์เพิ่มเติม
    ◦ ปุ่ม "ดาวน์โหลดรายงาน (CSV/PDF)"
5. Sprint สำหรับพัฒนาส่วนนี้ (3 วัน)
นี่คือแผน Sprint 3 วันสำหรับการพัฒนาส่วน "Experiment Automation & Research" บน GitHub:
Sprint Goal: Develop a Flask web interface for camera experiments, enabling configuration, execution, data collection, and basic reporting, with initial support for night mode lens comparison.
Milestone: Experiment_Automation_v1.0_Initial_Release
--------------------------------------------------------------------------------
Day 1: Foundation & Experiment Setup
• Issue #1: Setup Flask Blueprint & Basic Routes
    ◦ Task 1.1: Create app/experiments directory. (2 hours)
    ◦ Task 1.2: Define experiment_bp Blueprint in app/experiments/routes.py. (2 hours)
    ◦ Task 1.3: Implement dashboard() route and dashboard.html template. (3 hours)
    ◦ Task 1.4: Implement new_experiment() route (GET and POST) and new_experiment.html template with basic form fields for experiment type, camera type, lens cover, and distances. (8 hours)
    ◦ Task 1.5: Register experiment_bp with the main Flask app. (1 hour)
• Issue #2: Implement Core Experiment Service & Data Model
    ◦ Task 2.1: Create app/experiments/services.py and define ExperimentService class. (4 hours)
    ◦ Task 2.2: Implement __init__ method, _ensure_csv_exists for data logging. (3 hours)
    ◦ Task 2.3: Integrate easyocr and degirum model loading into ExperimentService. (4 hours)
--------------------------------------------------------------------------------
Day 2: Experiment Execution & Data Collection
• Issue #3: Develop Core Experiment Logic (run_experiment_step)
    ◦ Task 3.1: Implement run_experiment_step in ExperimentService for image capture using rpicam-still. (6 hours) 
    ◦ Task 3.2: Implement metadata extraction (_extract_metadata). (4 hours) [อ้างอิงจาก 22]
    ◦ Task 3.3: Implement license plate detection (_resize_with_letterbox, _crop_license_plates). (8 hours) 
    ◦ Task 3.4: Implement OCR processing (_read_text_with_easyocr) for both cropped and full images. (4 hours) 
    ◦ Task 3.5: Implement sharpness (Laplacian) and blur (Gaussian) calculation. (4 hours) 
• Issue #4: Design & Implement User Interfaces for Running Experiment
    ◦ Task 4.1: Implement run_experiment() route and run_experiment.html template for step-by-step execution. (6 hours)
    ◦ Task 4.2: Develop AJAX endpoint api/run_step to call run_experiment_step service. (4 hours)
    ◦ Task 4.3: Implement JavaScript on run_experiment.html to send requests and update UI with live results. (6 hours)
--------------------------------------------------------------------------------
Day 3: Reporting & Night Mode Integration
• Issue #5: Implement Results Summary & Reporting
    ◦ Task 5.1: Implement _save_csv_row to log all collected data. (4 hours) [อ้างอิงจาก 24, 61]
    ◦ Task 5.2: Implement summarize_results() in ExperimentService to read and aggregate data from CSV. (8 hours) [อ้างอิงจาก 10, 61]
    ◦ Task 5.3: Implement view_results() route and results.html template to display summary tables and basic graphs (using chart.js or similar for frontend). (8 hours)
• Issue #6: Integrate Night Mode Lens Comparison Experiment Specifics
    ◦ Task 6.1: Update new_experiment.html form to include specific parameters for Night Mode (Exposure Times, Analog Gains, Manual Lens Position, Sharpness, Noise Reduction). (4 hours) [อ้างอิงจาก 3, 4, 5, 7]
    ◦ Task 6.2: Modify run_experiment_step to apply Night Mode parameters to rpicam-still command when is_night_mode is true. (4 hours)
--------------------------------------------------------------------------------
หมายเหตุ:
• เวลาที่ประมาณไว้เป็นเพียงแนวทาง อาจมีการปรับเปลี่ยนตามความซับซ้อนและทักษะของทีม.
• การรวม CameraService และ DetectionService เข้าไปใน ExperimentService ในโค้ดตัวอย่างนี้ทำเพื่อความกระชับ แต่ในระบบจริงควรมีการ DI (Dependency Injection) หรือเรียกใช้ผ่าน current_app.extensions หรือที่เก็บ Service กลาง.
• rpicam-still เป็น command line tool การควบคุมพารามิเตอร์ที่ละเอียดอ่อน (เช่น Auto Exposure, Auto White Balance on/off) อาจต้องใช้ picamera2 Python library โดยตรงแทน subprocess.run.
• สำหรับการวิเคราะห์ผลและสร้างกราฟบน results.html ควรใช้ JavaScript library เช่น Chart.js หรือ D3.js โดยดึงข้อมูลจาก AJAX endpoint ที่ส่งข้อมูลสรุปมาให้.
• การทำ Post-processing สำหรับ OCR (regex/verify) สามารถเพิ่มเป็น Task ในภายหลังได้.