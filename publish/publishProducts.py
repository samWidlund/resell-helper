import sys
from pathlib import Path
from time import time
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from notification.telegramBot import notify_publish

# Set up Google Sheets API credentials
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open('publishProducts').sheet1
records = sheet.get_all_values()

# Function to convert column number to letter
def col_letter(n):
    letter = ''
    while n > 0:
        n -= 1
        letter = chr(n % 26 + ord('A')) + letter
        n //= 26
    return letter

# Find pos of publish boolean in sheet
cell = sheet.findall("TRUE")
print(cell)
for r in cell:
    print(r.col, r.row)

if cell is None:
    print("No products to publish, could not find any TRUE value in the sheet.")
    sys.exit(1)

for r in cell:
    cel_pos = col_letter[r](cell.col) + str(cell.row) # only first one is used, if there are multiple TRUE values, only the first one will be sent to telegram and then all will be set to FALSE
    
# cel_pos = col_letter(cell.col) + str(cell.row) # only first one is used, if there are multiple TRUE values, only the first one will be sent to telegram and then all will be set to FALSE

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
        "hashtags": record[7],
        "publish": record[8]
    }

    for r in product:
        if product[r] == "TRUE": # Send message if publish boolean is true
            notify_publish(product)
        else:
            pass

# sheet.update_acell(cel_pos, 'FALSE') # Restore sheet boolean
