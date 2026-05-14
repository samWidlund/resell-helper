# CAUTION - this code is contains a non official API client for blocket, and is not guaranteed to fully follow blockets terms of service. Use at your own risk. The code is for educational purposes only and should not be used for commercial purposes without proper authorization from blocket.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from notification.telegramBot import notify_product, get_sent_notifications
from database.database import SupabaseClient
from fetch.fetch_variables import search_term, max_price_sek, min_price_sek
from blocket_api import (
    BlocketAPI,
    SortOrder,
    Location,
)


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
        api = BlocketAPI()
    except Exception as e:
        print(f"error: failed to initialize BlocketAPI: {e}")
        sys.exit(1)

    all_locations = [
        Location.BLEKINGE, Location.DALARNA, Location.GOTLAND, Location.GAVLEBORG,
        Location.HALLAND, Location.JAMTLAND, Location.JONKOPING, Location.KALMAR,
        Location.KRONOBERG, Location.NORRBOTTEN, Location.SKANE, Location.STOCKHOLM,
        Location.SODERMANLAND, Location.UPPSALA, Location.VARMLAND, Location.VASTERBOTTEN,
        Location.VASTERNORRLAND, Location.VASTMANLAND, Location.VASTRA_GOTALAND,
        Location.OREBRO, Location.OSTERGOTLAND
    ]

    try:
        response = api.search(
            search_term,
            sort_order=SortOrder.PRICE_ASC,
            locations=all_locations
        )
    except Exception as e:
        print(f"error: failed to search Blocket: {e}")
        sys.exit(1)

    if not isinstance(response, dict):
        print(f"error: unexpected response type from Blocket API: {type(response).__name__}")
        sys.exit(1)

    products = response.get('docs', [])
    if not products:
        print("No products found from Blocket.")
        sys.exit(1)

    for product in products:
        try:
            heading = product.get('heading', 'N/A')
            price = product.get('price', {})
            amount = price.get('amount')
            if amount is None or not isinstance(amount, (int, float)):
                print(f"Skipping item '{heading}' without valid price")
                continue

            currency = price.get('price_unit', 'N/A')
            product_id = product.get('id', 'N/A')
            location = product.get('location', 'N/A')
            url = product.get('canonical_url', 'N/A')

            if amount > max_price_sek or amount < min_price_sek:
                continue

            print(f"Title: {heading}")
            print(f"Price: {amount} {currency}")
            print(f"Location: {location}")
            print(f"ID: {product_id}")
            print(f"URL: {url}")
            total_items += 1

            if db.is_new_product("blocket_products", product_id):
                db.add_product("blocket_products", product_id, heading, amount, currency, url)
                if not notify_product("blocket", heading, amount, currency, url):
                    print(f"warning: failed to send notification for {heading}")
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
