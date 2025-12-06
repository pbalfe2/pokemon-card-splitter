# price_lookup.py
import requests
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PokémonCardApp/1.0)"
}

def lookup_prices(card_name):
    safe = quote_plus(card_name)

    cm_url = f"https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={safe}"
    tcg_url = f"https://www.tcgplayer.com/search/pokemon/product?productName={safe}"

    results = {
        "cardmarket": cm_url,
        "tcgplayer": tcg_url
    }

    # Try to fetch CardMarket price (optional)
    try:
        r = requests.get(cm_url, headers=HEADERS, timeout=5)
        if "EUR" in r.text:
            results["cardmarket_price_guess"] = "See page — prices detected"
        else:
            results["cardmarket_price_guess"] = "No price detected"
    except:
        results["cardmarket_price_guess"] = "Unavailable"

    return results
