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
        
        out_lines = []
        for entry in calendar_list['items']:
            summary = entry['summary']
            cal_id = entry['id']
            out_lines.append(f"Calendar: {summary} ({cal_id})")
            
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
                    out_lines.append("  No events found.")
                for ev in events:
                    start = ev['start'].get('dateTime', ev['start'].get('date'))
                    end = ev['end'].get('dateTime', ev['end'].get('date'))
                    title = ev.get('summary', '')
                    desc = ev.get('description', '')
                    out_lines.append(f"  [{start} ~ {end}] {title} | {desc}")
            except Exception as e:
                out_lines.append(f"  Error: {e}")
            out_lines.append("")
            
        with open("scratch/calendar_events_decoded.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines))
        print("Success writing scratch/calendar_events_decoded.txt")
    else:
        print("No token file found.")

if __name__ == '__main__':
    main()
