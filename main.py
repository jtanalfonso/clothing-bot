import asyncio
import aiohttp
from playwright.sync_api import sync_playwright

# Grailed API endpoint and application ID
URL = "https://mnrwefss2q-dsn.algolia.net/1/indexes/*/queries"
GRAILED_APP_ID = "MNRWEFSS2Q"

# Payload for Algolia search request
PAYLOAD = {
  "requests": [
    {
      "indexName": "Listing_by_date_added_production",
      "params": "query=isamu katayama backlash&hitsPerPage=40&page=0"
    }
  ]
}

# Function to fetch an API key from Grailed using Playwright
def fetch_key(search_query="isamu katayama backlash", timeout=15, headless=False):
  key = None

  # Request handler to capture the API key from network requests
  def handle_request(request):
    nonlocal key

    # Check if the request URL contains the Algolia endpoint
    if "algolia.net/1/indexes" in request.url:
      headers = request.headers                   # Get the API key 
      api_key = headers.get("x-algolia-api-key")  #   from request headers

      # Store if the API key is valid
      if api_key and ("validUntil" in api_key or len(api_key) > 60):
        key = api_key
        print(key)

  # Use Playwright to open a browser and navigate to Grailed
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=headless)
    page = browser.new_page()
    page.on("request", handle_request)  # Register request handler to capture API key from network requests

    # Navigate to Grailed search page with the specified query
    query_encoded = search_query.replace(" ", "%20")
    page.goto(f"https://www.grailed.com/shop?query={query_encoded}&sort=new")

    # Wait for the API key to be captured or until the timeout is reached
    elapsed = 0.0
    while key is None and elapsed < timeout:
      page.wait_for_timeout(100)
      elapsed += 0.1
    
    # Close the browser
    browser.close()

  # Raise an exception if timeout is reached without capturing the API key
  if key is None:
    raise Exception("Failed to fetch API key within the timeout period.")
  
  return key

# Asynchronous function to make a request to the Grailed API using the captured API key
async def main(key):
  headers = {
  "Content-Type": "application/x-www-form-urlencoded",
  "X-Algolia-Application-Id": GRAILED_APP_ID,
  "X-Algolia-Api-Key": key
  }
  
  # Make an asynchronous POST request to the Grailed API
  async with aiohttp.ClientSession() as session:
    async with session.post(URL, headers=headers, json=PAYLOAD) as response:
      print("Status: ", response.status)  

      if response.status != 200:
        exit()

      # Parse the JSON response and extract the listing hits
      data = await response.json()
      hits = data["results"][0]["hits"]

      # Print the URLs of the listings retrieved from the API response
      for item in hits:
        listing_id = item["id"]
        listing_url = f"https://www.grailed.com/listings/{listing_id}"
        print(listing_url)

if __name__ == "__main__":
  api_key = fetch_key()
  asyncio.run(main(api_key))