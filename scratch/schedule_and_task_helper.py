import os
import datetime
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
token_tasks_path = os.path.join(base_dir, 'token_tasks_write.json')
token_calendar_path = os.path.join(base_dir, 'token_calendar.json')

def get_creds(path, scopes):
    creds = None
    if os.path.exists(path):
        creds = Credentials.from_authorized_user_file(path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed credentials back to file
            with open(path, 'w') as f:
                f.write(creds.to_json())
        else:
            raise Exception(f"Credentials at {path} are invalid and cannot be refreshed.")
    return creds

def add_task(title, due_date_str):
    """
    due_date_str: '2026-07-14'
    """
    creds = get_creds(token_tasks_path, ["https://www.googleapis.com/auth/tasks"])
    service = build('tasks', 'v1', credentials=creds)
    
    # Form due time as RFC3339 timestamp (midnight UTC or specific timezone)
    due_timestamp = due_date_str + 'T09:00:00Z' # 9:00 AM UTC
    task_body = {
        'title': title,
        'due': due_timestamp,
        'notes': '구글 문서 링크: https://docs.google.com/document/d/1UL3XQP8-l_jiRUCihO-YNI_FWI5cfRCn8VVYfySIV80/edit?usp=drivesdk'
    }
    
    result = service.tasks().insert(tasklist='@default', body=task_body).execute()
    print(f"Task created successfully in Google Tasks:")
    print(f"  Title: {result.get('title')}")
    print(f"  Due: {result.get('due')}")
    return result

def get_tomorrow_events(date_str):
    """
    date_str: '2026-07-14'
    """
    creds = get_creds(token_calendar_path, ["https://www.googleapis.com/auth/calendar"])
    service = build('calendar', 'v3', credentials=creds)
    
    time_min = f"{date_str}T00:00:00+09:00"
    time_max = f"{date_str}T23:59:59+09:00"
    
    print(f"\nFetching Google Calendar events for tomorrow ({date_str})...")
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    if not events:
        print("No events found for tomorrow.")
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            print(f"- Start: {start} | Summary: {summary}")
            
def main():
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    # Add Task
    task_title = "진해고 입학 챗봇 Q&A 100선 구글 문서 작성 및 검토"
    add_task(task_title, tomorrow)
    
    # Get Tomorrow's Schedule
    get_tomorrow_events(tomorrow)

if __name__ == '__main__':
    main()
