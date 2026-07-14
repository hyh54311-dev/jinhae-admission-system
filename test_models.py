import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODELS_TO_TEST = ["gemini-1.5-pro", "gemini-3.1-flash-lite", "gemini-2.0-flash", "gemini-2.0-pro", "gemini-2.5-flash", "gemini-3.0-flash"]

for model in MODELS_TO_TEST:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Hello, are you available?"}]}]
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"OK: {model}: Available")
        else:
            print(f"FAILED: {model}: Status {response.status_code}")
    except Exception as e:
        print(f"ERROR: {model}: {e}")
