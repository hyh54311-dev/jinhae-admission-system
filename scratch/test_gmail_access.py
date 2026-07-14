import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def test_gmail():
    token_path = 'token_gmail.json'
    if not os.path.exists(token_path):
        print("Error: token_gmail.json does not exist.")
        return
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the refreshed credential
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found.")
            return
            
        print("Successfully connected! Here are your 5 most recent email subjects:")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = "No Subject"
            for header in headers:
                if header['name'].lower() == 'subject':
                    subject = header['value']
                    break
            print(f"- {subject}")
            
    except Exception as e:
        print(f"Failed to access Gmail API: {e}")

if __name__ == '__main__':
    test_gmail()
