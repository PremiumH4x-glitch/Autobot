import os
import time
import json
import threading
import random
import base64
from curl_cffi import requests 
from dm_responder import run_dm_responder

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = [1478627273363034215, 1435876872775929916]
IMAGE_PATH = "freeze_trade_image.jpg"

ORIGINAL_MESSAGE = """# INTRODUCING Our
**Free Freeze Trade script 🔥**
It's completely free! Works on multiple executor like solara, delta, Codex, etc it works **absolutely** perfectly 🤑 

# DM Me for the Best Freeze Trade script for free!!!"""

BUILD_NUMBER = 271450 
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def get_super_properties():
    props = {"os": "Windows", "browser": "Chrome", "device": "", "system_locale": "en-US",
             "browser_user_agent": USER_AGENT, "browser_version": "122.0.0.0", "os_version": "10",
             "client_build_number": BUILD_NUMBER, "release_channel": "stable"}
    return base64.b64encode(json.dumps(props).encode()).decode()

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": USER_AGENT,
    "X-Super-Properties": get_super_properties(),
    "Accept": "*/*",
}

session = requests.Session(impersonate="chrome120")

def generate_nonce():
    return str((int(time.time() * 1000) - 1420070400000) << 22)

def send_message_stealth(channel_id, text, img_path):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    payload = {"content": text, "nonce": generate_nonce(), "tts": False}

    try:
        if img_path and os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                image_data = f.read()
            
            # FIXED: curl_cffi requires a list of tuples for multipart, not a dict
            multipart_data = [
                ("payload_json", (None, json.dumps(payload), "application/json")),
                ("file", ("image.jpg", image_data, "image/jpeg"))
            ]
            
            resp = session.post(url, headers=HEADERS, multipart=multipart_data, timeout=30)
        else:
            resp = session.post(url, headers=HEADERS, json=payload, timeout=15)
        
        return resp.status_code in (200, 201), resp.text
    except Exception as e:
        return False, str(e)

def main():
    threading.Thread(target=run_dm_responder, daemon=True).start()
    print(f"🚀 MAX SPEED | Build {BUILD_NUMBER}")
    
    while True:
        for channel_id in CHANNEL_IDS:
            success, result = send_message_stealth(channel_id, ORIGINAL_MESSAGE, IMAGE_PATH)
            if success:
                print(f"✅ Sent -> {channel_id}")
            else:
                print(f"❌ Error -> {result[:100]}")
            # Minimal 1s pause to avoid immediate Discord rate limits
            time.sleep(1) 
        
        print("🔄 Cycle Restarting...")

if __name__ == '__main__':
    main()
