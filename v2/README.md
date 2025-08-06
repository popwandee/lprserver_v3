## 1. Project Overview
* **ชื่อโปรเจกต์:**AI Camera (ALPR)
* **เป้าหมายหลัก:** สร้างระบบกล้องตรวจจับและจดจำป้ายทะเบียนที่ทำงานเป็นอิสระแบบ Edge Computing โดยใช้ Raspberry Pi5 และกล้อง Camera Module 3 พร้อมด้วย AI Accelerator  Hailo 8 ตรวจจับยานพาหนะ บริเวณด่านตรวจยานพาหนะตามแนวชายแดน 
* **ปัญหาที่ต้องการแก้ไข:** 
-ช่วยบันทึกและจดจำว่ายานพาหนะที่เข้ามาผ่านด่านเป็นรถประเภทอะไร สีอะไร ใช้ทะเบียนอะไร ผ่านด่านเวลา และพิกัดของด่าน เพื่อช่วยให้เจ้าหน้าที่ประจำด่านตรวจสามาถวิเคราะห์ คัดกรองยานพาหนะที่อยู่ใน Blacklist ได้บน Flask Web UI ของกล้อง 
-สำหรับข้อมูลผลการตรวจจับจะเก็บบันทึกลงใน SQLite ก่อนส่งไปเก็บที่ LPR Server (PosgreSQL) ผ่าน Websocket เพื่อช่วยให้เจ้าหน้าที่ระดับผู้บังคับบัญชา และเจ้าหน้าที่วิเคราะห์ข้อมูล สามารถวิเคราะห์เส้นทางการเดินทางของยานพาหนะจากกล้องหลาย ๆ ตัวได้ในลักษณะ Route Analysis ในภาพรวมของระบบบนเว็บ Django App/Flask Server 
-ทั้งนี้ระบบกล้อง AI Camera (ALPR) มีระบบตรวจสอบสภาพการทำงานของระบบกล้องเอง เพื่อให้เจ้าหน้าที่ผู้ดูแลระบบสามารถตรวจสอบสถานะการทำงานของระบบกล้อง สำหรับการวางแผนดูแลรักษาและปรับปรุงประสิทธิภาพต่อไป
-ระบบกล้องมีการบริหารจัดการข้อมูลไฟล์ภาพและไฟล์ logs การทำงาน เพื่อป้องกันข้อมูลในระบบถูกบันทึกจนเต็ม ด้วยการลบข้อมูลที่เก่าที่สุดออกก่อน และมีระดับของการใช้พื้นที่ไม่ให้เกิน ร้อยละ 80 ของพื้นที่ทังหมด

## 2. Key Stakeholders & Users
* **ผู้ใช้งานหลัก (Actors):** 
[User, Admin, Manager, Analyst.]
* **บทบาทและหน้าที่:**
 [User:ดูการทำงานของกล้อง, ตรวจสอบการตรวจจับยานพาหนะและการอ่านป้ายทะเบียนย้อนหลัง ผ่าน Flask App UI /video_feed]
[Admin: ติดตามสถานะการทำงานของระบบในภาพรวม และการปรับปรุง เปลี่ยนแปลงค่าพารามิเตอร์ของกล้อง เปลี่ยน Model ของระบบ object detecction ผ่าน Flask App UI รวมถึงการจัดการข้อมูลผู้ใช้ของระบบ ]
[ Manager:ติดตาม ตรวจสอบการทำงานในภาพรวม เช่นผลการตรวจจับยานพาหนะ จำนวนยานพาหนะที่ผ่านด่านในแต่ละวัน, เจ้าหน้าที่ที่เข้าใช้งานระบบ ผ่าน Flask App UI ]
[ Analyst :ติดตาม วิเคราะห์ยานพาหนะที่ผ่านด่าน จัดการข้อมูล Blacklist ของยานพาหนะต้องสงสัย ติดตามยานพาหนะที่ผ่านด่านในห้วงเวลาไม่ปกติ เช่นกลางคืน บ่อยครั้งในห้วงเวลาที่กำหนด เป็นต้น ผ่าน Flask App UI ]
## 3. System Scope (ขอบเขตของระบบ)
* **Functionalities (ฟังก์ชันการทำงาน):**

