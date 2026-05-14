import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
from dotenv import load_dotenv
from apify_client import ApifyClient
from notification.telegramBot import notify_product, get_sent_notifications
from database.database import SupabaseClient
from fetch.fetch_variables import search_term, max_price_sek, min_price_sek


def main():
    load_dotenv()
    APIFY_TOKEN = os.getenv("APIFY_TOKEN")
    if not APIFY_TOKEN:
        print("error: APIFY_TOKEN environment variable not set")
        sys.exit(1)

    try:
        client = ApifyClient(APIFY_TOKEN)
    except Exception as e:
        print(f"error: failed to initialize ApifyClient: {e}")
        sys.exit(1)

    run_input = {
        "startUrls": [
            { "url": f"https://www.facebook.com/marketplace/110976692260411/search?query={search_term}" },
        ],
        "resultsLimit": 20,
    }

    try:
        run = client.actor("U5DUNxhH3qKt5PnCf").call(run_input=run_input)
    except Exception as e:
        print(f"error: failed to run Apify actor: {e}")
        sys.exit(1)

    try:
        db = SupabaseClient()
        db.login()
    except ValueError as e:
        print(f"configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"error: failed to connect to database: {e}")
        sys.exit(1)

    total_items = 0
    new_items = 0

    default_dataset_id = run.get("defaultDatasetId")
    if not default_dataset_id:
        print("error: no defaultDatasetId in Apify run response")
        sys.exit(1)

    print("Fetching products from Facebook Marketplace...")

    try:
        items = client.dataset(default_dataset_id).iterate_items()
    except Exception as e:
        print(f"error: failed to access Apify dataset: {e}")
        sys.exit(1)

    for item in items:
        try:
            if not item.get('listing_price'):
                print(f"Skipping item without price: {item.get('marketplace_listing_title', 'unknown')}")
                continue

            item_price = float(item['listing_price']['amount'])
            if item_price > max_price_sek or item_price < min_price_sek:
                print(f"Skipping item outside price range: {item['marketplace_listing_title']} at {item_price}")
                continue

            print(f"Found item: {item['marketplace_listing_title']} at {item['listing_price']['amount']}")
            total_items += 1

            if db.is_new_product("facebook_products", item['id']):
                db.add_product("facebook_products", item['id'], item['marketplace_listing_title'], item['listing_price'], item['listing_price']['amount'], item['listingUrl'])
                if not notify_product("facebook", item['marketplace_listing_title'], item['listing_price']['amount'], item['listing_price'].get('currency', 'SEK'), item['listingUrl']):
                    print(f"warning: failed to send notification for {item['marketplace_listing_title']}")
                new_items += 1
        except Exception as e:
            print(f"error processing item {item.get('id', 'unknown')}: {e}")
            continue

    sent_notifications = get_sent_notifications()
    print(f"Total items found: {total_items}")
    print(f"New items found: {new_items}")
    print(f"Sent notifications: {sent_notifications}")


if __name__ == "__main__":
    main()
