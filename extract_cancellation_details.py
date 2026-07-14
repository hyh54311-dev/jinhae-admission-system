import base64
import re
from gmail_tool import get_gmail_service

def search_messages(service, query):
    # Try different query formats
    queries = [query, query.replace(" ", ""), "Agoda Hidden Cliff", "Agoda Whistle"]
    all_msgs = []
    for q in queries:
        result = service.users().messages().list(userId='me', q=q).execute()
        all_msgs.extend(result.get('messages', []))
    return all_msgs

def get_message_content(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    parts = msg.get('payload', {}).get('parts', [])
    data = ""
    if parts:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                break
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data', '')
    else:
        data = msg.get('payload', {}).get('body', {}).get('data', '')
    
    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return ""

def main():
    service = get_gmail_service()
    hotels = ["?섏뒳??, "?덈뱺 ?대━??]
    
    for hotel in hotels:
        print(f"\n--- {hotel} Cancellation Policy ---")
        msgs = search_messages(service, f"Agoda {hotel}")
        if not msgs:
            print("No email found.")
            continue
            
        content = get_message_content(service, msgs[0]['id'])
        # Strip HTML briefly
        text = re.sub('<[^<]+?>', ' ', content)
        
        # Look for the policy block
        # Usually contains "痍⑥냼 湲고븳", "?꾩빟湲?, "Check-in", "Deadline"
        keywords = ["痍⑥냼", "湲고븳", "?섏닔猷?, "?꾩빟湲?, "Cancellation", "Penalty"]
        
        lines = text.split('\n')
        found = False
        for i, line in enumerate(lines):
            if any(kw in line for kw in keywords):
                # Print current line and next few
                display = "\n".join(lines[i:i+8]).strip()
                if len(display) > 20: # Lowered threshold to see more
                    safe_display = display.replace('\u20a9', 'KRW').replace('??, 'KRW')
                    # Search for specific price/date info in this block
                    print(safe_display)
                    print("-" * 20)
                    found = True
        if not found:
            print("Keyword not found in content snippet.")

if __name__ == "__main__":
    main()
