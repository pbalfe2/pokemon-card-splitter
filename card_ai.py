import base64
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def identify_and_grade_card(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    You are an expert in Pokémon card grading and identification.
    Analyze the card and return ONLY JSON:

    {
        "name": "",
        "set": "",
        "number": "",
        "rarity": "",
        "condition": "",
        "notes": ""
    }
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "type": "message",
                "content": prompt
            },
            {
                "role": "user",
                "type": "input_image",
                "image_url": f"data:image/png;base64,{img_b64}"
            }
        ]
    )

    return json.loads(response.output_text)
