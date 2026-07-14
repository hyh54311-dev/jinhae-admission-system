import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token_calendar.json'
    if not os.path.exists(token_path):
        print("Calendar token not found.")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    # Range: June 1, 2026 to October 15, 2026
    start_time = datetime.datetime(2026, 6, 1).astimezone().isoformat()
    end_time = datetime.datetime(2026, 10, 15).astimezone().isoformat()
    
    try:
        calendar_list = service.calendarList().list().execute()
        # Find primary calendar
        primary_id = 'primary'
        for entry in calendar_list['items']:
            if entry.get('primary'):
                primary_id = entry['id']
                print(f"Primary Calendar ID: {primary_id}")
                break
        
        events_result = service.events().list(
            calendarId=primary_id,
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"Total events found: {len(events)}")
        with open('calendar_events_report.txt', 'w', encoding='utf-8') as f:
            for e in events:
                start = e['start'].get('dateTime', e['start'].get('date'))
                end = e['end'].get('dateTime', e['end'].get('date'))
                summary = e.get('summary', '')
                desc = e.get('description', '')
                f.write(f"[{start} ~ {end}] {summary} | {desc}\n")
        print("Report written to calendar_events_report.txt")
        
    except Exception as e:
        print("API error:", e)

if __name__ == '__main__':
    main()
