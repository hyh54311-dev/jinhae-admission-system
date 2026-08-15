import json
import requests

# 한국투자증권 Open API 모의투자 접근 토큰 발급 샘플 코드
# 사전 준비: KIS Developers (https://api.koreainvestment.com:9443)에서 App Key와 App Secret 발급 필요

# 기본 설정 (모의투자 기준)
URL_BASE = "https://openapivts.koreainvestment.com:9443"  # 모의투자 서버 (실전: https://openapi.koreainvestment.com:9443)

APP_KEY = "YOUR_APP_KEY_HERE"       # 발급받은 App Key 입력
APP_SECRET = "YOUR_APP_SECRET_HERE" # 발급받은 App Secret 입력

def get_access_token():
    """
    접근 토큰(Access Token) 발급 함수
    유효기간: 24시간
    """
    path = "oauth2/tokenP"
    url = f"{URL_BASE}/{path}"
    
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    res = requests.post(url, headers=headers, data=json.dumps(body))
    
    if res.status_code == 200:
        data = res.json()
        access_token = data.get("access_token")
        print("토큰 발급 성공!")
        print(f"Access Token: {access_token[:20]}...")
        return access_token
    else:
        print(f"토큰 발급 실패 (Error Code: {res.status_code})")
        print(res.text)
        return None

if __name__ == "__main__":
    # 테스트 실행
    print("한국투자증권 Open API 접근 토큰 발급 테스트")
    # token = get_access_token()
