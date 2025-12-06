import base64
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_json_output(text):
    """Remove Markdown ```json fences and extract pure JSON."""
    if text is None:
        return ""

    # Remove code fences
    text = text.replace("```json", "")
    text = text.replace("```", "")

    # Strip whitespace
    return text.strip()

def try_parse_json(text):
    try:
        return json.loads(text)
    except:
        return None

def repair_json_with_gpt(bad_text):
    prompt = f"""
    The following text was meant to be valid JSON but is not:

    {bad_text}

    Return ONLY valid JSON. No explanations.
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    cleaned = clean_json_output(resp.choices[0].message.content)
    return cleaned

def detect_card_boxes(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Detect all Pokémon cards in the image.
    Return ONLY valid JSON in this exact structure:

    {
      "cards": [
        {"index":1, "x":0, "y":0, "width":0, "height":0}
      ]
    }
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                ]
            }
        ]
    )

    output_text = response.choices[0].message.content
    print("==== RAW GPT OUTPUT (DETECTION) ====")
    print(output_text)

    # Clean markdown fences
    cleaned = clean_json_output(output_text)

    # Try parsing cleaned JSON
    data = try_parse_json(cleaned)
    if data is not None:
        return data.get("cards", [])

    print("WARNING: JSON failed to parse. Attempting repair...")

    repaired = repair_json_with_gpt(output_text)
    print("==== REPAIRED JSON ATTEMPT ====")
    print(repaired)

    repaired_json = try_parse_json(repaired)
    if repaired_json is not None:
        return repaired_json.get("cards", [])

    print("ERROR: JSON could not be repaired. Returning empty list.")
    return []