import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# We can test with a dummy or public test check to see the HTTP Status Code / Error Response returned by Google's official API endpoint.
# Endpoint format: https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key=TEST_KEY

models_to_test = [
    "gemini-3.1-flash-lite",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b"
]

print("=== Google Gemini API 모델명 실제 응답 테스트 ===")
print()

headers = {'Content-Type': 'application/json'}
test_payload = json.dumps({
    "contents": [{"parts": [{"text": "Hello"}]}]
}).encode('utf-8')

for model in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=AIzaSy_TEST_DUMMY_KEY"
    req = urllib.request.Request(url, data=test_payload, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"[MODEL] {model} -> HTTP {resp.status} SUCCESS")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(err_body)
            message = err_json.get('error', {}).get('message', '')
            status = err_json.get('error', {}).get('status', '')
            code = err_json.get('error', {}).get('code', '')
            print(f"[MODEL] {model} -> HTTP {code} ({status}): {message}")
        except:
            print(f"[MODEL] {model} -> HTTP {e.code}: {err_body[:100]}")
    except Exception as ex:
        print(f"[MODEL] {model} -> EXCEPTION: {ex}")

