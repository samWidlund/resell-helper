import os
from typing import Optional
from dotenv import load_dotenv
import requests

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
def notify_publish(product: Optional[dict] = None):
    global sent_notifications
    # stop if tokens not valid
    if not TOKEN or not CHAT_ID:
        print("error: BOT_TOKEN or BOT_CHAT_ID could not be found as environment variables")
        return False
    
    # telegram message
    if product:
        title = product.get('title', 'No title')
        price = product.get('price', 'N/A')
        brand = product.get('brand', 'N/A')
        condition = product.get('condition', 'N/A')
        description = product.get('description', 'N/A')
        hashtags = product.get('hashtags', 'N/A')
        
        text = f"**{title}**\n"
        text += f"Pris: {price}\n"
        text += f"Märke: {brand}\n"
        text += f"Skick: {condition}\n"
        text += f"Beskrivning: {description}\n"
        text += f"Hashtags: {hashtags}"
        
        if len(text) > 4096:
            text = text[:4093] + "..."
    else:
        text = "testing publish notification"
    
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    try:
        r = requests.post(url_api, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
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
    except Exception as e:
        print(f"unexpected error: {e}")
        return False