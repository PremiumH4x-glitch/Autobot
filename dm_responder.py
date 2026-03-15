import time
import os
import random
import base64
import json
from curl_cffi import requests

TOKEN = os.getenv("DISCORD_TOKEN")
HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
}

session = requests.Session(impersonate="chrome120")

def send_dm(channel_id, text):
    payload = {
        "content": text,
        "nonce": str((int(time.time() * 1000) - 1420070400000) << 22),
        "tts": False
    }
    try:
        # DM responder usually doesn't send images, so we use json= to avoid multipart errors
        session.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", 
                     headers=HEADERS, json=payload, timeout=15)
    except: pass

def run_dm_responder():
    print(f"⚡ DM RESPONDER: FAST MODE")
    while True:
        try:
            r = session.get("https://discord.com/api/v10/users/@me/channels", headers=HEADERS)
            if r.status_code == 200:
                # Add your logic to check for unread messages here
                pass
        except: pass
        time.sleep(5) # Checks for DMs every 5 seconds
