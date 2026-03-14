import requests
import os
import time
import re
import json

# Direct token
TOKEN = "NzY0ODQxMzU4MTk5NjE5NTk1.G3Mx2w.ESWYFZss2oj9beQZxYW_xpL4hUOaKTwjkuuuJ4"

# Channel IDs to send to
CHANNEL_IDS = [
    1406319942701158531,
    1431010689635586128,
    1431010690835156992,
    1435876872775929916,
    1478627273363034215
]

# Original message to send
ORIGINAL_MESSAGE = """# [ ❄️ ] Freeze Trade Script
——————————————————
**📥 Status: Free / Available**
🚀 Version: Latest Update
# DM me to get the script for free! 💬"""

# Image path
IMAGE_PATH = "freeze_trade_image.jpg"

# Headers with user token
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI2MjI1NiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
}

# Cyrillic lookalike map — visually identical to Latin but different Unicode
CYRILLIC_MAP = {
    'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с',
    'x': 'х', 'y': 'у', 'i': 'і', 'A': 'А', 'B': 'В',
    'C': 'С', 'E': 'Е', 'H': 'Н', 'K': 'К', 'M': 'М',
    'O': 'О', 'P': 'Р', 'T': 'Т', 'X': 'Х', 'Y': 'У',
}

def extract_blocked_words(error_message):
    """Extract blocked words from Discord's error message"""
    blocked = []
    match = re.findall(r'"([^"]+)"', error_message)
    if match:
        raw = match[0]
        words = re.split(r'\s+and\s+this\s+word|\s+are\s+not\s+allowed', raw)
        for w in words:
            w = w.strip().strip('"').strip('.')
            if w and len(w) > 2:
                blocked.append(w)
    return blocked

def cyrillic_bypass(word):
    """Replace Latin chars with Cyrillic lookalikes — visually identical, bypasses filters"""
    result = []
    for ch in word:
        result.append(CYRILLIC_MAP.get(ch, ch))
    return ''.join(result)

def smart_sanitize(message, blocked_words):
    """Replace each blocked word using Cyrillic lookalikes"""
    sanitized = message
    for word in blocked_words:
        bypassed = cyrillic_bypass(word)
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        sanitized = pattern.sub(bypassed, sanitized)
    return sanitized

def full_cyrillic_sanitize(message):
    """Apply Cyrillic substitution to ALL words in the message (last resort)"""
    result = []
    for ch in message:
        result.append(CYRILLIC_MAP.get(ch, ch))
    return ''.join(result)

