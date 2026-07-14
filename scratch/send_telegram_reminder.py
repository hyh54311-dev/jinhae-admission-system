import os
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    load_dotenv()
    
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        print("Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing in .env")
        return
        
    message = (
        "🔔 [K-듀얼모멘텀 리밸런싱 수동 실행 알림]\n\n"
        "오늘 오전 10시 30분, 구글 클라우드에서 일회성 수동 실행을 하실 시간입니다.\n\n"
        "아래 순서대로 진행해 주세요:\n\n"
        "1. 👉 [구글 클라우드 콘솔 바로가기](https://console.cloud.google.com/functions/list) 링크를 클릭하여 Cloud Functions 목록으로 바로 접속합니다.\n"
        "2. 리밸런싱 함수를 선택한 후 상단 탭 메뉴 중 **[테스트(Testing)]** 탭을 클릭합니다.\n"
        "3. Triggering event (트리거 이벤트) 입력 상자에 기본 적혀있는 중괄호를 지우고, 아래와 같이 강제 실행 옵션을 JSON 형태로 입력합니다:\n\n"
        "{\n"
        "  \"force\": \"true\"\n"
        "}\n\n"
        "*(내일은 원래 실행일인 17일이 아니기 때문에, 이 옵션을 생략하면 날짜 필터링에 의해 가동이 즉시 중단되므로 필수 입력해야 합니다.)*\n\n"
        "4. 하단의 [함수 테스트(Test the function)] 파란색 버튼을 클릭합니다.\n"
        "5. 로봇이 KST 타임존과 TPS 회피(대기 및 재시도) 로직을 거쳐 거래를 안전하게 실행하고 완료할 것입니다. 체결 결과는 연동된 텔레그램 채널로 즉시 전송됩니다."
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10, verify=False)
        if res.status_code == 200:
            print("Successfully sent telegram reminder.")
        else:
            print(f"Failed to send telegram: {res.text}")
    except Exception as e:
        print(f"Error sending telegram: {e}")

if __name__ == "__main__":
    main()
