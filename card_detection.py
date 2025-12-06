# card_detection.py
import base64
import json
from shared_openai_client import get_openai_client

def detect_card_boxes(image_path):
    client = get_openai_client()

    # Load & encode image
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    print("=== CARD DETECTION START:", image_path)

    # GPT-5-preview multimodal call
    response = client.chat.completions.create(
        model="gpt-5-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", 
                     "text": (
                         "You are a card detector. Analyze the image and output ONLY a JSON object "
                         "with an array called 'cards'. Each card must have: index, x, y, width, height. "
                         "Coordinates must be integers. No explanations."
                     )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ],
            }
        ],
        temperature=0
    )

    raw_text = response.choices[0].message.content

    print("=== RAW DETECTION OUTPUT ===")
    print(raw_text)

    # Force JSON parsing safely
    try:
        return json.loads(raw_text)
    except Exception:
        # Try to extract JSON if surrounded by text
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw_text[start:end+1])
        raise ValueError("GPT did not return valid JSON.")
