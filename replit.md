# Discord Self-Bot

A Python-based Discord self-bot that sends messages with optional images to specified servers.

## Setup

1. **Get your token:**
   - Visit https://discord.com/developers/applications
   - Use your user account (not a bot application)
   - Copy your user token

2. **Set environment variable:**
   - Add `DISCORD_TOKEN` with your token value

3. **Configure targets in main.py:**
   - Set `TARGET_SERVERS` dictionary with guild IDs and messages
   - Set `IMAGE_PATH` if you want to attach an image

## Usage

The bot logs in, sends messages to configured servers, then automatically closes.

## Requirements

- discord.py
- python-dotenv
