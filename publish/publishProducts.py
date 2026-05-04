# script to publish products at mulitple platforms at once

import gspread
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
first_row = sheet.row_values(1)
second_row = sheet.row_values(2)
print(f"First row of data: {first_row}")
print(f"Second row of data: {second_row}")