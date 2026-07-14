import datetime
import os.path
import sys
import io

# Ensure UTF-8 output
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token_calendar.json'
    if not os.path.exists(token_path):
        print("Error: token_calendar.json not found.")
        return

    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)

    # 1. 11:00 AM Reservation Reminder Event
    reminder_event = {
        'summary': '📞 [예약] 진해 푸름각 전화 예약 (055-546-5557)',
        'description': (
            '★ 교무부 회식 자리 확보를 위한 오전 전화 예약 리마인더\n\n'
            '- 매장명: 푸름각 (진해 소재 맛집, 블루리본 서베이 등재)\n'
            '- 전화번호: 055-546-5557\n'
            '- 개업 시간: 오전 11:00 (월요일 정기휴무)\n'
            '- 예약 정보: 교무부 단체 회식 예약 (인원 및 시간 조율)'
        ),
        'start': {
            'dateTime': '2026-06-30T11:00:00',
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': '2026-06-30T11:30:00',
            'timeZone': 'Asia/Seoul',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 5},      # 5분 전 팝업
                {'method': 'email', 'minutes': 30},     # 30분 전 이메일
            ],
        },
    }

    # 2. 6:00 PM Gathering Event
    gathering_event = {
        'summary': '🍽️ [회식] 교무부 회식 (진해 푸름각)',
        'location': '푸름각 (경남 창원시 진해구)',
        'description': (
            '★ 교무부 회식 일정\n\n'
            '- 장소: 진해 푸름각\n'
            '- 시각: 오후 6:00 (예약 여부에 따라 조정 필요)\n'
            '- 대표 메뉴: 탕수육찜 등\n'
            '※ 오전 11시에 전화 예약(055-546-5557)이 정상적으로 완료되었는지 확인해 주세요.'
        ),
        'start': {
            'dateTime': '2026-06-30T18:00:00',
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': '2026-06-30T21:00:00',
            'timeZone': 'Asia/Seoul',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30},     # 30분 전 팝업
            ],
        },
    }

    try:
        # Create Reservation Reminder
        created_reminder = service.events().insert(calendarId='primary', body=reminder_event).execute()
        print(f"예약 리마인더 일정 등록 완료: {created_reminder.get('summary')} ({created_reminder.get('htmlLink')})")

        # Create Gathering Event
        created_gathering = service.events().insert(calendarId='primary', body=gathering_event).execute()
        print(f"회식 일정 등록 완료: {created_gathering.get('summary')} ({created_gathering.get('htmlLink')})")
        
    except Exception as e:
        print("API error:", e)

if __name__ == '__main__':
    main()
