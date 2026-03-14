import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("ERROR: DISCORD_TOKEN not set in environment variables")
    exit(1)

# Server ID and message config - CUSTOMIZE THESE
TARGET_SERVERS = {
    # 'server_id': 'message_text'
    # Example: 1234567890: 'Hello Server 1!'
}

# Image path - CUSTOMIZE THIS
IMAGE_PATH = None  # Set to image file path if you want to attach an image

class SelfBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.sent_messages = False

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        
        if not self.sent_messages:
            self.sent_messages = True
            await self.send_targeted_messages()
            
            # Close bot after sending messages
            await asyncio.sleep(2)
            await self.close()

    async def send_targeted_messages(self):
        """Send messages to specified servers"""
        for guild_id, message_text in TARGET_SERVERS.items():
            try:
                guild = self.get_guild(guild_id)
                if guild is None:
                    print(f"Guild {guild_id} not found")
                    continue
                
                # Get first text channel in the guild
                channel = None
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                
                if channel is None:
                    print(f"No accessible text channel in guild {guild_id}")
                    continue
                
                # Send message with optional image
                if IMAGE_PATH and os.path.exists(IMAGE_PATH):
                    file = discord.File(IMAGE_PATH)
                    await channel.send(message_text, file=file)
                    print(f"Sent message with image to {guild.name} (#{channel.name})")
                else:
                    await channel.send(message_text)
                    print(f"Sent message to {guild.name} (#{channel.name})")
                    
            except Exception as e:
                print(f"Error sending message to guild {guild_id}: {e}")

    async def on_message(self, message):
        """Handle incoming messages - self-bots typically don't respond to messages"""
        pass

def main():
    if not TARGET_SERVERS:
        print("WARNING: TARGET_SERVERS is empty. Configure your servers and messages in the script.")
        print("Format: TARGET_SERVERS = { guild_id: 'message text' }")
    
    bot = SelfBot()
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
