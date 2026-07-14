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

    # 1. 비바샘 원격연수원 직무연수 일정 (종일 일정)
    vivasam_event = {
        'summary': '[직무연수] 학생 주도성이 살아 있는 에듀테크 활용 수업 (비바샘 원격연수원)',
        'description': (
            '★ 2026년 정보(AI·SW)교육 역량강화 원격 직무연수\n\n'
            '- 연수기관: 비바샘 원격연수원\n'
            '- 수강과정: 학생 주도성이 살아 있는 에듀테크 활용 수업 외 10강좌\n'
            '- 연수시간: 15시간\n'
            '- 연수인원: 600명\n'
            '- 신청 및 운영기간: 2026. 6. 15.(월) ~ 9. 30.(수)\n'
            '- 신청방법: 원격연수원 사이트 개별 신청\n'
            '- 주의사항: 연수비 경상남도교육청 지원. 선착순 모집으로 조기 마감 가능.'
        ),
        'start': {
            'date': '2026-06-15',
        },
        'end': {
            'date': '2026-10-01', # 9/30 까지 (exclusive)
        },
    }

    # 2. 티처빌 원격연수원 직무연수 일정 (종일 일정)
    teachervill_event = {
        'summary': '[직무연수] 수업에 바로 쓰는 AI 로봇 교육 (티처빌 원격연수원)',
        'description': (
            '★ 2026년 정보(AI·SW)교육 역량강화 원격 직무연수\n\n'
            '- 연수기관: 티처빌 원격연수원\n'
            '- 수강과정: 수업에 바로 쓰는 AI 로봇 교육 외 5강좌\n'
            '- 연수시간: 15시간\n'
            '- 연수인원: 400명\n'
            '- 신청 및 운영기간: 2026. 6. 15.(월) ~ 9. 30.(수)\n'
            '- 신청방법: 원격연수원 사이트 개별 신청\n'
            '- 주의사항: 연수비 경상남도교육청 지원. 선착순 모집으로 조기 마감 가능.'
        ),
        'start': {
            'date': '2026-06-15',
        },
        'end': {
            'date': '2026-10-01', # 9/30 까지 (exclusive)
        },
    }

    # 3. 신청 개시일 당일 리마인더 (6월 15일 08:30 AM)
    reminder_event = {
        'summary': '🚨 [직무연수 신청 개시] 정보(AI·SW)교육 직무연수 신청 시작 (비바샘/티처빌)',
        'description': (
            '선생님, 오늘부터 2026년 정보(AI·SW)교육 역량강화 원격 직무연수 신청이 시작됩니다!\n\n'
            '1. 비바샘 원격연수원: 학생 주도성이 살아 있는 에듀테크 활용 수업 외 10강좌 (600명 선착순)\n'
            '2. 티처빌 원격연수원: 수업에 바로 쓰는 AI 로봇 교육 외 5강좌 (400명 선착순)\n\n'
            '※ 연수비는 경상남도교육청에서 전액 지원하나, 선착순 모집이므로 조기 마감될 수 있습니다. 지금 접속하여 신청하시기 바랍니다.'
        ),
        'start': {
            'dateTime': '2026-06-15T08:30:00',
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': '2026-06-15T09:30:00',
            'timeZone': 'Asia/Seoul',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 10},      # 10분 전 팝업
                {'method': 'email', 'minutes': 24 * 60},  # 1일 전 이메일
            ],
        },
    }

    try:
        # Check existing events in primary calendar to avoid duplication
        start_time = datetime.datetime(2026, 6, 14).astimezone().isoformat()
        end_time = datetime.datetime(2026, 10, 2).astimezone().isoformat()
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True
        ).execute()
        existing_events = events_result.get('items', [])

        # Delete existing reminder event if it exists to overwrite it with new time
        for e in existing_events:
            if e.get('summary') == reminder_event['summary']:
                service.events().delete(calendarId='primary', eventId=e['id']).execute()
                print(f"기존 리마인더 제거 완료: {e.get('summary')}")

        existing_summaries = [e.get('summary') for e in existing_events if e.get('summary') != reminder_event['summary']]

        for ev in [vivasam_event, teachervill_event, reminder_event]:
            if ev['summary'] in existing_summaries:
                print(f"이미 등록된 일정입니다: {ev['summary']}")
                continue
            created_event = service.events().insert(calendarId='primary', body=ev).execute()
            print(f"일정 등록 완료: {created_event.get('summary')} ({created_event.get('htmlLink')})")
    except Exception as e:
        print("API error:", e)

if __name__ == '__main__':
    main()
