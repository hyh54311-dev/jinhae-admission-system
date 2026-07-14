import datetime
import os.path
import sys
import io

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

    events_to_add = [
        {
            'summary': '대신해 AI 동아리 수업 (1회차 - CBT 사전평가)',
            'location': '본교 컴퓨터실',
            'description': '대신해 AI 동아리 (14명) 수업\n1회차 (사전역량평가(CBT))\n강사: 교사 황요한',
            'start': '2026-07-06T14:35:00',
            'end': '2026-07-06T16:30:00'
        },
        {
            'summary': '대신해 AI 동아리 수업 (2회차 - 분과교육 1)',
            'location': '본교 컴퓨터실',
            'description': '대신해 AI 동아리 (14명) 수업\n2회차 (분과교육 1)\n강사: 교사 황요한',
            'start': '2026-07-20T14:35:00',
            'end': '2026-07-20T17:35:00'
        },
        {
            'summary': '대신해 AI 동아리 수업 (3회차 - 분과교육 2)',
            'location': '본교 컴퓨터실',
            'description': '대신해 AI 동아리 (14명) 수업\n3회차 (분과교육 2)\n강사: 교사 황요한',
            'start': '2026-08-24T14:35:00',
            'end': '2026-08-24T17:35:00'
        },
        {
            'summary': '대신해 AI 동아리 수업 (4회차 - 분과교육 3)',
            'location': '본교 컴퓨터실',
            'description': '대신해 AI 동아리 (14명) 수업\n4회차 (분과교육 3)\n강사: 교사 황요한',
            'start': '2026-08-31T14:35:00',
            'end': '2026-08-31T17:35:00'
        },
        {
            'summary': '대신해 AI 동아리 수업 (5회차 - 분과교육 4)',
            'location': '본교 컴퓨터실',
            'description': '대신해 AI 동아리 (14명) 수업\n5회차 (분과교육 4)\n강사: 교사 황요한',
            'start': '2026-09-07T14:35:00',
            'end': '2026-09-07T17:35:00'
        },
        {
            'summary': '대신해 AI 동아리 수업 (6회차 - CBT 사후평가)',
            'location': '본교 컴퓨터실',
            'description': '대신해 AI 동아리 (14명) 수업\n6회차 (사후역량평가(CBT))\n강사: 교사 황요한',
            'start': '2026-09-14T14:35:00',
            'end': '2026-09-14T16:30:00'
        }
    ]

    try:
        # Search range: 2026-07-01 to 2026-09-30
        start_search = datetime.datetime(2026, 7, 1).astimezone().isoformat()
        end_search = datetime.datetime(2026, 9, 30).astimezone().isoformat()
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_search,
            timeMax=end_search,
            singleEvents=True
        ).execute()
        existing_events = events_result.get('items', [])
        
        # Build map of existing events by summary for quick lookup
        existing_map = {}
        for e in existing_events:
            summary = e.get('summary')
            if summary:
                existing_map[summary] = e

        print("Updating/Adding events in primary calendar:")
        for ev in events_to_add:
            event_body = {
                'summary': ev['summary'],
                'location': ev['location'],
                'description': ev['description'],
                'start': {
                    'dateTime': ev['start'],
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': ev['end'],
                    'timeZone': 'Asia/Seoul',
                },
            }

            # Check if this event already exists by summary
            existing_event = existing_map.get(ev['summary'])
            
            if existing_event:
                # Update existing event
                event_id = existing_event['id']
                updated_event = service.events().update(
                    calendarId='primary',
                    eventId=event_id,
                    body=event_body
                ).execute()
                print(f"- UPDATED: {updated_event.get('summary')} ({ev['start']} ~ {ev['end']})")
            else:
                # Insert new event
                created_event = service.events().insert(
                    calendarId='primary',
                    body=event_body
                ).execute()
                print(f"- ADDED: {created_event.get('summary')} ({ev['start']} ~ {ev['end']})")
            
        print("\nAll calendar operations completed.")
        
    except Exception as e:
        print("API error:", e)

if __name__ == '__main__':
    main()
