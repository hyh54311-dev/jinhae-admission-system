import os
import sys
import io
import json
import re
import time
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
    # 마크다운 기호 제거
    text = text.replace("**", "").replace("##", "").replace("`", "")
    # 금지어 치환
    text = re.sub(r'\b진해\b', '우리 지역', text)
    text = re.sub(r'진해시', '우리 지역', text)
    text = re.sub(r'장복제', '축제', text)
    text = re.sub(r'장복', '축제', text)
    text = re.sub(r'대회', '활동', text)
    # 일반 작은따옴표를 둥근 작은따옴표로 변환 (필요시)
    return text.strip()

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    # 1반 1번(강준우), 1반 3번(고은석), 1반 5번(김대현), 1반 13번(박범준), 1반 14번(박시완)
    # 정성껏 작성된 고품질 6단계 세특 초안 (바이트 규격: 1,100 ~ 1,250 Bytes)
    
    seteuk_1 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 문학 작품이 단순한 서사를 넘어 사회적 질병 지표로 기능할 수 있다는 점에 주목하여 이범선의 ‘오발탄’을 선정함. 주인공 철호의 비극적 환경과 극심한 치통이 전후 사회 안전망 부재에서 비롯된 육체적 형상화임을 주체적으로 분석하고, ‘전후 서민의 의료 소외 실태가 현대 공공보건 제도 강화의 정당성으로 연결될 수 있는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 이를 소설 속 주인공의 치통 수술 상실 상황에 대입하고, 예방의학의 사회적 질병 모델을 접목하여 현대 도서·산간 지역의 필수 의료 서비스 접근성 상실 문제와 연계하여 고찰함. 전쟁으로 인한 사회적 혼란이 서민의 건강권 상실로 이어졌음을 재해석하고, 공공보건의료실태 통계 자료를 분석하여 국가 보건 안전망의 당위성을 논증하는 학문적 역량을 발휘함. 이를 통해 전후 사회적 상흔 분석이 과거의 기록이 아닌 현대의 의료 복지 정책 수립을 위한 핵심 자산이라는 결론을 도출함. 문학을 사회 구조적 문제 해결과 연결 짓는 종합적 사고력이 돋보이며, ‘의료 사각지대 해소를 위한 공공보건 인프라 확충 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )
    
    seteuk_2 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 개인의 절망과 무기력이 사회 구조적 고립에서 비롯되는 양상에 주목하여 이범선의 ‘오발탄’을 선정함. 전후 서민들이 겪은 극심한 경제적 빈곤과 자아 정체성 상실 과정을 사회학적 비평 관점에서 해석하고, ‘전후 사회적 고립 현상이 현대 1인 가구의 고독사 및 청년층 은둔 현상과 어떤 인과성을 공유하는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 철호 가족의 해체 과정을 현대 사회의 사회적 안전망 결여에 대입하고, 이를 사회학의 아노미 이론과 연계하여 공동체적 유대감 붕괴의 위험성을 깊이 있게 분석함. 경제적 결핍이 단순한 물질적 문제를 넘어 인간 존엄성과 삶의 의지를 잠식한다는 인과적 원인을 도출하고, 사회학 학술 논문 및 고독사 관련 최신 데이터를 분석하여 논거를 보완함. 이를 통해 서민의 절망이 개인의 성격적 결함이 아니라 사회 구조적 안전망 부재에 기인한다는 학술적 결론을 제시함. 문학 작품을 통해 현대 사회의 소외 이웃과 사회적 고립 문제를 다각도로 통찰하는 시각이 인상적이며, ‘사회적 약자를 포함하는 공동체적 안녕 체계 구축 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_3 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 시적 소재의 은유를 분석하여 현대 사회의 통제 메커니즘을 규명하고자 최승호의 ‘대설주의보’를 선정함. 시에 등장하는 폭설이 단순한 자연 현상을 넘어 군사 독재 시절의 감시와 통제를 상징하는 ‘백색 계엄령’의 은유적 매개체임을 주체적으로 분석하고, ‘현대 정보통신 사회의 빅데이터 알고리즘 수집 권력이 시 속 폭설의 통제성과 어떻게 부합하는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 시적 화자의 억압된 상황을 현대 사회의 디지털 판옵티콘 구조에 대입하고, 사용자 행동을 무의식중에 제한하는 정보 통제 현상과 대조하여 통신·경영적 관점에서 비판적으로 조명함. 자연 재해의 통제성이 정보 기술의 윤리적 가이드라인 부재와 결합할 때 발생하는 위험성을 인과적으로 재해석하고, 관련 언론 기사 및 IT 데이터 윤리 보고서를 분석하여 비평적 논거를 보완함. 이를 통해 문학적 은유가 현대 사회의 정보 독점과 알고리즘 편향 현상을 비판하는 유용한 도구로 작동할 수 있다는 결론을 제시함. 비판적 사고력과 문학적 통찰이 우수하며, ‘디지털 감시 사회에서 개인의 자율성을 보장하기 위한 윤리적 기술 제어 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_4 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 문학 속 통제력 상실 상황을 공학적 안전 제어 체계와 연계하고자 이범선의 ‘오발탄’을 선정함. 주인공 철호가 방향성을 잃고 오발탄이라 자조하는 절박한 심리를 분석하고, ‘항공우주 공학에서 유도 시스템 오작동이 유발하는 제어 상실 위험이 문학적 오발탄의 상황과 어떻게 부합하는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 목적을 잃은 무기가 서민의 비극으로 이어진 전쟁사를 현대 항공우주 공학의 V1 로켓 개발 사례 및 아리안호 오작동 사건에 대입하여 과학 기술의 안전망 책임을 깊이 있게 분석함. 한 줄의 소프트웨어 오류가 대형 참사로 직결될 수 있음을 공학적 관점에서 재해석하고, 항공우주 유도 항법 제어(GNC) 시스템 관련 학술 자료 및 논문을 탐독하여 기술적 논거를 보완함. 이를 통해 기술적 제어 시스템 완비가 인간의 생명과 평화를 지키는 필수 전제 조건이라는 학술적 결론을 제시함. 문학적 은유를 전공 공학 분야의 기술 윤리와 연결 짓는 지적 유연성이 뛰어나며, ‘항공우주 기술의 신뢰성 향상을 위한 시스템 다중화 설계 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_5 = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 인물의 심리적 붕괴 과정을 간호학의 스트레스 대처 모델로 해석하고자 이범선의 ‘오발탄’을 선정함. 주인공 철호가 겪는 극심한 치통과 감정 억압이 단순한 개인 질환이 아닌 외부 환경 자극에 의한 방어기제 붕괴임을 주체적으로 분석하고, ‘극심한 환경적 스트레스가 취약계층의 정신건강 파국으로 이어지는 메커니즘을 간호학적으로 어떻게 중재할 것인가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 인물의 심리적 무기력 상태를 정신간호학의 스트레스-취약성 모델에 대입하고, 현대 사회 취약계층이 겪는 정신건강 사각지대 문제와 연계하여 지지 체계의 중요성을 도출함. 인물의 비극을 개인의 성격 결함이 아닌 환경적 자극의 누적으로 인한 정신적 소진으로 재해석하고, 간호학 논문 및 정신사회적 발달 이론 서적을 탐독하여 학술적 논거를 보완함. 이를 통해 조기 간호 개입과 지역사회 정신건강 복지 체계 구축이 삶을 구하는 핵심 열쇠라는 객관적 결론을 제시함. 인간 고통에 대한 깊은 공감과 전인적 간호관이 돋보이며, ‘취약계층의 정신건강 관리를 위한 효과적인 초기 심리 지지 프로그램은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuks = [
        (2, seteuk_1),
        (3, seteuk_2),
        (4, seteuk_3),
        (5, seteuk_4),
        (6, seteuk_5)
    ]
    
    print("=== 첫 5명 세특 검증 및 시트 기입 ===")
    for row_idx, seteuk_text in seteuks:
        b_cnt = calculate_byte(seteuk_text)
        c_cnt = len(seteuk_text)
        print(f"Row {row_idx}: {c_cnt}자 / {b_cnt} Bytes")
        print(f"내용: {seteuk_text}\n")
        
        # Update Sheets (O열: 세특 초안, P열: 바이트 수, Q열: 처리 상태)
        body = {
            'values': [[seteuk_text, b_cnt, "완료"]]
        }
        service_sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"탐구보고서_응답!O{row_idx}:Q{row_idx}",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
    print("Successfully updated first 5 students in Google Sheets!")

if __name__ == '__main__':
    main()
