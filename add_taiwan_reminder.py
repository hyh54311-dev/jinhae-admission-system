import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    token_path = 'token_calendar.json'
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # 2026년 7월 1일 알림 설정
        event_date = "2026-07-01"
        event_body = {
            'summary': '[대만 여행] 항공권 동계 스케줄 오픈 확인 (에어부산/제주항공)',
            'description': '남자 4명 2027년 1월/2월 대만 여행 항공권 예매 타이밍 확인. 2+2 분할 예매 및 가오슝 루트 체크.',
            'start': {'date': event_date},
            'end': {'date': (datetime.datetime.strptime(event_date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")},
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60}, # 1일 전 알림
                ],
            },
        }
        
        service.events().insert(calendarId='primary', body=event_body).execute()
        print(f"SUCCESS: Added Taiwan travel reminder for {event_date}")

    except Exception as error:
        print(f"API ERROR: {error}")

if __name__ == '__main__':
    main()