"AI Camera (ALPR) System Startup" {
1.	config.py Load config load_dotenv(env_path(.env.production)
2.	เริ่มต้นการทำงานตั้งค่า Logging แยก level INFO สำหรับ Terminal และ DEBUG สำหรับ File logging ให้แยกเป็น log รายวัน สร้างไฟล์ใหม่หลังเที่ยงคืน เก็บ 30 วันย้อนหลัง แล้วลบไฟล์เก่าเพื่อประหยัดพื้นที่
3.	สร้าง Queue สำหรับสื่อสารระหว่าง CameraHandler และ DetectionProcessor ; frames_queue = queue.Queue(maxsize=10) ; metadata_queue = queue.Queue(maxsize=1) # ใช้สำหรับเก็บ metadata ของเฟรมล่าสุด
4.	db_lock = threading.Lock() # สำหรับป้องกันการเข้าถึงฐานข้อมูลพร้อมกัน
5.	เรียกใช้ CameraHandler Class เพื่อจัดการกล้อง
6.	เรียกใช้ DatabaseManager Class เพื่อจัดการฐานข้อมูล.
7.	เรียกใช้ DetectionProcessor Class สำหรับการตรวจจับและรู้จำป้ายทะเบียน.
8.	เรียกใช้ WebSocketClient Class สำหรับการส่งข้อมูลไปยัง LPR Server.
9.	เรียกใช้ HealthMonitor Class สำหรับการตรวจสอบสถานะระบบ.
10.	สร้าง Thread Camera_thread, object_detection_thread, sender_thread, healthmonitor_thread, metadata_thread
11.	เรียกใช้ CameraHandler initialize_camera ด้วยค่าเริ่มต้น pre-set controls.
12.	DetectionProcessor load_model() เพื่อโหลด DeGirum model
13.	ทำการ HealthMonitor run_all_checks เพื่อตรวจสอบสุขภาพระบบเบื้องต้น ความพร้อมของกล้อง, AI Model, CPU, RAM, HDD,Internet connection, Websocket server connection) .
14.	เมื่อสถานะทุกอย่างปกติ เริ่มการทำงาน Start Thread แต่ละ Thread แยกกันทำงานอย่างอิสระ แต่หากมีสิ่งผิดปกติให้หยุดการทำงานและแจ้งผู้ใช้ทราบผ่าน Terminal logging 
15.	Thread 1: Camera_Thread ถ่ายภาพ capture พร้อม meta data เก็บเข้า Queue
16.	Thread 2: Video Feed ส่งภาพไป Stream บน Flask App
17.	Thread 3: Metadata_thread: ดึงข้อมูลเมตาดาต้าจากคิว metadata_queue แล้วส่งไปยัง Flask App UI ผ่าน SocketIO
18.	Thread 4:  Detection_thread: ดึงเฟรมภาพจากคิว frames_queue เพื่อประมวลผล Object Detection, License Plate Detection, OCR แล้วบันทึกลงฐานข้อมูล.
19.	Thread 5:  Health Monitor: ทำการตรวจสอบสุขภาพระบบตามช่วงเวลาที่กำหนด แล้วบันทึกลงฐานข้อมูล.
20.	Thread 6:  WebSocket Sender: จัดการการเชื่อมต่อ WebSocket และส่งข้อมูลที่ยังไม่ได้ส่งจากฐานข้อมูล ส่งไป LPR Server.
21.	เมื่อ User ส่งคำสั่งผ่านหน้าเว็บ ให้ปิด-เปิดกล้อง หรือ Reset Camera ทำการหยุดการทำงานของ Detection thread และ healthmonitor แล้วปิดกล้อง จากนั้น เปิดกล้องใหม่ และเริ่มการทำงานของ Camera , Detection, HealthMonitor Thread
22.	เมื่อ User  ส่งคำสั่งผ่านหน้าเว็บ ให้ปรับเปลี่ยนค่า พารามิเตอร์ของกล้อง apply setting camera controls ให้ทำการหยุดการทำงานของ Detection thread และ healthmonitor แล้วปิดกล้อง จากนั้น set controls ตามที่ user กำหนด  จากนั้น เปิดกล้องใหม่ และเริ่มการทำงานของ Camera , Detection, HealthMonitor Thread
23.	เมื่อ User ส่งคำสั่งผ่านหน้าเว็บ ให้หยุดการทำงานของทุก Thread ให้หยุดการทำงานของ sender, healthmonitor, detection, video feed, camera ตามลำดับ แล้วรอคำสั่งเริ่มการทำงานอีกครั้ง
24.	เมื่อ User ส่งคำสั่งผ่านหน้าเว็บ ให้เริ่มการทำงานของทุก Thread ให้ตรวจสอบการทำงานของ sender, healthmonitor, detection, video feed, camera ตามลำดับ หากยังทำงาน ให้หยุดการทำงานตามลำดับก่อน แล้วสั่งให้เริ่มการทำงาน Start Threadของทุก Trhread อีกครั้ง
25.	เมื่อ User ส่งคำสั่งผ่านหน้าเว็บ ให้หยุดการทำงานของระบบ Shutdown ให้หยุดการทำงานของ sender, healthmonitor, detection, video feed, camera ตามลำดับ แล้วคืนทรัพยากรทุกอย่างของระบบ แล้วหยุดการทำงานของระบบ
}


