import os
import time
import json
import threading
import random
import base64
from curl_cffi import requests # Requires: pip install curl_cffi
from dm_responder import run_dm_responder

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable not set")
    exit(1)

# Target Channel IDs
CHANNEL_IDS = [1478627273363034215, 1435876872775929916]

# The advertisement text
ORIGINAL_MESSAGE = """# INTRODUCING Our
**Free Freeze Trade script 🔥**
It's completely free! Works on multiple executor like solara, delta, Codex, etc it works **absolutely** perfectly 🤑 

# DM Me for the Best Freeze Trade script for free!!!"""

IMAGE_PATH = "freeze_trade_image.jpg"

# March 2026 Stealth Metrics
BUILD_NUMBER = 271450 
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# --- STEALTH HEADERS & SESSION ---
def get_super_properties():
    props = {
        "os": "Windows", "browser": "Chrome", "device": "", "system_locale": "en-US",
        "browser_user_agent": USER_AGENT, "browser_version": "122.0.0.0", "os_version": "10",
        "client_build_number": BUILD_NUMBER, "release_channel": "stable"
    }
    return base64.b64encode(json.dumps(props).encode()).decode()

# Note: We keep HEADERS global but copy/modify them for multipart requests
HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": USER_AGENT,
    "X-Super-Properties": get_super_properties(),
    "Accept": "*/*",
    "X-Discord-Locale": "en-US",
    "Origin": "https://discord.com",
    "Referer": "https://discord.com/channels/@me",
}

# Impersonate Chrome 120+ TLS Handshake (Vital for bypass)
session = requests.Session(impersonate="chrome120")

# --- HUMANIZED ACTIONS ---

def simulate_reading(channel_id):
    """Mimics a human clicking the channel and viewing messages"""
    try:
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=30"
        session.get(url, headers=HEADERS, timeout=10)
        time.sleep(random.uniform(4.0, 8.5)) 
    except: pass

def send_typing(channel_id):
    url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    try: session.post(url, headers=HEADERS, timeout=5)
    except: pass

def generate_nonce():
    """Generates a Snowflake-style nonce used by the real Discord client"""
    return str((int(time.time() * 1000) - 1420070400000) << 22)

def send_message_stealth(channel_id, text, img_path):
    # 1. Simulate reading context
    simulate_reading(channel_id)
    
    # 2. Show 'typing' signal
    send_typing(channel_id)
    # Realistic typing time for the length of ORIGINAL_MESSAGE
    time.sleep(random.uniform(5.0, 10.0)) 
    
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    
    payload = {
        "content": text,
        "nonce": generate_nonce(),
        "tts": False,
        "flags": 0
    }

    try:
        if img_path and os.path.exists(img_path):
            # FIXED: curl_cffi uses 'multipart' instead of 'files'
            with open(img_path, 'rb') as f:
                image_data = f.read()
            
            # For multipart, we must NOT set Content-Type in HEADERS manually
            h = HEADERS.copy()
            if "Content-Type" in h:
                del h["Content-Type"]

            multipart_data = {
                "payload_json": json.dumps(payload),
                "file": ("image.jpg", image_data, "image/jpeg")
            }
            
            resp = session.post(url, headers=h, multipart=multipart_data, timeout=30)
        else:
            resp = session.post(url, headers=HEADERS, json=payload, timeout=15)
            
        return resp.status_code in (200, 201), resp.text
    except Exception as e:
        return False, str(e)

# --- MAIN LOOP ---

def main():
    # Start the DM responder background thread
    threading.Thread(target=run_dm_responder, daemon=True).start()

    print(f"👻 Ghost Mode Engaged | Build {BUILD_NUMBER}")
    send_count = 0

    while True:
        # Shuffle targets to avoid predictable patterns
        queue = CHANNEL_IDS.copy()
        random.shuffle(queue)

        for channel_id in queue:
            # Human element: 15% chance to skip a post this cycle
            if random.random() < 0.15: 
                print(f"⏭️ Skipping {channel_id} this round for stealth...")
                continue

            success, result = send_message_stealth(channel_id, ORIGINAL_MESSAGE, IMAGE_PATH)

            if success:
                send_count += 1
                print(f"✅ Message sent to {channel_id} (Total: {send_count})")
                # Wait 1-3 minutes between channels
                time.sleep(random.randint(60, 180)) 
            else:
                print(f"❌ Failed to send: {result[:100]}")
                time.sleep(random.randint(30, 60))

        # Take a long break after finishing the queue
        rest = random.randint(1200, 3000) # 20 to 50 minutes
        print(f"☕ Finished cycle. Resting for {rest//60} minutes...")
        time.sleep(rest)

if __name__ == '__main__':
    main()