def get_channel_info(channel_id):
    """Get channel info including slowmode"""
    try:
        response = requests.get(
            f"https://discord.com/api/v10/channels/{channel_id}",
            headers={k: v for k, v in HEADERS.items() if k != "Content-Type"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "slowmode": data.get('rate_limit_per_user', 0),
                "name": data.get('name', str(channel_id)),
                "type": data.get('type', 0),
                "guild_id": data.get('guild_id', None)
            }
        else:
            print(f"   ⚠️ Could not fetch channel info: {response.status_code} {response.text}")
            return {"slowmode": 0, "name": str(channel_id), "type": 0, "guild_id": None}
    except Exception as e:
        print(f"   ⚠️ Error fetching channel info: {e}")
        return {"slowmode": 0, "name": str(channel_id), "type": 0, "guild_id": None}

def do_request(url, send_headers, message_text, image_path):
    """Perform the actual HTTP request"""
    if image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            files = {'file': ('image.jpg', f, 'image/jpeg')}
            data = {'content': message_text}
            return requests.post(url, headers=send_headers, files=files, data=data, timeout=30)
    else:
        return requests.post(url, headers=send_headers, json={"content": message_text}, timeout=15)

def send_message(channel_id, channel_name, original_text, image_path=None):
    """Send a message with full auto-detection and error fixing"""
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    send_headers = {k: v for k, v in HEADERS.items() if k != "Content-Type"}

    # Build list of variants to try in order
    variants = [
        (original_text, image_path, "Original"),
        (full_cyrillic_sanitize(original_text), image_path, "Full Cyrillic"),
        (full_cyrillic_sanitize(original_text), None, "Full Cyrillic, no image"),
        (original_text, None, "No image"),
    ]

    for msg_text, img, label in variants:
        rate_limit_retries = 0
        while True:
            try:
                resp = do_request(url, send_headers, msg_text, img)
                code = resp.status_code

                # SUCCESS
                if code in (200, 201):
                    if label != "Original":
                        print(f"   ✅ Sent with variant: {label}")
                    return True, "Sent"

                # RATE LIMITED — retry same variant
                elif code == 429:
                    info = resp.json()
                    wait = info.get('retry_after', 2) + 0.5
                    rate_limit_retries += 1
                    if rate_limit_retries <= 5:
                        print(f"   ⏱️ Rate limited — waiting {wait:.1f}s (retry {rate_limit_retries})...")
                        time.sleep(wait)
                        continue  # retry same variant
                    else:
                        print(f"   ⚠️ Too many rate limits on [{label}], trying next variant...")
                        break  # move to next variant

                # CONTENT FILTER
                elif code == 400:
                    info = resp.json()
                    msg = info.get('message', '')
                    err_code = info.get('code', 0)
                    if 'blocked by this server' in msg.lower() or err_code == 200000:
                        blocked_words = extract_blocked_words(msg)
                        print(f"   🚫 [{label}] Filter blocked: {blocked_words or msg[:60]}")
                        break  # try next variant
                    elif err_code == 50035:
                        return False, f"Invalid message format: {msg}"
                    else:
                        return False, f"400 Error: {msg}"

                # NO ACCESS
                elif code == 403:
                    info = resp.json()
                    err_code = info.get('code', 0)
                    if err_code == 50013:
                        return False, "Missing Permissions (no Send Messages perm in this channel)"
                    elif err_code == 50001:
                        return False, "Missing Access (not in server or channel is restricted)"
                    else:
                        return False, f"Forbidden: {info.get('message', '')}"

                # NOT FOUND
                elif code == 404:
                    return False, "Channel not found (invalid ID or deleted)"

                else:
                    print(f"   ⚠️ [{label}] Unexpected {code}: {resp.text[:100]}")
                    break  # try next variant

            except requests.exceptions.Timeout:
                rate_limit_retries += 1
                if rate_limit_retries <= 3:
                    print(f"   ⏱️ Timeout, retrying [{label}]...")
                    time.sleep(3)
                    continue
                break
            except Exception as e:
                return False, f"Exception: {str(e)}"

        time.sleep(1.5)  # brief pause before trying next variant

    return False, "All send variants failed (blocked by filters or other errors)"

def main():
    print("=" * 50)
    print("  Discord Self-Bot — Starting")
    print("=" * 50)
    print(f"  Channels to send to: {len(CHANNEL_IDS)}")
    print(f"  Image: {'YES' if os.path.exists(IMAGE_PATH) else 'NOT FOUND'}\n")

    results = []

    for channel_id in CHANNEL_IDS:
        print(f"\n📡 Processing channel: {channel_id}")
        info = get_channel_info(channel_id)
        name = info['name']
        slowmode = info['slowmode']

        print(f"   Name: #{name}")

        if slowmode > 0:
            print(f"   ⏳ Slowmode: {slowmode}s — waiting...")
            time.sleep(slowmode)

        success, result_msg = send_message(channel_id, name, ORIGINAL_MESSAGE, IMAGE_PATH)

        if success:
            print(f"   ✅ Sent successfully to #{name}")
            results.append((channel_id, name, "✅ Success"))
        else:
            print(f"   ❌ Failed: {result_msg}")
            results.append((channel_id, name, f"❌ {result_msg}"))

        time.sleep(1.5)

    print("\n" + "=" * 50)
    print("  FINAL RESULTS")
    print("=" * 50)
    for cid, name, status in results:
        print(f"  {status} — #{name} ({cid})")
    print("=" * 50)

if __name__ == '__main__':
    main()