* **Out of Scope:** 
[การสร้างแบบจำลอง object detection model ไม่รวมอยู่ในโปรเจกต์นี้]

## 4. Architectural Overview (ภาพรวมสถาปัตยกรรม)
* **Components (ส่วนประกอบ):** 
CameraHandler (Capture & Queueing){
1.	ใช้ Singleton pattern เพื่อให้แน่ใจว่ามีอินสแตนซ์เดียว.
2.	initialize_camera ทำการตั้งค่าและเริ่มกล้อง Picamera2. ตรวจสอบว่าหากกล้องทำงานอยู่แล้วจะหยุดและเริ่มต้นใหม่.
3.	generate_frames เป็น Generator function ที่ดึงเฟรมภาพ (จาก lores stream สำหรับการ Streaming บนเว็บ) และเมตาดาต้า.
4.	นำเฟรมภาพ (main stream) และเมตาดาต้าใส่คิว: frames_queue (สำหรับ DetectionProcessor) และ metadata_queue (สำหรับ Metadata Sender ผ่าน SocketIO).
5.	แปลงเฟรมภาพเป็น JPEG: สำหรับการสตรีมไปยัง Flask Response.
6.	ควบคุมกล้อง: สามารถปรับค่าความสว่าง, คอนทราสต์, ความอิ่มตัว, ความคมชัด, และโหมด AWB (Auto White Balance) , ระยะเวลา Expose time ได้. มีการตั้งค่า preset สำหรับกลางวัน/กลางคืน.
7.	start เริ่มทำงานของกล้อง, stop หยุดการทำงานของกล้อง, release ทรัพยากร

}
Video Feed {
1.	ดึงเฟรมภาพ (จาก lores stream สำหรับการ Streaming บนเว็บ) ไปแสดงบนเว็บ
2.	หากมีผลการตรวจจับจาก detection ให้แสดง 10  ผลการตรวจจับ ล่าสุด
}
Metadata_thread {
1.	ดึงข้อมูลเมตาดาต้าจากคิว metadata_queue แล้วส่งไปยัง Flask App UI ผ่าน SocketIO
}
Detection_thread{
1.	ดึงเฟรมภาพ (ที่เป็น numpy array จาก main stream) จาก frames_queue อย่างต่อเนื่อง.
2.	ตรวจจับยานพาหนะ (Vehicle Detection): ใช้โมเดล vehicle_detection_model (จาก config.py)  เพื่อตรวจจับยานพาหนะ เมื่อตรวจพบให้วาดกรอบ bounding box แล้วบันทึกภาพ ด้วยชื่อไฟล์ในรูปแบบวันที่ เวลา ลงในโฟลเดอร์ vehicle_detection_image แต่หากไม่พบจะไม่ทำงานในขั้นต่อไป ให้กลับไปรับเฟรมภาพจาก Queue ใหม่
3.	ตรวจจับป้ายทะเบียน (License Plate Detection): นำเฟรมจากขั้นตอนที่ 2. มาใช้โมเดล lp_detection_model เพื่อตรวจจับป้ายทะเบียน. หากไม่พบโมเดล จะไม่ทำการในขั้นต่อไป หากตรวจพบป้ายทะเบียน ค่าความเชื่อมั่นมากกว่า 70 ให้ Cropped ป้ายทะเบียน แล้วบันทึกเป็นไฟล์ภาพด้วยชื่อในรูปแบบวันที่ เวลา 
4.	นำเฟรมภาพป้ายทะเบียน Cropped จากขั้นตอนที่ 3 มาปรับปรุง Pre-Processing ให้เห็นขอบของข้อความให้ชัดเจนขึ้น จากนั้นทำการ OCR แล้วบันทึกผลลงฐานข้อมูล ได้แก่ ข้อความที่อ่านได้, วันเวลาที่ตรวจจับป้ายทะเบียนได้, path ของภาพยานพาหนะ และป้ายทะเบียนที่ตรวจจับได้.
5.	มีระบบตรวจสอบผลการตรวจจับที่เป็นรถคันเดียวกันในห้วงเวลาใกล้เคียงกัน เช่น tracking (รถเคลื่อนที่เข้าหากล้อง) หากเป็นคันเดียวกัน ให้พิจารณาค่าความเชื่อมั่นในการตรวจจับและการอ่าน OCR เพื่อเลือกข้อมูลที่มีค่าความเชื่อมั่นสูงสุดบันทึกลงฐานข้อมูล
}
Health Monitor{ 
1.	ทำการตรวจสอบสุขภาพระบบตามช่วงเวลาที่กำหนด (HEALTH_CHECK_INTERVAL จาก config.py ).แล้วบันทึกลงฐานข้อมูล.
2.	ตรวจสอบสถานะส่วนประกอบต่างๆ:
a.	Camera: ตรวจสอบว่ากล้องเริ่มต้นและกำลังสตรีมอยู่หรือไม่ (ไม่ต้องสั่งให้เริ่มทำงาน เพียงแค่ตรวจสอบเท่านั้น).
b.	Disk Space: ตรวจสอบพื้นที่ว่างในดิสก์ที่ใช้บันทึกรูปภาพ.
c.	CPU และ RAM อยู่ในสถานะพร้อมทำงาน เช่นอุณหภูมิ, พื้นที่ว่างเพียงพอ
d.	Detection Models: ตรวจสอบว่าไฟล์โมเดลการตรวจจับอยู่ครบถ้วนตาม Path ที่กำหนด.
e.	EasyOCR: ตรวจสอบว่า EasyOCR สามารถ import ได้.
f.	Database: ตรวจสอบว่าการเชื่อมต่อฐานข้อมูลยังคงทำงานอยู่.
g.	Network Connectivity: ตรวจสอบการเชื่อมต่อเครือข่ายภายนอก (เช่น Google DNS).และ websocket server
3.	บันทึกผลการตรวจสอบ: ผลการตรวจสอบทั้งหมดจะถูกบันทึกในตาราง health_checks ในฐานข้อมูลผ่าน DatabaseManager.
}
WebSocket Sender (Sending Data){
1.	พยายามเชื่อมต่อกับ WebSocket Server อย่างต่อเนื่อง.
2.	ดึงข้อมูลจากฐานข้อมูล:
2.1.	ดึง unsent_detections (ผลการตรวจจับที่ยังไม่ได้ส่ง) จาก DatabaseManager.
2.2.	ดึง unsent_health_checks (ผลการตรวจสอบสุขภาพที่ยังไม่ได้ส่ง) จาก DatabaseManager.
3.	ส่งข้อมูลไปยังเซิร์ฟเวอร์:
3.1.	สำหรับ unsent_detections: แปลงข้อมูลเป็น JSON และเพิ่มข้อมูลภาพ (Vehicle with Bounding Box, Cropped License Plate) ที่ลดขนาดภาพ และส่งผ่าน WebSocket. หลังจากส่งสำเร็จ จะอัปเดตสถานะ sent_to_server เป็น 1. หากส่งไม่เสร็จจะรอตามห้วงเวลาที่เหมาะสม หรือกำหนดใน config.py
3.2.	สำหรับ unsent_health_checks: แปลงข้อมูลเป็น JSON และส่งผ่าน WebSocket. หลังจากส่งสำเร็จ จะอัปเดตสถานะ sent_to_server เป็น 1.หากส่งไม่เสร็จจะรอตามห้วงเวลาที่เหมาะสม หรือกำหนดใน config.py
4.	มีกลไกการลองเชื่อมต่อใหม่ (reconnection attempts).

}
Flask Web Application (User Interface & API){
1.	ทำหน้าที่เป็นเว็บเซิร์ฟเวอร์.
2.	/ (หน้าหลัก): แสดงหน้าจอหลักที่มี Live Camera Feed, เมตาดาต้าล่าสุด, ฟอร์มตั้งค่ากล้อง , สถานะภาพระบบ และผลการตรวจจับยานพาหนะ vehicle detection and OCR (10 รายการล่าสุด).
3.	/video_feed: สตรีมวิดีโอจาก CameraHandler.generate_frames() ไปยังเบราว์เซอร์.
4.	/update_camera_settings (POST): รับค่าการตั้งค่ากล้องจากฟอร์ม. เมื่อส่งค่ามาจะสั่งให้ stop detection_threads(), healthmonitor_thread() และ close_camera() ก่อน แล้วจึง initialize_camera() ใหม่ด้วยการตั้งค่าใหม่ start camera()  และ start Camera , Detection, HealthMonitor Thread อีกครั้ง.
5.	/close_camera (POST): สั่งให้ stop detection_threads(), healthmonitor_thread() และ camera_handler.close_camera() 
6.	/reset_camera (POST) ทำการหยุดการทำงานของ Detection thread และ healthmonitor แล้วปิดกล้อง camera_handler.close_camera()  จากนั้น เปิดกล้องใหม่ และเริ่มการทำงานของ Camera , Detection, HealthMonitor Thread
7.	/stop_app (POST) เมื่อ User ส่งคำสั่งผ่านหน้าเว็บ เพื่อหยุดการทำงานของทุก Thread ให้หยุดการทำงานของ sender, healthmonitor, detection, video feed, camera ตามลำดับ แล้วรอคำสั่งเริ่มการทำงานอีกครั้ง
8.	/start_app (POST) เมื่อ User ส่งคำสั่งผ่านหน้าเว็บ ให้เริ่มการทำงานของทุก Thread ให้ตรวจสอบการทำงานของ sender, healthmonitor, detection, video feed, camera ตามลำดับ หากยังทำงาน ให้หยุดการทำงานตามลำดับก่อน แล้วสั่งให้เริ่มการทำงาน Start Thread ของทุก Trhread อีกครั้ง ตั้งแต่กการเปิดกล้อง initail camera, start camera, capture & get meta data, Detection thread, Healthmonitor Thread, Websocket sender เป็นต้น
9.	/shutdown (POST) เมื่อ User ส่งคำสั่งผ่านหน้าเว็บ ให้หยุดการทำงานของระบบ Shutdown ให้หยุดการทำงานของ sender, healthmonitor, detection, video feed, camera ตามลำดับ แล้วคืนทรัพยากรทุกอย่างของระบบ แล้วหยุดการทำงานของระบบ
10.	SocketIO: ใช้สำหรับส่งข้อมูลเมตาดาต้าของกล้องล่าสุดไปแสดงผลที่หน้าเว็บแบบ Real-time.
11.	/detection_view  แสดงข้อมูลผลการตรวจจับยานพาหนะ และอ่านป้ายทะเบียนย้อนหลัง ในรูปแบบ Table view พร้อม pagination and filter search สามารถคลิกดู Detail View แต่ละรายการ ได้, view รายงานภาพรวม\nการตรวจจับรายวัน, จัดการ Blacklist\nของยานพาหนะต้องสงสัย
12.	/healthmonitor แสดงผลการตรวจสอบสถานะกล้อง และสถานภาพระบบ  ในรูปแบบ Table view
13.	/config ปรับค่ากล้อง โดยละเอียดและเปลี่ยนโมเดลตรวจจับ ได้ (เปลี่ยนค่าใน Config.py, .env.production), จัดการ Blacklist\nของยานพาหนะต้องสงสัย, จัดการพื้นที่จัดเก็บภาพและ logs
14.	/usermanagement จัดการผู้ใช้งานระบบ create , edit , delete, update permission, View log การใช้งานระบบของเจ้าหน้าที่
}
LPR Server{
1.	Flask Web App ที่ติดตั้งบน LPR Server
2.	MySQL database
3.	ตรวจสอบสถานะกล้องและสถานภาพกล้องทั้งหมดในระบบ
4.	จัดการผู้ใช้งานระบบ, ติดตามการใช้งานระบบของเจ้าหน้าที่
5.	จัดการ Blacklist ของยานพาหนะต้องสงสัย
6.	ดูรายงานภาพรวม การตรวจจับรายวัน ของกล้องแต่ละตัว และทั้งหมดทุกตัว
7.	แสดงข้อมูลผลการตรวจจับยานพาหนะ และอ่านป้ายทะเบียนย้อนหลัง ในรูปแบบ Table view พร้อม pagination and filter search สามารถคลิกดู Detail View แต่ละรายการ ได้
8.	วิเคราะห์ยานพาหนะจากหลายกล้อง (Route Analysis)
9.	จัดการพื้นที่จัดเก็บ ภาพและ logs
10.	ส่งออกรายงาน
}

