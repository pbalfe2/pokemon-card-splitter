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

async def grade_condition(front_path: str, back_path: str):
    response = client.responses.create(
        model="gpt-5.2",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Estimate Pokémon card condition (Mint, NM, LP, MP, HP). No grading claims."
                },
                {
                    "type": "input_image",
                    "image_url": image_to_data_url(front_path)
                },
                {
                    "type": "input_image",
                    "image_url": image_to_data_url(back_path)
                }
            ]
        }]
    )

    return response.output_text
