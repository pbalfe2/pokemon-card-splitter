import statistics
import requests
from backend.config import EBAY_OAUTH_TOKEN


def price_card(identity: dict, condition: str):
    """
    identity = {
        name, set, number, rarity, holo
    }
    """

    headers = {
        "Authorization": f"Bearer {EBAY_OAUTH_TOKEN}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }

    # Build a clean search query
    query_parts = [
        identity.get("name", ""),
        identity.get("set", ""),
        identity.get("number", "")
    ]

    query = " ".join(p for p in query_parts if p)

    params = {
        "q": query,
        "filter": "soldItemsOnly:true",
        "limit": 25
    }

    response = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers=headers,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        return {
            "estimated_price": None,
            "confidence": "low",
            "error": "eBay API error"
        }

    data = response.json()
    items = data.get("itemSummaries", [])

    prices = []

    for item in items:
        price = item.get("price", {})
        value = price.get("value")

        if value:
            try:
                prices.append(float(value))
            except ValueError:
                pass

    if not prices:
        return {
            "estimated_price": None,
            "confidence": "low",
            "error": "No sold listings found"
        }

    median_price = round(statistics.median(prices), 2)

    confidence = (
        "high" if len(prices) >= 10
        else "medium" if len(prices) >= 5
        else "low"
    )

    return {
        "estimated_price": median_price,
        "confidence": confidence,
        "samples": len(prices)
    }
