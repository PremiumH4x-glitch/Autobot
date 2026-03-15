import requests
import os
import time
import re
import json
import threading
import random
from dm_responder import run_dm_responder

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable not set")
    exit(1)

# Multiple Channel IDs
CHANNEL_IDS = [
    1478627273363034215,
    1435876872775929916
]

ORIGINAL_MESSAGE = """# INTRODUCING Our
**Free Freeze Trade script 🔥**
It's completely free! Works on multiple executor like solara, delta, Codex, etc it works **absolutely** perfectly 🤑 

# DM Me for the Best Freeze Trade script for free!!!"""

IMAGE_PATH = "freeze_trade_image.jpg"

# --- HUMANIZED HEADERS ---
# These mimic a modern Chrome browser on Windows exactly.
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://discord.com",
    "Referer": "https://discord.com/channels/@me",
    "X-Discord-Locale": "en-US",
    "X-Debug-Options": "bugReporterEnabled",
}

CYRILLIC_MAP = {'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с', 'x': 'х', 'y': 'у', 'i': 'і'}

# --- UTILITY FUNCTIONS ---

def send_typing(channel_id):
    """Sends the 'is typing...' signal to Discord"""
    url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    try:
        requests.post(url, headers={"Authorization": TOKEN}, timeout=5)
    except:
        pass

def human_delay(min_s, max_s):
    """Wait for a random float between min and max seconds"""
    time.sleep(random.uniform(min_s, max_s))

def cyrillic_bypass(text):
    return "".join(CYRILLIC_MAP.get(c, c) for c in text)

def do_request(url, message_text, image_path):
    """Modified request to handle multipart or JSON naturally"""
    send_headers = {k: v for k, v in HEADERS.items() if k != "Content-Type"}
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            files = {'file': ('image.jpg', f, 'image/jpeg')}
            data = {'content': message_text}
            return requests.post(url, headers=send_headers, files=files, data=data, timeout=30)
    else:
        return requests.post(url, headers=HEADERS, json={"content": message_text}, timeout=15)

def send_message_logic(channel_id, text, img):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    
    # Randomly decide to use Cyrillic bypass or original to avoid fingerprinting
    final_text = cyrillic_bypass(text) if random.random() > 0.5 else text
    
    # 1. Start typing
    send_typing(channel_id)
    # 2. Wait a realistic amount of time to "type" (3-7 seconds)
    human_delay(3.2, 7.8)
    
    try:
        resp = do_request(url, final_text, img)
        if resp.status_code in (200, 201):
            return True, "Success"
        elif resp.status_code == 429:
            retry_after = resp.json().get('retry_after', 5)
            return False, f"Rate limited: wait {retry_after}s"
        return False, f"Status {resp.status_code}: {resp.text[:50]}"
    except Exception as e:
        return False, str(e)

def main():
    # Start the DM responder in the background
    threading.Thread(target=run_dm_responder, daemon=True).start()

    print("🚀 Anti-Detection Mode Engaged")
    send_count = 0

    while True:
        # Shuffle IDs so the sequence isn't predictable
        current_queue = CHANNEL_IDS.copy()
        random.shuffle(current_queue)

        for channel_id in current_queue:
            print(f"\n📡 Target: {channel_id}")
            
            # Random delay BEFORE sending (mimics checking the channel)
            human_delay(10, 30)
            
            img = IMAGE_PATH if os.path.exists(IMAGE_PATH) else None
            success, msg = send_message_logic(channel_id, ORIGINAL_MESSAGE, img)

            if success:
                send_count += 1
                print(f"   ✅ Sent! (Total: {send_count})")
                # Wait before next channel so it's not rapid-fire
                human_delay(45, 120)
            else:
                print(f"   ❌ Failed: {msg}")
                human_delay(20, 40)

        # Long "Rest Period" after finishing all channels
        rest_time = random.randint(600, 1800) # 10 to 30 minutes
        print(f"\n☕ Taking a human break for {rest_time//60} minutes...")
        time.sleep(rest_time)

if __name__ == '__main__':
    main()
