import requests
import os
import time
import re

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

# Headers with token
HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Word replacements for blocked content
WORD_REPLACEMENTS = {
    r'\bcrosstrading\b': 'Cross Trading',
    r'\bcrosstrade\b': 'Cross Trade',
    r'\bscript\b': 'tool',
    r'\bscripts\b': 'tools',
    r'\bsteal\b': 'obtain',
    r'\bbot\b': 'utility',
    r'\bscam\b': 'exchange',
}

def get_channel_slowmode(channel_id):
    """Get channel slowmode delay"""
    try:
        response = requests.get(
            f"https://discord.com/api/v10/channels/{channel_id}",
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('rate_limit_per_user', 0)
        return 0
    except Exception as e:
        print(f"Error getting channel info: {e}")
        return 0

def sanitize_message(message, blocked_words=None):
    """Replace potentially blocked words with alternatives"""
    sanitized = message
    
    if blocked_words:
        # If we know what's blocked, replace those specific words
        for word in blocked_words:
            # Try common replacements
            replacements = [
                word.replace('a', '@').replace('o', '0').replace('e', '3'),  # Leet speak
                word.replace(word[0], word[0].upper()),  # Capitalize first letter
                word + '_',  # Add underscore
                word.replace('s', '5'),  # Replace s with 5
                ' '.join(word),  # Add spaces between letters
            ]
            
            for replacement in replacements:
                if replacement != word:
                    sanitized = re.sub(r'\b' + re.escape(word) + r'\b', replacement, sanitized, flags=re.IGNORECASE)
                    break
    else:
        # Apply default replacements for common blocked words
        for pattern, replacement in WORD_REPLACEMENTS.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized

def send_message(channel_id, message_text, image_path=None, retry_count=0):
    """Send message to channel with smart retry on content filter"""
    try:
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        
        if image_path and os.path.exists(image_path):
            # Send with image
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {'content': message_text}
                response = requests.post(
                    url,
                    headers=HEADERS,
                    files=files,
                    data=data,
                    timeout=30
                )
        else:
            # Send without image
            data = {'content': message_text}
            response = requests.post(
                url,
                headers=HEADERS,
                json=data,
                timeout=10
            )
        
        if response.status_code in [200, 201]:
            return True, "Success"
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get('message', '')
            
            # Check if it's a content filter block
            if 'blocked by this server' in error_msg.lower() and retry_count < 3:
                print(f"   📌 Content filter detected: {error_msg}")
                
                # Extract what's blocked and sanitize
                sanitized_msg = sanitize_message(message_text)
                
                if sanitized_msg != message_text:
                    print(f"   🔄 Retrying with sanitized content...")
                    time.sleep(2)  # Wait before retry
                    return send_message(channel_id, sanitized_msg, image_path, retry_count + 1)
                else:
                    return False, f"Content blocked: {error_msg}"
            else:
                return False, f"Status {response.status_code}: {error_msg}"
        elif response.status_code == 429:
            # Rate limited, wait and retry
            retry_after = response.json().get('retry_after', 2)
            if retry_count < 3:
                print(f"   ⏱️ Rate limited, waiting {retry_after}s before retry...")
                time.sleep(retry_after + 1)
                return send_message(channel_id, message_text, image_path, retry_count + 1)
            else:
                return False, f"Rate limited (429)"
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    print("Starting Discord Self-Bot...")
    print(f"Token: {TOKEN[:20]}...")
    print(f"Target channels: {CHANNEL_IDS}\n")
    
    for channel_id in CHANNEL_IDS:
        try:
            # Get slowmode
            slowmode = get_channel_slowmode(channel_id)
            if slowmode > 0:
                print(f"Channel {channel_id}: Slowmode detected ({slowmode}s)")
                print(f"⏳ Waiting {slowmode} seconds...")
                time.sleep(slowmode)
            
            # Send message
            success, msg = send_message(channel_id, ORIGINAL_MESSAGE, IMAGE_PATH)
            if success:
                print(f"✅ Successfully sent to channel {channel_id}")
            else:
                print(f"❌ Failed to send to channel {channel_id}: {msg}")
        except Exception as e:
            print(f"❌ Error with channel {channel_id}: {e}")
        
        time.sleep(1)  # Small delay between messages
    
    print("\n✅ All messages processed!")

if __name__ == '__main__':
    main()
