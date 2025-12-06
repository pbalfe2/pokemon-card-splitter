# card_ai.py
import base64
import json
from shared_openai_client import get_openai_client
from price_lookup import lookup_prices

def identify_and_grade_card(card_path):
    client = get_openai_client()

    with open(card_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-5-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": (
                         "Identify this Pokémon card, including set name, number, rarity, "
                         "and estimated grade (PSA-scale). "
                         "Respond ONLY with a JSON object:\n\n"
                         "{\n"
                         "  'name': string,\n"
                         "  'set': string,\n"
                         "  'number': string,\n"
                         "  'rarity': string,\n"
                         "  'estimated_grade': string\n"
                         "}\n\n"
                         "No extra text."
                     )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    raw_text = response.choices[0].message.content
    print("=== CARD AI ANALYSIS:", card_path)
    print(raw_text)

    try:
        card_info = json.loads(raw_text)
    except:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        card_info = json.loads(raw_text[start:end+1])

    # Add prices from Card Market / TCGPlayer
    prices = lookup_prices(card_info["name"])

    card_info["prices"] = prices
    return card_info
