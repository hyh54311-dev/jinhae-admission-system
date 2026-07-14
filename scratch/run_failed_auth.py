import os
import sys
import time
from google_auth_oauthlib.flow import InstalledAppFlow

CRED_FILE = 'credentials.json'

def recover_tasks_token():
    print("\n--- [1/2] 구글 태스크(Tasks) Auth Start ---")
    try:
        SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
        TOKEN_PATH = 'token_tasks.json'
        
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            print(f"기존 {TOKEN_PATH}을 삭제했습니다.")

        print("태스크 조회용 브라우저 인증을 시작합니다...")
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
        # Port 8142
        creds = flow.run_local_server(port=8142, open_browser=True)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
        if os.path.exists(TOKEN_PATH):
            print(f"✔ 구글 태스크 인증 성공! ({TOKEN_PATH} 생성됨)")
    except Exception as e:
        print(f"Error: {e}")

def recover_gmail_token():
    print("\n--- [2/2] 지메일(Gmail) Auth Start ---")
    try:
        SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
        TOKEN_PATH = 'token_gmail.json'
        
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            print(f"기존 {TOKEN_PATH}을 삭제했습니다.")

        print("지메일 관리용 브라우저 인증을 시작합니다...")
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
        # Port 8143
        creds = flow.run_local_server(port=8143, open_browser=True)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
        if os.path.exists(TOKEN_PATH):
            print(f"✔ 지메일 인증 성공! ({TOKEN_PATH} 생성됨)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if not os.path.exists(CRED_FILE):
        print(f"Error: '{CRED_FILE}' 파일이 없습니다. 인증을 진행할 수 없습니다.")
        sys.exit(1)
        
    print("==================================================")
    print("   구글 태스크 및 지메일 재인증 도구")
    print("==================================================")
    print("이 스크립트는 브라우저 창을 열어 구글 로그인을 요청합니다.")
    print("로그인 후 권한을 허용해 주시면 새로운 토큰이 저장됩니다.")
    
    recover_tasks_token()
    recover_gmail_token()
    
    print("\n인증 완료! 5초 후에 창이 닫힙니다.")
    time.sleep(5)
