import os
import time
import json
import threading
import requests 

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = [1478627273363034215, 1435876872775929916]
IMAGE_PATH = "freeze_trade_image.jpg"

ORIGINAL_MESSAGE = """# INTRODUCING Our
**Free Freeze Trade script 🔥**
It's completely free! Works on multiple executor like solara, delta, Codex, etc it works **absolutely** perfectly 🤑 

# DM Me for the Best Freeze Trade script for free!!!"""

session = requests.Session()

def get_headers():
    return {
        "Authorization": TOKEN,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

def send_message_logic(channel_id, text, img_path):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    nonce = str((int(time.time() * 1000) - 1420070400000) << 22)
    payload = {"content": text, "nonce": nonce, "tts": False}

    try:
        headers = get_headers()
        if img_path and os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                files = {'file': ('image.jpg', f, 'image/jpeg')}
                data = {'payload_json': json.dumps(payload)}
                resp = session.post(url, headers=headers, files=files, data=data, timeout=30)
        else:
            resp = session.post(url, headers=headers, json=payload, timeout=15)
        
        return resp.status_code in (200, 201), resp.text
    except Exception as e:
        return False, str(e)

from dm_responder import run_dm_responder

def main():
    threading.Thread(target=run_dm_responder, daemon=True).start()
    print("🚀 HIGH SPEED MODE (REQUESTS) - NO BREAKS")
    
    while True:
        for cid in CHANNEL_IDS:
            success, result = send_message_logic(cid, ORIGINAL_MESSAGE, IMAGE_PATH)
            print(f"{'✅' if success else '❌'} {cid} | {result[:50]}")
            time.sleep(2) 
        time.sleep(1)

if __name__ == '__main__':
    main()
