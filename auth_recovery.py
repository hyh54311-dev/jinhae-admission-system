import os
import sys
import time

# ?꾩옱 ?붾젆?좊━瑜?path??異붽?
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def recover_docs_token():
    print("\n--- [1/2] 怨듬Ц 愿由?Document Manager) Auth Start ---")
    try:
        import document_manager
        # 湲곗〈 ?좏겙 ??젣 ?쒕룄 (?뺤떎???щ줈洹몄씤 ?좊룄)
        if os.path.exists('token.json'):
            os.remove('token.json')
            print("湲곗〈 token.json????젣?덉뒿?덈떎.")
        
        print("怨듬Ц 愿由ъ슜 釉뚮씪?곗? ?몄쬆???쒖옉?⑸땲??..")
        # open_browser=True濡?蹂寃쏀븯???ъ슜?먭? ?명븯寃??섎룄濡??좊룄
        # (湲곗〈 肄붾뱶媛 open_browser=False硫?URL??蹂듭궗?댁빞 ?댁꽌 遺덊렪??
        drive_service, _, _ = document_manager.get_google_services()
        if drive_service:
            print("??怨듬Ц 愿€由??몄쬆 ?깃났! (token.json created)")
        else:
            print("???몄쬆 ?ㅽ뙣. (Auth failed)")
    except Exception as e:
        print(f"?ㅻ쪟 諛쒖깮: {e}")

def recover_calendar_token():
    print("\n--- [2/2] 罹섎┛???쇱젙(Calendar) Auth Start ---")
    try:
        # unified_schedule.py??蹂꾨룄??flow 濡쒖쭅???놁쑝誘€濡?吏곸젒 援ы쁽?섍굅??
        # document_manager??濡쒖쭅??鍮뚮젮?€??token_calendar.json???€??        import document_manager
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        CRED_FILE = 'credentials.json'
        TOKEN_PATH = 'token_calendar.json'
        
        if not os.path.exists(CRED_FILE):
            print(f"??'{CRED_FILE}' ?뚯씪???놁뒿?덈떎. ?몄쬆??吏꾪뻾?????놁뒿?덈떎.")
            return

        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            print(f"湲곗〈 {TOKEN_PATH}????젣?덉뒿?덈떎.")

        print("罹섎┛??議고쉶 ?꾩슜 釉뚮씪?곗? ?몄쬆???쒖옉?⑸땲??..")
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
        creds = flow.run_local_server(port=8141, open_browser=True)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
        if os.path.exists(TOKEN_PATH):
            print(f"??罹섎┛???몄쬆 ?깃났! ({TOKEN_PATH} created)")
        
    except Exception as e:
        print(f"Error: {e}")

def recover_tasks_token():
    print("\n--- [3/4] 구글 태스크(Tasks) Auth Start ---")
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
        CRED_FILE = 'credentials.json'
        TOKEN_PATH = 'token_tasks.json'
        
        if not os.path.exists(CRED_FILE):
            print(f"⚠ '{CRED_FILE}' 파일이 없습니다. 인증을 진행할 수 없습니다.")
            return

        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            print(f"기존 {TOKEN_PATH}을 삭제했습니다.")

        print("태스크 조회용 브라우저 인증을 시작합니다...")
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
        creds = flow.run_local_server(port=8142, open_browser=True)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
        if os.path.exists(TOKEN_PATH):
            print(f"✔ 구글 태스크 인증 성공! ({TOKEN_PATH} 생성됨)")
    except Exception as e:
        print(f"Error: {e}")

def recover_gmail_token():
    print("\n--- [4/4] 지메일(Gmail) Auth Start ---")
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
        CRED_FILE = 'credentials.json'
        TOKEN_PATH = 'token_gmail.json'
        
        if not os.path.exists(CRED_FILE):
            print(f"⚠ '{CRED_FILE}' 파일이 없습니다. 인증을 진행할 수 없습니다.")
            return

        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            print(f"기존 {TOKEN_PATH}을 삭제했습니다.")

        print("지메일 관리용 브라우저 인증을 시작합니다...")
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
        creds = flow.run_local_server(port=8143, open_browser=True)
        
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
        if os.path.exists(TOKEN_PATH):
            print(f"✔ 지메일 인증 성공! ({TOKEN_PATH} 생성됨)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("==================================================")
    print("   Antigravity 자동화 시스템 구글 인증 복구 도구")
    print("==================================================")
    print("이 스크립트는 브라우저를 열어 구글 로그인을 요청합니다.")
    print("완료 후 'token*.json' 파일들이 생성되면 자동화가 정상화됩니다.")
    
    recover_docs_token()
    recover_calendar_token()
    recover_tasks_token()
    recover_gmail_token()
    
    print("\n모든 인증 절차가 마무리되었습니다.")
    print("이제 창을 닫으셔도 됩니다.")
    time.sleep(5)
