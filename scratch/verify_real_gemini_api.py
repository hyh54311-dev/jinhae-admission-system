import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Real Gemini API Key found in workspace
API_KEY = "MASKED_API_KEY"

models_to_test = [
    "gemini-3.1-flash-lite",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b"
]

print("==========================================================")
print("🔑 사용자 실제 Gemini API Key로 모델별 실시간 호출 테스트")
print("==========================================================")
print()

headers = {'Content-Type': 'application/json'}
payload = json.dumps({
    "contents": [{"parts": [{"text": "안녕하세요! 간단히 'Hello'라고 답변해주세요."}]}]
}).encode('utf-8')

for model in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
    
    print(f"👉 모델명: [{model}] 호출 테스트 시작...")
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode('utf-8')
            resp_json = json.loads(resp_body)
            answer = resp_json['candidates'][0]['content']['parts'][0]['text'].strip()
            print(f"   ✅ [성공 (HTTP {resp.status})]: 응답 내용 -> \"{answer}\"")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(err_body)
            message = err_json.get('error', {}).get('message', '')
            status = err_json.get('error', {}).get('status', '')
            code = err_json.get('error', {}).get('code', '')
            print(f"   ❌ [실패 (HTTP {code} - {status})]: {message}")
        except:
            print(f"   ❌ [실패 (HTTP {e.code})]: {err_body[:200]}")
    except Exception as ex:
        print(f"   ❌ [예외 발생]: {ex}")
    print("----------------------------------------------------------")
