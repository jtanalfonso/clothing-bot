import time

import aiohttp
import discord
from mercapi import Mercapi
from mercapi.requests import SearchRequestData

import seen_listings

# Frankfurter - free, keyless currency API backed by the ECB's daily rates. Refreshes once a day, so we cache it every hour.
FX_URL = "https://api.frankfurter.dev/v1/latest"
FX_CACHE_TTL_SECONDS = 3600  # 1 hour

# Cached JPY->USD rate and when it was last fetched. Shared across every poll() call instead of refetched per listing.
jpy_to_usd_rate = None
jpy_to_usd_rate_fetched_at = 0.0

async def get_jpy_to_usd_rate():
  """
  Returns the current JPY->USD exchange rate. Cached for FX_CACHE_TTL_SECONDS (3600). On a failed refresh, falls back to whatever rate was already cached.

  Returns:
    The number of USD per 1 JPY as a float.
  """
  global jpy_to_usd_rate, jpy_to_usd_rate_fetched_at

  # Use cached rate if we already have a rate and it's still inside the TTL.
  # monotonic() is used instead of time() so the cache age can't be thrown off by any system clock changes.
  if (jpy_to_usd_rate is not None) and (time.monotonic() - jpy_to_usd_rate_fetched_at < FX_CACHE_TTL_SECONDS):
    return jpy_to_usd_rate

  # Fetches the current JPY->USD rate from the API and records when the rate was successfully fetched.
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(FX_URL, params={"base": "JPY", "symbols": "USD"}) as response:
        response.raise_for_status()

        data = await response.json()

        jpy_to_usd_rate = data["rates"]["USD"]
        jpy_to_usd_rate_fetched_at = time.monotonic()
  except Exception as e:
    # Keep serving the cached rate for any errors
    print(f"Mercari - Failed to refresh JPY->USD rate, reusing cached value: {e}")

  return jpy_to_usd_rate

async def build_embed(item):
  """
  Builds a Discord embed for a single Mercari listing:
  Cover image, title, and price.

  Args:
    item: A SearchResultItem from mercapi's search results.
  
  Returns:
    A discord.Embed ready to send via channel.send(embed=...).
  """
  listing_url = f"https://jp.mercari.com/item/{item.id_}"
  title = item.name
  cover_image_url = item.thumbnails[0]

  if item.real_price is None:
    price = "None"  # For listings with no price
  else:
    usd_rate = await get_jpy_to_usd_rate()
    if usd_rate is None:
      # Show only JPY if nothing is cached yet
      price = f"\u00a5{item.real_price:,}"
    else:
      price = f"\u00a5{item.real_price:,} (${item.real_price * usd_rate:,.2f})"

  embed = discord.Embed(title=title, url=listing_url)
  embed.set_image(url=cover_image_url)
  embed.add_field(name="Site", value="Mercari JP", inline=True)
  embed.add_field(name="Price", value=price, inline=True)

  return embed

async def poll(bot, brand):
  """
  Polls mercari.jp for new listings matching the given brand and posts any unseen ones to the brand's configured Discord channel. Searches by brand ID only (empty keyword), sorted newest-first.

  Args:
    bot: The running discord.py bot instance.
    brand: A dict from config.BRANDS with "name", "channel_id", and "mercari_brand_ids" keys.
  """
  channel = bot.get_channel(brand["channel_id"])
  if channel is None:
    print(f"Mercari - Channel not found for {brand['name']}.")
    return

  seen_path = seen_listings.seen_file("mercari", brand["name"])
  seen = seen_listings.load_seen(seen_path)
  new_listing_found = False

  m = Mercapi()

  results = await m.search(
      '',                              # Empty - filters by brand id
      brands=brand["mercari_brand_ids"],
      sort_by=SearchRequestData.SortBy.SORT_CREATED_TIME,
      sort_order=SearchRequestData.SortOrder.ORDER_DESC,
  )

  for item in results.items:
    listing_id = item.id_ 

    if listing_id in seen:
      continue

    seen[listing_id] = True
    new_listing_found = True

    embed = await build_embed(item)
    await channel.send(embed=embed)

  if new_listing_found:
    seen_listings.save_seen(seen_path, seen)
  else:
    print(f"Mercari - No new listings found for {brand['name']}")