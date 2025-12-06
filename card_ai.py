import base64
import json
import requests
from openai import OpenAI

# -----------------------------------------------------------
# FIX for Render crash:
# Create client ONLY inside functions, never globally
# -----------------------------------------------------------
def get_client():
    return OpenAI()


# Convert image file to base64 for GPT vision
def load_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# Extract valid JSON from GPT output
def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass

    if "```" in text:
        for block in text.split("```"):
            block = block.strip()
            if block.startswith("{") and block.endswith("}"):
                try:
                    return json.loads(block)
                except:
                    pass

    print("WARNING: Could not parse GPT JSON → using fallback.")
    return {}


# -------------------------------------------------------------------
# Identify card name, set, number, rarity, AND estimated condition.
# -------------------------------------------------------------------
def identify_and_grade_card(image_path):
    print("\n=== Running Card AI for:", image_path)

    client = get_client()
    img_b64 = load_image_base64(image_path)

    response = client.responses.create(
        model="gpt-5.1",   # best for structured JSON
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text":
                            "Identify this Pokémon card. Return ONLY valid JSON:\n"
                            "{\n"
                            "  \"name\": \"...\",\n"
                            "  \"set\": \"...\",\n"
                            "  \"number\": \"...\",\n"
                            "  \"rarity\": \"...\",\n"
                            "  \"condition\": \"Near Mint / LP / MP / HP / DMG\"\n"
                            "}\n"
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{img_b64}"
                    }
                ]
            }
        ]
    )

    output_text = response.output_text
    print("\n=== RAW GPT OUTPUT (CARD AI) ===\n", output_text, "\n")

    return extract_json(output_text)


# -------------------------------------------------------------------
# PRICE LOOKUP – returns multiple sources (CAD)
# -------------------------------------------------------------------
def lookup_prices(card_name, card_set):
    print(f"\n=== Fetching prices for {card_name} ({card_set}) ===")

    results = {
        "name": card_name,
        "set": card_set,
        "prices": []
    }

    # ---------------------------  
    # 1. TCGPlayer (USD but we'll convert)
    # ---------------------------
    try:
        tcg_api_url = (
            "https://api.tcgplayer.com/catalog/products?"
            f"productName={card_name}&setName={card_set}"
        )
        r = requests.get(tcg_api_url, timeout=5)
        if r.status_code == 200:
            usd_price = 5.00  # placeholder unless API returns it
            cad_price = round(usd_price * 1.35, 2)

            results["prices"].append({
                "market": "TCGPlayer",
                "currency": "CAD",
                "price": cad_price,
                "url": "https://www.tcgplayer.com"
            })
    except Exception as e:
        print("TCG lookup failed:", e)

    # ---------------------------  
    # 2. CardTrader (EUR → CAD)
    # ---------------------------
    try:
        eur_price = 3.0  # placeholder
        cad_price = round(eur_price * 1.48, 2)
        results["prices"].append({
            "market": "CardTrader",
            "currency": "CAD",
            "price": cad_price,
            "url": "https://www.cardtrader.com"
        })
    except Exception as e:
        print("CardTrader lookup failed:", e)

    # ---------------------------  
    # 3. PriceCharting (USD → CAD)
    # ---------------------------
    try:
        usd_price = 4.2
        cad_price = round(usd_price * 1.35, 2)
        results["prices"].append({
            "market": "PriceCharting",
            "currency": "CAD",
            "price": cad_price,
            "url": f"https://www.pricecharting.com/search-products?q={card_name}"
        })
    except Exception as e:
        print("PriceCharting lookup failed:", e)

    return results
