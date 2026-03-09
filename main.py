import os
import requests
import pymssql
from supabase import create_client

# 1. รับค่ากุญแจ
LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
AZURE_SERVER = os.environ.get("AZURE_SERVER")
AZURE_DB = os.environ.get("AZURE_DB")
AZURE_USER = os.environ.get("AZURE_USER")
AZURE_PASS = os.environ.get("AZURE_PASS")

# 2. ฟังก์ชันส่ง LINE
def send_line_broadcast(message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    data = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=data)

# 3. เริ่มทำงาน
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

    # --- 2. Azure SQL ---
    try:
        # บังคับประกอบร่าง Username ใหม่ให้ถูกต้อง 100%
        server_prefix = str(AZURE_SERVER).split('.')[0]
        actual_user = str(AZURE_USER)
        if "@" not in actual_user:
            actual_user = f"{actual_user}@{server_prefix}"
            
        # ปรินต์เช็คเพื่อความชัวร์ (จะแสดงใน Log)
        print(f"🔍 [Debug] ระบบกำลังส่ง Username นี้ไปล็อกอิน: {actual_user}")
        
        conn = pymssql.connect(
            server=AZURE_SERVER,
            user=actual_user,
            password=AZURE_PASS,
            database=AZURE_DB,
            port="1433" # ล็อกพอร์ตมาตรฐานของ Azure SQL ไว้เลย
        )
        cursor = conn.cursor()
        
        # ⚠️ เปลี่ยน your_table_name เป็นชื่อตารางจริงด้วยนะครับ
        cursor.execute("SELECT COUNT(*) FROM your_table_name")
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
