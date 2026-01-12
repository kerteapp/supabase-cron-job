import os
import requests
from supabase import create_client

# 1. รับค่าจาก GitHub Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

# 2. ฟังก์ชันส่ง LINE (Messaging API)
def send_line_push(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("✅ ส่ง LINE สำเร็จ! (เช็คในมือถือได้เลย)")
        else:
            print(f"❌ ส่งไม่ผ่าน: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# 3. เริ่มทำงาน
if __name__ == "__main__":
    print("⏳ เริ่มทำงาน...")
    
    # เช็คกุญแจ
    if not all([SUPABASE_URL, SUPABASE_KEY, LINE_ACCESS_TOKEN, LINE_USER_ID]):
        print("Error: กุญแจไม่ครบ! กรุณาเช็ค GitHub Secrets")
    else:
        # เชื่อมต่อ Supabase
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # ดึงข้อมูล (นับจำนวนคน)
            response = supabase.table('users').select("*", count='exact').execute()
            count = len(response.data)
            
            # ข้อความที่จะส่ง
            msg = f"🤖 รายงานจาก Supabase\nขณะนี้มีสมาชิก: {count} คน"
            
            # ส่งเข้ามือถือ
            send_line_push(msg)
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")
