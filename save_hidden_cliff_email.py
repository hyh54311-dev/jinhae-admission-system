import base64
from gmail_tool import get_gmail_service

def main():
    service = get_gmail_service()
    # Use English names or more robust search
    result = service.users().messages().list(userId='me', q='Agoda "Hidden Cliff"').execute()
    messages = result.get('messages', [])
    
    if not messages:
        # Try Korean names
        result = service.users().messages().list(userId='me', q='Agoda "?덈뱺 ?대━??').execute()
        messages = result.get('messages', [])
        
    if not messages:
        print("NOT FOUND")
        return

    msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    
    # Try multiple parts if needed
    body = ""
    payload = msg['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                break
    else:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    
    with open('hidden_cliff_email_content.txt', 'w', encoding='utf-8') as f:
        f.write(body)
    print("SAVED")

if __name__ == "__main__":
    main()
