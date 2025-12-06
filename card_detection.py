import base64
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_card_boxes(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Detect all Pokémon cards in the image.
    Return ONLY JSON:
    {
      "cards": [
        {"index":1, "x":0, "y":0, "width":0, "height":0}
      ]
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
    data = json.loads(output_text)
    return data["cards"]
