from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_listing(cards):
    response = client.responses.create(
        model="gpt-5.2",
        input=f"Generate an eBay listing draft:\n{cards}"
    )
    return response.output_text
