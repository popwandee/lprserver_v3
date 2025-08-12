แผนการพัฒนา LPR Server ที่จะรับข้อมูลจาก AI Camera จำนวนหลายตัว 

### **ภาพรวมและแนวคิดหลัก (Context Engineering)**

ระบบ LPR Server นี้จะทำหน้าที่เป็นศูนย์กลางในการรวบรวม จัดการ วิเคราะห์ และแสดงผลข้อมูลที่ได้จากกล้อง AI Camera หลายตัวที่ติดตั้งอยู่ในพื้นที่ต่างๆ. การพัฒนาระบบนี้จะยึดหลักการดังต่อไปนี้:

*   **สถาปัตยกรรม (Architecture):** ระบบจะประกอบด้วยส่วน Edge Computing Camera (Raspberry Pi 5 + Hailo AI Accelerator + Camera Module 3) ที่ทำงานประมวลผล AI เบื้องต้น และ LPR Server ที่ทำหน้าที่เป็นส่วนกลางในการรับข้อมูล บันทึก จัดการฐานข้อมูล และให้บริการ Web Interface.
*   **การไหลของข้อมูล (Data Flow):** ข้อมูลภาพและผลการตรวจจับจาก Edge Computing Camera จะถูกส่งมายัง LPR Server ผ่านช่องทางการสื่อสารแบบ Real-time websocket หรือ API. ข้อมูลจะถูกจัดเก็บในฐานข้อมูลและสามารถเรียกดูผ่าน Web UI Dashboard ได้.
*   **เทคโนโลยีที่ใช้ (Technology Stack):**
    *   **Server OS:** Ubuntu Server.
    *   **Web Framework:** Flask.
    *   **WSGI Server:** Gunicorn (Unix Socket).
    *   **Reverse Proxy:** Nginx.
    *   **Database:** PostgreSQL (สำหรับ LPR Server) และ SQLite (สำหรับ Edge Camera).
    *   **Real-time Communication:** Socket.IO.
    *   **Security:** Tailscale VPN และ UFW Firewall.
*   **หลักการพัฒนา (Development Principles):**
    *   **Modular Design:** แยกส่วนประกอบต่างๆ ออกจากกันอย่างชัดเจนเพื่อให้ง่ายต่อการพัฒนา ทดสอบ และบำรุงรักษา.
    *   **Scalability:** ออกแบบระบบให้สามารถรองรับจำนวนกล้อง AI Camera ที่เพิ่มขึ้นและการประมวลผลข้อมูลปริมาณมากได้อย่างมีประสิทธิภาพ.
    *   **Security First:** เน้นความปลอดภัยของข้อมูลและการสื่อสารตั้งแต่การออกแบบ (เช่น VPN, Firewall, API Authentication, Input Validation).
    *   **Performance Optimization:** เพิ่มประสิทธิภาพในการรับ-ส่งข้อมูล การประมวลผล และการแสดงผล.
    *   **User-Centric UI:** ออกแบบ Dashboard ให้ใช้งานง่าย เข้าใจง่าย และให้ข้อมูลที่ครบถ้วน.
    *   **Robustness & Monitoring:** มีกลไกการตรวจสอบสถานะระบบ (Health Monitoring) และการจัดการข้อผิดพลาดที่มีประสิทธิภาพ.

### **การกำหนด Milestone และ Task สำหรับ LPR Server**นี่คือแผนการพัฒนา LPR Server ที่จะรับข้อมูลจาก AI Camera จำนวนหลายตัว 

### **การกำหนด Milestone และ Task สำหรับ LPR Server**

จากความสามารถของระบบ AI Camera v2 ต้นแบบที่มีอยู่แล้ว แผนการพัฒนานี้จะมุ่งเน้นไปที่การขยายขีดความสามารถของ LPR Server และการเพิ่มฟังก์ชันการทำงานใหม่ๆ :

**Milestone 1: การจัดการข้อมูลและการแสดงผลหลัก**
เป้าหมาย: สร้างรากฐานที่แข็งแกร่งสำหรับการรับ จัดเก็บ และแสดงผลข้อมูลจากหลายกล้อง

