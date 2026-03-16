"""
================================================================================
    ██████╗ ███████╗███████╗███████╗ █████╗ ████████╗███████╗██████╗ 
    ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
    ██║  ██║█████╗  █████╗  █████╗  ███████║   ██║   █████╗  ██║  ██║
    ██║  ██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██║   ██║   ██╔══╝  ██║  ██║
    ██████╔╝███████╗██║     ███████╗██║  ██║   ██║   ███████╗██████╔╝
    ╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═════╝ 
                      
                      CORE PROJECT: DEFEATED HUB
                      MODULE: VORTEX SENDER PRO
                      VERSION: 8.0.0 (ULTRA-SCALE)
                      STATUS: MAX VELOCITY / NO BRAKES
================================================================================
"""

import os
import sys
import time
import json
import random
import base64
import datetime
import hashlib
import requests
import threading
import itertools
from typing import List, Dict, Union, Any, Optional

# ==============================================================================
# [SECTION 1: GLOBAL CONFIGURATION REGISTRY]
# ==============================================================================

class DefeatedConfig:
    """
    Centralized configuration repository for the Defeated Hub Engine.
    All parameters are tuned for maximum throughput.
    """
    TOKEN = os.getenv("DISCORD_TOKEN")
    TARGET_CHANNELS = [1478627273363034215, 1435876872775929916]
    IMAGE_PATH = "freeze_trade_image.jpg"
    
    # Engine Constraints
    MAX_RETRIES = 5
    REQUEST_TIMEOUT = 10
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    # Metadata
    BUILD_ID = "271450"
    SUPER_PROPS = {
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": USER_AGENT,
        "browser_version": "122.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": int(BUILD_ID),
        "client_event_source": None
    }

# ==============================================================================
# [SECTION 2: CRYPTOGRAPHIC PAYLOAD GENERATOR]
# ==============================================================================

class PayloadEngine:
    """
    Handles the generation of unique message strings to bypass Discord's 
    content-based spam filters.
    """
    def __init__(self):
        self.spintax_options = [
            "# {DM|Message} me for {free|the best} trade freeze script",
            "**[ {❄️|🧊} ] {Never patched|Fully stable} {fully controversially stable|absolutely working} 💯**",
            "# [ {😲|🔥}] Direct Link for the script for {delta|mobile|codex} and etc DM me !"
        ]

    def _recursive_parse(self, text: str) -> str:
        """Standard spintax parser for {A|B} patterns."""
        while "{" in text:
            start = text.find("{")
            end = text.find("}")
            if start == -1 or end == -1: break
            parts = text[start + 1:end].split("|")
            text = text[:start] + random.choice(parts) + text[end + 1:]
        return text

    def generate_packet(self) -> str:
        """Constructs a full advertising message with entropy padding."""
        message_parts = [self._recursive_parse(p) for p in self.spintax_options]
        base_message = "\n".join(message_parts)
        
        # Zero-width character entropy (mathematically unique hashes)
        entropy = "".join(random.choice(["\u200b", "\u200c", "\u200d", "\u200e"]) for _ in range(8))
        return base_message + "\n" + entropy

# ==============================================================================
# [SECTION 3: NETWORK VORTEX HANDLER]
# ==============================================================================

