import base64
import json
import os
from openai import OpenAI
from shared_openai_client import get_openai_client


def detect_card_boxes(image_path: str):
    """
    Uses GPT-4.1 (or GPT-4o) to detect Pokémon card bounding boxes.
    Compatible with ALL OpenAI Python SDK versions currently used by Render.
    """

    print(f"=== CARD DETECTION START: {image_path}")

    client = get_openai_client()

    # Load image into base64
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode()

    system_prompt = """
You are a Pokémon card detector.
Return ONLY JSON structured like:

{
  "cards": [
    {"index": 1, "x": 0, "y": 0, "width": 200, "height": 300}
  ]
}

Rules:
- JSON only.
- No explanations or markdown.
"""

    # FIX: Correct Chat Completions Vision schema
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Detect Pokémon card bounding boxes."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image}"
                        }
                    },
                ],
            },
        ],
        temperature=0,
    )

    raw_output = response.choices[0].message.content.strip()
    print("=== RAW DETECTION OUTPUT ===")
    print(raw_output)

    # Attempt to parse JSON
    try:
        return json.loads(raw_output).get("cards", [])
    except Exception as e:
        print("JSON PARSE ERROR:", e)
        return []
