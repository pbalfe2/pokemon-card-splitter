# card_ai.py
import base64
import json
from shared_openai_client import get_openai_client


def identify_and_grade_card(image_path):
    print(f"=== CARD AI ANALYSIS: {image_path}")

    client = get_openai_client()

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = """
You are a Pokémon TCG card identifier.  
Return ONLY valid JSON in this format:

{
  "name": "...",
  "set": "...",
  "number": "...",
  "rarity": "...",
  "condition": "Near Mint",
  "price_ai_estimate": float
}

NO extra text.
"""

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_base64": b64}
                ]
            }
        ]
    )

    output = response.output_text

    try:
        return json.loads(output)
    except:
        print("AI JSON failed. Returning fallback.")
        return {
            "name": "Unknown",
            "set": "Unknown",
            "number": "?",
            "rarity": "?",
            "condition": "Unknown",
            "price_ai_estimate": 0.0
        }
