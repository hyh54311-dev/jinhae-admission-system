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

def find_prices(text):
    # Regex to find currency and price patterns
    # e.g., ??123,456, 123,456?? KRW 123,456, 123,456 ??    patterns = [
        r'??s?([\d,]+)',
        r'KRW\s?([\d,]+)',
        r'([\d,]+)\s???
    ]
    
    found_prices = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            found_prices.append(match.group(0))
            
    return list(set(found_prices))

def main():
    try:
        service = get_gmail_service()
        
        hotels = ["?섏뒳??, "?덈뱺 ?대━??]
        print("Searching for Agoda reservation emails...")
        
        for hotel in hotels:
            query = f"Agoda {hotel}"
            messages = search_messages(service, query)
            
            if not messages:
                print(f"[Not Found] 硫붿씪??李얠? 紐삵뻽?듬땲??")
                continue
                
                print(f"'{hotel}' related mail {len(messages)} items found. Analyzing...")
            
            # Get the most recent message
            content = get_message_content(service, messages[0]['id'])
            prices = find_prices(content)
            
            if prices:
                # Replace Unicode Won symbol with KRW for console compatibility
                clean_prices = [p.replace('??, 'KRW').replace('\u20a9', 'KRW') for p in prices]
                print(f"'{hotel}' estimated price info: {', '.join(clean_prices)}")
            else:
                print(f"[No Price] 硫붿씪? 李얠븯?쇰굹 媛寃??뺣낫瑜?異붿텧?섏? 紐삵뻽?듬땲??")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
