folder_path = "aicamera/captured_images"
min_free_space_gb = 10
retention_days = 7
batch_size = 100

def manage_image_folder(folder_path, min_free_space_gb, retention_days, batch_size):
    import os, time, shutil
    from datetime import datetime, timedelta

    # Step 1: ตรวจสอบพื้นที่ว่าง
    def get_free_space_gb(path):
        total, used, free = shutil.disk_usage(path)
        return free / (1024 ** 3)

    # Step 2: ถ้าพื้นที่ว่างต่ำกว่า threshold ให้เริ่มลบ
    if get_free_space_gb(folder_path) < min_free_space_gb:
        now = time.time()
        retention_limit = now - (retention_days * 86400)

        # Step 3: รวบรวมไฟล์ที่เก่ากว่าช่วง retention
        image_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.png')) and
               os.path.getmtime(os.path.join(folder_path, f)) < retention_limit
        ]

        # Step 4: เรียงตามเวลาเก่า -> ใหม่
        image_files.sort(key=lambda x: os.path.getmtime(x))

        # Step 5: ลบเป็น batch
        for file in image_files[:batch_size]:
            os.remove(file)
            print(f"Deleted: {file}")

        print(f"Deleted {min(len(image_files), batch_size)} files to free up space.")
    else:
        print("Disk space is sufficient. No action needed.")