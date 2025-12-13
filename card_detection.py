import base64
import os
from openai import OpenAI
client = OpenAI()

def detect_card_boxes(image_path):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Detect all Pokémon card rectangles in the image.
    Return a JSON object: {"cards":[{ "index":0,"x":int,"y":int,"width":int,"height":int }]}
    """

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",
             "content": [
                 {"type": "input_text", "text": "Find cards."},
                 {
                     "type": "input_image",
                     "image_url": {
                         "url": f"data:image/png;base64,{b64}"
                     }
                 }
             ]}
        ]
    )

    try:
        import json
        return json.loads(resp.choices[0].message.content)
    except:
        return {"cards": []}
