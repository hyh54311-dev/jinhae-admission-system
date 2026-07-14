import os.path
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token_calendar.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
        service = build('calendar', 'v3', credentials=creds)
        
        start_time = datetime.datetime(2026, 5, 25, 0, 0, 0).astimezone().isoformat()
        end_time = datetime.datetime(2026, 6, 10, 23, 59, 59).astimezone().isoformat()
        
        calendar_list = service.calendarList().list().execute()
        for entry in calendar_list['items']:
            summary = entry['summary']
            cal_id = entry['id']
            print(f"=== Calendar: {summary} ({cal_id}) ===")
            
            try:
                events_result = service.events().list(
                    calendarId=cal_id,
                    timeMin=start_time,
                    timeMax=end_time,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])
                if not events:
                    print("  No events found.")
                for ev in events:
                    start = ev['start'].get('dateTime', ev['start'].get('date'))
                    end = ev['end'].get('dateTime', ev['end'].get('date'))
                    print(f"  [{start} ~ {end}] {ev.get('summary')} (ID: {ev.get('id')})")
            except Exception as e:
                print(f"  Error fetching events: {e}")
            print()
    else:
        print("No token file found.")

if __name__ == '__main__':
    main()
