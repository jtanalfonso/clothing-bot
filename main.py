import os
from dotenv import load_dotenv
import asyncio
import aiohttp

load_dotenv()

URL = "https://mnrwefss2q-dsn.algolia.net/1/indexes/*/queries"

HEADERS = {
  "Content-Type": "application/x-www-form-urlencoded",
  "X-Algolia-Application-Id": "MNRWEFSS2Q",
  "X-Algolia-Api-Key": os.getenv("ALGOLIA_API_KEY")
}


PAYLOAD = {
  "requests": [
    {
      "indexName": "Listing_by_date_added_production",
      "params": "query=isamu katayama backlash&hitsPerPage=40&page=0"
    }
  ]
}

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, headers=HEADERS, json=PAYLOAD) as response:
            print("Status: ", response.status)

            if response.status != 200:
                exit()

            data = await response.json()

            hits = data["results"][0]["hits"]

            for item in hits:
                listing_id = item["id"]
                listing_url = f"https://www.grailed.com/listings/{listing_id}"
                print(listing_url)

if __name__ == "__main__":
    asyncio.run(main())