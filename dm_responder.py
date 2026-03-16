import time
import os
import json
import random
import threading
import base64
import requests
import websocket # You must add 'websocket-client' to your bot.yaml

TOKEN = os.getenv("DISCORD_TOKEN")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# --- HUMAN REPLIES DATABASE ---
# Making the script long by adding extensive response variations
REPLIES = {
    "greeting": ["yo", "hey", "sup", "hello?", "hi", "what's up"],
    "interest": [
        "yeah its free bro", 
        "check the link in my bio or i can send it here", 
        "it works on solara and mobile too",
        "best script out right now honestly"
    ],
    "how_to": [
        "just execute it and it works",
        "u need a good executor like delta or codex",
        "make sure u turn off antivirus if ur on pc"
    ],
    "default": ["?", "yo check my latest post in the channel", "dm me later i might be busy"]
}

class GhostClient:
    def __init__(self, token):
        self.token = token
        self.session = requests.Session()
        self.heartbeat_interval = 41250
        self.ws = None
        self.user_id = None
        
    def get_headers(self):
        return {
            "Authorization": self.token,
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "X-Discord-Locale": "en-US",
            "Origin": "https://discord.com"
        }

    # --- THE HUMAN ACTIONS ---

    def send_typing(self, channel_id):
        """Mimics the 'is typing...' indicator"""
        url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
        try:
            self.session.post(url, headers=self.get_headers(), timeout=5)
        except: pass

    def ack_message(self, channel_id, message_id):
        """Clears the unread notification dot"""
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}/ack"
        try:
            self.session.post(url, headers=self.get_headers(), json={"token": None}, timeout=5)
        except: pass

    def reply(self, channel_id, message_id, content):
        """Sends the actual message with human-like delays"""
        # 1. Wait for 'reaction time' (reading the message)
        time.sleep(random.uniform(2.5, 5.0))
        
        # 2. Start typing
        self.send_typing(channel_id)
        
        # 3. Typing speed simulation (0.07s per character)
        typing_duration = len(content) * random.uniform(0.05, 0.1)
        time.sleep(min(typing_duration, 8.0)) # Don't type for more than 8s
        
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        nonce = str((int(time.time() * 1000) - 1420070400000) << 22)
        
        data = {
            "content": content,
            "nonce": nonce,
            "tts": False,
            "message_reference": {"message_id": message_id} # Replies directly to them
        }
        
        try:
            self.session.post(url, headers=self.get_headers(), json=data, timeout=10)
            print(f"💬 Replied to DM in {channel_id}")
        except: pass

    # --- GATEWAY / WEBSOCKET LOGIC ---

    def heartbeat(self):
        """Keeping the connection alive (Critical for not being flagged)"""
        while True:
            time.sleep(self.heartbeat_interval / 1000)
            if self.ws and self.ws.connected:
                self.ws.send(json.dumps({"op": 1, "d": None}))

    def on_message(self, ws, message):
        data = json.loads(message)
        op = data.get("op")
        t = data.get("t")

        if op == 10: # Hello
            self.heartbeat_interval = data["d"]["heartbeat_interval"]
            # Identify (Log in)
            auth_payload = {
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": {"os": "Windows", "browser": "Chrome", "device": ""},
                    "presence": {"status": "online", "afk": False}
                }
            }
            ws.send(json.dumps(auth_payload))

        if t == "MESSAGE_CREATE":
            msg = data["d"]
            # Only reply if it's a DM (Type 1) and NOT from yourself
            if msg["author"]["id"] != self.user_id:
                channel_id = msg["channel_id"]
                content = msg["content"].lower()
                
                # Check if it's a DM (Optional check depending on your setup)
                self.ack_message(channel_id, msg["id"])
                
                # Simple logic: If they ask about the script
                response_text = random.choice(REPLIES["default"])
                if any(word in content for word in ["how", "use", "work"]):
                    response_text = random.choice(REPLIES["how_to"])
                elif any(word in content for word in ["free", "script", "link"]):
                    response_text = random.choice(REPLIES["interest"])
                
                # Run reply in a thread so it doesn't block the WebSocket
                threading.Thread(target=self.reply, args=(channel_id, msg["id"], response_text)).start()

    def run(self):
        # Get own ID first
        me = self.session.get("https://discord.com/api/v10/users/@me", headers=self.get_headers()).json()
        self.user_id = me.get("id")
        
        print(f"👻 Logged in as {me.get('username')} | Gateway connecting...")
        
        self.ws = websocket.WebSocketApp(
            "wss://gateway.discord.gg/?v=10&encoding=json",
            on_message=self.on_message
        )
        
        threading.Thread(target=self.heartbeat, daemon=True).start()
        self.ws.run_forever()

def run_dm_responder():
    client = GhostClient(TOKEN)
    while True:
        try:
            client.run()
        except Exception as e:
            print(f"WebSocket Error: {e}. Restarting...")
            time.sleep(10)
