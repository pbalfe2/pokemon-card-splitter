import base64
import json
from openai import OpenAI

# --------------------------------------------------------------------
# SAFE CLIENT CREATION (Fixes Render crash)
# --------------------------------------------------------------------
def get_client():
    return OpenAI()


# --------------------------------------------------------------------
# Convert an image file to base64
# --------------------------------------------------------------------
def load_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# --------------------------------------------------------------------
# FIX: Robust JSON extraction from GPT output
# --------------------------------------------------------------------
def extract_json(text):
    """Extract JSON from GPT output safely."""
    try:
        return json.loads(text)
    except:
        pass

    # Try extracting inside code fences
    if "```" in text:
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("{") and p.endswith("}"):
                try:
                    return json.loads(p)
                except:
                    pass

    print("ERROR: Unable to parse JSON. Returning empty list.")
    return {"cards": []}


# --------------------------------------------------------------------
# Main function: Detect card bounding boxes
# --------------------------------------------------------------------
def detect_card_boxes(image_path):
    print("\n=== Running CARD DETECTION on:", image_path)

    client = get_client()
    img_b64 = load_image_base64(image_path)

    # ----------------------------------------
    # GPT-4o Vision Detection Request
    # ----------------------------------------
    response = client.responses.create(
        model="gpt-4o",  # BEST model for image understanding
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text":
                            "You are a Pokémon card cropping assistant. "
                            "Detect each card in the image and output ONLY valid JSON in this structure:\n\n"
                            "{\n"
                            "  \"cards\": [\n"
                            "    {\"index\": 1, \"x\": 0, \"y\": 0, \"width\": 100, \"height\": 150},\n"
                            "    ...\n"
                            "  ]\n"
                            "}\n\n"
                            "Coordinates must be pixel values relative to the image."
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{img_b64}"
                    }
                ]
            }
        ]
    )

    # GPT Output
    output_text = response.output_text
    print("\n==== RAW GPT OUTPUT (DETECTION) ====\n", output_text, "\n")

    data = extract_json(output_text)

    cards = data.get("cards", [])

    print("Detected", len(cards), "cards.")
    return cards
