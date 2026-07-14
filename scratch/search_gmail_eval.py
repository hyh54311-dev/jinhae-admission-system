import os
import sys
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_email_body(msg):
    # Helper to recursively extract text body from mime parts
    payload = msg['payload']
    
    def decode_data(data, charset):
        if not data:
            return ""
        decoded = base64.urlsafe_b64decode(data)
        if not charset:
            charset = 'utf-8'
        try:
            return decoded.decode(charset, errors='ignore')
        except Exception:
            return decoded.decode('utf-8', errors='ignore')

    if 'parts' not in payload:
        data = payload.get('body', {}).get('data', '')
        charset = 'utf-8'
        for header in payload.get('headers', []):
            if header['name'].lower() == 'content-type':
                # Extract charset from header e.g. "text/plain; charset=UTF-8"
                parts = header['value'].split('charset=')
                if len(parts) > 1:
                    charset = parts[1].split(';')[0].strip().lower().replace('"', '').replace("'", "")
        return decode_data(data, charset)
    
    def walk_parts(parts):
        text_body = ""
        html_body = ""
        for part in parts:
            mime_type = part.get('mimeType', '')
            charset = 'utf-8'
            for header in part.get('headers', []):
                if header['name'].lower() == 'content-type':
                    sub_parts = header['value'].split('charset=')
                    if len(sub_parts) > 1:
                        charset = sub_parts[1].split(';')[0].strip().lower().replace('"', '').replace("'", "")
            
            if 'parts' in part:
                t, h = walk_parts(part['parts'])
                if t: text_body += t
                if h: html_body += h
            else:
                data = part.get('body', {}).get('data', '')
                if mime_type == 'text/plain':
                    text_body += decode_data(data, charset)
                elif mime_type == 'text/html':
                    html_body += decode_data(data, charset)
        return text_body, html_body

    text_body, html_body = walk_parts(payload['parts'])
    return text_body if text_body else html_body

def search_and_save():
    token_path = 'token_gmail.json'
    if not os.path.exists(token_path):
        print("Error: token_gmail.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        
        # We query for subjects containing "화법과 작문" or "수행평가"
        query = 'subject:("화법과 작문" OR "수행평가")'
        print(f"Searching with query: {query}")
        results = service.users().messages().list(userId='me', q=query, maxResults=30).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No matching emails found.")
            return
            
        print(f"Found {len(messages)} matching email(s). Processing...")
        email_data = []
        
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = "No Subject"
            sender = "Unknown Sender"
            date = "Unknown Date"
            for header in headers:
                name_lower = header['name'].lower()
                if name_lower == 'subject':
                    subject = header['value']
                elif name_lower == 'from':
                    sender = header['value']
                elif name_lower == 'date':
                    date = header['value']
            
            body = get_email_body(msg)
            
            email_data.append({
                'id': message['id'],
                'date': date,
                'from': sender,
                'subject': subject,
                'body': body
            })
            
        # Save output to JSON file with UTF-8 encoding
        output_file = 'scratch/gmail_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(email_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully processed and saved {len(email_data)} emails to {output_file}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    search_and_save()
