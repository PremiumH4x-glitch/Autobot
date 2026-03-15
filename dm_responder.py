import time
import os
import re
import random
import base64
import json
from curl_cffi import requests

TOKEN = os.getenv("DISCORD_TOKEN")

# March 2026 Build Metrics
BUILD_NUMBER = 271450 
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def get_super_properties():
    props = {
        "os": "Windows", "browser": "Chrome", "device": "", "system_locale": "en-US",
        "browser_user_agent": USER_AGENT, "browser_version": "122.0.0.0", "os_version": "10",
        "client_build_number": BUILD_NUMBER, "release_channel": "stable"
    }
    return base64.b64encode(json.dumps(props).encode()).decode()

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": USER_AGENT,
    "X-Super-Properties": get_super_properties(),
    "Accept": "*/*",
    "X-Discord-Locale": "en-US",
}

session = requests.Session(impersonate="chrome120")

# --- ADVANCED STEALTH ---

def simulate_reading(channel_id):
    """Simulates clicking the channel and 'reading' for a few seconds"""
    # Discord marks a channel as 'read' via this ack endpoint
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages/ack"
    try:
        session.post(url, headers=HEADERS, json={"token": None}, timeout=5)
        time.sleep(random.uniform(2.5, 6.0)) # Time spent 'reading'
    except: pass

def send_typing(channel_id):
    url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    try: session.post(url, headers=HEADERS, timeout=5)
    except: pass

def send_stealth_dm(channel_id, text):
    simulate_reading(channel_id)
    send_typing(channel_id)
    
    # Calculate typing time based on character count + human error pauses
    base_speed = len(text) * random.uniform(0.05, 0.1)
    extra_pauses = random.choice([0, 1, 2]) * random.uniform(0.5, 1.5)
    time.sleep(base_speed + extra_pauses)
    
    payload = {
        "content": text,
        "nonce": str(int(time.time() * 1000) << 22), # Mimics Snowflake-style nonce
        "tts": False,
        "flags": 0
    }
    
    try:
        r = session.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", 
                         headers=HEADERS, json=payload, timeout=15)
        return r.status_code in (200, 201)
    except: return False

def accept_request(channel_id):
    """Safely accepts a message request before replying"""
    url = f"https://discord.com/api/v10/channels/{channel_id}/message-requests/accept"
    try:
        session.put(url, headers=HEADERS, timeout=10)
        time.sleep(random.uniform(1.5, 3.0))
    except: pass

# --- THE MAIN LOOP ---

def run_dm_responder():
    print(f"👻 Ghost Stealth Engaged | Build: {BUILD_NUMBER}")
    
    while True:
        # 1. Randomize Downtime (Human Breaks)
        if random.random() < 0.1: # 10% chance to take a long break
            long_break = random.randint(600, 1800)
            print(f"☕ Taking a {long_break//60}m break...")
            time.sleep(long_break)

        try:
            # 2. Fetch DMs with variety
            # We fetch 'relationships' or 'library' sometimes to look like a real app loading
            session.get("https://discord.com/api/v10/users/@me/relationships", headers=HEADERS)
            time.sleep(random.uniform(1, 3))

            r = session.get("https://discord.com/api/v10/users/@me/channels", headers=HEADERS)
            if r.status_code == 200:
                channels = [c for c in r.json() if c['type'] == 1]
                random.shuffle(channels)
                
                for chan in channels[:2]: # Only check 2 at a time to be safe
                    # Your process_channel logic here, but use send_stealth_dm
                    time.sleep(random.uniform(10, 30)) # Wait between people

        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(random.randint(180, 600)) # 3-10 minute cycle
