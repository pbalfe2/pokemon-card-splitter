import json
import base64
from openai import OpenAI

client = OpenAI()


def load_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ------------------------------------------------------------
# DETECT CARD POSITIONS USING GPT-5 VISION
# ------------------------------------------------------------
def detect_card_boxes(image_path):
    """
    Uses GPT-5 to detect Pokémon card boundaries.
    Returns list of boxes: [{x, y, width, height}, ...]
    """

    b64 = load_image_base64(image_path)

    prompt = """
You are processing an image containing Pokémon cards arranged on a grid.

Your job: Detect EACH card and return a JSON array of rectangles.

Important rules:
- Return ONLY JSON.
- No comments, no explanations.
- Each card must be an object:
  { "x": INT, "y": INT, "width": INT, "height": INT }
- Ensure coordinates are integers.
- Ensure cropping does not cut off the card edges.
"""

    # CALL GPT-5 vision
    response = client.chat.completions.create(
        model="gpt-5o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64}"
                        }
                    }
                ]
            }
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    print("==== RAW GPT OUTPUT (DETECTION) ====")
    print(raw_output)

    # ------------------------------------------------------------
    # 1. Try to parse JSON directly
    # ------------------------------------------------------------
    try:
        boxes = json.loads(raw_output)
        if isinstance(boxes, dict) and "cards" in boxes:
            return boxes["cards"]
        if isinstance(boxes, list):
            return boxes
    except:
        print("WARNING: JSON failed to parse. Attempting repair...")

    # ------------------------------------------------------------
    # 2. Attempt JSON recovery (extract substring between {...})
    # ------------------------------------------------------------
    try:
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        cleaned = raw_output[start:end]

        print("==== REPAIRED JSON ATTEMPT ====")
        print(cleaned)

        boxes = json.loads(cleaned)

        if isinstance(boxes, dict) and "cards" in boxes:
            return boxes["cards"]
        if isinstance(boxes, list):
            return boxes

    except Exception as e:
        print("ERROR: JSON could not be repaired. Returning empty list.")
        print(e)

    # ------------------------------------------------------------
    # Fallback empty list
    # ------------------------------------------------------------
    return []
