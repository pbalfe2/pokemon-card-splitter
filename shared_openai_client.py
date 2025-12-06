# shared_openai_client.py

import os
from openai import OpenAI

def get_openai_client():
    """
    Render-compatible OpenAI client.
    No proxy settings, no custom client_options.
    The SDK automatically respects environment routing.
    """
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
