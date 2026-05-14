# alt use https://apify.com/ecomscrape/tradera-product-search-scraper/api/python

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tradera_api.tradera import TraderaAPI, BASE_URL, AuctionType
import json
from notification.telegramBot import notify_product, get_sent_notifications
from database.database import SupabaseClient
from fetch.fetch_variables import search_term, max_price_sek, min_price_sek


def find_items(response: dict):
    if not isinstance(response, dict):
        return []
    for k in ("items", "results", "hits", "itemsResult", "data"):
        v = response.get(k)
        if isinstance(v, list):
            return v
    for v in response.values():
        if isinstance(v, list):
            return v
    return []


def pick(item: dict, *keys):
    for k in keys:
        if k in item:
            return item[k]
    return None


def extract_simple(item: dict):
    _id = pick(item, "id", "listingId", "itemId", "Id", "ItemId")
    title = pick(item,
                 "title", "name", "listingTitle", "itemName",
                 "shortDescription", "heading", "Title", "Name") or ""
    if not title and "item" in item:
        title = pick(item["item"], "title", "name", "Title") or ""
    price_block = pick(item, "price", "currentPrice", "buyNowPrice", "startingPrice")
    if isinstance(price_block, dict):
        price = pick(price_block, "amount", "value", "Amount", "Value")
        currency = pick(price_block, "currency", "currencyCode", "currencyIso") or "SEK"
    else:
        price = price_block
        currency = pick(item, "currency", "currencyCode") or "SEK"
    url = pick(item, "url", "itemUrl", "listingUrl", "link", "permalink", "Url")
    if not url and _id:
        url = f"{BASE_URL}item/{_id}"
    return (_id, title, price, currency, url)


def main():
    try:
        api = TraderaAPI()
    except Exception as e:
        print(f"error: failed to initialize TraderaAPI: {e}")
        sys.exit(1)

    search_types = [AuctionType.auction, AuctionType.buy_now]

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

    for st in search_types:
        try:
            res = api.search(query=search_term, price=(min_price_sek, max_price_sek), auction_type=st)
        except Exception as e:
            print(f"error: failed to search Tradera for type {st.name}: {e}")
            continue

        items = find_items(res)
        if not items:
            print(f"No items found for type {st.name}")
            continue

        for it in items[:50]:
            try:
                total_items += 1
                _id, title, price, currency, url = extract_simple(it)
                print(f"Found item: {title} at {price} {currency} ({url})")

                try:
                    price_val = float(price) if price is not None else None
                except (ValueError, TypeError):
                    price_val = None

                if db.is_new_product("tradera_products", str(_id)):
                    db.add_product("tradera_products", str(_id), title, price_val, currency or "SEK", url)
                    if not notify_product("tradera", title, price_val, currency or "SEK", url, auction_type=st.name):
                        print(f"warning: failed to send notification for {title}")
                    new_items += 1
            except Exception as e:
                print(f"error processing item: {e}")
                continue

    print(f"Total items found: {total_items}")
    print(f"New items found: {new_items}")
    print(f"Sent notifications: {get_sent_notifications()}")


if __name__ == "__main__":
    main()
