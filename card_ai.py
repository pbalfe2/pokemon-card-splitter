import base64
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_json_output(text):
    if not text:
        return ""
    return (
        text.replace("```json", "")
            .replace("```", "")
            .strip()
    )

def try_parse_json(text):
    try:
        return json.loads(text)
    except:
        return None

def repair_json_with_gpt(bad_text):
    prompt = f"""
    The following output should be JSON but isn't:

    {bad_text}

    Fix it and return ONLY valid JSON with the structure:
    {{
      "cards": [
        {{"index":1, "x":0, "y":0, "width":0, "height":0}}
      ]
    }}
    """
    resp = client.chat.completions.create(
        model="gpt-5.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return clean_json_output(resp.choices[0].message.content)

def detect_card_boxes(image_path):
    """Use GPT-5.1 Vision to detect card bounding boxes."""
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Detect all Pokémon trading cards in the image.
    Return ONLY valid JSON with this structure:

    {
      "cards": [
        {"index":1, "x":0, "y":0, "width":0, "height":0}
      ]
    }

    Coordinates must reference exact pixel locations.
    """

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ]
    )

    raw = response.choices[0].message.content
    print("==== RAW GPT-5.1 DETECTION OUTPUT ====")
    print(raw)

    cleaned = clean_json_output(raw)
    data = try_parse_json(cleaned)
    if data:
        return data.get("cards", [])

    print("WARNING: Detection JSON invalid. Attempting repair...")

    repaired = repair_json_with_gpt(raw)
    repaired_data = try_parse_json(repaired)
    if repaired_data:
        return repaired_data.get("cards", [])

    print("ERROR: Unable to repair JSON. Returning empty list.")
    return []
