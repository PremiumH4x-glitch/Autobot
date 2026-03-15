import requests
import time
import os
import re
import random

TOKEN = os.getenv("DISCORD_TOKEN")

# Modernized Headers to match current Chrome standards
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://discord.com/channels/@me",
}

# --- THE AI BRAIN ---
def get_ai_response(user_input, state):
    """
    This mimics an AI's variety. 
    To make it 'True AI', you would call an API like OpenAI or Gemini here.
    """
    responses = {
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
            "perfect. ill be back soon to finish this up",
            "ight cool, i'll dm u properly when im back"
        ],
        "no_executor": [
            "ah u need delta then, its the best for mobile. here:",
            "u gotta get delta first. here r the links for android/ios:",
            "grab delta from here and then we can start:",
            "it wont work without an executor, get delta here:"
        ]
    }
    return random.choice(responses.get(state, ["ight"]))

# --- THE SENSORY FUNCTIONS ---

def send_typing(channel_id):
    """VITAL: Sends 'is typing...' signal"""
    url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    try:
        requests.post(url, headers={"Authorization": TOKEN}, timeout=5)
    except:
        pass

def human_delay(min_s, max_s):
    time.sleep(random.uniform(min_s, max_s))

def send_dm(channel_id, text, typing_time=(2, 5)):
    """Simulates a human reading and typing a message"""
    send_typing(channel_id)
    human_delay(typing_time[0], typing_time[1])
    
    try:
        r = requests.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=HEADERS,
            json={"content": text},
            timeout=15
        )
        return r.status_code in (200, 201)
    except:
        return False

# --- THE MAIN LOGIC ---

def process_dm_channel(channel_id, is_request=False):
    # (Assuming conversation_states and seen_messages are handled globally)
    state = conversation_states.get(channel_id, "new")
    
    if state == "new":
        if is_request:
            accept_message_request(channel_id)
            human_delay(2, 5)

        # Send two separate "human" messages
        msg1 = get_ai_response(None, "intro")
        msg2 = get_ai_response(None, "waiting")
        
        send_dm(channel_id, msg1, typing_time=(3, 6))
        human_delay(1, 3) # Short pause between 'thoughts'
        send_dm(channel_id, msg2, typing_time=(2, 4))
        
        conversation_states[channel_id] = "waiting_for_answer"

    elif state == "waiting_for_answer":
        # Get the last message from the user
        last_msg = get_recent_messages(channel_id)[0]["content"]
        intent = detect_intent(last_msg)
        
        if intent == "yes":
            reply = get_ai_response(last_msg, "has_executor")
            send_dm(channel_id, reply)
            conversation_states[channel_id] = "done"
        elif intent == "no":
            reply = get_ai_response(last_msg, "no_executor")
            send_dm(channel_id, reply)
            human_delay(1, 2)
            # Send links as a separate "copy-pasted" message
            links = "Android: https://deltaexploits.gg/delta-executor-android\niOS: https://deltaexploits.gg/delta-executor-ios"
            send_dm(channel_id, links, typing_time=(1, 2))
            conversation_states[channel_id] = "done"
