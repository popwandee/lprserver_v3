from picamera2 import Picamera2 # Preview
import time
from datetime import datetime
import cv2
import numpy as np

def capture_and_annotate_image(output_filename="anotate_image.jpg",annotate_roi = "roi_annotate_image.jpg",extracted_roi="roi_image.jpg"):
    """
    เปิดกล้อง PiCamera2, ถ่ายภาพ, เขียนค่าขอบเขตและจุดกึ่งกลางภาพ
    ลงบนภาพ และบันทึกเป็นไฟล์

    Args:
        output_filename (str): ชื่อไฟล์สำหรับบันทึกภาพ
    """
    picam2 = Picamera2()

    # กำหนดค่าคอนฟิกสำหรับกล้อง
    # คุณสามารถปรับ resolution ได้ตามต้องการ
    camera_config = picam2.create_still_configuration(main={"size": (3280, 2464)}) #main={"size": (4608, 2592)}
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

    # --- คำนวณค่าและเขียนข้อความลงบนภาพ ---
    height, width, _ = image_bgr.shape

    # กำหนดค่า x_min, x_max, y_min, y_max (ขอบเขตภาพ)
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

    # กำหนดตำแหน่งข้อความและวาดจุด
    # ตรวจสอบให้แน่ใจว่าพิกัดทั้งหมดเป็นจำนวนเต็ม
    text_positions = {
        "Top_Left": (x_min + 1, y_min + 50), # เพิ่ม y offset เพื่อไม่ให้ทับขอบ
        "Bottom_Left": (x_min + 1, y_max - 10),
        "Top_Right": (x_max - 500, y_min + 50), # ปรับ x offset ให้ข้อความไม่ล้นขอบ
        "Bottom_Right": (x_max - 600, y_max - 10), # ปรับ x offset ให้ข้อความไม่ล้นขอบ
        "Middle_top": (x_mean - 150, y_min + 50), # ปรับ x offset ให้ข้อความอยู่กลางๆ
        "Middle_bottom": (x_mean - 150, y_max - 10), # ปรับ x offset ให้ข้อความอยู่กลางๆ
        "Middle_left": (x_min + 10, y_mean),
        "Middle_right": (x_max - 600, y_mean), # ปรับ x offset ให้ข้อความไม่ล้นขอบ
    }
    point_positions = {
        "Top_Left": (x_min, y_min), # จุดมุมจริงๆ
        "Bottom_Left": (x_min, y_max), # จุดมุมจริงๆ
        "Top_Right": (x_max, y_min), # จุดมุมจริงๆ
        "Bottom_Right": (x_max, y_max), # จุดมุมจริงๆ
        "Middle_top": (x_mean, y_min), # จุดกลางด้านบน
        "Middle_bottom": (x_mean, y_max), # จุดกลางด้านล่าง
        "Middle_left": (x_min, y_mean), # จุดกลางด้านซ้าย
        "Middle_right": (x_max, y_mean), # จุดกลางด้านขวา
    }

    # วาดจุดกึ่งกลางภาพ
    cv2.circle(image_bgr, (center_x, center_y), 10, (0, 255, 255), -1) # วงกลมสีเหลืองทึบที่จุดกึ่งกลางภาพจริงๆ
    cv2.putText(image_bgr, f"Center: ({center_x}, {center_y})", (center_x + 20, center_y + 10), font, font_scale, text_color, font_thickness, line_type) # ข้อความจุดกึ่งกลาง

    # ฟังก์ชันช่วยในการเขียนข้อความและวาดจุด
    def draw_text_and_point(img, text, text_pos, point_pos, font, scale, color, thickness, line_type, point_color, point_radius):
        cv2.putText(img, text, text_pos, font, scale, color, thickness, line_type)
        cv2.circle(img, point_pos, point_radius, point_color, -1)

    # เขียนข้อความและวาดจุดสำหรับแต่ละตำแหน่ง
    draw_text_and_point(image_bgr, f"TL: ({x_min},{y_min})", text_positions["Top_Left"], point_positions["Top_Left"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)
    draw_text_and_point(image_bgr, f"BL: ({x_min},{y_max})", text_positions["Bottom_Left"], point_positions["Bottom_Left"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)
    draw_text_and_point(image_bgr, f"TR: ({x_max},{y_min})", text_positions["Top_Right"], point_positions["Top_Right"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)
    draw_text_and_point(image_bgr, f"BR: ({x_max},{y_max})", text_positions["Bottom_Right"], point_positions["Bottom_Right"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)
    draw_text_and_point(image_bgr, f"MT: ({x_mean},{y_min})", text_positions["Middle_top"], point_positions["Middle_top"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)
    draw_text_and_point(image_bgr, f"MB: ({x_mean},{y_max})", text_positions["Middle_bottom"], point_positions["Middle_bottom"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)
    draw_text_and_point(image_bgr, f"ML: ({x_min},{y_mean})", text_positions["Middle_left"], point_positions["Middle_left"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)
    draw_text_and_point(image_bgr, f"MR: ({x_max},{y_mean})", text_positions["Middle_right"], point_positions["Middle_right"], font, font_scale, text_color, font_thickness, line_type, coord_point_color, 10)


    cv2.imwrite(output_filename, image_bgr)
    print(f"บันทึกภาพที่ถูกเขียนข้อความและจุดพิกัดแล้วที่: {output_filename}")

    # กำหนดขนาด ROI ที่ต้องการ 
    roi_width = 2300 
    roi_height = 1200
    # คำนวณพิกัดของ ROI # (x, y) ของมุมซ้ายบนของ ROI 
    roi_x1 = center_x - (roi_width // 2) 
    roi_y1 = center_y - (roi_height // 2)
    roi_x2 = roi_x1 + roi_width 
    roi_y2 = roi_y1 + roi_height
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
    cv2.imwrite(annotate_roi, image_bgr) 
    cv2.imwrite(extracted_roi, roi)

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"roi_image_{timestamp}.jpg"
    annotate_roi = f"roi_annotate_image_{timestamp}.jpg"
    extracted_roi = f"roi_extracted_image_{timestamp}.jpg"
    capture_and_annotate_image(output_filename,annotate_roi,extracted_roi)