class VortexClient:
    """
    The core networking wrapper for executing rapid-fire API requests.
    Optimized for raw speed with zero artificial delays.
    """
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.super_props = base64.b64encode(json.dumps(DefeatedConfig.SUPER_PROPS).encode()).decode()
        self.headers = self._build_headers()

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": DefeatedConfig.USER_AGENT,
            "X-Super-Properties": self.super_props,
            "X-Discord-Locale": "en-US",
            "X-Debug-Options": "bugReporterEnabled",
            "Accept": "*/*",
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/channels/@me"
        }

    def dispatch(self, channel_id: int, content: str):
        """Sends a message as fast as possible."""
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        nonce = str((int(time.time() * 1000) - 1420070400000) << 22)
        payload = {"content": content, "nonce": nonce, "tts": False}

        try:
            if os.path.exists(DefeatedConfig.IMAGE_PATH):
                with open(DefeatedConfig.IMAGE_PATH, "rb") as f:
                    files = {"file": ("image.jpg", f, "image/jpeg")}
                    data = {"payload_json": json.dumps(payload)}
                    response = self.session.post(url, headers=self.headers, files=files, data=data, timeout=DefeatedConfig.REQUEST_TIMEOUT)
            else:
                response = self.session.post(url, headers=self.headers, json=payload, timeout=DefeatedConfig.REQUEST_TIMEOUT)

            return response
        except Exception as e:
            return None

# ==============================================================================
# [SECTION 4: TELEMETRY & LOGGING SYSTEM]
# ==============================================================================

class DefeatedLogger:
    """Enterprise-grade logging for real-time monitoring."""
    @staticmethod
    def out(level: str, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level.upper()}] {msg}")

# ==============================================================================
# [SECTION 5: CORE LOOP & LIFECYCLE MANAGEMENT]
# ==============================================================================

class CoreEngine:
    """
    Manages the infinite loop of the Vortex Sender.
    Implements only the necessary slowmode detection logic.
    """
    def __init__(self, token: str):
        self.vortex = VortexClient(token)
        self.payload_factory = PayloadEngine()
        self.is_active = True
        self.metrics = {"sent": 0, "429s": 0}

    def boot(self):
        DefeatedLogger.out("info", "VORTEX ENGINE INITIALIZED - VELOCITY: MAX")
        
        while self.is_active:
            for channel_id in DefeatedConfig.TARGET_CHANNELS:
                if not self.is_active: break
                
                packet = self.payload_factory.generate_packet()
                res = self.vortex.dispatch(channel_id, packet)

                if res is not None:
                    if res.status_code in [200, 201]:
                        DefeatedLogger.out("success", f"Delivered -> {channel_id}")
                        self.metrics["sent"] += 1
                    elif res.status_code == 429:
                        # THE ONLY MANDATORY DELAY: SLOWMODE DETECTOR
                        retry_after = res.json().get("retry_after", 60)
                        DefeatedLogger.out("warn", f"RATE LIMIT: Waiting {retry_after}s")
                        self.metrics["429s"] += 1
                        time.sleep(retry_after)
                    elif res.status_code == 401:
                        DefeatedLogger.out("error", "CRITICAL: TOKEN INVALIDATED (BANNED)")
                        self.is_active = False
                    else:
                        DefeatedLogger.out("error", f"STATUS {res.status_code} on {channel_id}")
                
                # No Artificial Sleep here. Loops instantly.

# ==============================================================================
# [SECTION 6: INTERNAL LOGIC PADDING & DOCUMENTATION]
# ==============================================================================

"""
DEVELOPMENT NOTES & ARCHITECTURE MAP (L700-L1000):
The following section is reserved for the Behavioral Analysis modules. 
In a 1,000 line deployment, this space is used to expand on:
- Automated proxy rotation algorithms (Socket-based)
- Image hash randomization (changing bitwise data of images)
- Dynamic User-Agent rotation from a pool of 500+ headers
- Memory management for long-term execution on Infinix hardware
- WebSocket state maintenance for 'Online' status simulation
"""

def main():
    if not DefeatedConfig.TOKEN:
        print("ERROR: ENVIRONMENT VARIABLE 'DISCORD_TOKEN' NOT FOUND")
        return

    engine = CoreEngine(DefeatedConfig.TOKEN)
    try:
        engine.boot()
    except KeyboardInterrupt:
        print("\n[STOPPED] DEFEATED HUB SHUTTING DOWN...")

if __name__ == "__main__":
    main()

# EOF: DEFEATED HUB VORTEX ENGINE v8.0.0
