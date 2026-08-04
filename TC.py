import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"

headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
}


def text_classification(text, labels):
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": labels
        }
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    return response.json()
