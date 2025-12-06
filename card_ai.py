# card_ai.py
import base64
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def identify_and_grade_card(card_path):
    img_b64 = encode_image(card_path)

    prompt = """
You are an expert in Pokémon card identification, rarity classification, and condition evaluation.

### REQUIRED OUTPUT FORMAT (JSON ONLY)
{
  "name": "...",
  "set": "...",
  "number": "...",
  "rarity": "...",
  "condition": "...",
  "price_ai_estimate": "..."
}

### RULES:
- Condition must be one of:
  "Near Mint", "Lightly Played", "Moderately Played", "Heavily Played", "Damaged"
- DO NOT use PSA grades or numbers.
- If unsure, assume “Near Mint” unless visible damage suggests otherwise.
- Estimate a realistic market price (CAD) based on recent sales.
- Keep JSON valid and do not include commentary.
"""

    response = client.chat.completions.create(
        model="gpt-5.1",  # confirmed working model on your system
        messages=[
            {"role": "system", "content": "You are a Pokémon TCG card expert."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ],
            },
        ],
        temperature=0
    )

    try:
        result = response.choices[0].message.content.strip()
        print("=== CARD AI RAW OUTPUT ===")
        print(result)
        data = eval(result) if result.startswith("{") else {}
    except Exception as e:
        print("AI JSON parse error:", e)
        data = {}

    # Fail-safe defaults so the app never breaks
    return {
        "name": data.get("name", "Unknown Card"),
        "set": data.get("set", "Unknown Set"),
        "number": data.get("number", "?"),
        "rarity": data.get("rarity", "Unknown"),
        "condition": data.get("condition", "Near Mint"),
        "price_ai_estimate": data.get("price_ai_estimate", "0")
    }
