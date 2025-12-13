import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean(t):
    if not t: return None
    return t.replace("\n","").replace("\t","").strip()


def lookup_tcgplayer(name, set_name):
    q = (name + " " + set_name).replace(" ", "+")
    url = f"https://www.tcgplayer.com/search/pokemon/product?q={q}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        block = soup.find("div", class_="inventory__price")
        if not block:
            return None

        low = block.find("span", {"data-price-type":"low"})
        market = block.find("span", {"data-price-type":"market"})

        return {
            "low": clean(low.text if low else None),
            "market": clean(market.text if market else None)
        }
    except:
        return None


def lookup_cardmarket(name, set_name):
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


def convert_currency(usd, eur):
    url = "https://api.exchangerate.host/latest?base=USD"
    try:
        r = requests.get(url, timeout=5).json()
        usd_to_cad = r["rates"]["CAD"]
        usd_to_eur = r["rates"]["EUR"]

        cad = None
        eur_val = None

        if usd:
            usd_num = float(usd.replace("$","").strip())
            cad = round(usd_num * usd_to_cad, 2)
            eur_val = round(usd_num * usd_to_eur, 2)

        return {"cad": cad, "eur": eur_val, "usd": usd}
    except:
        return {"cad": None, "eur": None, "usd": usd}


def lookup_prices(name, set_name):
    tcg = lookup_tcgplayer(name, set_name)
    mk = lookup_cardmarket(name, set_name)

    # pick a value for conversion
    usd_val = None
    if tcg and tcg.get("market"):
        usd_val = tcg["market"].replace("$","")

    converted = convert_currency(usd_val, None)

    return {"tcg": tcg, "mk": mk, "converted": converted}
