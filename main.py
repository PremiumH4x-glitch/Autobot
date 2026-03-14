import requests
import os
import time

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

# Message to send
MESSAGE = """# [ ❄️ ] Freeze Trade Script
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

def send_message(channel_id, message_text, image_path=None):
    """Send message to channel"""
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
            success, msg = send_message(channel_id, MESSAGE, IMAGE_PATH)
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
