-----

## การใช้ Systemd เพื่อให้ `pi_monitor.py` ทำงานอัตโนมัติ

การใช้ **Systemd** เป็นวิธีที่นิยมและมีประสิทธิภาพในการทำให้สคริปต์ Python ของคุณทำงานโดยอัตโนมัติเมื่อ Raspberry Pi เปิดเครื่อง หรือเมื่อเงื่อนไขบางอย่างตรงตามที่กำหนดไว้ มันช่วยให้คุณจัดการบริการ (service) ได้อย่างง่ายดดาย เช่น การเริ่มต้น หยุด หรือตรวจสอบสถานะ

### ขั้นตอนที่ 1: สร้างไฟล์ Service Unit

คุณจะต้องสร้างไฟล์ `.service` ในไดเรกทอรี `/etc/systemd/system/` เพื่อกำหนดค่าบริการ Systemd ของคุณ

1.  **เปิด Terminal** และสร้างไฟล์บริการด้วยสิทธิ์ `sudo`:

    ```bash
    sudo nano /etc/systemd/system/pi_monitor.service
    ```

2.  **เพิ่มเนื้อหาต่อไปนี้** ลงในไฟล์ (ปรับเปลี่ยนตามพาธและชื่อผู้ใช้ของคุณ):

    ```ini
    [Unit]
    Description=Raspberry Pi Monitor Service
    After=network.target # ให้บริการเริ่มทำงานหลังจาก network พร้อมใช้งาน
    # Optional: If your script needs access to I2C or other hardware interfaces,
    # you might need to add dependencies like this:
    # After=systemd-modules-load.service

    [Service]
    User=camuser # เปลี่ยนเป็นชื่อผู้ใช้ของคุณ (เช่น pi หรือชื่อผู้ใช้ที่คุณรันสคริปต์)
    Group=camuser # เปลี่ยนเป็นชื่อกลุ่มของคุณ (มักจะเป็นชื่อผู้ใช้เดียวกัน)
    WorkingDirectory=/home/camuser/aicamera/edge_status/ # เปลี่ยนเป็นพาธของโฟลเดอร์ที่เก็บ pi_monitor.py และ db_manager.py
    ExecStart=/usr/bin/python3 /home/camuser/aicamera/edge_status/pi_monitor.py # เปลี่ยนเป็นพาธเต็มของ python3 และสคริปต์ของคุณ
    Restart=always # รีสตาร์ทบริการอัตโนมัติหากหยุดทำงาน
    RestartSec=10 # รอ 10 วินาทีก่อนรีสตาร์ท

    StandardOutput=journal # ส่ง output ปกติไปยัง journalctl
    StandardError=journal # ส่ง error output ไปยัง journalctl

    [Install]
    WantedBy=multi-user.target # บริการจะเริ่มทำงานในโหมด multi-user (ปกติสำหรับ Raspberry Pi)
    ```

    **คำอธิบายแต่ละส่วน:**

      * **`[Unit]`**: กำหนดข้อมูลพื้นฐานของบริการ
          * `Description`: คำอธิบายสั้น ๆ ของบริการ
          * `After=network.target`: ตรวจสอบให้แน่ใจว่าเครือข่ายพร้อมใช้งานก่อนที่บริการจะเริ่มทำงาน สำคัญสำหรับการส่งข้อมูลผ่าน WebSocket
      * **`[Service]`**: กำหนดการทำงานของบริการ
          * `User`, `Group`: กำหนดผู้ใช้และกลุ่มที่สคริปต์จะทำงานด้วย **สำคัญมาก** เพื่อให้สคริปต์มีสิทธิ์เข้าถึงไฟล์และฮาร์ดแวร์ที่ถูกต้อง (เช่น GPIO, I2C, กล้อง)
          * `WorkingDirectory`: พาธของไดเรกทอรีที่สคริปต์จะรัน **สำคัญ** เพื่อให้สคริปต์สามารถหาไฟล์ `db_manager.py` และ `pi_status.db` ได้
          * `ExecStart`: คำสั่งที่ใช้ในการรันสคริปต์ **ต้องระบุพาธเต็ม** ของ `python3` และ `pi_monitor.py`
          * `Restart=always`: หากสคริปต์หยุดทำงานไม่ว่าจะด้วยสาเหตุใดก็ตาม Systemd จะพยายามรีสตาร์ทอัตโนมัติ
          * `RestartSec=10`: กำหนดระยะเวลารอ 10 วินาทีก่อนที่จะพยายามรีสตาร์ท
          * `StandardOutput`, `StandardError`: กำหนดให้ Systemd บันทึก logs ของสคริปต์ไปยัง `journalctl` ซึ่งช่วยในการ debug
      * **`[Install]`**: กำหนดว่าบริการนี้ควรจะถูกเปิดใช้งานเมื่อใด
          * `WantedBy=multi-user.target`: บริการจะถูกเปิดใช้งานเมื่อระบบเข้าสู่สถานะ multi-user (ซึ่งเป็นโหมดการทำงานปกติของ Raspberry Pi ที่ไม่มี GUI)

