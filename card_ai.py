import base64
import json
from openai import OpenAI

client = OpenAI()

# ------------------------------------------------------------
# Helper: Load an image as base64 (for GPT-5 vision)
# ------------------------------------------------------------
def load_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ------------------------------------------------------------
# CARD IDENTIFICATION + CONDITION ANALYSIS
# ------------------------------------------------------------
def identify_and_grade_card(image_path):
    """
    Sends the cropped card image to GPT-5 for:
    - name
    - set
    - number
    - rarity
    - condition guess
    """

    b64 = load_image_base64(image_path)

    prompt = """
You are analyzing a Pokémon TCG card image.

Extract ONLY the following fields in JSON:
- name
- set
- number
- rarity
- condition (estimate Near Mint / Lightly Played / Moderately Played)

Respond in pure JSON only.
"""

    response = client.chat.completions.create(
        model="gpt-5o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64}"
                        }
                    }
                ]
            }
        ]
    )

    raw = response.choices[0].message.content.strip()

    # Validate JSON response
    try:
        return json.loads(raw)
    except:
        return {
            "name": "",
            "set": "",
            "number": "",
            "rarity": "",
            "condition": "Unknown"
        }


# ------------------------------------------------------------
# MULTI-SOURCE PRICING (North America only)
# ------------------------------------------------------------
def lookup_prices(name, set_name):
    """
    Uses GPT-5 web search to fetch:
    - TCGPlayer USD price
    - eBay sold USD average
    - USD→CAD conversion
    - Recommended CAD price
    Returns clean JSON for UI.
    """

    query = f"""
Find live North American market prices for this Pokémon TCG card:

Name: {name}
Set: {set_name}

Return strictly JSON with:
- tcgplayer_usd (market price)
- tcgplayer_url (search link)
- ebay_avg_usd (average sold price last 10–20 sales, US+Canada)
- ebay_url (completed sold items link)
- fx_rate (USD→CAD live conversion)
- recommended_cad (a fair selling price in CAD)

No text outside JSON.
"""

    response = client.responses.create(
        model="gpt-5.1",
        reasoning={"effort": "medium"},
        input=[{"role": "user", "content": query}],
        max_output_tokens=300
    )

    raw = response.output_text.strip()

    # Fallback safety
    try:
        data = json.loads(raw)
    except:
        return {
            "tcgplayer_usd": None,
            "tcgplayer_url": "",
            "ebay_avg_usd": None,
            "ebay_url": "",
            "fx_rate": 1.35,
            "recommended_cad": None
        }

    # Ensure all keys exist
    data.setdefault("tcgplayer_usd", None)
    data.setdefault("tcgplayer_url", "")
    data.setdefault("ebay_avg_usd", None)
    data.setdefault("ebay_url", "")
    data.setdefault("fx_rate", 1.35)

    # Compute recommended CAD price
    if data["tcgplayer_usd"] and data["ebay_avg_usd"]:
        avg_usd = (data["tcgplayer_usd"] + data["ebay_avg_usd"]) / 2
        data["recommended_cad"] = round(avg_usd * data["fx_rate"], 2)
    elif data["tcgplayer_usd"]:
        data["recommended_cad"] = round(data["tcgplayer_usd"] * data["fx_rate"], 2)
    elif data["ebay_avg_usd"]:
        data["recommended_cad"] = round(data["ebay_avg_usd"] * data["fx_rate"], 2)
    else:
        data["recommended_cad"] = None

    return data
