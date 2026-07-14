import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token_calendar.json'
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    # Search from today
    now = datetime.datetime.utcnow().isoformat() + 'Z' 
    end_of_year = datetime.datetime(2026, 12, 31).isoformat() + 'Z'
    
    try:
        calendar_list = service.calendarList().list().execute()
        found = False
        for entry in calendar_list['items']:
            events_result = service.events().list(
                calendarId=entry['id'], 
                timeMin=now, 
                timeMax=end_of_year, 
                q='입학설명회',
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            if events:
                found = True
                print(f"Calendar: {entry.get('summary', entry['id'])}")
                for e in events:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    print(f"[{start}] {e.get('summary', '')}")
        if not found:
            print("No '입학설명회' found in calendar.")
    except Exception as e:
        print("API error:", e)
else:
    print("token_calendar.json not found.")