3.  **บันทึกและปิดไฟล์:** กด `Ctrl+X`, ตามด้วย `Y`, และ `Enter`

-----

### ขั้นตอนที่ 2: เปิดใช้งานและเริ่มต้นบริการ

เมื่อสร้างไฟล์บริการแล้ว คุณต้องสั่งให้ Systemd รู้จักบริการนี้และเปิดใช้งาน:

1.  **โหลด Systemd ใหม่** เพื่อให้รู้จักไฟล์บริการที่คุณเพิ่งสร้าง:

    ```bash
    sudo systemctl daemon-reload
    ```

2.  **เปิดใช้งานบริการ** เพื่อให้มันเริ่มต้นโดยอัตโนมัติเมื่อ Raspberry Pi บูตเครื่อง:

    ```bash
    sudo systemctl enable pi_monitor.service
    ```

    คุณจะเห็นข้อความคล้ายกับ `Created symlink /etc/systemd/system/multi-user.target.wants/pi_monitor.service -> /etc/systemd/system/pi_monitor.service.`

3.  **เริ่มต้นบริการทันที** (โดยไม่ต้องรีบูตเครื่อง):

    ```bash
    sudo systemctl start pi_monitor.service
    ```

-----

### ขั้นตอนที่ 3: ตรวจสอบสถานะและ Logs

คุณสามารถตรวจสอบว่าบริการของคุณทำงานอยู่หรือไม่ และดู logs เพื่อ debug ได้:

1.  **ตรวจสอบสถานะของบริการ:**

    ```bash
    systemctl status pi_monitor.service
    ```

    คุณควรเห็น `Active: active (running)` สีเขียว หากบริการทำงานอยู่ หากมีปัญหา คุณอาจเห็นสถานะเป็น `failed` และข้อมูลข้อผิดพลาด

2.  **ดู Logs ของบริการ:**

    ```bash
    journalctl -u pi_monitor.service -f
    ```

      * `journalctl`: เป็นเครื่องมือสำหรับดู Systemd logs
      * `-u pi_monitor.service`: ระบุว่าต้องการดู logs ของบริการ `pi_monitor.service`
      * `-f`: "follow" logs แบบเรียลไทม์ (กด `Ctrl+C` เพื่อออกจากโหมดนี้)

    นี่คือสิ่งสำคัญสำหรับการ debug หากสคริปต์ของคุณไม่ทำงานตามที่คาดหวัง คุณจะเห็น output หรือข้อผิดพลาดของสคริปต์ที่นี่

-----

### คำสั่ง Systemd ที่มีประโยชน์อื่นๆ:

  * **หยุดบริการ:**
    ```bash
    sudo systemctl stop pi_monitor.service
    ```
  * **รีสตาร์ทบริการ:**
    ```bash
    sudo systemctl restart pi_monitor.service
    ```
  * **ปิดการใช้งานบริการ** (ไม่ให้เริ่มอัตโนมัติเมื่อบูต):
    ```bash
    sudo systemctl disable pi_monitor.service
    ```

การใช้ Systemd จะช่วยให้สคริปต์ `pi_monitor.py` ของคุณทำงานได้อย่างเสถียรและจัดการได้ง่ายขึ้นบน Raspberry Pi ครับ