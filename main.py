import discord
import os
import asyncio

# Direct token (no dotenv needed)
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

class SelfBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.sent_messages = False

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f'User ID: {self.user.id}')
        
        if not self.sent_messages:
            self.sent_messages = True
            await self.send_to_channels()
            
            # Close bot after sending messages
            await asyncio.sleep(2)
            await self.close()

    async def send_to_channels(self):
        """Send messages to specified channels, respecting slowmode"""
        for channel_id in CHANNEL_IDS:
            try:
                channel = await self.fetch_channel(channel_id)
                print(f"\nProcessing channel: {channel.name} (ID: {channel_id})")
                
                # Check slowmode
                slowmode = channel.slowmode_delay if hasattr(channel, 'slowmode_delay') else 0
                if slowmode > 0:
                    print(f"⏳ Slowmode detected: {slowmode} seconds. Waiting...")
                    await asyncio.sleep(slowmode)
                
                # Try to send with image
                try:
                    if IMAGE_PATH and os.path.exists(IMAGE_PATH):
                        file = discord.File(IMAGE_PATH)
                        await channel.send(MESSAGE, file=file)
                        print(f"✅ Sent message with image to {channel.name}")
                    else:
                        await channel.send(MESSAGE)
                        print(f"✅ Sent message to {channel.name}")
                except discord.errors.HTTPException as e:
                    # If image sending fails, try without image
                    if "image" in str(e).lower() or e.code == 50003:
                        print(f"⚠️ Cannot send image to {channel.name}, sending message only...")
                        await channel.send(MESSAGE)
                        print(f"✅ Sent message to {channel.name}")
                    else:
                        print(f"❌ Error sending to {channel.name}: {e}")
                    
            except discord.errors.NotFound:
                print(f"❌ Channel {channel_id} not found")
            except discord.errors.Forbidden:
                print(f"❌ No permission to send message in channel {channel_id}")
            except Exception as e:
                print(f"❌ Error processing channel {channel_id}: {e}")

    async def on_message(self, message):
        """Handle incoming messages"""
        pass

def main():
    print("Starting Discord Self-Bot...")
    print(f"Token: {TOKEN[:20]}...")
    print(f"Target channels: {CHANNEL_IDS}")
    bot = SelfBot()
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
