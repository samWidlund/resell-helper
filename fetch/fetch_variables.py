import os
from dotenv import load_dotenv

load_dotenv()


def _int_env(key: str, default: int) -> int:
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        print(f"warning: {key} has invalid value '{val}', using default {default}")
        return default


search_term = os.environ.get("SEARCH_TERM") or "arcteryx"
min_price_sek = _int_env("MIN_PRICE_SEK", 0)
max_price_sek = _int_env("MAX_PRICE_SEK", 1000)
min_price_usd = _int_env("MIN_PRICE_USD", 0)
max_price_usd = _int_env("MAX_PRICE_USD", 100)
