# card_detection.py
import base64
import json
from shared_openai_client import get_openai_client


def detect_card_boxes(image_path):
    print(f"=== CARD DETECTION START: {image_path}")

    client = get_openai_client()

    # read image as base64
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = """
You are a JSON-only vision detector. 
Input is an image containing 1 or more Pokémon cards.

RETURN ONLY VALID JSON:
{
  "cards": [
    {"index": 1, "x": int, "y": int, "width": int, "height": int},
    ...
  ]
}
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

    # Extract text output
    output = response.output_text

    print("=== RAW DETECTION OUTPUT ===")
    print(output)

    # Parse JSON
    try:
        data = json.loads(output)
        return data.get("cards", [])
    except:
        print("JSON parse error — returning empty list")
        return []
