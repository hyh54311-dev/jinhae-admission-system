# -*- coding: utf-8 -*-
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
token_path = os.path.join(base_dir, 'token_calendar.json') # Use calendar token

def auth():
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        else:
            raise Exception("token_calendar.json is missing or invalid.")
    return creds

def check_calendar():
    creds = auth()
    calendar_service = build('calendar', 'v3', credentials=creds)

    print("Fetching calendar events for 2026-07-14...")
    # July 14, 2026
    time_min = '2026-07-14T00:00:00Z'
    time_max = '2026-07-14T23:59:59Z'
    
    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    if not events:
        print("No events found on July 14, 2026.")
    else:
        for event in events:
            print(f"\nEvent: {event.get('summary')}")
            print(f"  Description: {event.get('description')}")
            print(f"  Start: {event.get('start')}")
            print(f"  Attachments: {event.get('attachments')}")
            # If there are attachments, list them
            if 'attachments' in event:
                for att in event['attachments']:
                    print(f"    - {att.get('title')} ({att.get('fileUrl')})")

if __name__ == '__main__':
    check_calendar()
