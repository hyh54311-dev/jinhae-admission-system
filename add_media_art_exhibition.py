import datetime
import os.path
import sys
import io

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

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

        # 2026년 7월 23일 10:00 ~ 17:30 (전시 운영 시간 전체)
        event_body = {
            'summary': '🎨 [전시] 미디어아트 빛을 품다',
            'location': '창녕문화예술회관 대전시실 (경남 창녕군 창녕읍 군청1길 35)',
            'description': (
                '🎨 [기획] 미디어아트 빛을 품다 : 한여름 시원한 빛의 안식처\n\n'
                '무더운 여름철, 시원한 실내에서 미디어아트를 통해 빛의 아름다움을 경험하며 휴식을 취하는 전시입니다.\n\n'
                '📌 전시 상세 정보:\n'
                '- 기간: 2026-07-21 (화) ~ 2026-08-09 (일)\n'
                '- 장소: 창녕문화예술회관 대전시실\n'
                '- 전시시간: 10:00 ~ 17:30 (관람 시간 준수)\n'
                '- 관람등급: 전체관람가\n'
                '- 주최/주관: 창녕군, 창녕문화예술회관\n'
                '- 문의전화: 055-530-1911\n\n'
                '💡 관람 팁 및 참고사항:\n'
                '1. 매주 월요일은 휴관일입니다.\n'
                '2. 전시장 내 음식물 반입은 금지되어 있습니다.\n'
                '3. 상세 페이지 링크: https://www.cng.go.kr/art/02818/02825.web?amode=view&schHsort2=display&schCode=993'
            ),
            'start': {
                'dateTime': '2026-07-23T10:00:00',
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': '2026-07-23T17:30:00',
                'timeZone': 'Asia/Seoul',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60},   # 1시간 전 알림
                    {'method': 'popup', 'minutes': 1440},  # 1일 전 알림
                ],
            },
        }

        # Check if the event already exists
        start_min = '2026-07-23T00:00:00Z'
        start_max = '2026-07-23T23:59:59Z'
        events_result = service.events().list(calendarId='primary', timeMin=start_min, timeMax=start_max,
                                              singleEvents=True).execute()
        events = events_result.get('items', [])
        
        duplicate = False
        for ev in events:
            if '미디어아트' in ev.get('summary', '') or '빛을 품다' in ev.get('summary', ''):
                print(f"Skipped adding duplicate event: {ev.get('summary')}")
                duplicate = True
                break

        if not duplicate:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
            print(f"SUCCESS: Added Media Art Exhibition event. Link: {event.get('htmlLink')}")
        else:
            print("Event already exists in calendar.")

    except Exception as error:
        print(f"API ERROR: {error}")

if __name__ == '__main__':
    main()
