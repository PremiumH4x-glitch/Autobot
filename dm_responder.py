import requests
import time
import os
import json

TOKEN = os.getenv("DISCORD_TOKEN")

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI2MjI1NiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
}

INTRO_MESSAGE_1 = "Hello, before we start I have some questions do u have an executor like delta?"
INTRO_MESSAGE_2 = "this is an automated response so just wait for me to get online and answer ok?"

RESPONSE_HAS_EXECUTOR = "okay wait for me to get online I'm doing something"

RESPONSE_NO_EXECUTOR = """Download the delta executor for Android or iOS:

**Android:** https://deltaexploits.gg/delta-executor-android
**iOS:** https://deltaexploits.gg/delta-executor-ios"""

YES_KEYWORDS = [
    "yes", "yeah", "yep", "yup", "ok", "okay", "sure", "ye", "y",
    "i have", "i got", "got it", "have it", "i do", "already have",
    "have delta", "got delta", "use delta", "i use", "have executor",
    "got executor", "yea", "ofc", "of course", "definitely", "absolutely",
    "mhm", "ik", "i know", "correct", "right", "true"
]

NO_KEYWORDS = [
    "no", "nope", "nah", "n", "dont", "don't", "do not", "not have",
    "don't have", "dont have", "i don't", "i dont", "haven't", "havent",
    "what is", "what's", "whats", "what", "idk", "i don't know",
    "i dont know", "no idea", "never heard", "never", "not really",
    "not sure", "unsure", "huh", "?", "what that", "what dat",
    "never used", "don't know", "dont know", "no clue", "clueless",
    "first time", "new", "beginner", "how", "explain", "tell me"
]

conversation_states = {}
my_user_id = None
dm_channel_last_seen = {}


def get_my_user_id():
    global my_user_id
    if my_user_id:
        return my_user_id
    try:
        r = requests.get(
            "https://discord.com/api/v10/users/@me",
            headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
            timeout=10
        )
        if r.status_code == 200:
            my_user_id = r.json()["id"]
            return my_user_id
    except Exception as e:
        print(f"[DM] Error fetching user ID: {e}")
    return None


def get_dm_channels():
    try:
        r = requests.get(
            "https://discord.com/api/v10/users/@me/channels",
            headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
            timeout=10
        )
        if r.status_code == 200:
            channels = r.json()
            return [c for c in channels if c.get("type") == 1]
    except Exception as e:
        print(f"[DM] Error fetching DM channels: {e}")
    return []


def get_recent_messages(channel_id, after_id=None):
    params = {"limit": 10}
    if after_id:
        params["after"] = after_id
    try:
        r = requests.get(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
            params=params,
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            wait = r.json().get("retry_after", 2)
            time.sleep(wait)
    except Exception as e:
        print(f"[DM] Error fetching messages: {e}")
    return []


def send_dm(channel_id, text):
    try:
        r = requests.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
            json={"content": text},
            timeout=15
        )
        if r.status_code in (200, 201):
            return r.json().get("id")
        elif r.status_code == 429:
            wait = r.json().get("retry_after", 2)
            time.sleep(wait)
            return send_dm(channel_id, text)
        else:
            print(f"[DM] Failed to send message: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"[DM] Error sending message: {e}")
    return None


def detect_intent(text):
    text_lower = text.lower().strip()

    no_score = sum(1 for kw in NO_KEYWORDS if kw in text_lower)
    yes_score = sum(1 for kw in YES_KEYWORDS if kw in text_lower)

    if no_score == 0 and yes_score == 0:
        if any(c in text_lower for c in ["?", "what"]):
            return "no"
        return None

    if no_score > yes_score:
        return "no"
    elif yes_score > no_score:
        return "yes"
    else:
        if any(kw in text_lower for kw in ["what", "idk", "?", "huh"]):
            return "no"
        return "yes"


def process_dm_channel(channel_id, channel):
    uid = get_my_user_id()
    if not uid:
        return

    recipients = channel.get("recipients", [])
    if not recipients:
        return

    last_seen = dm_channel_last_seen.get(channel_id)
    messages = get_recent_messages(channel_id, after_id=last_seen)

    if not messages:
        return

    messages = sorted(messages, key=lambda m: m["id"])

    for msg in messages:
        msg_id = msg["id"]
        author_id = msg["author"]["id"]
        content = msg.get("content", "").strip()

        dm_channel_last_seen[channel_id] = msg_id

        if author_id == uid:
            continue

        if not content:
            continue

        state = conversation_states.get(channel_id, "new")

        print(f"[DM] Channel {channel_id} | State: {state} | Message: {content[:60]}")

        if state == "new":
            print(f"[DM] New conversation started in channel {channel_id}")
            send_dm(channel_id, INTRO_MESSAGE_1)
            time.sleep(1)
            send_dm(channel_id, INTRO_MESSAGE_2)
            conversation_states[channel_id] = "waiting_for_answer"

        elif state == "waiting_for_answer":
            intent = detect_intent(content)
            if intent == "yes":
                send_dm(channel_id, RESPONSE_HAS_EXECUTOR)
                conversation_states[channel_id] = "done"
                print(f"[DM] Replied: has executor")
            elif intent == "no":
                send_dm(channel_id, RESPONSE_NO_EXECUTOR)
                conversation_states[channel_id] = "done"
                print(f"[DM] Replied: sent download links")
            else:
                print(f"[DM] Could not determine intent from: {content[:60]}")


def initialize_seen_messages():
    print("[DM] Initializing — reading current DM history to avoid responding to old messages...")
    dm_channels = get_dm_channels()
    for channel in dm_channels:
        channel_id = channel["id"]
        messages = get_recent_messages(channel_id)
        if messages:
            messages = sorted(messages, key=lambda m: m["id"])
            dm_channel_last_seen[channel_id] = messages[-1]["id"]
            uid = get_my_user_id()
            for msg in reversed(messages):
                if msg["author"]["id"] != uid:
                    conversation_states[channel_id] = "waiting_for_answer"
                    break
        time.sleep(0.5)
    print(f"[DM] Initialized {len(dm_channels)} DM channels")


def run_dm_responder():
    print("[DM] Auto-responder starting...")
    get_my_user_id()
    initialize_seen_messages()
    print("[DM] Watching for new DMs...\n")

    while True:
        try:
            dm_channels = get_dm_channels()
            for channel in dm_channels:
                channel_id = channel["id"]
                process_dm_channel(channel_id, channel)
                time.sleep(0.3)
        except Exception as e:
            print(f"[DM] Unexpected error: {e}")

        time.sleep(5)
