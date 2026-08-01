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
    
    # 실제 구글 시트 Row 2 ~ 6 (고은석, 김대현, 김태엽, 박범준, 박시완) 정밀 맞춤 세특
    seteuk_go_eun_seok = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 전쟁 트라우마와 무기력이 신체적·정신적 건강에 미치는 영향에 주목하여 이범선의 ‘오발탄’을 선정함. 주인공 철호의 극심한 치통과 심리적 유기 상태를 전후 사회의 트라우마로 해석하고, ‘전후 사회적 절망감이 신체 활동 및 체육 교육적 중재를 통해 어떻게 정신 건강 회복으로 이어질 수 있는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 인물의 정서적 무기력을 스포츠 심리학의 신체 활동-스트레스 경감 모델에 대입하여 체육 교육의 치료적 가치를 도출함. 스포츠 의학 논문과 정서 회복 임상 데이터를 분석하여 신체 활동이 트라우마 극복의 유용한 기제라는 결론을 제시함. 문학적 비극을 체육학적 관점의 전인적 건강과 융합하는 시각이 인상적이며, ‘트라우마 예방을 위한 신체 활동 프로그램 설계 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )
    
    seteuk_kim_dae_hyeon = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 사회적 이념 갈등과 정보 통신 기술의 관계에 주목하여 최인훈의 ‘광장’을 선정함. 명준이 겪는 남북한 이념의 밀실과 광장의 한계를 통제 사회의 은유로 주체적으로 해석하고, ‘현대 AI 및 반도체 기술의 정보 수집 독점이 개인의 사상적 자율성을 억압하는 디지털 통제로 변질될 위험이 있는가?’라는 탐구 질문을 구성함. 시적 화자와 명준의 소외를 디지털 판옵티콘 구조에 대입하고 AI 윤리 가이드라인을 분석함. 이를 통해 문학 속 정보 독점 비판이 현대 AI 및 반도체 기술의 윤리적 제어 당위성으로 이어진다는 결론을 도출함. IT 기술 윤리와 문학을 융합하는 비판적 사고력이 뛰어나며, ‘인공지능 편향성을 제어하기 위한 반도체 및 기술 설계 가이드라인은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_kim_tae_yeop = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 국가적 위기 상황 속 군인의 숭고한 사명감에 주목하여 이범선의 ‘오발탄’을 선정함. 전후 사회 서민들의 비극과 안보적 혼란 속 인물 심리를 주체적으로 분석하고, ‘전후 사회적 혼란 속에서 군인의 안보적 책임감과 헌신이 국민의 평화적 일상을 지키는 데 어떤 역할을 하는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 철호의 비극을 국가 안전망 붕괴 상황에 대입하고, 이를 군사학의 국가 안보 및 리더십 가치관과 연계하여 분석함. 안보 관련 연구 논문을 탐독하여 군인의 철저한 사명감이 국가 존립의 핵심이라는 결론을 제시함. 문학 작품을 올바른 국가관과 군인 정신으로 재해석하는 통찰이 돋보이며, ‘국민의 안전을 보장하기 위한 미래 군 리더십 역량 강화 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_park_beom_jun = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 문학 속 통제력 상실 상황을 공학적 안전 제어 체계와 연계하고자 이범선의 ‘오발탄’을 선정함. 주인공 철호가 방향성을 잃고 오발탄이라 자조하는 심리를 분석하고, ‘항공우주 공학의 유도 시스템 오작동이 유발하는 제어 상실 위험이 문학적 오발탄의 상황과 어떻게 부합하는가?’라는 탐구 질문을 능동적으로 구성하여 비평함. 목적을 잃은 무기의 비극을 항공우주 V1 로켓 개발 사례 및 아리안호 오작동 사건에 대입하여 기술 윤리의 책임을 조명하고 유도 항법 제어(GNC) 시스템 관련 학술 논문을 탐독함. 이를 통해 기술적 제어 시스템 완비가 인간의 생명과 평화를 지키는 필수 조건이라는 결론을 제시함. 문학적 은유를 전공 공학 기술 윤리와 융합하는 시각이 뛰어나며, ‘항공우주 기술의 신뢰성 향상을 위한 시스템 다중화 설계 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuk_park_si_wan = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 인물의 심리적 붕괴 과정을 간호학의 스트레스 대처 모델로 해석하고자 이범선의 ‘오발탄’을 선정함. 주인공 철호가 겪는 극심한 치통과 감정 억압을 환경적 자극에 의한 방어기제 붕괴로 주체적으로 분석하고, ‘극심한 환경적 스트레스가 취약계층의 정신건강 파국으로 이어지는 메커니즘을 간호학적으로 어떻게 중재할 것인가?’라는 탐구 질문을 구성함. 인물의 심리적 무기력 상태를 스트레스-취약성 모델에 대입하고 간호학 논문을 탐독하여 지역사회 초기 심리 지지 서비스의 당위성을 도출함. 조기 간호 개입과 복지 체계 구축이 삶을 구하는 핵심 열쇠라는 객관적 결론을 제시함. 전인적 간호관이 돋보이며, ‘취약계층 정신건강 관리를 위한 효과적인 초기 심리 지지 프로그램은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )

    seteuks = [
        (2, seteuk_go_eun_seok),
        (3, seteuk_kim_dae_hyeon),
        (4, seteuk_kim_tae_yeop),
        (5, seteuk_park_beom_jun),
        (6, seteuk_park_si_wan)
    ]
    
    print("=== 정밀 시트 행 매칭 (Row 2~6: 고은석~박시완) 세특 갱신 ===")
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
        
    print("Successfully updated actual first 5 students in Google Sheets!")

if __name__ == '__main__':
    main()
