import requests
import time
import os
import re

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

# Word-level yes/no keywords — matched as whole words to avoid false positives
YES_WORDS = [
    "yes", "yeah", "yep", "yup", "ok", "okay", "sure", "ye", "yea",
    "ofc", "mhm", "yessir", "yup", "fasho", "fs", "bet", "ight",
    "aight", "alright"
]

YES_PHRASES = [
    "i have", "i got", "got it", "have it", "i do", "already have",
    "have delta", "got delta", "use delta", "i use", "have executor",
    "got executor", "of course", "definitely", "absolutely",
    "i know", "ik", "correct"
]

NO_WORDS = [
    "no", "nope", "nah", "nah", "idk", "huh", "nvm"
]

NO_PHRASES = [
    "don't have", "dont have", "i don't", "i dont", "haven't", "havent",
    "what is", "what's", "whats", "what is delta", "no idea",
    "never heard", "not really", "not sure", "no clue",
    "first time", "never used", "don't know", "dont know",
    "do not have", "do not know", "what that", "what dat",
    "i don't know", "i dont know", "never", "beginner", "new to this"
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


def get_message_requests():
    """Fetch pending DM message requests (non-friend DMs waiting to be accepted)"""
    try:
        r = requests.get(
            "https://discord.com/api/v10/users/@me/message-requests",
            headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            channels = data if isinstance(data, list) else data.get("channels", [])
            return [c for c in channels if c.get("type") == 1]
        elif r.status_code == 404:
            # Try alternate endpoint
            r2 = requests.get(
                "https://discord.com/api/v9/users/@me/message-requests",
                headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
                timeout=10
            )
            if r2.status_code == 200:
                data = r2.json()
                channels = data if isinstance(data, list) else data.get("channels", [])
                return [c for c in channels if c.get("type") == 1]
    except Exception as e:
        print(f"[DM] Error fetching message requests: {e}")
    return []


def accept_message_request(channel_id):
    """Accept a pending message request so we can reply"""
    try:
        r = requests.put(
            f"https://discord.com/api/v10/channels/{channel_id}/message-requests/accept",
            headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
            timeout=10
        )
        if r.status_code in (200, 201, 204):
            print(f"[DM] Accepted message request for channel {channel_id}")
            return True
        else:
            # Try alternate method — just sending a message implicitly accepts the request
            print(f"[DM] Accept endpoint returned {r.status_code}, will try sending directly")
            return True
    except Exception as e:
        print(f"[DM] Error accepting message request: {e}")
    return False


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
            print(f"[DM] Failed to send: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"[DM] Error sending message: {e}")
    return None


def detect_intent(text):
    """
    Determine if the user is saying yes (has executor) or no (doesn't have it).
    Uses word-boundary matching to avoid false positives like 'shady' matching 'y'.
    """
    t = text.lower().strip()

    # Remove mentions like <@123456> and punctuation noise
    t = re.sub(r"<@!?[0-9]+>", "", t).strip()

    # Check multi-word phrases first (more specific)
    for phrase in NO_PHRASES:
        if phrase in t:
            return "no"

    for phrase in YES_PHRASES:
        if phrase in t:
            return "yes"

    # Check single words using word boundaries so 'y' won't match 'shady'
    for word in NO_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', t):
            return "no"

    for word in YES_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', t):
            return "yes"

    # If message is only a mention or empty after cleanup, skip
    if not t or t in ["", "???"]:
        return None

    # If it's a question mark or contains "what/how/?" it's likely asking = no
    if "?" in t or t.startswith("what") or t.startswith("how") or t.startswith("who"):
        return "no"

    return None


def process_dm_channel(channel_id, channel, is_request=False):
    uid = get_my_user_id()
    if not uid:
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

        print(f"[DM] Channel {channel_id} | State: {state} | Msg: {content[:60]}")

        if state == "new":
            if is_request:
                accept_message_request(channel_id)
                time.sleep(0.5)
            print(f"[DM] Starting convo in channel {channel_id}")
            send_dm(channel_id, INTRO_MESSAGE_1)
            time.sleep(1)
            send_dm(channel_id, INTRO_MESSAGE_2)
            conversation_states[channel_id] = "waiting_for_answer"

        elif state == "waiting_for_answer":
            intent = detect_intent(content)
            if intent == "yes":
                send_dm(channel_id, RESPONSE_HAS_EXECUTOR)
                conversation_states[channel_id] = "done"
                print(f"[DM] -> Has executor, told them to wait")
            elif intent == "no":
                send_dm(channel_id, RESPONSE_NO_EXECUTOR)
                conversation_states[channel_id] = "done"
                print(f"[DM] -> No executor, sent download links")
            else:
                print(f"[DM] -> Can't determine intent, waiting for clearer reply")


def initialize_seen_messages():
    print("[DM] Initializing — reading DM history to skip old messages...")
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
        time.sleep(0.4)
    print(f"[DM] Initialized {len(dm_channels)} existing DM channels")


def run_dm_responder():
    print("[DM] Auto-responder starting...")
    get_my_user_id()
    initialize_seen_messages()
    print("[DM] Watching for new DMs and message requests...\n")

    while True:
        try:
            # Process regular DMs
            dm_channels = get_dm_channels()
            for channel in dm_channels:
                channel_id = channel["id"]
                process_dm_channel(channel_id, channel, is_request=False)
                time.sleep(0.3)

            # Process pending message requests (DMs from non-friends)
            requests_list = get_message_requests()
            for channel in requests_list:
                channel_id = channel["id"]
                if channel_id not in dm_channel_last_seen:
                    print(f"[DM] New message request from channel {channel_id}")
                process_dm_channel(channel_id, channel, is_request=True)
                time.sleep(0.3)

        except Exception as e:
            print(f"[DM] Unexpected error: {e}")

        time.sleep(5)
