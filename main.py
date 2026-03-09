import os
import requests
import pyodbc
from supabase import create_client

# 1. รับค่ากุญแจทั้งหมด
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
    print("⏳ กำลังดึงข้อมูลจากทั้ง 2 แหล่ง...")
    
    # สร้างหัวข้อความ
    report_lines = ["📊 สรุปข้อมูลประจำวัน"]
    
    # --- ดึงข้อมูลที่ 1: Supabase (PostgreSQL) ---
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table('users').select("*", count='exact').execute()
        count_supa = len(response.data)
        report_lines.append(f"🟢 PostgreSQL: {count_supa} รายการ")
    except Exception as e:
        report_lines.append(f"🔴 PostgreSQL ล้มเหลว")

    # --- ดึงข้อมูลที่ 2: Azure SQL ---
    try:
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER=tcp:{AZURE_SERVER},1433;"
            f"DATABASE={AZURE_DB};"
            f"UID={AZURE_USER};"
            f"PWD={AZURE_PASS};"
            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # ⚠️ อย่าลืมเปลี่ยน your_table_name ตรงบรรทัดด้านล่างนี้นะครับ
        cursor.execute("SELECT COUNT(*) FROM users")
        count_azure = cursor.fetchone()[0]
        conn.close()
        
        report_lines.append(f"🔵 Azure SQL: {count_azure} รายการ")
    except Exception as e:
        report_lines.append(f"🔴 Azure SQL ล้มเหลว")

    # --- รวมข้อความและส่ง LINE ---
    final_message = "\n".join(report_lines)
    send_line_broadcast(final_message)
    print("✅ ส่งรายงานสรุปเข้า LINE เรียบร้อยแล้ว!")
