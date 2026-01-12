import os
import requests
from supabase import create_client

# รับค่า
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

# ฟังก์ชันส่ง LINE
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
            print("✅ ส่ง LINE สำเร็จ! (ถ้าไม่เด้งให้เช็ค UserID)")
        else:
            print(f"❌ ส่งไม่ผ่าน: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# เริ่มทำงาน
if __name__ == "__main__":
    print("⏳ เริ่มทำงาน (เวอร์ชันใหม่)...")
    
    if not all([SUPABASE_URL, SUPABASE_KEY, LINE_ACCESS_TOKEN, LINE_USER_ID]):
        print("Error: กุญแจไม่ครบ!")
    else:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = supabase.table('users').select("*", count='exact').execute()
            count = len(response.data)
            
            msg = f"🤖 Test Bot\nสมาชิก: {count} คน"
            send_line_push(msg)
            
        except Exception as e:
            print(f"Error: {e}")
