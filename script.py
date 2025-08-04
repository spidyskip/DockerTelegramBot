# Telethon utility # pip install telethon
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import datetime
import asyncio
import requests

import configparser # Library for reading from a configuration file, # pip install configparser
import datetime # Library that we will need to get the day and time, # pip install datetime


#### Access credentials
#config = configparser.ConfigParser() # Define the method to read the configuration file
#config.read('config.ini') # read config.ini file
#
#api_id = config.get('default','api_id') # get the api id
#api_hash = config.get('default','api_hash') # get the api hash
#BOT_TOKEN = config.get('default','BOT_TOKEN') # get the bot token

import os
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL= os.getenv('API_URL')

# Create the client and the session called session_master. We start the session as the Bot (using bot_token)
client = TelegramClient('sessions/session_master', api_id, api_hash).start(bot_token=BOT_TOKEN)

# Define the /start command
@client.on(events.NewMessage(pattern='/(?i)start')) 
async def start(event):
    sender = await event.get_sender()
    SENDER = sender.id
    text = "Docker Bot 🤖 ready\nHello! I'm answering you from Docker!"
    await client.send_message(SENDER, text, parse_mode="HTML")

### First command, get the time and day
@client.on(events.NewMessage(pattern='/(?i)hello')) 
async def time(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id
    text = "Hello".format(sender.first_name)
    await client.send_message(SENDER, text, parse_mode="HTML")

@client.on(events.NewMessage(pattern='/(?i)sender')) 
async def time(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id
    text = f"{SENDER} - {sender.first_name} {sender.last_name} ({sender.username})"
    await client.send_message(SENDER, text, parse_mode="HTML")

### First command, get the time and day
@client.on(events.NewMessage(pattern='/(?i)time')) 
async def time(event):
    # Get the sender of the message
    sender = await event.get_sender()
    SENDER = sender.id
    text = "Received! Day and time: " + str(datetime.datetime.now())
    await client.send_message(SENDER, text, parse_mode="HTML")

# Match /chat followed by any text (the query)
@client.on(events.NewMessage(pattern=r'/chat\s+(.+)', func=lambda e: e.is_private))
async def chat_with_api(event):
    sender = await event.get_sender()
    SENDER = sender.id

    if str(SENDER) not in os.getenv('ALLOWED_USERS', '').split(','):
        await event.respond("You are not allowed to use this bot.")
        return

    # Extract the query part from the message
    query = event.pattern_match.group(1)

    # Placeholder API endpoint — replace with your actual one
    api_url = API_URL

    payload = {
        "query": query,
        "agent_id": "general-agent",
        "thread_id": str(SENDER),
        "user_id": str(SENDER),
        "include_history": True
    }
    headers = {"Content-Type": "application/json"} 
    
    def make_request():
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response field found.")
            else:
                return f"API Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Request failed: {str(e)}"

    # Run the blocking request in an executor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, make_request)

    await client.send_message(SENDER, result, parse_mode="HTML")


### MAIN
if __name__ == '__main__':
    print("Bot Started!")
    client.run_until_disconnected()
