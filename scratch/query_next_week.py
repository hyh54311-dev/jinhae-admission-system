import datetime
import os
import sys
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_calendar_events():
    token_path = r'd:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\token_calendar.json'
    if not os.path.exists(token_path):
        print("No token_calendar.json")
        return
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
        service = build('calendar', 'v3', credentials=creds)
        
        # Today is 2026-05-15 (Friday)
        # Next week Monday to Sunday: 18th to 24th
        start_date = datetime.date(2026, 5, 18)
        end_date = datetime.date(2026, 5, 24)
        
        start_time = datetime.datetime.combine(start_date, datetime.time.min).astimezone().isoformat()
        end_time = datetime.datetime.combine(end_date, datetime.time.max).astimezone().isoformat()
        
        print(f"Checking from {start_date} to {end_date}")
        calendar_list = service.calendarList().list().execute()
        
        for entry in calendar_list['items']:
            events_result = service.events().list(
                calendarId=entry['id'], 
                timeMin=start_time, 
                timeMax=end_time, 
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            if events:
                calendar_summary = entry['summary']
                for e in events:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    print(f"[{calendar_summary}] {e.get('summary')} ({start})")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    get_calendar_events()
