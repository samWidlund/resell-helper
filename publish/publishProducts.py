# script to publish products at mulitple platforms at once

import webbrowser
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

# Fetch all rows of data
records = sheet.get_all_records()

print("file:///home/samme/repos/productScraper/output.html")

# Build HTML with a copy button per product
products_html = ""
for i, r in enumerate(records):
    product_id = f"product-{i}"
    product_text = f"""
{r.get('title', '')}
{r.get('price', '')}
{r.get('brand', '')}
{r.get('condition', '')}
{r.get('description', '')}
{r.get('hashtags', '')}"""

    products_html += f"""
    <div class="product-card">
      <div class="copy-section" id="{product_id}">{product_text}</div>
      <button class="copy-btn" onclick="copyProduct('{product_id}')">Kopiera</button>
    </div>
    """

html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
  .product-card {{ background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 8px; }}
  .copy-section {{ white-space: pre-wrap; line-height: 1.6; }}
  .copy-btn {{ cursor: pointer; background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-top: 10px; }}
  .copy-btn:hover {{ background: #45a049; }}
</style>
</head>
<body>
{products_html}
<script>
function copyProduct(id) {{
  const text = document.getElementById(id).innerText;
  navigator.clipboard.writeText(text).then(() => alert('Kopierat!'));
}}
</script>
</body>
</html>"""

with open('output.html', 'w', encoding='utf-8') as f:
    f.write(html)

webbrowser.open('output.html')