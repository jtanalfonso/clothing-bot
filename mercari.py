from mercapi import Mercapi
from mercapi.requests import SearchRequestData

import seen_listings

SEEN_FILE = "seen_mercari.json"

# ISAMUKATAYAMA BACKLASH, ISAMU KATAYAMA, BACKLASH
BRAND_IDS = [5808, 15421, 11072]

async def poll(bot, channel_id):
  """
  Polls mercari.jp for new listings and post any unseen ones to the configured Discord channel.
  Searches by brand ID only (empty keyword), sorted newest-first. 

  Args:
    bot: The running discord.py bot instance.
    channel_id: ID of the Discord channel to post new listings to.
  """
  channel = bot.get_channel(channel_id)
  if channel is None:
    print("Mercari - Channel not found.")
    return

  seen = seen_listings.load_seen(SEEN_FILE)
  new_listing_found = False

  m = Mercapi()

  results = await m.search(
      '',                              # Empty - filters by brand id
      brands=BRAND_IDS,
      sort_by=SearchRequestData.SortBy.SORT_CREATED_TIME,
      sort_order=SearchRequestData.SortOrder.ORDER_DESC,
  )

  for item in results.items:
    listing_id = item.id_ 

    if listing_id in seen:
      continue

    seen[listing_id] = True
    new_listing_found = True
    listing_url = f"https://jp.mercari.com/item/{item.id_}"
    await channel.send(listing_url)

  if new_listing_found:
    seen_listings.save_seen(SEEN_FILE, seen)
  else:
    print("Mercari - No new listings found")