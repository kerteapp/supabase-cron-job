import os
import requests
import pymssql
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

    # --- 2. Azure SQL ---
    try:
        # 💡 ทริคของ Azure: ตัดเอาชื่อเซิร์ฟเวอร์ท่อนแรกมาต่อท้าย Username
        server_prefix = str(AZURE_SERVER).split('.')[0]
        # ถ้าในกุญแจมี @ อยู่แล้วก็ไม่ต้องเติมซ้ำ
        full_azure_user = AZURE_USER if "@" in str(AZURE_USER) else f"{AZURE_USER}@{server_prefix}"
        
        conn = pymssql.connect(
            server=AZURE_SERVER,
            user=full_azure_user, # ใช้ Username ที่ประกอบร่างใหม่
            password=AZURE_PASS,
            database=AZURE_DB
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
