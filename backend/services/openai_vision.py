from openai import OpenAI
from backend.config import OPENAI_API_KEY
import base64
import mimetypes

client = OpenAI(api_key=OPENAI_API_KEY)

def image_to_data_url(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/jpeg"

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{b64}"

async def identify_card(image_path: str):
    response = client.responses.create(
        model="gpt-5.2",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Identify this Pokémon card. Return JSON with name, set, number, rarity, holo."
                },
                {
                    "type": "input_image",
                    "image_url": image_to_data_url(image_path)
                }
            ]
        }]
    )

    return response.output_text
