import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from notification.telegramBot import notify_publish

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open('publishProducts').sheet1

# Fetch all rows of data
records = sheet.get_all_values()

# Send products to Telegram

for record in records:
    print(record)
    product = {
        "title": record[0],
        "product": record[1],
        "price": record[2],
        "brand": record[3],
        "description": record[4],
        "images": record[5],
        "condition": record[6],
        "hashtags": record[7]
    }

    for r in product:
        print(product[r])
    
    notify_publish(product)
