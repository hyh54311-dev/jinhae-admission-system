import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token_calendar.json'
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z' 
    end_date = datetime.datetime(2026, 6, 15).isoformat() + 'Z'
    
    try:
        calendar_list = service.calendarList().list().execute()
        for entry in calendar_list['items']:
            events_result = service.events().list(
                calendarId=entry['id'], 
                timeMin=now, 
                timeMax=end_date, 
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            if events:
                print(f"Calendar: {entry.get('summary', entry['id'])}")
                for e in events:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    print(f"[{start}] {e.get('summary', '')}")
    except Exception as e:
        print("API error:", e)
else:
    print("token_calendar.json not found.")
