import os
import sys
import io
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    sheet_id = "1lF0UffUjfKUSyRxia7R3iJfl2A2Hvykc7vtfdaoP7Ts"
    token_path = "token.json"
    
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('sheets', 'v4', credentials=creds)
    
    test_students = [
        {
            "ban": 1, "num": 1, "name": "김문법",
            "topic": "교체 (음절의 끝소리 규칙 & 된소리되기)",
            "initialHypothesis": "음절 끝에 자음이 오면 7개 대표음으로 소리 나고, 안울림 받침 뒤의 예사소리는 무조건 된소리로 바뀐다.",
            "aiHistory": "학생: 옷[옫]이나 꽃[꼳]은 받침이 ㄷ이 되는데, 신고는 'ㄴ' 받침인데 왜 [신꼬]가 되나요?\nAI튜터: 명사인 '신고(申告)'와 동사 '신발을 신고'의 발음을 비교해 보세요! 단어 성격(용언 어간)에 힌트가 있어요.",
            "finalHypothesis": "음절 끝 자음은 7개 대표음(ㄱ,ㄴ,ㄷ,ㄹ,ㅁ,ㅂ,ㅇ)으로 교체되어 소리 난다. 안울림 받침 뒤 예사소리가 된소리로 바뀌는 것 외에도, 용언 어간 받침 'ㄴ, ㅁ' 뒤에 오는 어미의 첫소리 예사소리 역시 된소리로 교체되어 발음된다."
        },
        {
            "ban": 1, "num": 2, "name": "이유음",
            "topic": "교체 (비음화 & 유음화)",
            "initialHypothesis": "받침 ㄱ, ㄷ, ㅂ이 비음 ㄴ, ㅁ을 만나면 무조건 비음 ㅇ, ㄴ, ㅁ으로 변하고, ㄴ과 ㄹ이 만나면 무조건 ㄹㄹ로 변한다.",
            "aiHistory": "학생: 국물[궁물]은 비음화가 맞는데, 생산량[생산냥]은 왜 유음화가 아니라 ㄴ으로 발음되나요?\nAI튜터: 2음절 단어와 3음절 한자어(생산+량)의 구조적 차이를 파악해 볼까요? 한자어 결합에서는 비음화/ㄴ첨가 현상이 선행할 수 있습니다.",
            "finalHypothesis": "받침 ㄱ,ㄷ,ㅂ 뒤에 비음 ㄴ,ㅁ이 오면 각 자음의 위치를 유지한 채 비음(ㅇ,ㄴ,ㅁ)으로 교체된다. ㄴ과 ㄹ이 만나면 유음화(ㄹㄹ)가 일어나는 것이 원칙이나, 독립된 한자어 단어가 결합한 복합어의 경우 [생산냥]처럼 비음화가 적용되는 예외가 존재한다."
        },
        {
            "ban": 1, "num": 3, "name": "박자음",
            "topic": "탈락 (자음군 단순화 & 'ㅎ' 탈락)",
            "initialHypothesis": "음절 끝에 겹받침이 오면 항상 첫 번째 자음만 남고 두 번째 자음은 탈락하며, ㅎ은 모음 뒤에서 사라진다.",
            "aiHistory": "학생: 닭[닥]은 뒤 자음 ㄱ이 남는데 왜 겹받침은 앞 자음만 남는다고 생각했을까요?\nAI튜터: 겹받침 'ㄳ, ㄵ, ㄼ'과 'ㄺ, ㄻ, ㄿ'을 나누어 관찰해 보세요! 어간의 위치에 따라 남는 자음의 규칙성이 달라집니다.",
            "finalHypothesis": "음절 끝 자음군 단순화 시 ㄳ, ㄵ, ㄼ 등은 앞 자음이 남고, ㄺ, ㄻ, ㄿ 등은 뒤 자음이 남는 탈락 현상이 발생한다. 단, '밟-'은 자음 앞에서 [밥-]으로, '넓-'은 특정 단어(넓죽하다)에서 예외적으로 앞 자음 대신 뒤 자음이 탈락하는 현상을 관찰하였다."
        },
        {
            "ban": 1, "num": 4, "name": "최모음",
            "topic": "탈락 (모음 탈락: '으' 탈락, '아/어' 탈락)",
            "initialHypothesis": "어간 끝 모음 '으'는 모음으로 시작하는 어미를 만나면 무조건 탈락하고, 동일한 모음 '아/어'가 겹치면 하나가 소멸한다.",
            "aiHistory": "학생: '크- + -어'가 '커'가 되는 것은 '으' 탈락인데, '가- + -아'가 '가'가 되는 것도 탈락인가요 축약인가요?\nAI튜터: '가아'에서 두 모음 중 하나가 완전히 사라져 표기와 발음이 줄어든 것은 동일 모음 탈락 현상에 해당합니다.",
            "finalHypothesis": "어간 끝 모음 '으'는 모음으로 시작하는 어미(-아/-어)와 결합할 때 표기와 발음에서 모두 탈락하며, 어간 끝 모음이 '아/어'이고 동일한 모음 어미가 결합할 때도 한 모음이 탈락하는 모음 탈락 현상이 일어남을 검증함."
        },
        {
            "ban": 1, "num": 5, "name": "정첨가",
            "topic": "첨가 ('ㄴ' 첨가 & 반모음 첨가)",
            "initialHypothesis": "합성어나 파생어에서 앞 단어가 자음으로 끝나고 뒤 단어가 '이, 야, 여, 요, 유'로 시작하면 소리에 'ㄴ'이 붙어 소리 난다.",
            "aiHistory": "학생: 맨입[맨닙], 알약[알략]은 모두 ㄴ이 첨가된 것 같은데 [알략]은 왜 ㄹ 소리가 나나요?\nAI튜터: '알+약' ➔ 1단계 ㄴ첨가 [알약➔알냑] ➔ 2단계 유음화 [알냑➔알략]으로 연속 변동이 일어난 과정을 추적해 보세요!",
            "finalHypothesis": "자음으로 끝나는 복합어 뒤에 'ㅣ'나 반모음 'ㅣ[j]'로 시작하는 단어가 오면 'ㄴ' 소리가 첨가된다. '알약[알략]'의 경우 'ㄴ' 첨가 후 앞의 유음 'ㄹ'의 영향을 받아 2차적으로 유음화가 일어남을 귀납적으로 도출함."
        },
        {
            "ban": 1, "num": 6, "name": "한축약",
            "topic": "축약 (거센소리되기: 자음 축약)",
            "initialHypothesis": "예사소리 ㄱ, ㄷ, ㅂ, ㅈ이 'ㅎ'을 앞뒤로 만나면 합쳐져서 거센소리 ㅋ, ㅌ, ㅍ, ㅊ 하나로 축약되어 발음된다.",
            "aiHistory": "학생: 좋고[조코], 잡히다[자피다]처럼 ㅎ이 앞에 있든 뒤에 있든 항상 거센소리로 축약되나요?\nAI튜터: 맞습니다! 'ㅎ' 자음의 성격상 예사소리와 결합 순서에 관계없이 거센소리로 융합되는 축약 현상이 발현됩니다.",
            "finalHypothesis": "자음 축약(거센소리되기)은 예사소리(ㄱ, ㄷ, ㅂ, ㅈ)와 'ㅎ'이 앞뒤 위치와 무관하게 결합하여 하나의 거센소리(ㅋ, ㅌ, ㅍ, ㅊ)로 줄어드는 음운 축약 현상임을 관찰 및 검증함."
        }
    ]

    rows = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for s in test_students:
        rows.append([
            now_str, s["ban"], s["num"], s["name"], s["topic"],
            s["initialHypothesis"], s["aiHistory"], s["finalHypothesis"],
            "", "", "대기"
        ])

    body = {'values': rows}
    
    try:
        headers = [[
            "제출일시", "반", "번호", "이름", 
            "문법 탐구 주제", "최초 수립 가설", 
            "AI 피드백 대화 이력", "최종 수정 가설", 
            "세특 초안 (AI)", "글자수(바이트)", "처리 상태"
        ]]
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="문법_수행평가_응답!A1:K1",
            valueInputOption="RAW",
            body={'values': headers}
        ).execute()
        
        res = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="문법_수행평가_응답!A2:K7",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
        print("==========================================================")
        print("✅ 구글 스프레드시트에 6개 문법 주제별 테스트 데이터 기입 완료!")
        print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        print("==========================================================")
    except Exception as e:
        print("Error populating test data:", e)

if __name__ == '__main__':
    main()
