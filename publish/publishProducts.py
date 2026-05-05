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

# Build HTML with copy buttons for each field and a common copy button
products_html = ""
for i, r in enumerate(records):
    product_html = ""
    fields = [
        ('title', 'Titel'),
        ('price', 'Pris'),
        ('brand', 'Märke'),
        ('condition', 'Skick'),
        ('description', 'Beskrivning'),
        ('hashtags', 'Hashtags')
    ]

    product_all_id = f"product-{i}-all"
    product_text = f"""{r.get('title', '')}
{r.get('price', '')}
{r.get('brand', '')}
{r.get('condition', '')}
{r.get('description', '')}
{r.get('hashtags', '')}"""

    for field_key, field_label in fields:
        field_id = f"product-{i}-{field_key}"
        field_value = r.get(field_key, '')
        product_html += f"""
        <div class="field-row">
            <span class="field-label">{field_label}:</span>
            <span class="field-value" id="{field_id}">{field_value}</span>
            <button class="copy-btn" onclick="copyField('{field_id}')">Kopiera</button>
        </div>
        """

    products_html += f"""
    <div class="product-card">
        {product_html}
        <div class="copy-section" id="{product_all_id}" style="display:none;">{product_text}</div>
        <button class="copy-all-btn" onclick="copyProduct('{product_all_id}')">Kopiera allt</button>
    </div>
    """

html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
  .product-card {{ background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 8px; }}
  .field-row {{ display: flex; align-items: center; margin: 8px 0; }}
  .field-label {{ font-weight: bold; min-width: 120px; }}
  .field-value {{ flex: 1; margin: 0 10px; }}
  .copy-btn {{ cursor: pointer; background: #4CAF50; color: white; border: none; padding: 6px 12px; border-radius: 4px; }}
  .copy-btn:hover {{ background: #45a049; }}
  .copy-all-btn {{ cursor: pointer; background: #2196F3; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-top: 10px; }}
  .copy-all-btn:hover {{ background: #1976D2; }}
  .copy-section {{ display: none; }}
</style>
</head>
<body>
{products_html}
<script>
function copyField(id) {{
  const text = document.getElementById(id).innerText;
  navigator.clipboard.writeText(text).then(() => alert('Kopierat!'));
}}

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