import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def trash_messages():
    token_path = 'token_gmail.json'
    results_path = 'scratch/gmail_results.json'
    
    if not os.path.exists(token_path):
        print("Error: token_gmail.json does not exist. Please authorize first.")
        return
        
    if not os.path.exists(results_path):
        print("Error: scratch/gmail_results.json does not exist.")
        return
        
    try:
        # Load Gmail service
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        
        # Load search results
        with open(results_path, 'r', encoding='utf-8') as f:
            emails = json.load(f)
            
        trash_count = 0
        print("Starting to move submitted evaluation emails to Trash...")
        print("-" * 50)
        
        for email in emails:
            msg_id = email['id']
            subject = email['subject']
            
            # Skip calendar notifications or other non-evaluation emails
            if "알림:" in subject or "Google Calendar" in subject or msg_id == "19d72b88dc01ded2":
                print(f"Skipping non-evaluation email: {subject}")
                continue
                
            try:
                print(f"Trashing: {subject} (ID: {msg_id})...")
                # Move to Trash using modify/trash API
                service.users().messages().trash(userId='me', id=msg_id).execute()
                print("  => Success (Moved to Trash)")
                trash_count += 1
            except Exception as msg_err:
                print(f"  => Failed to trash message {msg_id}: {msg_err}")
                
        print("-" * 50)
        print(f"Operation complete! Successfully trashed {trash_count} email(s).")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    trash_messages()
