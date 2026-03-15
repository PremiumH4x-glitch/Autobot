import time
import os
import requests

TOKEN = os.getenv("DISCORD_TOKEN")

def run_dm_responder():
    print("⚡ DM RESPONDER ONLINE")
    headers = {
        "Authorization": TOKEN,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    while True:
        try:
            # Poll for new DM channels
            r = requests.get("https://discord.com/api/v10/users/@me/channels", headers=headers, timeout=10)
            if r.status_code == 200:
                # Add your reply logic here
                pass
        except:
            pass
        time.sleep(5) # Check every 5 seconds
