from openai import OpenAI
from backend.config import OPENAI_API_KEY
import base64
import mimetypes
import json

client = OpenAI(api_key=OPENAI_API_KEY)


def image_to_data_url(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/jpeg"

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{b64}"


def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


async def identify_card(front_image_path: str, back_image_path: str | None = None):
    """
    Identify Pokémon card. Back image optional.
    Returns structured JSON with confidence.
    """

    content = [
        {
            "type": "input_text",
            "text": (
                "Identify this Pokémon card.\n"
                "Return ONLY valid JSON. No markdown.\n"
                "Schema:\n"
                "{"
                "\"name\": string,"
                "\"set\": string,"
                "\"number\": string,"
                "\"rarity\": string,"
                "\"holo\": boolean,"
                "\"confidence\": number (0-1)"
                "}"
            )
        },
        {
            "type": "input_image",
            "image_url": image_to_data_url(front_image_path)
        }
    ]

    if back_image_path:
        content.append({
            "type": "input_image",
            "image_url": image_to_data_url(back_image_path)
        })

    response = client.responses.create(
        model="gpt-5.2",
        input=[{"role": "user", "content": content}]
    )

    return safe_json_parse(response.output_text)
