import requests
import time
import threading
import os
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN", "")
GUILD_ID = os.environ.get("GUILD_ID", "")

headers = {"Authorization": TOKEN}

current_status = "OFFLINE"

def check_status():
    global current_status
    while True:
        try:
            res = requests.get(
                f"https://discord.com/api/v10/guilds/{GUILD_ID}/channels",
                headers=headers
            )

            if res.status_code == 401:
                print("Token sai hoặc hết hạn!")
            elif res.status_code == 403:
                print("Không có quyền truy cập server!")
            elif res.status_code == 200:
                channels = res.json()
                for ch in channels:
                    name = ch.get("name", "").strip()

                    # Bỏ icon khóa + khoảng trắng đầu tên
                    clean = name.lstrip("🔒🔓 ").strip()

                    # Chỉ xét kênh bắt đầu bằng "status"
                    if not clean.lower().startswith("status"):
                        continue

                    # Tìm bóng ở bất kỳ đâu trong tên
                    if "🟢" in name:
                        new_status = "ONLINE"
                    elif "🔴" in name:
                        new_status = "OFFLINE"
                    else:
                        continue

                    if new_status != current_status:
                        print(f"[CHANGED] {name} => {new_status}")
                        current_status = new_status
                    else:
                        print(f"[OK] {new_status}")

            else:
                print(f"HTTP {res.status_code}")

        except Exception as e:
            print(f"Lỗi: {e}")

        time.sleep(60)

@app.route("/")
def home():
    return current_status

thread = threading.Thread(target=check_status)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
