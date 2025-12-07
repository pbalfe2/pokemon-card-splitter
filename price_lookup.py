# price_lookup.py

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}


# -------------------------------
# Utility cleaner
# -------------------------------
def clean(text):
    if not text:
        return None
    return text.replace("\n", "").replace("\t", "").strip()


# -------------------------------
# Get live exchange rates (USD & EUR → CAD)
# -------------------------------
def get_fx_rates():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        data = requests.get(url, timeout=10).json()

        usd_to_cad = data["rates"].get("CAD", 1)
        eur_to_cad = data["rates"].get("CAD", 1) / data["rates"].get("EUR", 1)

        return {
            "usd_to_cad": usd_to_cad,
            "eur_to_cad": eur_to_cad
        }
    except:
        return {
            "usd_to_cad": 1.34,
            "eur_to_cad": 1.47
        }


# -------------------------------
# TCGplayer Scraper (USD)
# -------------------------------
def lookup_tcgplayer(name, set_name):
    query = f"{name} {set_name}".replace(" ", "+")
    url = f"https://www.tcgplayer.com/search/pokemon/product?q={query}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Newer layout price block
        price_block = soup.find("div", class_="inventory__price")
        if price_block:
            low = price_block.find("span", {"data-price-type": "low"})
            market = price_block.find("span", {"data-price-type": "market"})
            high = price_block.find("span", {"data-price-type": "high"})

            return {
                "usd_low": clean(low.text if low else None),
                "usd_market": clean(market.text if market else None),
                "usd_high": clean(high.text if high else None),
            }

        # Fallback layout (older design)
        price_alt = soup.find("span", class_="price-point__data")
        if price_alt:
            return {
                "usd_low": None,
                "usd_market": clean(price_alt.text),
                "usd_high": None,
            }

        return None

    except Exception:
        return None


# -------------------------------
# Cardmarket Scraper (EUR)
# -------------------------------
def lookup_cardmarket(name, set_name):
    safe = name.replace(" ", "+")
    url = f"https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={safe}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # First result row
        row = soup.find("div", class_="row no-gutters")
        if not row:
            return None

        low = row.find("div", class_="col-price")
        trend = row.find("div", class_="col-trend")

        return {
            "eur_low": clean(low.text if low else None),
            "eur_trend": clean(trend.text if trend else None)
        }

    except:
        return None


# -------------------------------
# Unified Price Lookup
# Converts only:
#   • USD Market → CAD
#   • EUR Trend  → CAD
# -------------------------------
def lookup_prices(name, set_name):
    tcg = lookup_tcgplayer(name, set_name)
    mk = lookup_cardmarket(name, set_name)
    fx = get_fx_rates()

    usd_to_cad = fx["usd_to_cad"]
    eur_to_cad = fx["eur_to_cad"]

    tcg_cad = None
    mk_cad = None

    # Convert USD → CAD (market only)
    if tcg and tcg.get("usd_market"):
        try:
            value = float(tcg["usd_market"].replace("$", ""))
            tcg_cad = round(value * usd_to_cad, 2)
        except:
            pass

    # Convert EUR → CAD (trend only)
    if mk and mk.get("eur_trend"):
        try:
            v = mk["eur_trend"]
            v = v.replace("€", "").replace(",", ".")
            value = float(v)
            mk_cad = round(value * eur_to_cad, 2)
        except:
            pass

    return {
        "tcg": tcg,
        "mk": mk,
        "fx": fx,
        "tcg_cad": tcg_cad,
        "mk_cad": mk_cad
    }
