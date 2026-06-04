import requests
import time
import threading
import os
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN", "")
GUILD_ID = os.environ.get("GUILD_ID", "")

headers = {"Authorization": TOKEN}

last_status = {}

def check_status():
    global last_status
    while True:
        try:
            res = requests.get(
                f"https://discord.com/api/v10/guilds/{GUILD_ID}/channels",
                headers=headers
            )

            if res.status_code == 401:
                print("❌ Token sai hoặc hết hạn!")
            elif res.status_code == 403:
                print("❌ Không có quyền truy cập server!")
            elif res.status_code == 200:
                channels = res.json()
                for ch in channels:
                    name = ch.get("name", "")
                    if "status" in name.lower():
                        old = last_status.get(ch["id"])

                        if "🟢" in name:
                            status = "ONLINE"
                        elif "🔴" in name:
                            status = "PATCHED"
                        else:
                            status = "UNKNOWN"

                        # Chỉ log khi status thay đổi
                        if old != status:
                            print(f"[STATUS CHANGED] {name} => {status}")
                            last_status[ch["id"]] = status
                        else:
                            print(f"[OK] {name} => {status}")
            else:
                print(f"⚠️ HTTP {res.status_code}")

        except Exception as e:
            print(f"Lỗi: {e}")

        time.sleep(60)

@app.route("/")
def home():
    if last_status:
        lines = [f"{k}: {v}" for k, v in last_status.items()]
        return "✅ Bot đang chạy\n\n" + "\n".join(lines)
    return "✅ Bot đang chạy — chưa có data"

thread = threading.Thread(target=check_status)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
