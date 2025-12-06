# shared_openai_client.py

import os
from openai import OpenAI

def get_openai_client():
    """
    Safe OpenAI client constructor.
    Handles Render's injected proxy variables properly.
    """

    proxies = {}
    if "HTTP_PROXY" in os.environ:
        proxies["http"] = os.environ["HTTP_PROXY"]
    if "HTTPS_PROXY" in os.environ:
        proxies["https"] = os.environ["HTTPS_PROXY"]

    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        client_options={
            "proxies": proxies if proxies else None
        }
    )
