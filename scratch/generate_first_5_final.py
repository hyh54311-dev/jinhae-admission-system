import os
import sys
import io
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def calculate_byte(text):
    if not text:
        return 0
    b_count = 0
    for ch in text:
        code = ord(ch)
        if code == 10:
            b_count += 2
        elif code == 13:
            pass
        elif code > 127:
            b_count += 3
        else:
            b_count += 1
    return b_count

def clean_and_replace_forbidden_terms(text):
    if not text:
        return ""
    text = text.replace("**", "").replace("##", "").replace("`", "")
    text = re.sub(r'\b진해\b', '우리 지역', text)
    text = re.sub(r'진해시', '우리 지역', text)
    text = re.sub(r'장복제', '축제', text)
    text = re.sub(r'장복', '축제', text)
    text = re.sub(r'대회', '활동', text)
    return text.strip()

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    # NEIS 바이트 기준 1,100 ~ 1,250 Bytes 목표 맞춤 세특 (430~470자 내외)
    seteuk_1 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 문학 작품이 단순 서사를 넘어 사회적 질병 지표로 기능함에 주목하여 이범선의 ‘오발탄’을 선정함. 주인공 철호의 극심한 치통을 전후 사회 안전망 부재가 유발한 육체적 형상화로 주체적으로 해석하고, ‘전후 서민의 의료 소외 실태가 현대 공공보건 제도 강화의 정당성으로 연결될 수 있는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 이를 소설 속 치통 치료 기회 상실 상황에 대입하고, 예방의학의 사회적 질병 모델을 접목하여 현대 도서·산간 지역의 필수 의료 서비스 접근성 상실 문제와 연계하여 고찰함. 전쟁으로 인한 사회적 혼란이 서민의 건강권 상실로 이어졌음을 재해석하고, 공공보건의료실태 통계 자료를 분석하여 국가 보건 안전망 구축의 당위성을 학문적으로 논증함. 이를 통해 전후 상흔 분석이 과거 기록에 머물지 않고 현대 의료 복지 정책 수립을 위한 핵심 자산이라는 결론을 도출함. 문학을 사회적 문제와 연결 짓는 종합적 사고력이 돋보이며, ‘의료 사각지대 해소를 위한 공공보건 인프라 확충 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )
    
    seteuk_2 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 개인의 절망과 무기력이 사회 구조적 고립에서 비롯되는 양상에 주목하여 이범선의 ‘오발탄’을 선정함. 전후 서민들이 겪은 경제적 빈곤과 자아 정체성 상실을 사회학적 관점에서 주체적으로 해석하고, ‘전후 사회적 고립 현상이 현대 1인 가구의 고독사 및 청년층 은둔 현상과 어떤 인과성을 공유하는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 철호 가족의 해체 과정을 사회학의 아노미 이론과 연계하여 공동체 유대감 붕괴의 위험성을 깊이 있게 분석함. 경제적 결핍이 인간 존엄성을 잠식한다는 원인을 도출하고, 고독사 관련 최신 통계 데이터를 분석하여 논거를 보완함. 이를 통해 서민의 절망이 개인의 성격적 결함이 아니라 사회 구조적 안전망 부재에 기인한다는 학술적 결론을 제시함. 문학을 통해 현대 사회 소외 이웃 문제를 통찰하는 시각이 인상적이며, ‘사회적 약자를 포함하는 공동체적 안녕 체계 구축 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_3 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 시적 소재의 은유를 통해 현대 사회의 통제 메커니즘을 규명하고자 최승호의 ‘대설주의보’를 선정함. 시 속 폭설이 단순 자연 현상을 넘어 군사 독재 시절의 감시를 상징하는 백색 계엄령의 매개체임을 주체적으로 분석하고, ‘현대 정보통신 사회의 빅데이터 알고리즘 수집 권력이 폭설의 통제성과 어떻게 부합하는가?’라는 탐구 질문을 능동적으로 구성함. 시적 화자의 억압된 상황을 디지털 판옵티콘 구조에 대입하여 정보 통제 현상을 경영·통신적 관점에서 조명하고 IT 데이터 윤리 보고서를 분석함. 이를 통해 문학적 은유가 현대 사회의 정보 독점과 알고리즘 편향 현상을 비판하는 유용한 학술적 도구라는 결론을 제시함. 비판적 사고력과 문학적 통찰이 우수하며, ‘디지털 감시 사회에서 개인 자율성을 보장하기 위한 윤리적 기술 제어 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_4 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 문학 속 통제력 상실 상황을 공학적 안전 제어 체계와 연계하고자 이범선의 ‘오발탄’을 선정함. 주인공 철호가 방향성을 잃고 오발탄이라 자조하는 심리를 분석하고, ‘항공우주 공학의 유도 시스템 오작동이 유발하는 제어 상실 위험이 문학적 오발탄의 상황과 어떻게 부합하는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 목적을 잃은 무기의 비극을 항공우주 V1 로켓 개발 사례 및 아리안호 오작동 사건에 대입하여 기술 윤리의 책임을 조명하고 유도 항법 제어(GNC) 시스템 관련 학술 논문을 탐독함. 이를 통해 기술적 제어 시스템 완비가 인간의 생명과 평화를 지키는 필수 조건이라는 결론을 제시함. 문학적 은유를 전공 공학 기술 윤리와 융합하는 시각이 뛰어나며, ‘항공우주 기술의 신뢰성 향상을 위한 시스템 다중화 설계 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_5 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 인물의 심리적 붕괴 과정을 간호학의 스트레스 대처 모델로 해석하고자 이범선의 ‘오발탄’을 선정함. 주인공 철호가 겪는 극심한 치통과 감정 억압을 환경적 자극에 의한 방어기제 붕괴로 주체적으로 분석하고, ‘극심한 환경적 스트레스가 취약계층의 정신건강 파국으로 이어지는 메커니즘을 간호학적으로 어떻게 중재할 것인가?’라는 탐구 질문을 구성함. 인물의 심리적 무기력 상태를 스트레스-취약성 모델에 대입하고 간호학 논문을 탐독하여 지역사회 초기 심리 지지 서비스의 당위성을 도출함. 조기 간호 개입과 복지 체계 구축이 삶을 구하는 핵심 열쇠라는 객관적 결론을 제시함. 전인적 간호관이 돋보이며, ‘취약계층 정신건강 관리를 위한 효과적인 초기 심리 지지 프로그램은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuks = [
        (2, seteuk_1),
        (3, seteuk_2),
        (4, seteuk_3),
        (5, seteuk_4),
        (6, seteuk_5)
    ]
    
    print("=== 바이트 규격(1,100~1,250B) 맞춤 세특 최종 갱신 ===")
    for row_idx, seteuk_text in seteuks:
        b_cnt = calculate_byte(seteuk_text)
        c_cnt = len(seteuk_text)
        print(f"Row {row_idx}: {c_cnt}자 / {b_cnt} Bytes")
        
        body = {
            'values': [[seteuk_text, b_cnt, "완료"]]
        }
        service_sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"탐구보고서_응답!O{row_idx}:Q{row_idx}",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
    print("Successfully updated perfect 5 Seteuk bytes in Google Sheets!")

if __name__ == '__main__':
    main()
