import os
import sys
import json
import datetime
import requests

def get_gemini_key():
    # Robustly find .env file up to parent directories
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    for _ in range(3):
        env_path = os.path.join(curr_dir, ".env")
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        key = line.strip().split("=", 1)[1]
                        if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
                            key = key[1:-1]
                        return key
        curr_dir = os.path.dirname(curr_dir)
    return None

GEMINI_API_KEY = get_gemini_key()
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("Error: Valid GEMINI_API_KEY not found in .env file.")
    sys.exit(1)

MODEL_NAME = "gemini-3.1-flash-lite-preview"

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
prompt = "Hello"
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "tools": [{"googleSearch": {}}],
    "generationConfig": {
        "maxOutputTokens": 65536,
        "temperature": 0.2
    }
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print(f"Error: {e}")
