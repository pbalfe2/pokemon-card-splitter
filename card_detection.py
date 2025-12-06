import base64
import json
from shared_openai_client import get_openai_client


def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_json(text):
    """Safely extract JSON from AI output."""
    try:
        return json.loads(text)
    except:
        pass

    # Attempt to fix markdown-wrapped JSON
    if "```" in text:
        for block in text.split("```"):
            block = block.strip()
            if block.startswith("{") and block.endswith("}"):
                try:
                    return json.loads(block)
                except:
                    pass

    print("❗ WARNING: Could not extract valid JSON from model.")
    return {"cards": []}


def detect_card_boxes(image_path):
    """
    Uses GPT-5.1 vision to detect all Pokémon card bounding boxes.
    Returns list of {index,x,y,width,height}.
    """

    print(f"=== CARD DETECTION START: {image_path}")

    client = get_openai_client()
    b64 = load_image_b64(image_path)

    response = client.responses.create(
        model="gpt-5.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image and find all Pokémon card bounding boxes. "
                            "Return ONLY JSON in this format:\n"
                            "{\"cards\":[{\"index\":1,\"x\":0,\"y\":0,\"width\":100,\"height\":150}, ...]}"
                        )
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{b64}"
                    }
                ]
            }
        ]
    )

    output = response.output_text
    print("\n=== RAW MODEL OUTPUT (BOXES) ===\n", output)

    parsed = extract_json(output)
    return parsed.get("cards", [])
