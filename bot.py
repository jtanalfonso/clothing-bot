import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import grailed
import mercari

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))  # Defaults to 0 if unset

POLL_LISTINGS_INTERVAL_MINS = 5 # Refresh every 5 mins

# Set up Discord bot with default intents, "!" command prefix (unused, no commands defined)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=POLL_LISTINGS_INTERVAL_MINS)
async def poll_mercari():
  """Polls mercari.jp for new listings and posts to CHANNEL_ID."""
  await mercari.poll(bot, CHANNEL_ID)

@tasks.loop(minutes=POLL_LISTINGS_INTERVAL_MINS)
async def poll_grailed():
  """Polls Grailed for new listings and posts to CHANNEL_ID"""
  await grailed.poll(bot, CHANNEL_ID)

@poll_mercari.before_loop
async def before_poll_mercari():
  """Waits for the bot to finish connecting before the Mercari poll loop starts."""
  await bot.wait_until_ready()

@poll_grailed.before_loop
async def before_poll_grailed():
  "Waits for the bot to finish connecting before the Grailed poll loop starts."
  await bot.wait_until_ready()

@bot.event
async def on_ready():
  """
  Discord event handler fired once the bot is connected and ready. 
  Starts listing poll loops if they aren't already running.
  """
  print(f"Logged in as {bot.user} (id: {bot.user.id})")

  if not poll_grailed.is_running():
    poll_grailed.start()
  if not poll_mercari.is_running():
    poll_mercari.start()

if __name__ == "__main__":
  if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set. Add to .env file")
  bot.run(TOKEN)