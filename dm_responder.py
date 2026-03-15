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

def run_dm_responder():
    print(f"⚡ DM RESPONDER: FAST MODE")
    while True:
        try:
            # Polling Discord for DM channels
            r = session.get("https://discord.com/api/v10/users/@me/channels", headers=HEADERS)
            if r.status_code == 200:
                # Add reply logic here if needed
                pass
        except: pass
        time.sleep(2) # Faster polling
