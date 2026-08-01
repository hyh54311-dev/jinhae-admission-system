import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

models_to_test = [
    "models/gemini-3.1-flash-lite",
    "models/gemini-1.5-flash",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash-8b"
]

print("=== Google Gemini API 모델 존재 여부(GET models/{model}) 직접 확인 ===")
print()

for model_path in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}?key=AIzaSy_TEST_KEY"
    req = urllib.request.Request(url, method='GET')
    
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"[CHECK] {model_path} -> SUCCESS")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(err_body)
            message = err_json.get('error', {}).get('message', '')
            status = err_json.get('error', {}).get('status', '')
            code = err_json.get('error', {}).get('code', '')
            print(f"[CHECK] {model_path} -> HTTP {code} ({status}): {message}")
        except:
            print(f"[CHECK] {model_path} -> HTTP {e.code}: {err_body[:120]}")
    except Exception as ex:
        print(f"[CHECK] {model_path} -> EXCEPTION: {ex}")
