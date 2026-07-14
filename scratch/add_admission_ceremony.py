import os.path
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token_calendar.json'
    if not os.path.exists(token_path):
        print("Error: token_calendar.json not found.")
        return

    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)

    description = """[2026학년도 진해고등학교 입학홍보단 발대식]
- 일시: 2026년 6월 1일(월) 16:00 ~ 17:00 (1시간)
- 장소: 본관 2층 시청각실
- 참석 대상: 총 23명 내외 (최종 선발 학생 20명, 학교장/교감 선생님, 담당 교사 및 부장교사)

★ 세부 시간 계획
- 16:00 ~ 16:05 (5분) | 개식 선언 및 국민의례 (사회: 담당 교사)
- 16:05 ~ 16:15 (10분) | 위임장 및 임명장 수여식 (합격 학생 20명 대상, 학교장 친수)
- 16:15 ~ 16:25 (10분) | 학교장 격려사 및 입학홍보단 대표 선서 (대표 학생 2인)
- 16:25 ~ 16:45 (20분) | 입학홍보단 주요 업무 및 연간 활동 방향 안내 (온·오프라인 콘텐츠 기획 안내)
- 16:45 ~ 16:55 (10분) | 단원 소감 발표 및 단체 기념 촬영 (시청각실 단상)
- 16:55 ~ 17:00 (5분) | 폐식 선언 및 단톡방 프로필 설정 등 마무리

★ 행정사항 및 사전 준비물
1. 임명장 제작: 단원 20명 대상 규격 임명장 및 케이스 준비 (교무실 협조)
2. 선서문 작성: 입학홍보단 대표 선서문 인쇄 및 낭독 보드 준비
3. 현수막 세팅: 시청각실 전면 스크린용 PPT 배경화면 디자인 및 띄우기
4. 다과 및 홍보 장비: 홍보단 단체복 배부, 촬영용 DSLR 및 삼각대 설치 세팅
5. 오픈채팅방 운영: 오픈채팅방 링크 (https://open.kakao.com/o/gVBn6Nwi) 진입 현황 확인 및 인원 대조

※ 본관 2층 시청각실 예약 상태를 확인하고 준비물 세팅 필요.
"""

    event = {
        'summary': '입학홍보단 발대식',
        'location': '진해고등학교 본관 2층 시청각실',
        'description': description.strip(),
        'start': {
            'dateTime': '2026-06-01T16:00:00+09:00',
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': '2026-06-01T17:00:00+09:00',
            'timeZone': 'Asia/Seoul',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30},
                {'method': 'popup', 'minutes': 120},
            ],
        },
    }

    try:
        # Add to primary calendar
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Success: Event created on primary calendar. Link: {event_result.get('htmlLink')}")
        
    except Exception as e:
        print(f"Error creating event: {e}")

if __name__ == '__main__':
    main()
