import requests
from bs4 import BeautifulSoup
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


# -------------------------------
# TCGPLAYER SCRAPER
# -------------------------------
def scrape_tcgplayer(name, set_name):
    try:
        query = urllib.parse.quote(f"{name} {set_name}")
        url = f"https://www.tcgplayer.com/search/pokemon/product?q={query}"

        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # Find price fields on search result tiles
        market = soup.select_one(".price-point__market .price-point__value")
        low = soup.select_one(".price-point__low .price-point__value")
        high = soup.select_one(".price-point__high .price-point__value")

        def clean(x):
            if not x:
                return None
            return float(x.text.replace("$", "").replace(",", "").strip())

        return {
            "market": clean(market),
            "low": clean(low),
            "high": clean(high),
        }

    except Exception as e:
        print("TCGPLAYER ERROR:", e)
        return None


# -------------------------------
# CARDMARKET SCRAPER
# -------------------------------
def scrape_cardmarket(name, set_name):
    try:
        query = urllib.parse.quote(f"{name} {set_name}")
        url = f"https://www.cardmarket.com/en/Pokemon/Products/Search?searchString={query}"

        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # Prices on Cardmarket search page
        low_el = soup.select_one(".price-container .col-6:nth-of-type(1)")
        trend_el = soup.select_one(".price-container .col-6:nth-of-type(2)")

        def extract_price(tag):
            if not tag:
                return None
            text = tag.get_text().replace("€", "").replace(",", ".").strip()
            try:
                return float(text)
            except:
                return None

        return {
            "low": extract_price(low_el),
            "trend": extract_price(trend_el),
        }

    except Exception as e:
        print("CARDMARKET ERROR:", e)
        return None


# -------------------------------
# MAIN WRAPPER FUNCTION
# -------------------------------
def lookup_prices(name, set_name):
    tcg = scrape_tcgplayer(name, set_name)
    mk = scrape_cardmarket(name, set_name)

    return {
        "tcg": tcg,
        "mk": mk
    }


if __name__ == "__main__":
    # Quick test
    print(lookup_prices("Charizard", "Base Set"))
