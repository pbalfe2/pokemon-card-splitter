from openai import OpenAI
from config import OPENAI_API_KEY
import base64

client = OpenAI(api_key=OPENAI_API_KEY)

def encode(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

async def identify_card(image_path):
    response = client.responses.create(
        model="gpt-5.2",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Identify this Pokémon card. Return JSON."},
                {"type": "input_image", "image_base64": encode(image_path)}
            ]
        }]
    )
    return response.output_text
