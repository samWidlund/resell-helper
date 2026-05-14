[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python&logoColor=ffd343)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase--gray?style=flat&logo=supabase)](https://supabase.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=flat&logo=telegram)](https://core.telegram.org/bots/api)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=FFFFFF)](https://github.com/features/actions)

# Automated marketplace tool for resellers

Marketplace scraper and publish tool that makes a reseller's daily life easier by combining multiple APIs, GitHub Actions, Telegram, and Google Sheets.

## Background

After years of reselling clothes, I grew tired of manually searching marketplaces for the best deals. Instead of spending hours doing it myself, I built a tool that automates the process and lets software handle the work for me. During the development process I also realized the fact that publishing products at different marketplaces is also kind of a hassle to do. With that in mind I later on implemented a feature to simplify this process.

## Features

- Scheduled product fetching across multiple marketplaces
- Real-time Telegram notifications
- Product filtering by keyword and price
   - One simple search term + price cap across all platforms
- Database integration preventing repeated notifications
- Cross-platform publishing via Google Sheets

# Scraper tool

## Supported Platforms

| Platform | Status |
|----------|--------|
| Facebook Marketplace | **Working** ✅|
| eBay | **Working** ✅|
| Blocket | **Working** ✅|
| Tradera | **Working** ✅|
| Vinted | **Working** ✅|
| Depop | Planned 🕜|

## Requirements

- Python 3.10+
- eBay API credentials
- Apify API (Facebook scraper)
- Supabase account
- Telegram Bot token
- Github account (Github actions)

> **Disclaimer:** This tool relies mostly on third-party APIs (Apify, blocket-api, tradera-api & vinted-api). Usage may be subject to those services' terms of service. Use responsibly and ensure compliance with their policies.

## Setup

### Installation

1. Clone the repository: 
```bash
git clone https://github.com/samWidlund/resell-helper.git
```
2. Create and activate a virtual environment

   - Linux / macOS (bash / zsh / fish)
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

   - Windows (PowerShell)
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

   > **Tip:** Include `.venv/` in `.gitignore` to avoid committing the environment.

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
> **Note:** Currenty the package tradera_api is not included in the ``requirements.txt`` because of a httpx conflict with blocket_api. Tradera fetcher run as a seperate job in workflow, therefore it still works with github actions.

4. Create `.env` file with your credentials:
   ```env
   BOT_TOKEN=your_telegram_token
   BOT_CHAT_ID=your_chat_id
   EBAY_CLIENT_ID=your_ebay_id
   EBAY_CLIENT_SECRET=your_ebay_secret
   APIFY_TOKEN=your_apify_token
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_EMAIL=your_email
   SUPABASE_PASSWORD=your_password
   ```
### Scraping specifications
To specify and narrow what kind of products the scraper is fetching, configure the variables in `fetch/fetch_variables.py`:
```python
# search word used when scraping marketplace
search_term = "Arcteryx"

# swedish listings
max_price_sek = 2000
min_price_sek = 500

# non swedish listings
max_price_usd = 200
min_price_usd = 50
```

### Telegram bot

1. Open Telegram and search for **BotFather**
2. Send `/newbot` to create a new bot
3. Choose a name and username (must end with `bot`)
4. Copy the **API Token** provided by BotFather

**Get your Chat ID:**

1. Start a conversation with your new bot and send any message
2. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates` (replace `<TOKEN>` with your bot token)
3. Find `"chat":{"id":...` in the response - this is your **CHAT_ID**

Add to `.env`:
```env
BOT_TOKEN=your_telegram_token
BOT_CHAT_ID=your_chat_id
```

### Database

This project uses Supabase (PostgreSQL) to store scraped products and prevent duplicate notifications.

**Create a Supabase project:**

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **Settings > API** and copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_KEY`
4. Go to **Authentication > Users** and create a user or use an existing one
5. Add the user's email and password to `.env`:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_EMAIL=your_email
   SUPABASE_PASSWORD=your_password
   ```

**Create product tables:**

Each marketplace requires its own table. Create the following tables in your Supabase SQL editor:

```sql
CREATE TABLE ebay_products (
    id BIGSERIAL PRIMARY KEY,
    itemid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    url TEXT NOT NULL,
    user_id UUID REFERENCES auth.users NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE blocket_products (
    id BIGSERIAL PRIMARY KEY,
    itemid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    url TEXT NOT NULL,
    user_id UUID REFERENCES auth.users NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tradera_products (
    id BIGSERIAL PRIMARY KEY,
    itemid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    url TEXT NOT NULL,
    user_id UUID REFERENCES auth.users NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE vinted_products (
    id BIGSERIAL PRIMARY KEY,
    itemid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    url TEXT NOT NULL,
    user_id UUID REFERENCES auth.users NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE facebook_products (
    id BIGSERIAL PRIMARY KEY,
    itemid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    url TEXT NOT NULL,
    user_id UUID REFERENCES auth.users NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

Enable **Row Level Security (RLS)** and add policies to ensure users can only access their own data:

```sql
ALTER TABLE ebay_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocket_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE tradera_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE vinted_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE facebook_products ENABLE ROW LEVEL SECURITY;

-- Example policy for each table (replace table name as needed)
CREATE POLICY "Users can only see their own data" ON ebay_products
    FOR ALL USING (auth.uid() = user_id);
```

> **Note:** Supabase automatically pauses the project/database after 7 days of inactivity. Visit [supabase.com](https://supabase.com) to restore your database, may take minutes up to several hours.

### Publishing

The `publish/` tool posts products to multiple platforms simultaneously using a Google Sheet as the source of truth.

**Setup:**

1. Enable the Google Sheets API and create service account credentials
2. Download the credentials JSON and save as `credentials.json` in the project root
3. Share your Google Sheet (named `publishProducts`) with the service account email
4. Populate the sheet with product data (title, price, description, images)

**Run:**

```bash
python3 publish/publishProducts.py
```

The script reads the first two rows from the sheet and prints them — extend it to integrate with your target platforms.

> **Note:** `gspread` and `oauth2client` are required. Install with `pip install gspread oauth2client`.

### Running

**Locally:**
> **Note:** Replace [PLATFORM_NAME] with the correspondig platform e.g. `facebook` and [FETCH_SCRIPT] with the python script e.g. `fb_marketplace.py`

```bash
python3 fetch/[PLATFORM_NAME]/[FETCH_SCRIPT].py
```

**Automated:**
Configured to run every 3 hours via github actions. See `.github/workflows/workflow.yml`
> **Note:** Make sure to create and include .env variables in environment secrets.

## Project Structure

```
├── fetch/                    # Marketplace scrapers
│   ├── blocket/
│   ├── ebay/
│   ├── facebook/
│   ├── tradera/
│   └── vinted/
├── database/                 # Database operations
├── publish/                  # Cross-platform publishing tool (Google Sheets)
├── notification/             # User bot notificiation       
└── README.md
```

## References
[EbayAPI](https://developer.ebay.com/develop) \
[TraderaAPI](https://pypi.org/project/tradera_api/) \
[BlocketAPI](https://blocket-api.se/) \
[FacebookAPI](https://apify.com/apify/facebook-pages-scraper) \
[VintedAPI](https://pypi.org/project/vinted-scraper/)

## License

MIT
