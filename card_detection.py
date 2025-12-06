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
    Return JSON ONLY:
    {
        "cards": [
          {"index":1, "x":0, "y":0, "width":0, "height":0}
        ]
    }
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "type": "message",
                "content": prompt
            },
            {
                "role": "user",
                "type": "input_image",
                "image_url": f"data:image/png;base64,{img_b64}"
            }
        ]
    )

    data = json.loads(response.output_text)
    return data["cards"]
