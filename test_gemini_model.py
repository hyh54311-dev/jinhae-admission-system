import os
import requests
import json

def get_api_key():
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('GEMINI_API_KEY='):
                    return line.strip().split('=', 1)[1].strip()
    return os.environ.get('GEMINI_API_KEY', '')

def test_gemini():
    # .env 파일에서 키 읽기 시도
    api_key = get_api_key()
    model = "gemini-1.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": "Hello, are you working correctly? Please answer in one short sentence."}]}]
    }
    
    print(f"Testing {model} with the new API key...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        if response.status_code == 200:
            answer = result['candidates'][0]['content']['parts'][0]['text']
            print(f"Success! Model Response: {answer}")
        else:
            print(f"Error: Status Code {response.status_code}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_gemini()
