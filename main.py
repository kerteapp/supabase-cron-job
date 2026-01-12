import os
from supabase import create_client

# รับค่าจาก "ความลับ" (Secrets) ที่เราจะไปตั้งใน GitHub
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("หา Key ไม่เจอ! อย่าลืมตั้งค่าใน GitHub Secrets")

# สร้าง Client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_job():
    print("⏳ เริ่มทำงานตามเวลา...")
    # ... ใส่ Logic การทำงานของคุณตรงนี้ ...
    # ตัวอย่าง:
    try:
        res = supabase.table('users').select("*").limit(1).execute()
        print("✅ เชื่อมต่อสำเร็จ! ตัวอย่างข้อมูล:", res.data)
    except Exception as e:
        print("❌ เกิดข้อผิดพลาด:", e)

if __name__ == "__main__":
    run_job()
