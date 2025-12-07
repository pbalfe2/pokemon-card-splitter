# price_lookup.py
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

def clean(text):
    if not text:
        return None
    return text.replace("\n", "").replace("\t", "").strip()

def lookup_tcgplayer(name, set_name):
    """Scrape minimal live prices from TCGplayer search."""
    query = f"{name} {set_name}".replace(" ", "+")
    url = f"https://www.tcgplayer.com/search/pokemon/product?q={query}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        price_block = soup.find("div", class_="inventory__price")
        if not price_block:
            return None

        low = price_block.find("span", {"data-price-type": "low"})
        market = price_block.find("span", {"data-price-type": "market"})

        return {
            "low": clean(low.text if low else None),
            "market": clean(market.text if market else None),
            "high": None
        }
    except Exception:
        return None


def lookup_cardmarket(name, set_name):
    """Scrape minimal Cardmarket pricing."""
    safe = name.replace(" ", "+")
    url = f"https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={safe}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        row = soup.find("div", class_="row no-gutters")
        if not row:
            return None

        low = row.find("div", class_="col-price")
        trend = row.find("div", class_="col-trend")

        return {
            "low": clean(low.text if low else None),
            "trend": clean(trend.text if trend else None)
        }
    except:
        return None


def lookup_prices(name, set_name):
    """Return both TCGPlayer and Cardmarket live prices."""
    return {
        "tcg": lookup_tcgplayer(name, set_name),
        "mk": lookup_cardmarket(name, set_name)
    }
