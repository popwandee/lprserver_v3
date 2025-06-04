# main.py
import time
from picamera import CameraStream
from ocr_process import OCRProcessor
from send_socket import send_data
from edge_status import check_and_send_status
import degirum as dg
# Set inference host address, model zoo, and token in these variables.
 hw_location = "@local"
lp_det_model_zoo_url = "resources"
lp_det_model_name = "yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1"
lp_ocr_model_zoo_url = "resources"
lp_ocr_model_name = "yolov8n_relu6_lp_ocr--256x128_quant_hailort_hailo8_1"

# Load license plate detection and license plate OCR models
lp_det_model=dg.load_model(
    model_name=lp_det_model_name,
    inference_host_address=hw_location,
    zoo_url=lp_det_model_zoo_url,
    token='',
    overlay_color=[(255,255,0),(0,255,0)]
)
lp_ocr_model=dg.load_model(
    model_name=lp_ocr_model_name,
    inference_host_address=hw_location,
    zoo_url=lp_ocr_model_zoo_url,
    token='',
    output_use_regular_nms=False,
    output_confidence_threshold=0.1
)
#supported_types = inference_manager.supported_device_types()
#print(supported_types)

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
