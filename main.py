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

CHANNEL_IDS = [1478627273363034215, 1435876872775929916]
IMAGE_PATH = "freeze_trade_image.jpg"
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

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": USER_AGENT,
    "X-Super-Properties": get_super_properties(),
    "Accept": "*/*",
    "X-Discord-Locale": "en-US",
    "Origin": "https://discord.com",
    "Referer": "https://discord.com/channels/@me",
}

# Impersonate a real Chrome TLS handshake
session = requests.Session(impersonate="chrome120")

# --- HUMANIZED ACTIONS ---

def simulate_reading(channel_id):
    """Fetches channel history to mimic a human clicking the channel"""
    try:
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=50"
        session.get(url, headers=HEADERS, timeout=10)
        time.sleep(random.uniform(3.0, 7.5)) # Time spent 'reading' the chat
    except: pass

def send_typing(channel_id):
    url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    try: session.post(url, headers=HEADERS, timeout=5)
    except: pass

def generate_nonce():
    """Generates a Discord-compliant Snowflake-style nonce"""
    return str((int(time.time() * 1000) - 1420070400000) << 22)

def send_message_stealth(channel_id, text, img_path):
    # 1. Look at the channel first
    simulate_reading(channel_id)
    
    # 2. Show 'typing'
    send_typing(channel_id)
    time.sleep(random.uniform(4.5, 9.0)) # Realistic typing delay for a long message
    
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    
    # Prepare payload with Nonce (vital for stealth)
    payload = {
        "content": text,
        "nonce": generate_nonce(),
        "tts": False,
        "flags": 0
    }

    try:
        if img_path and os.path.exists(img_path):
            # For images, Discord uses a multipart/form-data request
            # We must remove Content-Type from headers to let the library set it
            h = HEADERS.copy()
            with open(img_path, 'rb') as f:
                files = {'file': ('image.jpg', f, 'image/jpeg')}
                # Note: Nonce and content must be in the 'payload_json' field for multipart
                data = {"payload_json": json.dumps(payload)}
                resp = session.post(url, headers=h, files=files, data=data, timeout=30)
        else:
            resp = session.post(url, headers=HEADERS, json=payload, timeout=15)
            
        return resp.status_code in (200, 201), resp.text
    except Exception as e:
        return False, str(e)

def main():
    # Start the DM responder
    threading.Thread(target=run_dm_responder, daemon=True).start()

    print(f"👻 Ghost Mode Engaged | Build {BUILD_NUMBER}")
    send_count = 0

    while True:
        # Shuffle IDs
        queue = CHANNEL_IDS.copy()
        random.shuffle(queue)

        for channel_id in queue:
            # Randomly skip a cycle to avoid 'perfect' consistency
            if random.random() < 0.15: 
                print(f"⏭️ Skipping {channel_id} this round for stealth...")
                continue

            success, result = send_message_stealth(channel_id, ORIGINAL_MESSAGE, IMAGE_PATH)

            if success:
                send_count += 1
                print(f"✅ Sent to {channel_id} (Total: {send_count})")
                time.sleep(random.randint(60, 180)) # Big gap between different channels
            else:
                print(f"❌ Failed: {result[:50]}")
                time.sleep(random.randint(30, 60))

        # Long break after a full cycle
        rest = random.randint(900, 2400) # 15 to 40 minutes
        print(f"☕ Resting for {rest//60}m...")
        time.sleep(rest)

if __name__ == '__main__':
    main()
