import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token_calendar.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
        service = build('calendar', 'v3', credentials=creds)
        calendar_list = service.calendarList().list().execute()
        for entry in calendar_list['items']:
            print(f"Summary: {entry['summary']} | ID: {entry['id']}")
    else:
        print("No token file found.")

if __name__ == '__main__':
    main()
