from openai import OpenAI
from backend.config import OPENAI_API_KEY
import base64

client = OpenAI(api_key=OPENAI_API_KEY)

def encode(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

async def grade_condition(front, back):
    response = client.responses.create(
        model="gpt-5.2",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Estimate card condition (Mint/NM/LP/MP/HP)."},
                {"type": "input_image", "image_base64": encode(front)},
                {"type": "input_image", "image_base64": encode(back)}
            ]
        }]
    )
    return response.output_text
