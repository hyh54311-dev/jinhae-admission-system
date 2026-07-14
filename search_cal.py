import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token_calendar.json'
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    start_time = datetime.datetime(2026, 4, 1).astimezone().isoformat()
    end_time = datetime.datetime(2026, 7, 30).astimezone().isoformat()
    
    try:
        calendar_list = service.calendarList().list().execute()
        for entry in calendar_list['items']:
            events_result = service.events().list(
                calendarId=entry['id'], 
                timeMin=start_time, 
                timeMax=end_time, 
                q='대학원',
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            if events:
                for e in events:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    end = e['end'].get('dateTime', e['end'].get('date'))
                    print(f"[{start} ~ {end}] {e.get('summary', '')} - {e.get('description', '')}")
    except Exception as e:
        print("API error:", e)
