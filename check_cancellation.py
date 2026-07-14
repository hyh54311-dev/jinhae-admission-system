import base64
import re
from gmail_tool import get_gmail_service

def search_messages(service, query):
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])
    return messages

def get_message_content(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message.get('payload')
    
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
                data = part['body'].get('data')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        data = payload['body'].get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
            
    return body

def extract_cancellation_policy(text):
    # Search for keywords and extract surrounding text or identifying patterns
    keywords = ["痍⑥냼", "?꾩빟湲?, "Cancellation", "Policy", "?섏닔猷?, "Non-refundable"]
    
    # Try to find a block of text that mentions these
    # Agoda often identifies the policy in a table or specific paragraph
    
    lines = text.split('\n')
    relevant_lines = []
    
    found = False
    for i, line in enumerate(lines):
        if any(kw.lower() in line.lower() for kw in keywords):
            # Take some context lines
            start = max(0, i - 1)
            end = min(len(lines), i + 4)
            relevant_lines.append("\n".join(lines[start:end]))
            found = True
            
    if not found:
        return "No specific cancellation keywords found in text."
    
    return "\n---\n".join(relevant_lines[:5]) # Limit to top 5 hits

def main():
    try:
        service = get_gmail_service()
        hotels = ["?섏뒳??, "?덈뱺 ?대━??]
        
        print("Searching for cancellation policies in emails...")
        
        for hotel in hotels:
            query = f"Agoda {hotel}"
            messages = search_messages(service, query)
            
            if not messages:
                print(f"[Not Found] '{hotel}'")
                continue
                
            print(f"\nAnalyzing '{hotel}' policy...")
            content = get_message_content(service, messages[0]['id'])
            
            # If it's HTML, we might need a better way to strip tags, but let's try raw text first
            # Simple HTML tag removal
            clean_text = re.sub('<[^<]+?>', '', content)
            
            policy = extract_cancellation_policy(clean_text)
            
            # Clean up the output for console (Unicode issues)
            safe_policy = policy.replace('\u20a9', 'KRW').replace('??, 'KRW')
            # Limit length for readability
            print(safe_policy[:1000]) # First 1000 chars
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
