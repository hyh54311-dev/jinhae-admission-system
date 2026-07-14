import urllib.request
import json

API_KEY = "AIzaSyCnK2Sbp_facY0A7zveaKU7ClEgURlOI-4"
MODEL_NAME = "gemini-3.1-flash-lite"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

payload = {
    "contents": [{"parts": [{"text": "Hello, what is your model version?"}]}],
    "generationConfig": {"temperature": 0.5}
}

req = urllib.request.Request(URL, method="POST")
req.add_header('Content-Type', 'application/json')
data = json.dumps(payload).encode('utf-8')

try:
    with urllib.request.urlopen(req, data=data) as response:
        result = json.loads(response.read().decode('utf-8'))
        if "candidates" in result and len(result["candidates"]) > 0:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"SUCCESS! Model '{MODEL_NAME}' responded:\n{text}")
        else:
            print("Response structure didn't contain candidates:", result)
except Exception as e:
    if hasattr(e, 'read'):
        print(f"ERROR: HTTP Failed: {e}\nResponse body: {e.read().decode('utf-8')}")
    else:
        print(f"ERROR: {e}")
