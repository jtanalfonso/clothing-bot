import asyncio
import json
from urllib.parse import urlencode

import aiohttp
import discord
from playwright.sync_api import sync_playwright

import seen_listings

# Algolia API endpoint and Grailed application ID
URL = "https://mnrwefss2q-dsn.algolia.net/1/indexes/*/queries"
GRAILED_APP_ID = "MNRWEFSS2Q"

# Cached Algolia API key shared across all brand polls.
# Fetched on the first poll, then reused until Algolia rejects it.
# When rejected, the key is set to None so the next poll fetches a new one.
api_key = None

def fetch_key(search_query, timeout = 20):
  """
  Launches a headless browser via Playwright, visits Grailed's search page, and
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

def build_payload(query, designer_ids=None):
  """
  Builds independent Grailed Algolia searches for a keyword and/or designer IDs.
  Matches from either search will be combined when poll() processes the results.
  Each search returns the 40 newest marching listings (page 0).

  Parameters:
    query: Optional free-text search term.
    designer_ids: Optional Grailed designer IDs.

  Returns:
    An Algolia multi-query request body.
  """
  requests = []
  index_name = "Listing_by_date_added_production"

  if query:
    params = {"query": query, "hitsPerPage": 40, "page": 0}
    requests.append({"indexName": index_name, "params": urlencode(params)})

  if designer_ids:
    # All designer IDs are alternatives (OR), not extra keyword restrictions.
    designer_filters = [[f"designers.id:{designer_id}" for designer_id in designer_ids]]
    params = {
      "query": "",
      "hitsPerPage": 40,
      "page": 0,
      "facetFilters": json.dumps(designer_filters),
    }
    requests.append({"indexName": index_name, "params": urlencode(params)})

  return {"requests": requests}

def build_embed(item, listing_id):
  """
  Builds a Discord embed for a single Grailed listing:
  Cover image, title, price, and size.

  Args:
    item: A single hit dict from an Algolia result's "hits" array.
    listing_id: This listing's ID.
  
  Returns:
    A discord.Embed ready to send via channel.send(embed=...).
  """
  listing_url = f"https://www.grailed.com/listings/{listing_id}"
  title = item["title"]
  price = f"${item['price']}"
  size = item["size"]
  cover_image_url = item["cover_photo"]["image_url"]

  embed = discord.Embed(title=title, url=listing_url)
  embed.set_image(url=cover_image_url)
  embed.add_field(name="Site", value="Grailed", inline=True)
  embed.add_field(name="Price", value=price, inline=True)
  embed.add_field(name="Size", value=size, inline=True)

  return embed

async def poll(bot, brand):
  """
  Searches by keyword and Grailed designer ID independently, then posts the combined unseen listings to the brand's configured Discord channel.

  Fetches and caches a fresh API key if one isn't already cached (the key is shared across every brand, since it isn't query-specific). If Algolia rejects the request, the cached key is cleared so the next run fetches a new one, and the cycle is skipped.

  Args:
    bot: The running discord.py bot instance.
    brand: A dict from config.BRANDS with "name", "channel_id", optional "grailed_query", and optional "grailed_designer_ids" keys.
  """
  global api_key

  channel = bot.get_channel(brand["channel_id"])
  if channel is None:
    print(f"Grailed - Channel not found for {brand['name']}.")
    return

  query = brand.get("grailed_query")
  designer_ids = brand.get("grailed_designer_ids") or []
  if not query and not designer_ids:
    print(f"Grailed - No query or designer IDs configured for {brand['name']}; skipping.")
    return

  # Fetch and cache a key if we don't have one yet
  if api_key is None:
    api_key = await get_api_key()

  headers = {
    "X-Algolia-Application-Id": GRAILED_APP_ID,
    "X-Algolia-Api-Key": api_key
    }
  payload = build_payload(query, designer_ids)
  seen_path = seen_listings.seen_file("grailed", brand["name"])

  seen = seen_listings.load_seen(seen_path)
  new_listing_found = False

  # A single HTTP request batches both searches
  # # Each result contains its own hits.
  async with aiohttp.ClientSession() as session:
    async with session.post(URL, headers=headers, json=payload) as response:
      # Treat a bad response as a sign the cached key is invalid. Clear it so the next poll fetches a fresh one
      if response.status != 200:
        print(f"Grailed - Status: {response.status} - Refreshing API key")
        api_key = None
        return

      data = await response.json()
      for result in data["results"]:
        if result.get("status", 200) != 200 or "hits" not in result:
          print(f"Grailed - Search failed for {brand['name']}: {result}")
          continue

        for item in result["hits"]:
          listing_id = str(item["id"])  # Same ID in either search only posts once.

          if listing_id in seen:
            continue

          embed = build_embed(item, listing_id)
          await channel.send(embed=embed)
          seen[listing_id] = True
          new_listing_found = True

  if new_listing_found:
    seen_listings.save_seen(seen_path, seen)
  else:
    print(f"Grailed - No new listings found for {brand['name']}")

    