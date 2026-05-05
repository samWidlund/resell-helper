# script to publish products at mulitple platforms at once

import webbrowser
import gspread
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open('publishProducts').sheet1

# Fetch the first row of data
val = sheet.get_all_records()
pprint(val)
print(f'file:///home/samme/repos/productScraper/output.html')

html = f"""
<p>{val} kr</p>
"""

with open('output.html', 'w', encoding='utf-8') as f:
    f.write(html)

webbrowser.open('output.html')