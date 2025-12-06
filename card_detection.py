# card_detection.py
import base64
import json
from shared_openai_client import get_openai_client

def detect_card_boxes(image_path):
    client = get_openai_client()

    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    print("=== CARD DETECTION START:", image_path)

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {
                "role": "user",
                "content": [
                    { "type": "text",
                      "text": (
                          "Analyze the image and return ONLY JSON:\n"
                          "{ 'cards': [ { 'index': n, 'x': int, 'y': int, 'width': int, 'height': int } ] }"
                      )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    raw_text = response.choices[0].message.content
    print("=== RAW DETECTION OUTPUT ===\n", raw_text)

    try:
        return json.loads(raw_text)
    except:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        return json.loads(raw_text[start:end+1])
