import requests
import time
import os
import re
import random

# --- CONFIGURATION ---
TOKEN = os.getenv("DISCORD_TOKEN")

# Modern Chrome Headers
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://discord.com/channels/@me",
}

# AI-Style Message Variations
AI_RESPONSES = {
    "intro": [
        "yo, u got an executor like delta fixed up yet?",
        "hey! before we get into it, u using delta or what?",
        "sup, quick question do u have delta or any other executor?",
        "yo! u already have an executor (delta etc) installed?"
    ],
    "waiting": [
        "im a bit busy rn but ill be back in a sec, lmk",
        "just wait for me to get back online and ill help u out",
        "im away from my phone atm but just drop a reply",
        "hang tight i got u, just doing something real quick"
    ],
    "has_executor": [
        "alright bet, just wait for me to get back and ill send the rest",
        "sweet, stay there i'll be online in a few mins",
        "perfect. ill be back soon to finish this up"
    ],
    "no_executor": [
        "ah u need delta then, its the best for mobile. here:",
        "u gotta get delta first. here r the links for android/ios:",
        "grab delta from here and then we can start:"
    ]
}

# State tracking
conversation_states = {}
dm_channel_last_seen = {}
my_user_id = None

# --- UTILITIES ---

def get_my_user_id():
    global my_user_id
    if my_user_id: return my_user_id
    try:
        r = requests.get("https://discord.com/api/v10/users/@me", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            my_user_id = r.json()["id"]
            return my_user_id
    except: pass
    return None

def send_typing(channel_id):
    url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    try: requests.post(url, headers={"Authorization": TOKEN}, timeout=5)
    except: pass

def human_delay(min_s, max_s):
    time.sleep(random.uniform(min_s, max_s))

def detect_intent(text):
    t = text.lower()
    yes_patterns = [r'\byes\b', r'\byeah\b', r'\bhave it\b', r'\bok\b', r'\bi do\b', r'\byep\b']
    no_patterns = [r'\bno\b', r'\bnope\b', r'\bdont\b', r'\bwhat\b', r'\bhow\b', r'\bnah\b']
    
    for p in no_patterns:
        if re.search(p, t): return "no"
    for p in yes_patterns:
        if re.search(p, t): return "yes"
    return None

def get_recent_messages(channel_id, after_id=None):
    params = {"limit": 5}
    if after_id: params["after"] = after_id
    try:
        r = requests.get(f"https://discord.com/api/v10/channels/{channel_id}/messages", headers=HEADERS, params=params, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def send_dm(channel_id, text, type_speed=(2, 5)):
    send_typing(channel_id)
    human_delay(type_speed[0], type_speed[1])
    try:
        requests.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", headers=HEADERS, json={"content": text}, timeout=15)
    except: pass

# --- CORE LOGIC ---

def process_channel(channel_id):
    uid = get_my_user_id()
    last_id = dm_channel_last_seen.get(channel_id)
    messages = get_recent_messages(channel_id, after_id=last_id)
    
    if not messages: return
    
    # Update last seen
    latest_msg = sorted(messages, key=lambda x: x['id'])[-1]
    dm_channel_last_seen[channel_id] = latest_msg['id']
    
    if latest_msg['author']['id'] == uid: return
    
    content = latest_msg.get('content', '')
    state = conversation_states.get(channel_id, "new")

    if state == "new":
        send_dm(channel_id, random.choice(AI_RESPONSES["intro"]))
        human_delay(1, 3)
        send_dm(channel_id, random.choice(AI_RESPONSES["waiting"]), (1, 3))
        conversation_states[channel_id] = "waiting_for_answer"
    
    elif state == "waiting_for_answer":
        intent = detect_intent(content)
        if intent == "yes":
            send_dm(channel_id, random.choice(AI_RESPONSES["has_executor"]))
            conversation_states[channel_id] = "done"
        elif intent == "no":
            send_dm(channel_id, random.choice(AI_RESPONSES["no_executor"]))
            human_delay(1, 2)
            links = "**Android:** https://deltaexploits.gg/delta-executor-android\n**iOS:** https://deltaexploits.gg/delta-executor-ios"
            send_dm(channel_id, links, (1, 2))
            conversation_states[channel_id] = "done"

# --- THE FUNCTION MAIN.PY CALLS ---

def run_dm_responder():
    print("🤖 AI DM Responder Active")
    my_id = get_my_user_id()
    
    while True:
        try:
            # Get DM list
            r = requests.get("https://discord.com/api/v10/users/@me/channels", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                channels = [c for c in r.json() if c['type'] == 1]
                for chan in channels:
                    process_channel(chan['id'])
                    human_delay(1, 2) # Delay between checking different people
            
            # Check Message Requests
            req = requests.get("https://discord.com/api/v10/users/@me/message-requests", headers=HEADERS, timeout=10)
            if req.status_code == 200:
                for r_chan in req.json():
                    process_channel(r_chan['id'])
                    
        except Exception as e:
            print(f"[DM Error] {e}")
            
        # Wait a random time before checking all DMs again
        time.sleep(random.randint(15, 45))
