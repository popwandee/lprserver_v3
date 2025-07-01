from picamera2 import Picamera2 # Preview
import time
from datetime import datetime
import cv2
import numpy as np

def capture_and_annotate_image(output_filename="anotate_image.jpg",extracted_roi="roi_image.jpg"):
    """
    เปิดกล้อง PiCamera2, ถ่ายภาพ, เขียนค่าขอบเขตและจุดกึ่งกลางภาพ
    ลงบนภาพ และบันทึกเป็นไฟล์

    Args:
        output_filename (str): ชื่อไฟล์สำหรับบันทึกภาพ
    """
    picam2 = Picamera2()

    # กำหนดค่าคอนฟิกสำหรับกล้อง
    # คุณสามารถปรับ resolution ได้ตามต้องการ
    camera_config = picam2.create_still_configuration(main={"size": (4608, 2592)})
    picam2.configure(camera_config)

    #picam2.start_preview(Preview.QTGL)
    picam2.start()
    time.sleep(2)  # รอให้กล้องปรับแสงและโฟกัส

    print("กำลังถ่ายภาพ...")
    # ถ่ายภาพเป็น array
    image_array = picam2.capture_array()
    print("ถ่ายภาพสำเร็จ!")

    #picam2.stop_preview()
    picam2.stop()
    picam2.close()

    # แปลงภาพจาก BGR (PiCamera2) เป็น RGB (OpenCV ต้องการ)
    # หรือในกรณีนี้ PiCamera2.capture_array() ให้ RGB อยู่แล้ว
    # แต่บางครั้งอาจต้องการแปลงกลับมาเป็น BGR สำหรับ OpenCV
    # ถ้าภาพที่ได้ดูสีเพี้ยน ลอง uncomment บรรทัดนี้:
    # image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    image_bgr = image_array # สำหรับ PiCamera2 รุ่นใหม่ มักจะได้ BGR โดยตรง

    # ตรวจสอบให้แน่ใจว่าภาพเป็น BGR
    if image_bgr.shape[2] == 4: # ถ้าเป็น RGBA ให้แปลงเป็น BGR
        image_bgr = cv2.cvtColor(image_bgr, cv2.COLOR_RGBA2BGR)
    elif image_bgr.shape[2] == 3: # ถ้าเป็น RGB ให้แปลงเป็น BGR
        image_bgr = cv2.cvtColor(image_bgr, cv2.COLOR_RGB2BGR)

    # --- รับค่าขนาดความละเอียดของภาพ  ---
    height, width, _ = image_bgr.shape

    # กำหนดค่า x_max,  y_max (ขอบเขตภาพ)
    x_min = 0
    x_max = width - 1
    x_mean = width//2
    y_min = 0
    y_max = height - 1
    y_mean = height//2

    # คำนวณจุดกึ่งกลางภาพ
    center_x = width // 2
    center_y = height // 2

    # กำหนดตำแหน่งสำหรับเขียนข้อความ
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    font_thickness = 2
    text_color = (0, 0, 255)  # สีแดง (BGR)
    coord_point_color = (0, 255, 0) # เขียว
    line_type = cv2.LINE_AA

    # กำหนดขนาด ROI ที่ต้องการ 
    roi_width = 2300 
    roi_height = 1200
    # คำนวณพิกัดของ ROI # (x1, y1) ของมุมซ้ายบนของ ROI 
    roi_x1 = x_max - roi_width -400
    roi_y1 = y_max - roi_height -500
    # คำนวณพิกัดของ ROI # (x2, y2) ของมุมขวาล่างของ ROI 
    roi_x2 = x_max -400
    roi_y2 = y_max -500
    # ตรวจสอบให้แน่ใจว่า ROI ไม่ออกนอกขอบภาพ 
    roi_x1 = max(0, roi_x1)
    roi_y1 = max(0, roi_y1) 
    roi_x2 = min(width, roi_x2) 
    roi_y2 = min(height, roi_y2)

    # ตัดภาพ ROI ออกมา 
    roi = image_bgr[roi_y1:roi_y2, roi_x1:roi_x2]
    # วาดกรอบ ROI บนภาพต้นฉบับเพื่อแสดง 
    cv2.rectangle(image_bgr, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 255), 3) # สีเหลือง
    # บันทึก ROI 
    cv2.imwrite(output_filename, image_bgr) 
    cv2.imwrite(extracted_roi, roi)
if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"roi_image_{timestamp}.jpg"
    extracted_roi = f"roi_extracted_image_{timestamp}.jpg"
    capture_and_annotate_image(output_filename,extracted_roi)