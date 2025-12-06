import base64
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def identify_and_grade_card(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Identify and grade this Pokémon card.
    Return ONLY JSON with fields:
    {
      "name": "",
      "set": "",
      "number": "",
      "rarity": "",
      "condition": "",
      "notes": ""
    }
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": prompt },
                    {
                        "type": "input_image",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ]
    )

    output_text = response.choices[0].message.content
    return json.loads(output_text)
