import datetime
import os
import json
import re
import sys
import io

# Windows 肄섏넄?먯꽌 UTF-8(?대え吏 ?ы븿) 異쒕젰 吏??if sys.platform == 'win32':
    try:
        if sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_calendar_events(target_date=None):
    """援ш? 罹섎┛?붿뿉??吏?뺣맂 ?좎쭨???쇱젙??媛?몄샃?덈떎."""
    if target_date is None:
        target_date = datetime.date.today()
    
    token_path = 'token_calendar.json'
    if not os.path.exists(token_path):
        return None, "?좑툘 援ш? 罹섎┛???몄쬆 ?뚯씪???놁뒿?덈떎. PC?먯꽌 濡쒓렇?몄씠 ?꾩슂?⑸땲??"
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
        service = build('calendar', 'v3', credentials=creds)
        
        start_time = datetime.datetime.combine(target_date, datetime.time.min).astimezone().isoformat()
        end_time = datetime.datetime.combine(target_date, datetime.time.max).astimezone().isoformat()
        
        calendar_list = service.calendarList().list().execute()
        all_events = []
        
        for entry in calendar_list['items']:
            events_result = service.events().list(
                calendarId=entry['id'], 
                timeMin=start_time, 
                timeMax=end_time, 
                singleEvents=True, 
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            if events:
                calendar_summary = entry['summary']
                for e in events:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    all_events.append(f"[{calendar_summary}] {e.get('summary')} ({start})")
        
        return all_events, None
    except Exception as e:
        return None, f"??罹섎┛??議고쉶 以?API ?ㅻ쪟 諛쒖깮: {str(e)}"

def scan_local_logs_for_plans():
    """?붾젅洹몃옩 濡쒓렇?먯꽌 理쒓렐 ?멸툒??鍮꾧났???쇱젙?대굹 怨꾪쉷???먯깋?⑸땲??"""
    log_path = 'telegram_assistant.log'
    if not os.path.exists(log_path):
        return []
    
    informal_plans = []
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()[-200:] # 理쒓렐 200以?遺꾩꽍
            
            # ?쇱젙 愿???ㅼ썙???⑦꽩
            patterns = [
                r"(?:?쎌냽|?뚯쓽|誘명똿|?곕뱶?쇱씤|湲고븳|?쇱젙|?ㅼ?以??덉빟).*(?:?????뺤씤)",
                r"(?:?ㅻ뒛|?댁씪|?대쾲 二?.*(?:?댁빞|媛?留뚮궇)"
            ]
            
            for line in lines:
                if '[?섏떊]' in line: # ?ъ슜??硫붿떆吏 ?쇱씤留??꾪꽣留?                    for p in patterns:
                        if re.search(p, line):
                            # ?쒓컙 ?뺣낫? ?④퍡 蹂닿?
                            informal_plans.append(line.strip())
                            break
    except:
        pass
    return informal_plans

def get_unified_briefing(date_offset=0):
    """紐⑤뱺 ?뚯뒪瑜?醫낇빀?섏뿬 釉뚮━???띿뒪?몃? ?앹꽦?⑸땲??"""
    target_date = datetime.date.today() + datetime.timedelta(days=date_offset)
    date_str = target_date.strftime("%Y-%m-%d")
    
    briefing = [f"?뱟 {date_str} ?쇱젙 釉뚮━???곗씠??]
    
    # 1. 罹섎┛???뺤씤
    events, error = get_calendar_events(target_date)
    briefing.append("\n--- [援ш? 罹섎┛??怨듭떇 ?쇱젙] ---")
    if error:
        briefing.append(error)
    elif not events:
        briefing.append("?깅줉??怨듭떇 ?쇱젙???놁뒿?덈떎.")
    else:
        briefing.extend([f"??{ev}" for ev in events])
    
    # 2. 濡쒖뺄 湲곗뼲(濡쒓렇) ?뺤씤
    log_plans = scan_local_logs_for_plans()
    briefing.append("\n--- [?쒖뒪??湲곗뼲 諛?鍮꾧났??怨꾪쉷] ---")
    if not log_plans:
        briefing.append("理쒓렐 ??붿뿉???멸툒???뱀씠?ы빆???놁뒿?덈떎.")
    else:
        briefing.extend([f"??湲곕줉: {plan}" for plan in log_plans[-5:]]) # 理쒓렐 5媛쒕쭔
        
    briefing.append("\n--- [援ш? ?쒖뒪??????] ---")
    briefing.append("?꾩옱 ?쒖뒪???곕룞? 罹섎┛???몄쬆 ???④퍡 ?뺤씤?⑸땲??")
    
    return "\n".join(briefing)

if __name__ == "__main__":
    print(get_unified_briefing())

    # ?뵄 [異붽?] ?묒뾽 ?꾨즺 ?앹뾽 ?뚮┝ (?꾩옱 ?낅Т??PC?먯꽌留??ㅽ뻾)
    try:
        import subprocess
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        current_pc = os.environ.get('COMPUTERNAME', 'UNKNOWN').upper()
        popup_script = os.path.join(BASE_DIR, "notify_popup_perfect.py")
        
        # '2026'???ы븿?섏뼱 ?덇굅??DESKTOP ??愿由ъ슜 PC??寃쎌슦 ?뚮┝ 異쒕젰
        is_correct_pc = ("2026" in current_pc) or ("DESKTOP" in current_pc)
        
        if is_correct_pc and os.path.exists(popup_script):
            subprocess.Popen([sys.executable, popup_script])
    except Exception as e:
        pass
