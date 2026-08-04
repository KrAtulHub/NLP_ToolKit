import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/hf-inference/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"

headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
}


def sentiment(text):
    payload = {
        "inputs": text
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    return response.json()
