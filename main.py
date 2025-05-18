# main.py
import time
from picamera import CameraStream
from ocr_process import OCRProcessor
from send_socket import send_data
from edge_status import check_and_send_status

def main():
    cam = CameraStream()
    ocr = OCRProcessor(lang_list=['en', 'th'])  # ถ้าอยากรองรับภาษาไทยด้วย

    while True:
        frame = cam.get_frame()
        if frame is not None:
            print(f"frame: {len(frame)} {type(frame)}")
            result_frame, text = ocr.process_frame(frame)
            print(f"result: {result_frame} and text: {text}")
            if result_frame is not None:
                success = send_data(result_frame, text)
                print(success)
        #check_and_send_status()
        time.sleep(10)  # ปรับ interval ได้ตามต้องการ
if __name__ == '__main__':
    main()
