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
    
    # 임지민 학생 정밀 고품질 세특 초안 (진로: 의약학 계열, 희망진로 필드의 사족 멘트 완벽 제거)
    clean_seteuk = clean_and_replace_forbidden_terms(
        "고전시가 현대적 관점으로 비평하기 활동에서 문학 속 의료 접근성 문제를 현대 보건의료 정책과 연계하고자 이범선의 ‘오발탄’을 선정함. 소설 속 철호 아내의 출산 비극과 극심한 치통 방치를 전후 사회 보건 의료 안전망의 부재로 해석하고, ‘오발탄으로 본 대한민국 의료 접근성-지역의사제는 치료받을 권리의 공백을 메울 수 있을까’라는 탐구 질문을 능동적으로 구성함. 철호 가족의 비극을 현대 지역 간 의료 불균형 현상에 대입하여 의약학적 관점에서 지역 필수 의료 인프라 확충의 당위성을 도출함. 보건복지부 관련 자료 및 의약학 논문을 분석하여 치료받을 권리의 공공성 강화를 위한 정책적 논거를 보완함. 이를 통해 문학적 비극 비평이 현대 필수 의료 공백 해소를 위한 학술적 대안 도출로 연결된다는 객관적 결론을 제시함. 전인적 보건의료관이 돋보이며, ‘의약학 분야에서 공공보건 인프라의 지역적 형평성을 보장할 제도적 방안은 무엇인가?’라는 물음으로 탐구를 확장하려는 태도가 돋보임."
    )
    
    b_cnt = calculate_byte(clean_seteuk)
    c_cnt = len(clean_seteuk)
    print(f"Lim Ji-min Seteuk: {c_cnt}자 / {b_cnt} Bytes")
    print(f"내용: {clean_seteuk}")
    
    # 42행 갱신
    body = {
        'values': [[clean_seteuk, b_cnt, "완료"]]
    }
    service_sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="탐구보고서_응답!O42:Q42",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    print("Successfully updated Lim Ji-min's Seteuk in Google Sheets Row 42!")

if __name__ == '__main__':
    main()
