import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from notification.telegramBot import notify_publish


def col_letter(n):
    letter = ''
    while n > 0:
        n -= 1
        letter = chr(n % 26 + ord('A')) + letter
        n //= 26
    return letter


def main():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(credentials)
    except FileNotFoundError:
        print("error: credentials.json not found")
        sys.exit(1)
    except Exception as e:
        print(f"error: failed to authenticate with Google Sheets: {e}")
        sys.exit(1)

    try:
        sheet = client.open('publishProducts').sheet1
        records = sheet.get_all_values()
    except requests.exceptions.RequestException as e:
        print(f"network error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"error: failed to access Google Sheet: {e}")
        sys.exit(1)

    try:
        cell = sheet.findall("TRUE")
    except requests.exceptions.RequestException as e:
        print(f"network error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"error: failed to search sheet: {e}")
        sys.exit(1)

    print(cell)

    if not cell:
        print("No products to publish, could not find any TRUE value in the sheet.")
        sys.exit(1)

    for record in records:
        if len(record) < 8:
            print(f"warning: skipping row with insufficient columns (expected 8, got {len(record)})")
            continue

        product = {
            "title": record[0],
            "product": record[1],
            "price": record[2],
            "brand": record[3],
            "description": record[4],
            "condition": record[5],
            "hashtags": record[6],
            "publish": record[7]
        }

        if product["publish"] == "TRUE":
            if not notify_publish(product):
                print(f"warning: failed to send notification for {product.get('title', 'unknown')}")

    for c in cell:
        cell_ref = col_letter(c.col) + str(c.row)
        print("Restoring " + cell_ref)
        try:
            sheet.update_acell(cell_ref, 'FALSE')
        except requests.exceptions.RequestException as e:
            print(f"network error: failed to update {cell_ref}: {e}")
        except Exception as e:
            print(f"error: failed to update {cell_ref}: {e}")


if __name__ == "__main__":
    main()
