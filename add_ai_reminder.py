import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token_calendar.json'
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    event = {
        'summary': '🤖 AI 대학원 지원 신청 및 서류 준비 (교육대학원 연계 AI융합교육)',
        'description': '작년에 계획하셨던 AI 대학원 신청 기간입니다.\n\n4월 중 서류 접수 및 추천 절차가 진행되므로, 소속 기관장(교장 선생님) 추천서 및 응시 서류 준비를 시작해 주세요.',
        'start': {
            'date': '2027-04-01',
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'date': '2027-04-02',
            'timeZone': 'Asia/Seoul',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 9 * 60},
                {'method': 'email', 'minutes': 24 * 60 * 3},
            ],
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except Exception as e:
        print('API error:', e)
else:
    print('token_calendar.json not found.')
