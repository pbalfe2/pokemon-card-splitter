import base64
import json
from openai import OpenAI

# -----------------------------------------------------------
# PROXY-SAFE OpenAI client creation
# -----------------------------------------------------------
def get_client():
    return OpenAI()  # no global client


def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass

    if "```" in text:
        for block in text.split("```"):
            block = block.strip()
            if block.startswith("{") and block.endswith("}"):
                try:
                    return json.loads(block)
                except:
                    pass

    print("WARNING: Detection JSON invalid — returning empty.")
    return {"cards": []}


def detect_card_boxes(image_path):
    print(f"=== Running CARD DETECTION on: {image_path}")

    client = get_client()
    img_b64 = load_image_b64(image_path)

    response = client.responses.create(
        model="gpt-5.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text":
                            "Detect all Pokémon card bounding boxes. "
                            "Return only JSON: {cards:[{index,x,y,width,height}...]}"
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{img_b64}"
                    }
                ]
            }
        ]
    )

    raw = response.output_text
    print("\n=== RAW GPT OUTPUT (DETECTION) ===\n", raw, "\n")

    data = extract_json(raw)
    return data.get("cards", [])
