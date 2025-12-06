import base64
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def identify_and_grade_card(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
    You are an expert in Pokémon card identification and grading.
    Return ONLY JSON with fields:
    name, set, number, rarity, condition, notes.
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"type": "text", "text": prompt},
            {"type": "input_image", "image_url": f"data:image/png;base64,{img_b64}"}
        ]
    )

    return response.output_text
