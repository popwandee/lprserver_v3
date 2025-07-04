import sqlite3
import datetime

DATABASE_NAME = 'db/edge_status.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edge_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_usage REAL,
            cpu_temp REAL,
            ram_total REAL,
            ram_used REAL,
            ram_percent REAL,
            hdd_total REAL,
            hdd_used REAL,
            hdd_percent REAL,
            camera_status TEXT,
            power_status TEXT,
            overall_status TEXT,
            sent_to_server INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def insert_status(data):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO edge_status (
            timestamp, cpu_usage, cpu_temp, ram_total, ram_used, ram_percent,
            hdd_total, hdd_used, hdd_percent, camera_status, 
            power_status,  overall_status
        ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['timestamp'], data['cpu_usage'], data['cpu_temp'],
        data['ram_total'], data['ram_used'], data['ram_percent'],
        data['hdd_total'], data['hdd_used'], data['hdd_percent'],
        data['camera_status'],  data['power_status'],
        data['overall_status']
    ))
    conn.commit()
    conn.close()

def get_unsent_data():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM edge_status WHERE sent_to_server = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_as_sent(ids):
    if not ids:
        return
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(ids))
    cursor.execute(f"UPDATE edge_status SET sent_to_server = 1 WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print(f"Database '{DATABASE_NAME}' initialized successfully.")
    # Example usage:
    # data = {
    #     'timestamp': datetime.datetime.now().isoformat(),
    #     'cpu_usage': 10.5,
    #     'cpu_temp': 45.0,
    #     'ram_total': 4000.0,
    #     'ram_used': 1000.0,
    #     'ram_percent': 25.0,
    #     'hdd_total': 60.0,
    #     'hdd_used': 10.0,
    #     'hdd_percent': 16.67,
    #     'camera_status': 'OK',
    #     'power_status': 'Stable',
    #     'overall_status': 'Normal'
    # }
    # insert_status(data)
    # print("Data inserted.")
    #
    # unsent = get_unsent_data()
    # for row in unsent:
    #     print(row)
    #
    # if unsent:
    #     ids_to_mark = [row[0] for row in unsent]
    #     mark_as_sent(ids_to_mark)
    #     print(f"Marked {len(ids_to_mark)} rows as sent.")