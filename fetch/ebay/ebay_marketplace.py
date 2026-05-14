import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from notification.telegramBot import notify_product, get_sent_notifications
from fetch.ebay.ebay_api import EbayAPI
from database.database import SupabaseClient
import fetch.ebay.config as config
from fetch.fetch_variables import search_term, max_price_usd, min_price_usd


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
        ebay = EbayAPI(
            client_id=config.EBAY_CLIENT_ID,
            client_secret=config.EBAY_CLIENT_SECRET,
            sandbox=config.EBAY_SANDBOX
        )

        products = ebay.search(
            query=search_term,
            max_price=max_price_usd,
            min_price=min_price_usd,
            marketplace='US'
        )
    except Exception as e:
        print(f"error: failed to search eBay: {e}")
        sys.exit(1)

    print("Fetching products from eBay Marketplace...")
    for product in products:
        try:
            print(f"Found item: {product['title']} at {product['price']} {product['currency']} id: {product['id']}")
            total_items += 1

            if db.is_new_product("ebay_products", product['id']):
                db.add_product("ebay_products", product['id'], product['title'], product['price'], product['currency'], product['url'])
                if not notify_product("ebay", product['title'], product['price'], product['currency'], product['url']):
                    print(f"warning: failed to send notification for {product['title']}")
                new_items += 1
        except Exception as e:
            print(f"error processing item {product.get('id', 'unknown')}: {e}")
            continue

    sent_notifications = get_sent_notifications()
    print(f"Total items found: {total_items}")
    print(f"New items found: {new_items}")
    print(f"Sent notifications: {sent_notifications}")


if __name__ == "__main__":
    main()
