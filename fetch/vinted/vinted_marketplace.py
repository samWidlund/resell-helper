from vinted_scraper import VintedScraper
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from notification.telegramBot import notify_product, get_sent_notifications
from database.database import SupabaseClient
from fetch.fetch_variables import search_term, max_price_sek, max_price_usd, min_price_sek, min_price_usd


def main():
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

    try:
        se_scraper = VintedScraper("https://www.vinted.se")
        se_items = se_scraper.search({"search_text": search_term})
    except Exception as e:
        print(f"error: failed to fetch Vinted listings: {e}")
        sys.exit(1)

    print("Fetching vinted marketplace...")
    for item in se_items:
        try:
            print(f"{item.title} - {item.price} {item.currency} - {item.url} - {item.id}")

            if item.currency == "USD" and (item.price > max_price_usd or item.price < min_price_usd):
                continue
            if item.currency == "SEK" and (item.price > max_price_sek or item.price < min_price_sek):
                continue

            total_items += 1
            if db.is_new_product("vinted_products", item.id):
                db.add_product("vinted_products", item.id, item.title, item.price, item.currency, item.url)
                if not notify_product("vinted", item.title, item.price, item.currency, item.url):
                    print(f"warning: failed to send notification for {item.title}")
                new_items += 1
        except Exception as e:
            print(f"error processing item {getattr(item, 'id', 'unknown')}: {e}")
            continue

    sent_notifications = get_sent_notifications()
    print(f"Total items found: {total_items}")
    print(f"New items found: {new_items}")
    print(f"Sent notifications: {sent_notifications}")


if __name__ == "__main__":
    main()