* **External Systems:** 
[ Flask Web Application for LPR Server สำหรับการวิเคราะห์ข้อมูลยานพาหนะและข้อมูลป้ายทะเบียน จาก Edge AI Camera การค้นหา การกรองข้อมูล และการจัดทำรายงานรูปแบบต่างๆ]
[ MySQL Database on LPR Server สำหรับการจัดเก็บข้อมูลผลการตรวจจับยานพาหนะและข้อมูลป้ายทะเบียน จาก Edge AI Camera ทั้งหมด]
[ Websocket Server on LPR Server สำหรับการสื่อสาร รับส่งข้อมูลจาก Edge AI Camera ทั้งหมด]

* **Technology Stack:** 
[Programming :Python]
[ Framework: Flask, Gunicorn, Nginx, Systemd Service]
[ SQLite Database on Edge AI Camera (ALPR)]
[ MySQL Database on LPR Server]
[AI: DeGirum, Hailo, .hef]

[Class Diagram](docs/class_diagram.plantuml)
[Component Diagram](docs/component_diagram.planuml)
[Cross-Function Diagram](docs/cross-function.plantuml)
[Deployment Diagram](docs/deployment_diagram.planuml)
[Flowchart](docs/flowchart.plantuml)
[Sequence Diagram](docs/sequence_diagram.planuml)
[Startup Flowchart](docs/startup_flowchart.planuml)
[Thread Behavior Diagram](docs/thread_behavior.planuml)
[Use Case Diagram](docs/use_case_diagram.planuml)
[User Command Diagram](docs/user_command.planuml)