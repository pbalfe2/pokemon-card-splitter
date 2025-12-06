import base64
import json
import os
from openai import OpenAI
from shared_openai_client import get_openai_client


def detect_card_boxes(image_path: str):
    """
    Sends the uploaded image to GPT-4.1/GPT-5 vision model to detect Pokémon card bounding boxes.
    Returns a list of dicts: {index, x, y, width, height}
    """

    print(f"=== CARD DETECTION START: {image_path}")

    client = get_openai_client()

    # Read image as base64
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    prompt_text = """
You are a Pokémon trading card image detector.

Your job:
- Analyze the scanned image.
- Detect all Pokémon cards present.
- Return JSON ONLY with this structure:

{
  "cards": [
    {"index": 1, "x": 0, "y": 0, "width": 200, "height": 300},
    ...
  ]
}

Rules:
- DO NOT include explanations.
- DO NOT output ```json blocks.
- Only raw JSON.
    """

    # Use the *new* Responses API (OpenAI >= 1.61.1)
    response = client.responses.create(
        model="gpt-4.1",  # can be updated to gpt-5-vision when available
        input=[
            {"role": "system", "content": prompt_text},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this Pokémon card sheet image."},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{b64_image}"
                    }
                ]
            }
        ]
    )

    raw_output = response.output_text
    print("=== RAW GPT DETECTION OUTPUT ===")
    print(raw_output)

    try:
        data = json.loads(raw_output)
        return data.get("cards", [])
    except Exception as e:
        print("JSON PARSE ERROR:", e)
        return []
