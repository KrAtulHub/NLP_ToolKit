import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/hf-inference/models/dslim/bert-base-NER"

headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
}


def ner(text):
    payload = {
        "inputs": text
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    return response.json()
