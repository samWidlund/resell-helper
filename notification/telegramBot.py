import os
import json
from dotenv import load_dotenv
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton

# load enviroment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("BOT_CHAT_ID")
sent_notifications = 0


# fetch 
def notify_product(platform, title, price, currency, url, auction_type=None):
    global sent_notifications

    # stop if tokens not valid
    if not TOKEN or not CHAT_ID:
        print("error: BOT_TOKEN or BOT_CHAT_ID could not be found as environment variables")
        return False
    
    # telegram message
    hyperlink = f"[Link]({url})"
    text = f"{price} {currency} - {platform}\n{title}\n{hyperlink}"
    if auction_type:
        text += f"\nType: {auction_type}"
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    try:
        r = requests.post(url_api, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        r.raise_for_status() # throw exception when http error
        
        response = r.json()
        if response.get("ok"):
            print("notification sent!")
            sent_notifications += 1
            return True
        else:
            print(f"wrong answer from Telegram API: {response}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"network error: {e}")
        return False
    except Exception as e:
        print(f"unexpected error: {e}")
        return False

def get_sent_notifications():
    return sent_notifications

# publish
def notify_publish(product: dict):
    global sent_notifications
    if not TOKEN or not CHAT_ID:
        print("error: BOT_TOKEN or BOT_CHAT_ID could not be found as environment variables")
        return False

    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    text = (
        f"title: {product['title']}\n"
        f"product: {product['product']}\n"
        f"price: {product['price']}\n"
        f"brand: {product['brand']}\n"
        f"description: {product['description']}\n"
        f"condition: {product['condition']}\n"
        f"hashtags: {product['hashtags']}\n"


    )


    # text + copy buttons for each field
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Title", "copy_text": {"text": product["title"]}},
                {"text": "Product",  "copy_text": {"text": product["product"]}},
            ],
            [
                {"text": "Price",  "copy_text": {"text": product["price"]}},
                {"text": "Brand",  "copy_text": {"text": product["brand"]}},
            ],
            [
                {"text": "Description",  "copy_text": {"text": product["description"]}},
                {"text": "Condition",  "copy_text": {"text": product["condition"]}},
            ],
            [
                {"text": "Hashtags",  "copy_text": {"text": product["hashtags"]}},
                {"text": "Copy All", "copy_text": {"text": text}},
            ],
        ]}

    try:
        r = requests.post(url_api, data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(keyboard)
        }, timeout=10)
        r.raise_for_status()
        response = r.json()
        if response.get("ok"):
            print("notification sent!")
            sent_notifications += 1
            return True
        else:
            print(f"wrong answer from Telegram API: {response}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"network error: {e}")
        return False