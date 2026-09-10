from mercapi import Mercapi
from mercapi.requests import SearchRequestData

import seen_listings

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
    listing_url = f"https://jp.mercari.com/item/{item.id_}"
    await channel.send(listing_url)

  if new_listing_found:
    seen_listings.save_seen(seen_path, seen)
  else:
    print(f"Mercari - No new listings found for {brand['name']}")