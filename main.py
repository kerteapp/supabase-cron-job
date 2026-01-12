import os
import requests
from supabase import create_client

# 1. รับค่า (User ID ไม่ต้องใช้แล้วในโหมดนี้ แต่ค้างไว้ไม่เป็นไร)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# 2. ฟังก์ชันส่ง LINE แบบ Broadcast (ส่งหาทุกคนที่เป็นเพื่อน)
def send_line_broadcast(message):
    url = 'https://api.line.me/v2/bot/message/broadcast' # <-- เปลี่ยน URL เป็น broadcast
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    # ไม่ต้องระบุ "to" แล้ว เพราะส่งหาทุกคน
    data = {
        "messages": [{"type": "text", "text": message}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("✅ ส่ง Broadcast สำเร็จ! (ทุกคนควรได้รับ)")
        else:
            print(f"❌ ส่งไม่ผ่าน: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# 3. เริ่มทำงาน
if __name__ == "__main__":
    print("⏳ เริ่มทำงาน (โหมด Broadcast)...")
    
    if not all([SUPABASE_URL, SUPABASE_KEY, LINE_ACCESS_TOKEN]):
        print("Error: กุญแจไม่ครบ!")
    else:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = supabase.table('users').select("*", count='exact').execute()
            count = len(response.data)
            
            msg = f"🤖 ประกาศจากบอท\nสมาชิกทั้งหมด: {count} คน"
            
            # เรียกใช้ฟังก์ชันใหม่
            send_line_broadcast(msg)
            
        except Exception as e:
            print(f"Error: {e}")
