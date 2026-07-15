import os
import sys
import json
import datetime
import requests

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
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
