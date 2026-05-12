from vinted_scraper import VintedScraper
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from notification.telegramBot import notify_product, get_sent_notifications
from database.database import SupabaseClient
from fetch.fetch_variables import search_term, max_price_sek, max_price_usd, min_price_sek, min_price_usd

## inital supabase client
db = SupabaseClient()
db.login()

## counter variables
total_items = 0
new_items = 0

# scraper = VintedScraper("https://www.vinted.com")
se_scraper = VintedScraper("https://www.vinted.se")
# items = scraper.search({"search_text": search_term})
se_items = se_scraper.search({"search_text": search_term})

print("Fetching vinted marketplace...")
for item in se_items: # removed + items to only fetch from sweden for now
    print(f"{item.title} - {item.price} {item.currency} - {item.url} - {item.id}")

    if item.currency == "USD" and (item.price > max_price_usd or item.price < min_price_usd):
        continue
    if item.currency == "SEK" and (item.price > max_price_sek or item.price < min_price_sek):
        continue

    total_items += 1
    if db.is_new_product("vinted_products", item.id):
        db.add_product("vinted_products", item.id, item.title, item.price, item.currency, item.url)
        notify_product("vinted", item.title, item.price, item.currency, item.url)
        new_items += 1

sent_notifications = get_sent_notifications()
print(f"Total items found: {total_items}")
print(f"New items found: {new_items}")
print(f"Sent notifications: {sent_notifications}")