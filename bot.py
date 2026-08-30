import asyncio
import json
import os

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))  # Defaults to 0 if unset

POLL_LISTINGS_INTERVAL_MINS = 5 # Refresh every 5 mins
SEEN_FILE = "seen.json"

# Algolia API endpoint and Grailed application ID
URL = "https://mnrwefss2q-dsn.algolia.net/1/indexes/*/queries"
GRAILED_APP_ID = "MNRWEFSS2Q"

# Payload sent to Algolia - searches the "Listing_by_date_added_production" index for the given query string
PAYLOAD = {
  "requests": [
    {
      "indexName": "Listing_by_date_added_production",
      "params": "query=isamu katayama backlash&hitsPerPage=40&page=0"
    }
  ]
}

# Algolia API key, shared across poll_listings() calls
# Populated on first poll_listings() call, reset to None if a poll gets a bad response, fresh key is fetched on the next poll
api_key = None

# Set up Discord bot with default intents, "!" command prefix (unused, no commands defined)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def fetch_key(search_query="isamu katayama backlash", timeout = 20):
  """
  Launches a headless browser via Playwright, visits Grailed's search page,
  inspects outgoing network requests for ones going to Algolia's index endpoint.
  Captures public Algolia search API key which is used for our own direct API calls.

  Returns captured API key. or raises an Exception if none is found within the timeout window.

  Parameters:
    search_query: The search term to submit on Grailed
    timeout: Maximum time, in seconds, to wait for the API key to be captured before giving up. Exception is raised
  
  Returns:
    The captured Algolia API key as a string

  Raises:
    Exception: If no API key is captured within the timeout window
  """
  key = None

  def handle_request(request):
    """
    Playwright request callback. Inspects outgoing requests for calls to Algolia's index endpoint.
    If a plausible API key is found in the x-algolia-api-key header, it is pulled and stored.

    Args:
      request: Playright request object for the outgoing request
    """
    nonlocal key

    # Filter out requests being sent to the endpoint
    if "algolia.net/1/indexes" in request.url:
      headers = request.headers                   # Get API key from request headers
      found = headers.get("x-algolia-api-key")

      # Store if the API key looks valid
      if found and ("validUntil" in found or len(found) > 60):
        key = found

  # Launch a Chromium browser via Playwright
  # Context uses a custom desktop Chrome UA since default UA gets flagged as a bot
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
      user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
      )
    )
    
    page = context.new_page()
    page.on("request", handle_request)  # Fires for every outgoing network request on this page

    # Navigate to Grailed search page for target query
    # Triggers the page's own search calls, which are inspected for plausible API keys
    query_encoded = search_query.replace(" ", "%20")
    page.goto(f"https://www.grailed.com/shop?query={query_encoded}&sort=new")

    # Wait for the API key to be captured or until the timeout is reached
    elapsed = 0.0
    while key is None and elapsed < timeout:
      page.wait_for_timeout(100)
      elapsed += 0.1
    
    browser.close()

  if key is None:
    raise Exception("Failed to fetch API key within the timeout period.")

  return key

async def get_api_key():
  """
  Runs fetch_key in a background thread, since it is synchronous and would otherwise block the asyncio event loop.

  Returns:
    The captured Algolia API key as a string

  Raises:
    Exception: If no API key is captured within the timeout window
  """
  loop = asyncio.get_running_loop()
  return await loop.run_in_executor(None, fetch_key)

def load_seen():
  """
  Loads the set of listing IDs already posted to Discord.

  Returns:
    Dict mapping listing ID strings to True. Returns an empty dict if SEEN_FILE doesn't exist yet (first run).
  """
  try:
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    return {}

def save_seen(seen):
  """
  Writes the current set of posted listing IDs to SEEN_FILE, overwriting its contents.

  Args:
    seen: Dict mapping listing ID strings to True, as returned by load_seen().
  """
  with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen, f, indent=2)

@tasks.loop(minutes=POLL_LISTINGS_INTERVAL_MINS)
async def poll_listings():
  """
  Polls Grailed's Algolia search endpoint for listings matching PAYLOAD's query and posts any newly seen 
  listing URLs to the configured Discord channel.

  Fetches and caches a fresh API key if one isn't already cached. If Algolia rejects the request, the cached
  key is cleared so the next run fetches a new one, and the cycle is skipped.
  """
  global api_key

  channel = bot.get_channel(CHANNEL_ID)
  if channel is None:
    print("Channel not found.")
    return

  # Fetch and cache a key if we don't have one yet
  if api_key is None:
    api_key = await get_api_key()

  headers = {
    "X-Algolia-Application-Id": GRAILED_APP_ID,
    "X-Algolia-Api-Key": api_key
    }

  seen = load_seen()
  new_listing_found = False

  # Query Algolia directly for the latest listings matching PAYLOAD
  async with aiohttp.ClientSession() as session:
    async with session.post(URL, headers=headers, json=PAYLOAD) as response:
      # Treat a bad response as a sign the cached key is invalid. Clear it so the next poll fetches a fresh one
      if response.status != 200:
        print(f"Status: {response.status} - Refreshing API key")
        api_key = None
        return

      data = await response.json()
      hits = data["results"][0]["hits"]

      for item in hits:
        listing_id = str(item["id"])  # Convert listing IDs to string to match seen.json keys

        if listing_id in seen:
          continue

        seen[listing_id] = True
        new_listing_found = True
        listing_url = f"https://www.grailed.com/listings/{listing_id}"
        await channel.send(listing_url)

  if new_listing_found:
    save_seen(seen)
  else:
    print("No new listings found")

@poll_listings.before_loop
async def before_poll_listings():
  """Waits for the bot to finish connecting before the poll loop starts."""
  await bot.wait_until_ready()

@bot.event
async def on_ready():
  """
  Discord event handler fired once the bot is connected and ready. 
  Starts the listing poll loop if it isn't already running.
  """
  print(f"Logged in as {bot.user} (id: {bot.user.id})")

  if not poll_listings.is_running():
    poll_listings.start()

if __name__ == "__main__":
  if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set. Add to .env file")
  bot.run(TOKEN)