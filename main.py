# main.py
import time
from picamera import CameraStream
from ocr_process import OCRProcessor
from send_socket import send_data
from edge_status import check_and_send_status
import degirum as dg
# Set your inference host address, model zoo, and token in these variables.
your_host_address = dg.CLOUD # Can be dg.CLOUD, host:port, or dg.LOCAL
your_model_zoo = "resources"
your_token = ""

# Connect to DeGirum Application Server and an AI Hub model zoo
inference_manager = dg.connect(
    inference_host_address = your_host_address, 
    zoo_url = your_model_zoo, 
    token = your_token
)
supported_types = inference_manager.supported_device_types()
print(supported_types)
exit(0)
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
         # Wait for the specified interval
        if  0xFF == ord('q'):  # Press 'q' to quit
            print("Detection stopped by user (q pressed).")
            return
if __name__ == '__main__':
    main()
