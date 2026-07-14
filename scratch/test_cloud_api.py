import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

def test_api():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "What is the current stock price of Samsung Electronics? Please use Google Search."}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {
            "maxOutputTokens": 1000,
            "temperature": 0.2
        }
    }
    
    print(f"Testing URL: {url}")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            json_data = response.json()
            candidates = json_data.get("candidates", [])
            print(f"Candidates Count: {len(candidates)}")
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for i, part in enumerate(parts):
                    print(f"Part {i}: {part.keys()}")
                    if "text" in part:
                        print(f"Text snippet: {part['text'][:100]}...")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
