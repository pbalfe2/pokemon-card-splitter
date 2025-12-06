# price_lookup.py
import requests

USD_TO_CAD = 1.36
EUR_TO_CAD = 1.48


def lookup_prices(name, set_name):
    safe = f"{name} {set_name}".replace(" ", "%20")

    results = []

    # ------------------------------
    # 1) TCGPlayer (unofficial quick search)
    # ------------------------------
    tcg_url = f"https://www.tcgplayer.com/search/pokemon/product?productName={safe}"
    results.append({
        "source": "TCGPlayer",
        "url": tcg_url,
        "currency": "CAD",
        "price": round(15 * USD_TO_CAD, 2)  # mock price (API key needed for real value)
    })

    # ------------------------------
    # 2) CardMarket
    # ------------------------------
    mk_url = fhttps://www.cardmarket.com/en/Pokemon/Products/Search?searchString={safe}"
    results.append({
        "source": "CardMarket",
        "url": mk_url,
        "currency": "CAD",
        "price": round(10 * EUR_TO_CAD, 2)
    })

    # ------------------------------
    # 3) PriceCharting
    # ------------------------------
    pc_url = f"https://www.pricecharting.com/search-products?type=prices&q={safe}"
    results.append({
        "source": "PriceCharting",
        "url": pc_url,
        "currency": "CAD",
        "price": round(12 * USD_TO_CAD, 2)
    })

    return results
