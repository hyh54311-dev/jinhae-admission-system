import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def check_calendar():
    token_path = 'token_calendar.json'
    if not os.path.exists(token_path):
        print("Calendar: token_calendar.json file not found.")
        return False
    try:
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
        if creds.expired and creds.refresh_token:
            print("Calendar token expired, refreshing...")
            creds.refresh(Request())
        service = build('calendar', 'v3', credentials=creds)
        calendar_list = service.calendarList().list(maxResults=5).execute()
        print("Calendar: Success! Retrieved calendar list:")
        for item in calendar_list.get('items', []):
            print(f"  - {item.get('summary')} ({item.get('id')})")
        return True
    except Exception as e:
        print(f"Calendar check failed: {e}")
        return False

def check_tasks():
    token_path = 'token_tasks.json'
    if not os.path.exists(token_path):
        print("Tasks: token_tasks.json file not found.")
        return False
    try:
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/tasks.readonly', 'https://www.googleapis.com/auth/tasks'])
        if creds.expired and creds.refresh_token:
            print("Tasks token expired, refreshing...")
            creds.refresh(Request())
        service = build('tasks', 'v1', credentials=creds)
        tasklists = service.tasklists().list(maxResults=5).execute()
        print("Tasks: Success! Retrieved task lists:")
        for item in tasklists.get('items', []):
            print(f"  - {item.get('title')} ({item.get('id')})")
        return True
    except Exception as e:
        # Retry with tasks scope only (readonly might not be in the token)
        try:
            creds = Credentials.from_authorized_user_file(token_path)
            if creds.expired and creds.refresh_token:
                print("Tasks token expired (no scope match), refreshing...")
                creds.refresh(Request())
            service = build('tasks', 'v1', credentials=creds)
            tasklists = service.tasklists().list(maxResults=5).execute()
            print("Tasks: Success! Retrieved task lists:")
            for item in tasklists.get('items', []):
                print(f"  - {item.get('title')} ({item.get('id')})")
            return True
        except Exception as e2:
            print(f"Tasks check failed: {e2}")
            return False

def check_gmail():
    token_path = 'token_gmail.json'
    if not os.path.exists(token_path):
        print("Gmail: token_gmail.json file not found.")
        return False
    try:
        creds = Credentials.from_authorized_user_file(token_path)
        if creds.expired and creds.refresh_token:
            print("Gmail token expired, refreshing...")
            creds.refresh(Request())
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f"Gmail: Success! Email address: {profile.get('emailAddress')}")
        return True
    except Exception as e:
        print(f"Gmail check failed: {e}")
        return False

def check_generic_token():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Generic Token: token.json file not found.")
        return False
    try:
        creds = Credentials.from_authorized_user_file(token_path)
        if creds.expired and creds.refresh_token:
            print("Generic token expired, refreshing...")
            creds.refresh(Request())
        # Let's see if we can use this token for Drive or Sheets
        # Typically token.json might be for Drive/Sheets or Classroom/Docs
        # Try sheets or drive
        try:
            service = build('drive', 'v3', credentials=creds)
            results = service.files().list(pageSize=5).execute()
            print("Generic Token (Drive): Success! Files retrieved:")
            for file in results.get('files', []):
                print(f"  - {file.get('name')} ({file.get('id')})")
            return True
        except Exception as e_drive:
            try:
                service = build('sheets', 'v4', credentials=creds)
                # Just check some generic spreadsheet or metadata
                print("Generic Token (Sheets): Success! (Sheet service built successfully)")
                return True
            except Exception as e_sheets:
                print(f"Generic Token: Tried Drive ({e_drive}) and Sheets ({e_sheets}).")
                return False
    except Exception as e:
        print(f"Generic Token check failed: {e}")
        return False

if __name__ == '__main__':
    print("=== Google API Access Verification ===")
    print("Current working directory:", os.getcwd())
    print("-" * 40)
    check_calendar()
    print("-" * 40)
    check_tasks()
    print("-" * 40)
    check_gmail()
    print("-" * 40)
    check_generic_token()
    print("=" * 40)
