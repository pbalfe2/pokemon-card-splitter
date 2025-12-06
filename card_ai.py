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
    The following response was supposed to be JSON but isn't:

    {bad_text}

    Repair it and return ONLY valid JSON with keys:
    name, set, number, rarity, condition, price
    """
    resp = client.chat.completions.create(
        model="gpt-5.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return clean_json_output(resp.choices[0].message.content)

def identify_and_grade_card(image_path):
    """Identify + grade Pokémon card using GPT-5.1 multimodal."""

    # Convert image to base64
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Analyze this Pokémon card and return information in JSON only:

    {
      "name": "",
      "set": "",
      "number": "",
      "rarity": "",
      "condition": "",
      "price": 0
    }

    - "condition" must be NM, LP, MP, HP, or DMG
    - "price" must be a realistic Canadian market estimate
    """

    resp = client.chat.completions.create(
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

    raw = resp.choices[0].message.content
    print("==== RAW GPT-5.1 CARD AI OUTPUT ====")
    print(raw)

    cleaned = clean_json_output(raw)
    data = try_parse_json(cleaned)

    if data:
        return data

    print("WARNING: Card AI JSON invalid. Attempting repair…")

    repaired = repair_json_with_gpt(raw)
    repaired_json = try_parse_json(repaired)

    if repaired_json:
        return repaired_json

    print("ERROR: Returning fallback defaults.")

    return {
        "name": "Unknown Card",
        "set": "",
        "number": "",
        "rarity": "",
        "condition": "Unknown",
        "price": 0
    }
