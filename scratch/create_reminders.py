import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def create_calendar_event(service, event_body):
    try:
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        print(f"Created event: {event.get('htmlLink')}")
        return True
    except Exception as e:
        print(f"Error creating event: {e}")
        return False

def main():
    token_path = 'token_calendar.json'
    if not os.path.exists(token_path):
        print("token_calendar.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    # Event 1: 1 day before club activity (activity on 2026-06-17, reminder on 2026-06-16)
    event1 = {
        'summary': '[경남영상공모전] 내일 동아리 활동 - 학생 팀 모집 안내',
        'description': (
            '내일(6/17, 수요일)은 창체 동아리 활동일입니다!\n'
            '경남교육영상공모대회 참가를 위한 학생 팀(2~5명)을 모집하고 홍보를 준비하세요.'
        ),
        'start': {
            'date': '2026-06-16',
        },
        'end': {
            'date': '2026-06-17',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 540}, # Notification at 9:00 AM on June 16
                {'method': 'email', 'minutes': 540},
            ],
        }
    }
    
    # Event 2: 1 week before summer vacation (vacation starts 2026-07-22, reminder on 2026-07-15)
    event2 = {
        'summary': '[경남영상공모전] 방학 1주일 전 - 영상 기획 및 AI 아이디어 검토',
        'description': (
            '여름방학(7/22 시작)이 일주일 남았습니다! 공모전 영상 기획 및 준비를 시작하세요.\n\n'
            '[추천 AI 교육 영상 주제 및 아이디어]\n'
            '1. "AI, 나의 첫 번째 러닝메이트" (새로운 교육 방식과 성장)\n'
            '   - AI 튜터/보조교사 서비스를 활용해 자신의 한계를 극복하고 스스로 학업 성취와 자존감을 키워나가는 학생의 성장기 및 이를 격려하는 교사의 이야기.\n'
            '2. "질문하는 교실, 생각하는 우리" (변화하는 학교)\n'
            '   - 주입식 학습 대신 프롬프트 엔지니어링이나 AI 코딩 프로젝트 수업을 진행하며, "좋은 질문을 던지는 법"과 주체적인 문제해결력을 배워가는 교실의 변화 다큐멘터리.\n'
            '3. "기술에 온기를 더하다" (교육적 감성/감동 순간)\n'
            '   - AI 음성 합성(TTS)이나 AI 번역 기술을 활용해 특수학급 학생 또는 다문화 가정 학생의 수업 장벽을 허물고 따뜻하게 소통하는 감동적인 학교 일상 드라마.'
        ),
        'start': {
            'date': '2026-07-15',
        },
        'end': {
            'date': '2026-07-16',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 540}, # Notification at 9:00 AM on July 15
                {'method': 'email', 'minutes': 540},
            ],
        }
    }
    
    print("Registering reminders in Google Calendar...")
    success1 = create_calendar_event(service, event1)
    success2 = create_calendar_event(service, event2)
    
    if success1 and success2:
        print("Both reminders registered successfully!")
    else:
        print("There was an issue registering one or both events.")

if __name__ == '__main__':
    main()
