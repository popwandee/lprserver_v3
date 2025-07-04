import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import datetime

# --- กำหนดค่าคงที่ ---
DATABASE_NAME = 'db/edge_status.db' 
OUTPUT_DIR = 'edge_status/reports'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- ฟังก์ชันสำหรับดึงข้อมูลจาก SQLite ---
def fetch_data_to_dataframe(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM edge_status", conn)
    conn.close()

    # Convert timestamp to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Ensure 'id' is the primary key for pandas as well
    df = df.set_index('id')

    # Drop 'sent_to_server' as it's not relevant for analysis graphs
    if 'sent_to_server' in df.columns:
        df = df.drop(columns=['sent_to_server'])

    print(f"Data fetched. Total records: {len(df)}")
    print(df.head())
    return df

# --- ฟังก์ชันสำหรับสร้างกราฟวิเคราะห์สถานะรอบวันในแต่ละสัปดาห์ ---
# แกน y แทนค่า, แกน x แทนชั่วโมงใน 7 วัน, แต่ละคอลัมน์เป็นกราฟเส้น
def plot_weekly_hourly_trends(df, columns_to_plot, filename_prefix="weekly_hourly_trend"):
    print("\nGenerating Weekly Hourly Trends...")

    # Extract day of week and hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['hour'] = df['timestamp'].dt.hour

    # Define order for days of the week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)

    # Group by day of week and hour, then calculate mean for each metric
    weekly_hourly_avg = df.groupby(['day_of_week', 'hour'])[columns_to_plot].mean().unstack(level=0)

    # Plot each metric
    for col in columns_to_plot:
        plt.figure(figsize=(16, 8))
        for day in day_order:
            if (col, day) in weekly_hourly_avg.columns:
                plt.plot(weekly_hourly_avg.index, weekly_hourly_avg[(col, day)], label=day)

        plt.title(f'{col} - Average Hourly Trend Across Days of Week')
        plt.xlabel('Hour of Day')
        plt.ylabel(col)
        plt.xticks(range(0, 24))
        plt.legend(title='Day of Week', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'{filename_prefix}_{col.lower().replace(" ", "_")}.png'))
        plt.close()
        print(f"Saved: {filename_prefix}_{col.lower().replace(' ', '_')}.png")

# --- ฟังก์ชันสำหรับสร้างกราฟแสดงค่าของแต่ละคอลัมน์ในวันที่กำหนด ---
# แกน y แทนค่า, แกน x แทนชั่วโมงในวัน
def plot_daily_hourly_trends(df, date_str, columns_to_plot, filename_prefix="daily_hourly_trend"):
    print(f"\nGenerating Daily Hourly Trends for {date_str}...")

    try:
        selected_date = pd.to_datetime(date_str).date()
    except ValueError:
        print(f"Error: Invalid date format for '{date_str}'. Please use YYYY-MM-DD.")
        return

    daily_df = df[df['timestamp'].dt.date == selected_date].copy()

    if daily_df.empty:
        print(f"No data found for {date_str}.")
        return

    # Sort by timestamp to ensure correct plotting
    daily_df = daily_df.sort_values('timestamp')

    # Plot each metric for the selected day
    for col in columns_to_plot:
        plt.figure(figsize=(14, 7))
        plt.plot(daily_df['timestamp'], daily_df[col], marker='o', linestyle='-')

        plt.title(f'{col} - Hourly Trend on {date_str}')
        plt.xlabel('Time of Day')
        plt.ylabel(col)
        plt.grid(True)

        # Format x-axis to show hours clearly
        formatter = mdates.DateFormatter('%H:%M')
        locator = mdates.HourLocator(interval=1) # Set interval to 1 hour
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gcf().autofmt_xdate() # Auto-format for better readability

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'{filename_prefix}_{date_str}_{col.lower().replace(" ", "_")}.png'))
        plt.close()
        print(f"Saved: {filename_prefix}_{date_str}_{col.lower().replace(' ', '_')}.png")

# --- ฟังก์ชันสำหรับส่งออกข้อมูลเป็น CSV ---
def export_to_csv(df, filename="edge_status_data.csv"):
    csv_path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(csv_path, index=False) # index=False prevents writing the DataFrame index as a column
    print(f"\nData exported to: {csv_path}")

# --- Main execution ---
if __name__ == "__main__":
    # 1. ดึงข้อมูล
    try:
        data_df = fetch_data_to_dataframe(DATABASE_NAME)
    except FileNotFoundError:
        print(f"Error: Database file '{DATABASE_NAME}' not found. Please ensure the path is correct.")
        exit()
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        exit()

    if data_df.empty:
        print("No data in the database to analyze. Exiting.")
        exit()

    # 2. กำหนดคอลัมน์ที่จะนำไปวิเคราะห์
    # ตรวจสอบว่าคอลัมน์เหล่านี้มีอยู่ใน DataFrame
    analysis_columns = [
        'cpu_usage', 'cpu_temp', 'ram_percent', 'hdd_percent',
        # เพิ่มคอลัมน์อื่นๆ ที่เป็นตัวเลขและต้องการวิเคราะห์ (เช่น humidity, temperature หากมี)
        # 'humidity', 'temperature'
    ]
    # Filter out columns that don't exist in the dataframe
    actual_analysis_columns = [col for col in analysis_columns if col in data_df.columns]

    if not actual_analysis_columns:
        print("No valid numerical columns found for analysis. Please check your data or `analysis_columns` list.")
    else:
        # 3. สร้างกราฟวิเคราะห์สถานะรอบวันในแต่ละสัปดาห์
        plot_weekly_hourly_trends(data_df, actual_analysis_columns)

        # 4. สร้างกราฟแสดงค่าของแต่ละคอลัมน์ในวันที่กำหนด
        # เลือกวันที่ล่าสุดในข้อมูลของคุณเป็นตัวอย่าง
        latest_date_str = data_df['timestamp'].max().strftime('%Y-%m-%d')
        print(f"\nPlotting daily trends for the latest available date: {latest_date_str}")
        plot_daily_hourly_trends(data_df, latest_date_str, actual_analysis_columns)

        # คุณสามารถเลือกวันที่อื่นๆ ที่ต้องการวิเคราะห์ได้
        # plot_daily_hourly_trends(data_df, '2024-06-25', actual_analysis_columns)

    # 5. ส่งออกข้อมูลทั้งหมดเป็น CSV
    export_to_csv(data_df)

    print("\nAnalysis complete. Check the 'reports' folder for outputs.")