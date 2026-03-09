import os
import requests
import pyodbc
from supabase import create_client

# รับค่ากุญแจ
LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
AZURE_SERVER = os.environ.get("AZURE_SERVER")
AZURE_DB = os.environ.get("AZURE_DB")
AZURE_USER = os.environ.get("AZURE_USER")
AZURE_PASS = os.environ.get("AZURE_PASS")

def send_line_broadcast(message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    data = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    print("⏳ กำลังดึงข้อมูล...")
    report_lines = ["📊 สรุปข้อมูลประจำวัน"]
    
    # --- 1. PostgreSQL ---
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table('users').select("*", count='exact').execute()
        count_supa = len(response.data)
        report_lines.append(f"🟢 PostgreSQL: {count_supa} รายการ")
        print("✅ ดึงข้อมูล PostgreSQL สำเร็จ")
    except Exception as e:
        report_lines.append(f"🔴 PostgreSQL ล้มเหลว")
        print(f"❌ Error PostgreSQL: {e}")

    # --- 2. Azure SQL (เวอร์ชัน Auto-detect Driver) ---
    try:
        # 💡 ให้ Python ค้นหาว่า GitHub มี Driver ชื่ออะไรติดตั้งอยู่
        driver_list = pyodbc.drivers()
        print(f"🔍 ไดรเวอร์ที่มีในเครื่อง: {driver_list}")
        
        sql_driver = None
        for d in driver_list:
            if 'SQL Server' in d:
                sql_driver = f"{{{d}}}"
                break
                
        if not sql_driver:
            # ถ้าหาไม่เจอจริงๆ ให้บังคับใช้ตัวมาตรฐาน
            sql_driver = "{ODBC Driver 18 for SQL Server}"

        print(f"🎯 เลือกใช้ Driver: {sql_driver}")

        # ประกอบร่าง Username 
        server_prefix = str(AZURE_SERVER).split('.')[0]
        actual_user = str(AZURE_USER)
        if "@" not in actual_user:
            actual_user = f"{actual_user}@{server_prefix}"

        # เชื่อมต่อ (pyodbc จะเก่งเรื่องการจัดการพอร์ตของ Azure ครับ)
        conn_str = (
            f"DRIVER={sql_driver};"
            f"SERVER=tcp:{AZURE_SERVER},1433;"
            f"DATABASE={AZURE_DB};"
            f"UID={actual_user};"
            f"PWD={AZURE_PASS};"
            "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # ⚠️ เปลี่ยน your_table_name เป็นชื่อตารางจริงด้วยนะครับ
        cursor.execute("SELECT COUNT(*) FROM Users")
        count_azure = cursor.fetchone()[0]
        conn.close()
        
        report_lines.append(f"🔵 Azure SQL: {count_azure} รายการ")
        print("✅ ดึงข้อมูล Azure SQL สำเร็จ")
    except Exception as e:
        report_lines.append(f"🔴 Azure SQL ล้มเหลว")
        print(f"❌ Error Azure: {e}") 

    # --- ส่งเข้า LINE ---
    final_message = "\n".join(report_lines)
    send_line_broadcast(final_message)
    print("✅ ส่งรายงานเข้า LINE เรียบร้อย!")
