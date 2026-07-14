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

        # 2026년 7월 8일 오전 9시 50분 ~ 10시 30분
        event_body = {
            'summary': '✈️ 제주항공 찜특가 국제선 오픈 - 대만(타이베이/가오슝) 2월 항공권 예매',
            'description': (
                '제주항공 찜특가(JJIM) 국제선 노선 판매가 오전 10시에 오픈됩니다!\n\n'
                '📌 대상 노선: 부산(PUS) ↔ 타이베이(TPE) / 가오슝(KHH)\n'
                '📌 탑승 기간: 2026년 10월 1일 ~ 2027년 3월 27일 (2월 대만 여행 포함)\n'
                '📌 이벤트 링크: https://www.jejuair.net/ko/event/eventDetail.do?eventNo=0000003950\n\n'
                '💡 예약 팁:\n'
                '1. 접속 폭주가 예상되므로 9시 30분~45분경 미리 로그인해 두세요.\n'
                '2. 위탁수하물이 불포함된 특가이므로 유의하세요.\n'
                '3. 빠른 결제를 위해 간편결제 수단을 사전에 등록해 두시면 좋습니다.\n'
                '4. 동행인 영문 이름과 생년월일을 메모장 등에 적어두고 복사해서 붙여넣기 하세요.'
            ),
            'start': {
                'dateTime': '2026-07-08T09:50:00',
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': '2026-07-08T10:30:00',
                'timeZone': 'Asia/Seoul',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},  # 9시 40분 알림
                    {'method': 'popup', 'minutes': 20},  # 9시 30분 알림
                    {'method': 'popup', 'minutes': 30},  # 9시 20분 알림
                ],
            },
        }
        
        # 겹치는 이전 찜특가 이벤트가 있는지 확인하여 삭제 (최근 1일 이내 또는 미래의 스케줄만 검색)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=50, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        for ev in events:
            if '제주항공' in ev.get('summary', '') or '찜특가' in ev.get('summary', ''):
                try:
                    service.events().delete(calendarId='primary', eventId=ev['id']).execute()
                    print(f"Removed previous event ID: {ev['id']}")
                except Exception:
                    pass

        event = service.events().insert(calendarId='primary', body=event_body).execute()
        
        # Safe printing for Windows CP949 console
        success_msg = f"SUCCESS: Added Jeju Air JJIM reminder. Link: {event.get('htmlLink')}"
        print(success_msg.encode('ascii', errors='replace').decode('ascii'))

    except Exception as error:
        print(f"API ERROR: {error}")

if __name__ == '__main__':
    main()
