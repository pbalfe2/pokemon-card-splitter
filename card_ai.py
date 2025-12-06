import base64
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_json_output(text):
    """Remove markdown fences and return pure JSON."""
    if not text:
        return ""
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()

def try_parse_json(text):
    try:
        return json.loads(text)
    except:
        return None

def repair_json_with_gpt(bad_text):
    """Ask GPT to repair invalid JSON."""
    prompt = f"""
    The following response was expected to be JSON but is malformed:

    {bad_text}

    Return ONLY corrected JSON. No explanations.
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    cleaned = clean_json_output(resp.choices[0].message.content)
    return cleaned

def identify_and_grade_card(image_path):
    """AI card identification + grading."""

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    Identify this Pokémon TCG card and grade its condition.
    Return ONLY valid JSON in this exact structure:

    {
      "name": "",
      "set": "",
      "number": "",
      "rarity": "",
      "condition": "",
      "price": 0
    }
    """

    # ---- GPT CALL ----
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                    }
                ]
            }
        ]
    )

    output_text = response.choices[0].message.content
    print("==== RAW GPT OUTPUT (CARD AI) ====")
    print(output_text)

    # ---- CLEAN + PARSE ----
    cleaned = clean_json_output(output_text)

    data = try_parse_json(cleaned)
    if data:
        return data

    print("WARNING: Card AI JSON failed, attempting repair...")

    repaired = repair_json_with_gpt(output_text)
    repaired_json = try_parse_json(repaired)

    if repaired_json:
        return repaired_json

    print("ERROR: Card AI could not produce valid JSON. Returning defaults.")

    # ----- DEFAULT SAFE VALUES -----
    return {
        "name": "Unknown Card",
        "set": "",
        "number": "",
        "rarity": "",
        "condition": "Unknown",
        "price": 0
    }
