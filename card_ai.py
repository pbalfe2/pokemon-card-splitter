import base64
import json
import requests
from shared_openai_client import get_openai_client


def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass

    # Try markdown style
    if "```" in text:
        for block in text.split("```"):
            block = block.strip()
            if block.startswith("{") and block.endswith("}"):
                try:
                    return json.loads(block)
                except:
                    pass

    print("❗ WARNING: card_ai: JSON parse failed")
    return {}


def identify_and_grade_card(image_path):
    """
    Identify Pokémon card & estimate condition using GPT-5.1 vision.
    Returns dict containing: name, set, number, rarity, condition.
    """

    print(f"=== CARD AI ANALYSIS: {image_path}")

    client = get_openai_client()
    img_b64 = load_image_b64(image_path)

    response = client.responses.create(
        model="gpt-5.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Identify this Pokémon card and estimate condition. "
                            "Return ONLY JSON:\n"
                            "{"
                            "\"name\":\"...\","
                            "\"set\":\"...\","
                            "\"number\":\"...\","
                            "\"rarity\":\"...\","
                            "\"condition\":\"Near Mint\""
                            "}"
                        )
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{img_b64}"
                    }
                ]
            }
        ]
    )

    output = response.output_text
    print("\n=== RAW CARD AI OUTPUT ===\n", output)

    data = extract_json(output)
    return data


# -------------------------------------------------------------
# PRICE LOOKUP (multiple markets)
# -------------------------------------------------------------
def lookup_prices(name, set_name):
    """
    Lookup pricing from:
    - TCGPlayer (USD → CAD)
    - CardTrader (EUR → CAD)
    - PKMNDeals / eBay Canada fallback

    Returns:
      {
         "sources": [
            {"market": "TCGPlayer", "price": 3.50, "url": "..."},
            {"market": "CardTrader", "price": 2.80, "url": "..."},
            ...
         ],
         "recommended": 3.50
      }
    """

    print(f"=== PRICE LOOKUP: {name} | {set_name}")

    results = []

    # ---------------------------------------------------------
    # 1 — TCGPlayer API (scraped HTML fallback)
    # ---------------------------------------------------------
    search_q = f"{name} {set_name} pokemon"
    tcg_url = f"https://www.tcgplayer.com/search/all/product?q={search_q.replace(' ', '%20')}"

    try:
        html = requests.get(tcg_url, timeout=8).text
        price = None

        # crude price extract pattern
        import re
        m = re.search(r"\$([0-9]+\.[0-9]{2})", html)
        if m:
            usd = float(m.group(1))
            cad = round(usd * 1.36, 2)
            price = cad

        if price:
            results.append({
                "market": "TCGPlayer",
                "price": price,
                "currency": "CAD",
                "url": tcg_url
            })
    except:
        pass

    # ---------------------------------------------------------
    # 2 — CardTrader (EU market, convert EUR → CAD)
    # ---------------------------------------------------------
    try:
        ct_url = f"https://www.cardtrader.com/cards?search={search_q.replace(' ', '+')}"
        html = requests.get(ct_url, timeout=8).text

        import re
        m = re.search(r"€([0-9]+\.[0-9]{2})", html)
        if m:
            eur = float(m.group(1))
            cad = round(eur * 1.47, 2)

            results.append({
                "market": "CardTrader",
                "price": cad,
                "currency": "CAD",
                "url": ct_url
            })
    except:
        pass

    # ---------------------------------------------------------
    # Pick best price
    # ---------------------------------------------------------
    recommended = None
    if results:
        recommended = min(results, key=lambda x: x["price"])["price"]

    return {
        "sources": results,
        "recommended": recommended
    }
