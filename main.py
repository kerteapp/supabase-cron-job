import os
import requests
from datetime import datetime, timezone, timedelta
from supabase import create_client

# 1. รับค่า
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# 2. ฟังก์ชันส่ง LINE Broadcast
def send_line_broadcast(message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    data = {"messages": [{"type": "text", "text": message}]}
    try:
        requests.post(url, headers=headers, json=data)
        print("✅ ส่งข้อความสำเร็จ!")
    except Exception as e:
        print(f"❌ Error: {e}")

# 3. ฟังก์ชันสร้างคำทักทาย (ตามเวลาไทย)
def get_greeting_message():
    # แปลงเป็นเวลาไทย (UTC+7)
    tz_thai = timezone(timedelta(hours=7))
    now_thai = datetime.now(tz_thai)
    hour = now_thai.hour
    
    # เลือกคำพูดตามช่วงเวลา
    if 5 <= hour < 11:
        return "อรุณสวัสดิ์ยามเช้าครับ! ☀️ เริ่มต้นวันใหม่อย่างสดใสนะครับ"
    elif 11 <= hour < 13:
        return "เที่ยงแล้ว อย่าลืมหาอะไรทานนะครับ 🍱"
    elif 13 <= hour < 17:
        return "สู้ๆ กับงานช่วงบ่ายนะครับ ✌️"
    elif 17 <= hour < 20:
        return "เลิกงานแล้ว เดินทางกลับบ้านปลอดภัยนะครับ 🚗"
    else:
        return "ค่ำแล้ว พักผ่อนให้เต็มที่นะครับ 🌙"

# 4. เริ่มทำงาน
if __name__ == "__main__":
    print("⏳ เริ่มทำงาน...")
    
    if not all([SUPABASE_URL, SUPABASE_KEY, LINE_ACCESS_TOKEN]):
        print("Error: กุญแจไม่ครบ!")
    else:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            response = supabase.table('users').select("*", count='exact').execute()
            count = len(response.data)
            
            # ดึงคำทักทาย
            greeting = get_greeting_message()
            
            # รวมข้อความ
            msg = f"🤖 รายงานสมาชิก\nจำนวนปัจจุบัน: {count} คน\n\n{greeting}"
            
            send_line_broadcast(msg)
            
        except Exception as e:
            print(f"Error: {e}")
