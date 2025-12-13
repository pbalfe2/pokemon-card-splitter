import base64
import json
from openai import OpenAI
client = OpenAI()

def identify_and_grade_card(image_path):

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Identify this Pokémon card with the following fields:

    {
      "name": "",
      "set": "",
      "number": "",
      "rarity": "",
      "condition": "Near Mint",
      "price_ai_estimate": "value in CAD"
    }

    Condition must be TCG-style (Near Mint, Lightly Played, Moderately Played).
    Do not use PSA grades.
    """

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",
             "content": [
                 {"type": "input_text", "text": "Identify this card."},
                 {"type": "input_image",
                  "image_url": {"url": f"data:image/png;base64,{b64}"}
                 }
             ]}
        ]
    )

    try:
        return json.loads(resp.choices[0].message.content)
    except:
        return {
            "name": "Unknown",
            "set": "Unknown",
            "number": "",
            "rarity": "",
            "condition": "Near Mint",
            "price_ai_estimate": "N/A"
        }
