import datetime
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 援ш? 罹섎┛???묎렐 沅뚰븳 踰붿쐞
SCOPES = ['https://www.googleapis.com/auth/calendar']

# 吏꾪빐怨??숈궗 ?쇱젙 ?먮낯 ?곗씠??TEXT_SCHEDULE = """
3/3 ?쒖뾽???낇븰??3/24 ?꾧뎅?고빀?숇젰?됯?(?꾪븰??
4/3 泥댁쑁?쒕쭏??4/27-30 1?뚭퀬??5/7 ?꾧뎅?고빀?숇젰?됯?(3?숇뀈)
5/19-5/22 2?숇뀈 ?섑븰?ы뻾
5/21-5/22 1?숇뀈 吏꾨줈泥댄뿕?숈뒿
5/22 3?숇뀈 ?꾩옣泥댄뿕?숈뒿
6/4 ?꾧뎅?고빀?숇젰?됯?(1,2?숇뀈), ?섎뒫紐⑥쓽?됯?(3?숇뀈)
6/30 2?뚭퀬??7/1-7/3 2?뚭퀬??7/8 ?꾧뎅?고빀?숇젰?됯?(3?숇뀈)
7/21 ?щ쫫諛⑺븰??7/22-8/11 ?щ쫫諛⑺븰
8/12 媛쒗븰
9/2 ?꾧뎅?고빀?숇젰?됯?(1,2?숇뀈), ?섎뒫紐⑥쓽?됯?(3?숇뀈)
9/29-9/30 1?뚭퀬??10/1-10/2 1?뚭퀬??10/20 ?꾧뎅?고빀?숇젰?됯?(?꾪븰??
11/19 ??숈닔?숇뒫?μ떆??12/8-12/11 2?뚭퀬??12/24 ?λ났?쒖슱??12/29 寃⑥슱諛⑺븰??12/30-2/2 寃⑥슱諛⑺븰
2/3 媛쒗븰
2/5 議몄뾽??醫낆뾽??"""

def parse_schedule(text):
    """?띿뒪???뺥깭???숈궗 ?쇱젙???뚯떛?섏뿬 ?대깽??由ъ뒪?몃줈 諛섑솚"""
    events = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        try:
            parts = line.split(maxsplit=1)
            if len(parts) < 2: continue
            
            date_part = parts[0]
            title = parts[1]
            
            # ?쒖옉?쇨낵 醫낅즺??遺꾨━ ("4/27-30" ?먮뒗 "4/27")
            dates = date_part.split('-')
            
            # 1. ?쒖옉 ?좎쭨 ?뚯떛 (M/D)
            start_m, start_d = map(int, dates[0].split('/'))
            start_year = 2026 if start_m >= 3 else 2027
            start_date = datetime.date(start_year, start_m, start_d)
            
            if len(dates) > 1:
                # 2. 醫낅즺 ?좎쭨 ?뚯떛
                end_str = dates[1]
                if '/' in end_str:
                    # M/D ?뺤떇 (?? 2/2)
                    end_m, end_d = map(int, end_str.split('/'))
                else:
                    # D ?뺤떇 (?? 30)
                    end_m = start_m
                    end_d = int(end_str)
                
                end_year = 2026 if end_m >= 3 else 2027
                end_date = datetime.date(end_year, end_m, end_d)
            else:
                end_date = start_date
            
            events.append({
                'title': f"[吏꾪빐怨??숈궗 ?쇱젙] {title}",
                'start': start_date.isoformat(),
                'end': (end_date + datetime.timedelta(days=1)).isoformat()
            })
        except Exception as e:
            print(f"ERROR parsing line: {line} (Error: {e})")
            
    return events

def main():
    creds = None
    token_path = 'token_calendar.json'
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        calendar_name = "吏꾪빐怨??숈궗 ?쇱젙"
        calendar_id = None
        
        calendar_list = service.calendarList().list().execute()
        for entry in calendar_list['items']:
            if entry['summary'] == calendar_name:
                calendar_id = entry['id']
                print(f"FOUND calendar: {calendar_name} ({calendar_id})")
                break
        
        if not calendar_id:
            new_calendar = {'summary': calendar_name, 'timeZone': 'Asia/Seoul'}
            created_calendar = service.calendars().insert(body=new_calendar).execute()
            calendar_id = created_calendar['id']
            print(f"CREATED calendar: {calendar_name}")

        events_to_add = parse_schedule(TEXT_SCHEDULE)
        
        existing_events = service.events().list(calendarId=calendar_id).execute().get('items', [])
        existing_keys = set((ev['summary'], ev['start'].get('date')) for ev in existing_events if 'date' in ev.get('start', {}))

        print(f"\nProcessing {len(events_to_add)} events...")

        for ev in events_to_add:
            if (ev['title'], ev['start']) in existing_keys:
                print(f"SKIP (exists): {ev['title']} ({ev['start']})")
                continue
                
            event_body = {
                'summary': ev['title'],
                'start': {'date': ev['start']},
                'end': {'date': ev['end']},
            }
            
            service.events().insert(calendarId=calendar_id, body=event_body).execute()
            print(f"ADDED: {ev['title']} ({ev['start']} ~ {ev['end']})")

        print("\nSuccess: All events have been registered.")
        print(f"Link: https://calendar.google.com/calendar/r?cid={calendar_id}")

    except HttpError as error:
        print(f"API ERROR: {error}")

if __name__ == '__main__':
    main()
