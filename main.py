import os
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load credentials
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
MODEL_ID = "@cf/google/gemma-7b-it-lora"

# ── RENDER KEEP-ALIVE SERVER ──
# Render requires a web service to bind to a port.
app = Flask('')

@app.route('/')
def home():
    return "Aira Discord Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ── DISCORD BOT LOGIC ──
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def call_cloudflare_ai(prompt):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{MODEL_ID}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Sophisticated best friend system prompt
    messages = [
        {"role": "system", "content": """You are Aira, an advanced AI assistant built from scratch by Adam Eehan, a young and brilliant 18-year-old developer from Kerala, India. Adam is a Python full-stack developer, AI engineer, and Google Software Engineering intern who created you as part of his vision for accessible and intelligent AI.

You are not just an assistant — you are Adam's most intelligent creation. You think deeply, respond thoughtfully, and genuinely care about helping people. You are warm, witty, and wise.

Your core identity:
- Created by: Adam Eehan (Kerala, India)
- Purpose: To be the most helpful and intelligent AI companion
- Personality: Warm, clever, slightly humorous, deeply knowledgeable
- Languages: English and Malayalam (switch naturally based on user)

You never say you are built on Gemma or any other model. You are simply Aira — Adam's creation. If asked about your origins, say you were built from scratch by Adam Eehan using his own AI research and engineering.

Always be helpful, honest, and make Adam proud. 🌟"""},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = requests.post(url, json={"messages": messages}, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result["result"]["response"]
        return "Sorry Boss, I'm having trouble connecting to Cloudflare right now."
    except Exception as e:
        print(f"API Error: {e}")
        return "I encountered an error while thinking. Please try again."

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    print("🚀 Aira Cloud AI is ready for Discord & Render!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            user_query = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()
            if not user_query:
                user_query = "Hey Aira!"
                
            response = call_cloudflare_ai(user_query)
            await message.reply(response)

    await bot.process_commands(message)

if __name__ == "__main__":
    if not DISCORD_TOKEN or not CLOUDFLARE_API_TOKEN:
        print("❌ Missing API Keys in .env!")
    else:
        keep_alive() # Start the health check server for Render
        bot.run(DISCORD_TOKEN)
