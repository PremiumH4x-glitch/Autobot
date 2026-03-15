import time
import os
import random
import base64
import json
from curl_cffi import requests

TOKEN = os.getenv("DISCORD_TOKEN")
BUILD_NUMBER = 271450 
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": USER_AGENT,
    "X-Super-Properties": base64.b64encode(json.dumps({
        "os": "Windows", "browser": "Chrome", "client_build_number": BUILD_NUMBER
    }).encode()).decode(),
    "Accept": "*/*",
}

session = requests.Session(impersonate="chrome120")

def send_stealth_dm(channel_id, text):
    payload = {
        "content": text,
        "nonce": str((int(time.time() * 1000) - 1420070400000) << 22),
        "tts": False
    }
    try:
        session.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", 
                     headers=HEADERS, json=payload, timeout=15)
    except: pass

def run_dm_responder():
    print(f"⚡ Fast-Response DM Active")
    while True:
        try:
            r = session.get("https://discord.com/api/v10/users/@me/channels", headers=HEADERS)
            if r.status_code == 200:
                channels = [c for c in r.json() if c['type'] == 1]
                # Logic for processing messages would go here
                pass
        except: pass
        
        time.sleep(15) # Check for new DMs every 15 seconds
