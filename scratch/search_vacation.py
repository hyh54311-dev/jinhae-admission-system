import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token_calendar.json'
    if not os.path.exists(token_path):
        print("token_calendar.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    start_time = datetime.datetime(2026, 6, 1).astimezone().isoformat()
    end_time = datetime.datetime(2026, 8, 31).astimezone().isoformat()
    
    output_lines = []
    
    try:
        calendar_list = service.calendarList().list().execute()
        output_lines.append("=== Searching Calendar for Vacation Events ===")
        found_any = False
        for entry in calendar_list.get('items', []):
            calendar_id = entry['id']
            calendar_name = entry.get('summary', '')
            
            events_result = service.events().list(
                calendarId=calendar_id, 
                timeMin=start_time, 
                timeMax=end_time, 
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            vacation_keywords = ['방학', '방학식', '개학', '종업식', '휴업일']
            for e in events:
                summary = e.get('summary', '')
                if any(kw in summary for kw in vacation_keywords):
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    end = e['end'].get('dateTime', e['end'].get('date'))
                    output_lines.append(f"[{calendar_name}] [{start} ~ {end}] {summary} | Desc: {e.get('description', '')}")
                    found_any = True
                    
        if not found_any:
            output_lines.append("No vacation-related events found.")
            
    except Exception as e:
        output_lines.append(f"API error: {e}")
        
    with open("scratch/vacation_search_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done. Saved results to scratch/vacation_search_results.txt")

if __name__ == '__main__':
    main()
