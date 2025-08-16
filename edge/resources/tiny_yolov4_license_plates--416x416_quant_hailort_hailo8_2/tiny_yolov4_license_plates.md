# Model name
tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2

# Code
```python
import degirum as dg

zoo = dg.connect(
    dg.CLOUD, "https://cs.degirum.com/degirum/hailo", "<your cloud API access token>"
)

model = zoo.load_model("tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2")

result = model("<file_path>")
print(result)
```

# Model JSON
```JSON
{
  "ConfigVersion": 10,
  "Checksum": "b5b2728ee0e9799121feffacdc679464aee558f844a3de8251076b4924faf37a",
  "DEVICE": [
    {
      "DeviceType": "HAILO8",
      "RuntimeAgent": "HAILORT",
      "SupportedDeviceTypes": "HAILORT/HAILO8"
    }
  ],
  "PRE_PROCESS": [
    {
      "InputN": 1,
      "InputH": 416,
      "InputW": 416,
      "InputC": 3,
      "InputQuantEn": true
    }
  ],
  "MODEL_PARAMETERS": [
    {
      "ModelPath": "tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2.hef"
    }
  ],
  "POST_PROCESS": [
    {
      "OutputPostprocessType": "None"
    }
  ]
}
```

# Parse-hef
```terminal
hailortcli parse-hef resources/tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2/tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2.hef
Architecture HEF was compiled for: HAILO8
Network group name: tiny_yolov4_license_plates, Single Context
    Network name: tiny_yolov4_license_plates/tiny_yolov4_license_plates
        VStream infos:
            Input  tiny_yolov4_license_plates/input_layer1 UINT8, NHWC(416x416x3)
            Output tiny_yolov4_license_plates/conv19_centers UINT8, NHWC(13x13x6)
            Output tiny_yolov4_license_plates/conv19_scales UINT8, NHWC(13x13x6)
            Output tiny_yolov4_license_plates/conv19_obj UINT8, NHWC(13x13x3)
            Output tiny_yolov4_license_plates/conv19_probs UINT8, NHWC(13x13x3)
            Output tiny_yolov4_license_plates/conv21_centers UINT8, NHWC(26x26x6)
            Output tiny_yolov4_license_plates/conv21_scales UINT8, NHWC(26x26x6)
            Output tiny_yolov4_license_plates/conv21_obj UINT8, NHWC(26x26x3)
            Output tiny_yolov4_license_plates/conv21_probs UINT8, NHWC(26x26x3)
```

# Input
```bash
hailortcli parse-hef resources/tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2/tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2.hef
Architecture HEF was compiled for: HAILO8
Network group name: tiny_yolov4_license_plates, Single Context
    Network name: tiny_yolov4_license_plates/tiny_yolov4_license_plates
        VStream infos:
            Input  tiny_yolov4_license_plates/input_layer1 UINT8, NHWC(416x416x3)
```
# Output
```bash
hailortcli parse-hef resources/tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2/tiny_yolov4_license_plates--416x416_quant_hailort_hailo8_2.hef
Architecture HEF was compiled for: HAILO8
Network group name: tiny_yolov4_license_plates, Single Context
     Network name: tiny_yolov4_license_plates/tiny_yolov4_license_plates
         VStream infos:
            Output tiny_yolov4_license_plates/conv19_centers UINT8, NHWC(13x13x6)
            Output tiny_yolov4_license_plates/conv19_scales UINT8, NHWC(13x13x6)
            Output tiny_yolov4_license_plates/conv19_obj UINT8, NHWC(13x13x3)
            Output tiny_yolov4_license_plates/conv19_probs UINT8, NHWC(13x13x3)
            Output tiny_yolov4_license_plates/conv21_centers UINT8, NHWC(26x26x6)
            Output tiny_yolov4_license_plates/conv21_scales UINT8, NHWC(26x26x6)
            Output tiny_yolov4_license_plates/conv21_obj UINT8, NHWC(26x26x3)
            Output tiny_yolov4_license_plates/conv21_probs UINT8, NHWC(26x26x3)
```
ใน YOLOv4 ที่คุณกำลังใช้บน Hailo-8 โมเดลถูกออกแบบให้มีหลาย output เพราะมันทำงานบนสองระดับของ feature maps:  
- **ขนาด 13x13** (conv19 series)  
- **ขนาด 26x26** (conv21 series)  

### **เหตุผลที่มีหลาย output:**  
1. **Multi-scale detection**:  
   - Feature map ที่มีขนาด **13x13** จะใช้ตรวจจับวัตถุขนาดใหญ่  
   - Feature map ที่มีขนาด **26x26** จะใช้ตรวจจับวัตถุขนาดเล็ก  

2. **ประเภทของ output** (ในแต่ละ scale):
   - **centers** (ตำแหน่งศูนย์กลางของ bounding box)  
   - **scales** (ขนาดของ bounding box)  
   - **obj** (ค่าความมั่นใจว่าเป็นวัตถุ)  
   - **probs** (ค่าความน่าจะเป็นของคลาส)  

### **การนำไปใช้:**  
- ข้อมูลจาก output layers จะถูกนำไปใช้ใน **post-processing**:
  - **Bounding Box Extraction**: ใช้ **centers** และ **scales** กำหนดตำแหน่งและขนาด  
  - **Object Confidence Filtering**: ใช้ **obj** คัดกรอง bounding boxes ที่มีค่าความมั่นใจสูง  
  - **Class Prediction**: ใช้ **probs** กำหนดว่าป้ายทะเบียนเป็นวัตถุที่ถูกตรวจพบหรือไม่  

โมเดลนี้รองรับทั้งสอง scale เพื่อให้สามารถตรวจจับป้ายทะเบียนได้แม้ว่าจะมีขนาดต่างกันในภาพ ขึ้นอยู่กับสถานการณ์จริงที่ต้องการ เช่น ระยะใกล้หรือไกล!  


