import requests
from backend.config import EBAY_OAUTH_TOKEN

async def price_card(identity, condition):
    headers = {
        "Authorization": f"Bearer {EBAY_OAUTH_TOKEN}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }

    requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers=headers,
        params={"q": f"{identity} {condition}", "filter": "soldItemsOnly:true"}
    )

    return {
        "estimated_price": 100.0,
        "confidence": "medium"
    }
