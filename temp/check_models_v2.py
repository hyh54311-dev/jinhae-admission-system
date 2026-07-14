import requests

API_KEY = "os.getenv("GEMINI_API_KEY")"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("?ъ슜 媛?ν븳 紐⑤뜽 紐⑸줉:")
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(m['name'])
    else:
        print("Error:", response.status_code, response.text)
except Exception as e:
    print("Exception:", e)