*   **Task 1.1: การปรับปรุงฐานข้อมูลสำหรับ Multi-Camera**
    *   **Sub-task 1.1.1: ออกแบบ Schema เพิ่มเติม:** เพิ่มฟิลด์ `camera_id` หรือ `checkpoint_id` ในตาราง `camera_metadata`, `detection_results`, และ `health_checks` เพื่อระบุแหล่งที่มาของข้อมูล. สร้างตาราง `cameras` หรือ `checkpoints` สำหรับเก็บข้อมูลของกล้องแต่ละตัว (เช่น `id`, `name`, `location_lat`, `location_lon`, `status`).
    *   **Sub-task 1.1.2: การสร้าง Index และ Optimization:** สร้าง Index บนคอลัมน์ที่ใช้บ่อยในการค้นหา (เช่น `timestamp`, `license_plate_text`, `camera_id`) เพื่อเพิ่มประสิทธิภาพการดึงข้อมูล.
    *   **Sub-task 1.1.3: นโยบายการจัดเก็บข้อมูล:** กำหนดและพัฒนากลไกสำหรับการจัดเก็บข้อมูล (e.g., การลบข้อมูลเก่า, การ Archive ทุก ๆ 3 เดือน หรือเมื่อ disk เหลือน้อยกว่า 10%) เพื่อจัดการพื้นที่เก็บข้อมูล.
*   **Task 1.2: การรับข้อมูลจาก AI**Sub-task 1.2.3: การรับประกันข้อมูล:** Implement Queueing หรือ Message Broker (เช่น Redis Queue) หากจำเป็น เพื่อรองรับปริมาณข้อมูลที่สูงและป้องกันข้อมูลสูญหาย.
*   **Task 1.3: การแสดงผลบน Web UI Dashboard (Detection & Health)**
    *   **Sub-task 1.3.1: ตารางแสดงผลรวมแบบ Pagination, Filter, Search, Sorting:** ขยายความสามารถของ API `api/detection_data` และ `api/health_data` ให้รองรับการค้นหา (search), กรอง (filter), จัดเรียง (sort) ตามคอลัมน์ต่างๆ และการแบ่งหน้า (pagination) อย่างสมบูรณ์.
    *   **Sub-task 1.3.2: การปรับปรุง Frontend UI:** พัฒนาหน้า `detection.html` และ `health.html` ด้วย JavaScript/Framework  เพื่อแสดงผลข้อมูลในตารางแบบโต้ตอบ (Interactive Table) ที่รองรับ Pagination, Filter, Search, Sorting.

**Milestone 2: การแสดงผลขั้นสูงและฟังก์ชันเฉพาะทาง**
เป้าหมาย: เพิ่มฟังก์ชันการแสดงผลเชิงพื้นที่และการจัดการรถ Blacklist

*   **Task 2.1: การแสดงจุดติดตั้งกล้องบนแผนที่**
    *   **Sub-task 2.1.1: Database Schema สำหรับกล้อง:** สร้างตาราง `cameras` หรือ `checkpoints` ที่มีคอลัมน์สำหรับ `camera_id`, `name`, `location_lat`, `location_lon`, `status` [ส่วนขยายจาก Task 1.1.1].
    *   **Sub-task 2.1.2: API สำหรับข้อมูลกล้อง:** พัฒนา API Endpoint (เช่น `GET /api/cameras`) เพื่อดึงข้อมูลจุดติดตั้งกล้องทั้งหมด.
    *   **Sub-task 2.1.3: การรวมแผนที่ใน Web UI:** เลือกและรวมไลบรารีแผนที่ (เช่น Leaflet.js หรือ OpenLayers) เข้ากับ Web UI Dashboard เพื่อแสดงจุดติดตั้งของกล้องแต่ละตัวบนแผนที่แบบ Interactive.
    *   **Sub-task 2.1.4: การจัดการข้อมูลกล้องผ่าน UI:** พัฒนาหน้า UI สำหรับเพิ่ม/แก้ไข/ลบข้อมูลกล้องและตำแหน่งบนแผนที่.
