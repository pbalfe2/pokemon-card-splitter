import base64
import json
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_card_boxes(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Detect all Pokémon cards in the image.
    Return ONLY JSON:
    {
      "cards": [
        {"index": 1, "x":..., "y":..., "width":..., "height":...}
      ]
    }
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"type": "text", "text": prompt},
            {"type": "input_image", "image_url": f"data:image/png;base64,{img_b64}"}
        ]
    )

    data = json.loads(response.output_text)
    return data["cards"]
