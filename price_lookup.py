# price_lookup.py
import requests
import urllib.parse

def lookup_prices(card_name, set_name):
    safe = urllib.parse.quote_plus(f"{card_name} {set_name}")

    # TCGplayer search (unofficial GET scraping)
    tcg_url = f"https://api.tcgplayer.com/catalog/products?productName={safe}"
    # Cardmarket price guide (HTML parse)
    mk_url = f"https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={safe}"

    prices = {
        "tcgplayer": None,
        "cardmarket": None,
        "best_price": None
    }

    # -------- TCGPLAYER (scrape low/market/high) ----------
    try:
        r = requests.get(tcg_url, timeout=8)
        data = r.json()

        if "results" in data and len(data["results"]) > 0:
            # First matching product
            p = data["results"][0]

            prices["tcgplayer"] = {
                "low": p.get("lowPrice", None),
                "market": p.get("marketPrice", None),
                "high": p.get("highPrice", None)
            }
    except:
        pass

    # -------- CARDMARKET (scrape price guide) ----------
    try:
        r = requests.get(mk_url, timeout=8)
        html = r.text

        low = extract_between(html, 'product-cell-price', '</')
        trend = extract_between(html, 'product-cell-trend', '</')

        prices["cardmarket"] = {
            "low": clean_price(low),
            "trend": clean_price(trend)
        }
    except:
        pass

    # -------- BEST PRICE DECISION ----------
    candidates = []

    if prices["tcgplayer"]:
        for v in prices["tcgplayer"].values():
            if v is not None:
                candidates.append(float(v) * 1.35)  # USD→CAD approx

    if prices["cardmarket"]:
        for v in prices["cardmarket"].values():
            if v is not None:
                candidates.append(float(v) * 1.48)  # EUR→CAD approx

    prices["best_price"] = round(min(candidates), 2) if candidates else None

    return prices


def extract_between(text, start, end):
    """Simple inline HTML substring extraction."""
    try:
        idx = text.find(start)
        if idx == -1:
            return None
        idx += len(start)
        sub = text[idx:]
        end_idx = sub.find(end)
        return sub[:end_idx].strip()
    except:
        return None


def clean_price(val):
    if not val:
        return None
    val = val.replace("€", "").replace("$", "").replace(",", ".").strip()
    try:
        return float(val)
    except:
        return None