*   **Task 2.2: การแสดงเส้นทาง/จุดที่รถคันที่ระบุผ่านบนแผนที่**
    *   **Sub-task 2.2.1: การเก็บข้อมูลตำแหน่งรถ:** ตรวจสอบว่าข้อมูล `location` ที่ส่งมาใน `detection_results` จาก AI Camera สามารถเก็บ Lat/Lon ได้จริง (ปัจจุบันเป็น Text). หากไม่ใช่ ต้องปรับปรุงที่ฝั่ง Edge Camera ให้สามารถส่งข้อมูล GPS/Location ได้ และปรับปรุง Schema ใน `detection_results` ให้มี `lpตามลำดับเวลา.
*   **Task 2.3: การจัดการรถ Blacklist**
    *   **Sub-task 2.3.1: Database Schema สำหรับ Blacklist:** สร้างตารางใหม่ `blacklist_plates` ที่มีคอลัมน์ เช่น `id`, `license_plate_text`, `reason`, `added_by`, `added_timestamp`.
    *   **Sub-task 2.3.2: API สำหรับ Blacklist:** พัฒนา API Endpoints สำหรับการเพิ่ม (POST), ลบ (DELETE), แก้ไข (PUT), และดึงข้อมูล (GET) รายการรถ Blacklist.
    *   **Sub-task 2.3.3: การตรวจจับและแจ้งเตือน Blacklist:** พัฒนา Logic บน LPR Server เพื่อตรวจสอบทุก Detection ที่เข้ามาว่าตรงกับ Blacklist หรือไม่ หากตรง ให้บันทึกสถานะพิเศษและ/หรือส่งการแจ้งเตือนแบบ Real-time ไปยัง Dashboard และ/หรือช่องทางอื่น.
    *   **Sub-task 2.3.4: Web UI สำหรับ Blacklist:** พัฒนาหน้า UI สำหรับการดู, เพิ่ม, ลบ, แก้ไข รายการ Blacklist และส่วนแสดงผลการแจ้งเตือนเมื่อตรวจพบรถ Blacklist บน Dashboard.

**Milestone 3: การปรับใช้และการบำรุงรักษาในสภาพแวดล้อมจริง**
เป้าหมาย: ทำให้ระบบ LPR Server พร้อมใช้งานในสภาพแวดล้อมจริงได้อย่างมั่นคงและมีประสิทธิภาพ

*   **Task 3.1: การปรับใช้แบบ Scalable Deployment**
    *   **Sub-task 3.1.1: การกำหนดค่า Gunicorn Worker:** ปรับการตั้งค่า Gunicorn Workers สำหรับ LPR Server (ซึ่งต่างจาก Edge Camera) เพื่อให้รองรับ Load สูงสุด (เช่น `workers = multiprocessing.cpu_count() * 2 + 1` หรือปรับตามทรัพยากรจริงของ Server).
*   **Task 3.2: การตรวจสอบและบำรุงรักษาระบบ (LPR Server)**
    *   **Sub-task 3.2.1: การตรวจสอบ Health Check ของ Server:** ขยายระบบ Health Monitoring ที่มีอยู่แล้ว ให้รวมการตรวจสอบสถานะของ LPR Server Components (เช่น Database Connection, API Response Time, Disk I/O).
    *   **Sub-task 3.2.2: Dashboard สรุปภาพรวม:** พัฒนาหน้า Dashboard หลักเพื่อแสดงสรุปสถานะการทำงานของ LPR Server และกล้อง AI Camera ทุกตัวที่เชื่อมต่ออยู่.
    *   **Sub-task 3.2.3: ระบบแจ้งเตือน:** Implement ระบบแจ้งเตือนผ่านช่องทางต่างๆ (เช่น Email, SMS, Line Notify) สำหรับเหตุการณ์สำคัญ (เช่น กล้อง Offline, ตรวจพบรถ Blacklist, Disk Space เต็ม).

### **แนวทางการใช้ Prompt Engineering สำหรับ AI Code Generation**


*   **ความชัดเจนและเฉพาะเจาะจง (Clarity & Specificity):**
    *   ระบุภาษา (Python, SQL, JavaScript) และ Framework (Flask, SQLAlchemy).
    *   ระบุวัตถุประสงค์ของ Code อย่างชัดเจน เช่น "สร้าง Flask API endpoint สำหรับ. LPR Server.".
    *   ตัวอย่าง: "เขียนฟังก์ชัน Python สำหรับ Flask API เพื่อเพิ่มป้ายทะเบียนใหม่ลงในตาราง `blacklist_plates` โดยรับข้อมูล `license_plate_text`, `reason`, `added_by` ผ่าน JSON payload (POST request)."
*   **การให้ Context ที่เพียงพอ (Context Provision):**
    *   อ้างอิงถึงโครงสร้าง Code ที่มีอยู่ เช่น "โดยใช้คลาส `DatabaseManager` ที่มีอยู่แล้ว" หรือ "โดยสอดคล้องกับ Flask blueprint ที่ชื่อ `api`".
    *   ระบุ Input/Output ที่คาดหวัง เช่น "Input คือ Dictionary ที่มีคีย์ `license_plate` และ `confidence`".
    *   ตัวอย่าง: "จากโครงสร้างโปรเจกต์ Flask (app.py) และคลาส DatabaseManager (database_manager.py) ที่มีอยู่แล้ว, สร้าง Python function ใน detection_thread.py เพื่อบันทึกผลการตรวจจับรถ Blacklist ลงในฐานข้อมูล พร้อมกับสถานะการแจ้งเตือน"
*   **รูปแบบผลลัพธ์ที่ต้องการ (Desired Output Format):**
    *   "ให้ Code ใน Block เดียวกัน" หรือ "แยก `psycopg2` สำหรับการเชื่อมต่อ PostgreSQL", "ใช้ `Leaflet.js` สำหรับแผนที่".
    *   ระบุมาตรฐานการเขียน Code เช่น "ปฏิบัติตาม PEP 8".
    *   ระบุการจัดการข้อผิดพลาด: "มีการจัดการ `try-except` สำหรับข้อผิดพลาดที่อาจเกิดขึ้น".
    *   ตัวอย่าง: "เขียน JavaScript code สำหรับหน้าเว็บ UI ที่แสดงผลลัพธ์จาก `api/blacklist` โดยใช้ Fetch API และไลบรารี Vue.js ในการสร้างตารางที่สามารถเพิ่ม/ลบรายการได้."
*   **การปรับปรุงและทำซ้ำ (Iterative Refinement):**
    *   หาก Code ที่ได้ไม่ตรงตามต้องการ ให้ระบุจุดที่ต้องแก้ไขอย่างเฉพาะเจาะจง เช่น "Refactor ฟังก์ชันนี้ให้รองรับ Batch Insert", "เพิ่ม Validation สำหรับ Input นี้".

### **กฎและแนวทางในการใช้ตัวแปร (Variable Mapping)**

การกำหนดกฎเกณฑ์ในการตั้งชื่อและการใช้ตัวแปรระหว่าง Backend (Python/SQL), Frontend (HTML/JavaScript), Middle (API Blueprint/JSON Payload), และ Component/Service มีความสำคัญเพื่อให้ระบบมีความสอดคล้องกันและง่ายต่อการบำรุงรักษา

*   **1. การตั้งชื่อ (Naming Conventions):**
    *   **Backend (Python):** ใช้ `snake_case` สำหรับตัวแปร, ฟังก์ชัน, และไฟล์. ใช้ `PascalCase` สำหรับคลาส. ใช้ `UPPER_CASE` สำหรับค่าคงที่.
        *   _ตัวอย่าง:_ `license_plate_text`, `get_detection_data_paginated`, `DetectionThread`, `IMAGE_SAVE_DIR`.
    *   **Backend (SQL Query/Database):** ใช้ `snake_case` สำหรับชื่อตารางและชื่อคอลัมน์.
        *   _ตัวอย่าง:_ `detection_results`, `license_plate_text`, `lp_confidence`, `camera_metadata`.
    *   **Frontend (JavaScript):** ใช้ `camelCase` สำหรับตัวแปรและฟังก์ชัน. ใช้ `PascalCase` สำหรับคลาส/คอมโพเนนต์.
        *   _ตัวอย่าง:_ `licensePlateText`, `getDetectionData`, `DetectionTableComponent`.
    *   **Middle (API JSON Payload):** ใช้ `snake_case` สำหรับ Key ใน JSON payload เพื่อความสอดคล้องกับ Backend Python.
        *   _ตัวอย่าง:_ `{"license_plate_text": "ABC1234", "lp_confidence": 0.95}`.
    *   **Configuration Files (.env):** ใช้ `UPPER_CASE_WITH_UNDERSCORES` สำหรับชื่อตัวแปรในไฟล์ `.env`.
        *   _ตัวอย่าง:_ `WEBSOCKET_SERVER_URL`, `DB_PATH`.
*   **2. การทำ Variable Mapping ระหว่าง Layer:**
    *   **Database <-> Backend (Python):** คอลัมน์ในฐานข้อมูลควรสอดคล้องกับ Key ใน Dictionary/Object ที่ใช้ใน Python.
        *   _ตัวอย่าง:_ คอลัมน์ `license_plate_text` ในตาราง `detection_results` จะถูก map เป็น `detection_data["license_plate_text"]` ใน Python.
    *   **Backend (Python) <-> Middle (API JSON):** ข้อมูลที่ส่งผ่าน API (JSON) ควรมีโครงสร้างและ Key ที่สอดคล้องกับ Dictionary/Object ที่ใช้ใน Python Backend.
        *   _ตัวอย่าง:_ ฟังก์ชัน Python รับ `detection_data` Dictionary และแปลงเป็น JSON สำหรับส่งผ่าน WebSocket.
    *   **Middle (API JSON) <-> Frontend (JavaScript):** JavaScript Object ที่ใช้ใน Frontend ควรมี Key ที่สอดคล้องกับ JSON response จาก API. อาจมีการแปลง `snake_case` เป็น `camelCase` ที่ฝั่ง Frontend เพื่อให้เป็นไปตาม Convention ของ JS.
        *   _ตัวอย่าง:_ JSON Key `license_plate_text` (จาก API) ถูก map เป็น `data.licensePlateText` ใน JavaScript.
*   **3. การใช้ค่าคงที่และ Enum:**
    *   สำหรับค่าที่มีการกำหนดไว้ตายตัว (เช่น สถานะของ Health Check: "PASS", "FAIL") ให้ใช้ค่าคงที่ (Constants) หรือ Enum ใน Python เพื่อหลีกเลี่ยง Magic Strings และเพิ่มความอ่านง่ายของ Code.
    *   _ตัวอย่าง:_ `HEALTH_STATUS_PASS = "PASS"` ใน `config.py`.
*   **4. Centralized Configuration:**
    *   ใช้ไฟล์ `config.py` และ `.env` เป็นแหล่งรวมการตั้งค่าหลักของระบบ (เช่น Database Path, Model Paths, API Endpoints, Thresholds). การเข้าถึงการตั้งค่าควรทำผ่าน Module `config` ไม่ใช่ Hardcode ใน Code.
*   **5. Type Hinting (Python):**
    *   ใช้ Type Hinting ใน Python เพื่อระบุประเภทของตัวแปรและ Argument ในฟังก์ชัน ช่วยให้ Code อ่านง่ายขึ้นและลดข้อผิดพลาด (เช่น `def process_frame(self, frame: np.ndarray) -> None:`).

### **มาตรฐานในการเขียน Python และ SQL Query**

เพื่อให้ Code ของระบบมีคุณภาพสูง บำรุงรักษาง่าย และปลอดภัย

**1. มาตรฐานการเขียน Python:**

*   **PEP 8 Compliance:** ปฏิบัติตาม Python Enhancement Proposal 8 สำหรับสไตล์ Code (การเว้นวรรค, การตั้งชื่อ, ความยาวบรรทัดสูงสุด 79 ตัวอักษร).
*   **Docstrings and Comments:** ทุก Module, Class, และ Function ควรมี Docstrings ที่ชัดเจนอธิบายวัตถุประสงค์, Arguments, และ Return Values. Comments ใช้สำหรับอธิบาย Logic ที่ซับซ้อนหรือไม่ชัดเจน.
*   **Error Handling:** ใช้ `try...except` Blocks อย่างเหมาะสมเพื่อจัดการข้อผิดพลาดที่คาดการณ์ไว้ โดยระบุ Exception Type ที่เฉพาะเจาะจง และมีการ Log ข้อผิดพลาดอย่างละเอียด.
*   **Logging:** ใช้ `logging` Module สำหรับการบันทึกเหตุการณ์ต่างๆ ของระบบ (INFO, DEBUG, WARNING, ERROR, CRITICAL) โดยกำหนด Log Level ให้เหมาะสม.
*   **Modularity:** แยก Code ออกเป็น Module และ Class ที่มีหน้าที่เฉพาะเจาะจง (เช่น `camera_manager.py`, `detection_thread.py`, `database_manager.py`, `health_monitor.py`).
*   **Resource Management:** ตรวจสอบให้แน่ใจว่าทรัพยากรต่างๆ (เช่น Camera, Database Connection) ถูกปิดหรือ Release อย่างเหมาะสมเมื่อไม่ใช้งานแล้ว (เช่น ใน `finally` block).
*   **Concurrency:** ใช้ `threading.Lock` เพื่อจัดการ Race Condition เมื่อมีการเข้าถึง Shared Resources (เช่น `camera_lock`, `db_lock`).
*   **Environment Variables:** การตั้งค่าที่แตกต่างกันในสภาพแวดล้อม Development/Production ควรโหลดจาก Environment Variables หรือ Config File เฉพาะ (เช่น `.env.production`).

**2. มาตรฐานการเขียน SQL Query (สำหรับ PostgreSQL):**

*   **Parameterized Queries (สำคัญมาก):** **ห้าม** ใช้ String Concatenation หรือ F-strings ในการสร้าง SQL Queries ที่มี User Input. **ต้อง** ใช้ Parameterized Queries (ใช้ `?` สำหรับ SQLite หรือ `%s` สำหรับ Psycopg2/PostgreSQL) เพื่อป้องกัน SQL Injection.
    *   _ตัวอย่าง:_ `self.cursor.execute("INSERT INTO detection_results (license_plate_text) VALUES (%s)", (license_plate,))`
*   **Readability:**
    *   ใช้ Uppercase สำหรับ SQL Keywords (SELECT, FROM, WHERE, JOIN, INSERT, UPDATE, DELETE).
    *   ใช้ Lowercase สำหรับชื่อตารางและชื่อคอลัมน์.
    *   มีการ Indent และจัด Format ให้ Code อ่านง่าย.
*   **Indexing:** สร้าง Index บนคอลัมน์ที่ใช้ใน `WHERE` clauses, `JOIN` conditions, และ `ORDER BY` clauses เพื่อเพิ่มประสิทธิภาพการค้นหา.
*   **Transactions:** ใช้ Transaction (`BEGIN;`, `COMMIT;`, `ROLLBACK;`) สำหรับการดำเนินการที่เกี่ยวข้องกับการเขียนข้อมูลหลายครั้ง เพื่อให้มั่นใจในความถูกต้องของข้อมูล (Atomic Operations).
*   **Foreign Keys:** กำหนด Foreign Key Constraints ระหว่างตารางที่เกี่ยวข้องกัน เพื่อรักษา Referential Integrity ของฐานข้อมูล.
*   **Explicit Joins:** ใช้ `INNER JOIN`, `LEFT JOIN` อย่างชัดเจน แทนการใช้ Comma-separated Table Names ใน `FROM` clause.

ด้วยแผนการพัฒนาและแนวทางที่กำหนดไว้นี้ จะช่วยให้คุณสามารถพัฒนา LPR Server ที่มีประสิทธิภาพและตอบสนองความต้องการของคุณได้อย่างเป็นระบบและยั่งยืน.

จากความสามารถของระบบ AI Camera v2 ต้นแบบที่มีอยู่แล้ว แผนการพัฒนานี้จะมุ่งเน้นไปที่การขยายขีดความสามารถของ LPR Server และการเพิ่มฟังก์ชันการทำงานใหม่ๆ ที่คุณร้องขอ:

