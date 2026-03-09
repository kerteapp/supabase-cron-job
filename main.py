import os
import requests
import pyodbc
import oracledb
from supabase import create_client

# 1. รับค่ากุญแจทั้งหมด
LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

AZURE_SERVER = os.environ.get("AZURE_SERVER")
AZURE_DB = os.environ.get("AZURE_DB")
AZURE_USER = os.environ.get("AZURE_USER")
AZURE_PASS = os.environ.get("AZURE_PASS")

ORACLE_USER = os.environ.get("ORACLE_USER")
ORACLE_PASS = os.environ.get("ORACLE_PASS")
ORACLE_DSN = os.environ.get("ORACLE_DSN")

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
    print("⏳ กำลังดึงข้อมูลจาก 3 แหล่ง...")
    report_lines = ["📊 สรุปข้อมูลประจำวัน"]
    
    # --- 1. PostgreSQL (Supabase) ---
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
        driver_list = pyodbc.drivers()
        sql_driver = next((f"{{{d}}}" for d in driver_list if 'SQL Server' in d), "{ODBC Driver 18 for SQL Server}")
        
        server_prefix = str(AZURE_SERVER).split('.')[0]
        actual_user = str(AZURE_USER) if "@" in str(AZURE_USER) else f"{AZURE_USER}@{server_prefix}"

        conn_str = (
            f"DRIVER={sql_driver};"
            f"SERVER=tcp:{AZURE_SERVER},1433;"
            f"DATABASE={AZURE_DB};"
            f"UID={actual_user};"
            f"PWD={AZURE_PASS};"
            "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
        )
        conn_azure = pyodbc.connect(conn_str)
        cursor_azure = conn_azure.cursor()
        
        # คิวรีตาราง Users ของ Azure
        cursor_azure.execute("SELECT COUNT(*) FROM Users")
        count_azure = cursor_azure.fetchone()[0]
        conn_azure.close()
        
        report_lines.append(f"🔵 Azure SQL: {count_azure} รายการ")
        print("✅ ดึงข้อมูล Azure SQL สำเร็จ")
    except Exception as e:
        report_lines.append(f"🔴 Azure SQL ล้มเหลว")
        print(f"❌ Error Azure: {e}") 

    # --- 3. Oracle DB ---
    try:
        # เชื่อมต่อ Oracle แบบ One-Way TLS (พอร์ต 1521) ไม่ต้องใช้ Wallet
        conn_oracle = oracledb.connect(
            user=ORACLE_USER, 
            password=ORACLE_PASS, 
            dsn=ORACLE_DSN
        )
        cursor_oracle = conn_oracle.cursor()
        
        # คิวรีตาราง EMPLOYEES ของ Oracle
        cursor_oracle.execute("SELECT COUNT(*) FROM EMPLOYEES")
        count_oracle = cursor_oracle.fetchone()[0]
        conn_oracle.close()
        
        report_lines.append(f"🟠 Oracle DB: {count_oracle} รายการ")
        print("✅ ดึงข้อมูล Oracle สำเร็จ")
    except Exception as e:
        report_lines.append(f"🔴 Oracle ล้มเหลว")
        print(f"❌ Error Oracle: {e}")

    # --- ส่งเข้า LINE ---
    final_message = "\n".join(report_lines)
    send_line_broadcast(final_message)
    print("✅ ส่งรายงานเข้า LINE เรียบร้อย!")
