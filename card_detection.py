import base64
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def try_parse_json(text):
    """Try to parse JSON. If invalid, return None."""
    try:
        return json.loads(text)
    except:
        return None

def repair_json_with_gpt(bad_text):
    """Ask GPT to repair malformed JSON."""
    prompt = f"""
    The following text was expected to be valid JSON but is not:

    {bad_text}

    Return ONLY valid JSON that best matches the intended structure.
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return resp.choices[0].message.content


def detect_card_boxes(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Detect all Pokémon cards in the image.

    Return ONLY JSON in this format:
    {
      "cards": [
        {"index":1, "x":0, "y":0, "width":0, "height":0}
      ]
    }
    """

    # ---- CALL GPT ----
    response = client.chat.completions.create(
        model="gpt-4o",
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

    output_text = response.choices[0].message.content or ""

    # Log raw output to Render logs
    print("==== RAW GPT OUTPUT (DETECTION) ====")
    print(output_text)

    # ---- TRY DIRECT PARSE ----
    data = try_parse_json(output_text)

    if data is not None:
        return data.get("cards", [])

    print("WARNING: JSON failed to parse. Attempting repair...")

    # ---- REPAIR JSON ----
    repaired = repair_json_with_gpt(output_text)
    print("==== REPAIRED JSON ATTEMPT ====")
    print(repaired)

    repaired_json = try_parse_json(repaired)

    if repaired_json is not None:
        return repaired_json.get("cards", [])

    print("ERROR: JSON could not be repaired. Returning empty list.")
    return []
