import datetime
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token_calendar.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def add_family_outing_event():
    creds = None
    if os.path.exists('token_calendar.json'):
        creds = Credentials.from_authorized_user_file('token_calendar.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_calendar.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    description = """
[최종] 4월 25일(토) 진해 가족 나들이 일정

10:00 | 집에서 출발 & 식당 확인
- 식당(055-545-3232) 전화 확인 (아기 의자 등)

10:30 ~ 12:00 | 진해드림파크 나들이
- 목재문화체험장(실내) 먼저 관람 (유아놀이실, 수족관)
- 광석골 쉼터(야외) 산책 및 사진 촬영

12:10 ~ 13:30 | 점심 식사 (샤브연리지 진해본점)
- 주소: 창원시 진해구 진해대로1026번길 4
- 아기 의자 사용 가능

13:30 ~ | 식사 종료 및 바로 귀가 (아기 낮잠)

💡 체크리스트
- 일교차 대비 아기 가디건, 선크림, 모자 필수
- 유모차 지참 권장
"""

    event = {
      'summary': '[가족나들이] 진해드림파크 & 샤브연리지',
      'location': '진해드림파크 (창원시 진해구 천자로 507)',
      'description': description.strip(),
      'start': {
        'dateTime': '2026-04-25T10:00:00+09:00',
        'timeZone': 'Asia/Seoul',
      },
      'end': {
        'dateTime': '2026-04-25T14:00:00+09:00',
        'timeZone': 'Asia/Seoul',
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 60},
        ],
      },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")

if __name__ == '__main__':
    add_family_outing_event()
