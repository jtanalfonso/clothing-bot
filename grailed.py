import asyncio
import json
from urllib.parse import urlencode

import aiohttp
from playwright.sync_api import sync_playwright

import seen_listings
from config import BRANDS

# Algolia API endpoint and Grailed application ID
URL = "https://mnrwefss2q-dsn.algolia.net/1/indexes/*/queries"
GRAILED_APP_ID = "MNRWEFSS2Q"

# Algolia API key, shared across poll() calls for every brand
# Populated on first poll() call, reset to None if a poll gets a bad response, fresh key is fetched on the next poll
api_key = None

def fetch_key(search_query, timeout = 20):
  """
  Launches a headless browser via Playwright, visits Grailed's search page,
  inspects outgoing network requests for ones going to Algolia's index endpoint.
  Captures public Algolia search API key which is used for our own direct API calls.

  Returns captured API key. or raises an Exception if none is found within the timeout window.

  The captured key is reused for every configured brand's queries. 

  Parameters:
    search_query: The search term to submit on Grailed to trigger the request the key is read from
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
  return await loop.run_in_executor(None, fetch_key, "shirts")  # Arbitrary search query to fetch a key

def build_payload(query):
  """
  Builds the Algolia request payload for searching Grailed. Searches Grailed's "Listing_by_date_added_production" index by date added.

  Encodes the query params into a URL-encoded string, then swaps "+" back to literal spaces.

  Always requests page 0 with 40 hits per page.

  Parameters:
    query: The search term to query the index with.

  Returns:
    A dict formatted s an Algolia query request body, with a single request targeting the "Listing_by_date_added_production" index.
  """
  params = {
  "query": query,
  "hitsPerPage": 40,
  "page": 0
  }

  return {
    "requests": [
      {
        "indexName": "Listing_by_date_added_production",
        "params": urlencode(params).replace("+", " ")
      }
    ]
  }

async def poll(bot, brand):
  """
  Polls Grailed's Algolia search endpoint for the given brand's query and posts any newly seen listing URLS to the brand's configured Discord channel.

  Fetches and caches a fresh API key if one isn't already cached (the key is shared across every brand, since it isn't query-specific). If Algolia rejects the request, the cached key is cleared so the next run fetches a new one, and the cycle is skipped.

  Args:
    bot: The running discord.py bot instance.
    brand: A dict from config.BRANDS, containing "name", "grailed_query", and "channel_id" keys
  """
  global api_key

  channel = bot.get_channel(brand["channel_id"])
  if channel is None:
    print(f"Grailed - Channel not found for {brand['name']}.")
    return

  # Fetch and cache a key if we don't have one yet
  if api_key is None:
    api_key = await get_api_key()

  query = brand.get("grailed_query")

  headers = {
    "X-Algolia-Application-Id": GRAILED_APP_ID,
    "X-Algolia-Api-Key": api_key
    }
  payload = build_payload(query)
  seen_path = seen_listings.seen_file("grailed", brand["name"])

  seen = seen_listings.load_seen(seen_path)
  new_listing_found = False

  # Query Algolia directly for the latest listings matching this brand's query
  async with aiohttp.ClientSession() as session:
    async with session.post(URL, headers=headers, json=payload) as response:
      # Treat a bad response as a sign the cached key is invalid. Clear it so the next poll fetches a fresh one
      if response.status != 200:
        print(f"Grailed - Status: {response.status} - Refreshing API key")
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
    seen_listings.save_seen(seen_path, seen)
  else:
    print(f"Grailed - No new listings found for {brand['name']}")

    