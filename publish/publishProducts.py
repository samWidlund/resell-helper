import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from notification.telegramBot import notify_publish, notify_document

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open('publishProducts').sheet1

# Fetch all rows of data
records = sheet.get_all_records()

# Send products to Telegram

for record in records:
    print(record) # fetches way more than it should?
