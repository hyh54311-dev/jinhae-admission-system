import os
import sys
import json
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 추가 설정
TARGET_DIR = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 2학년 수업&수행&평가\1학기"
MD_FILE_NAME = "2026학년도_2학년_문학_수행평가_세특_자동화_시스템_개발_보고서.md"
SHORTCUT_FILE_NAME = "2026학년도_2학년_문학_수행평가_세특_자동화_시스템_개발_보고서.url"

# 구글 인증 스코프
SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
        token_path = os.path.join(base_dir, 'token.json')
        
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json is missing or invalid. Please re-authenticate.")
    return creds

def upload_as_gdoc(md_path, doc_title):
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # 마크다운을 HTML로 변환
    html_body = markdown.markdown(md_text, extensions=['extra', 'nl2br'])
    
    # 구글 문서 스타일링
    styled_html = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <style>
            body {{ font-family: 'Arial', '맑은 고딕', sans-serif; line-height: 1.6; color: #333333; font-size: 11pt; }}
            h1 {{ color: #0284c7; border-bottom: 2px solid #e0f2fe; padding-bottom: 8px; margin-top: 30px; font-size: 20pt; }}
            h2 {{ color: #0369a1; border-left: 6px solid #0284c7; padding-left: 12px; margin-top: 25px; font-size: 15pt; }}
            h3 {{ color: #0f172a; margin-top: 20px; font-size: 12pt; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 10pt; }}
            th, td {{ border: 1px solid #bae6fd; padding: 10px; text-align: left; }}
            th {{ background-color: #f0f9ff; font-weight: bold; color: #0369a1; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            blockquote {{ border-left: 4px solid #0284c7; padding: 12px; color: #475569; background-color: #f0f9ff; margin: 15px 0; border-radius: 4px; }}
            code {{ font-family: 'Consolas', 'Nanum Gothic Coding', monospace; background-color: #f8fafc; padding: 2px 6px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 9.5pt; color: #0f172a; }}
            pre {{ background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; overflow-x: auto; }}
            pre code {{ border: none; padding: 0; background-color: transparent; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    temp_html_path = md_path.replace('.md', '_temp.html')
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)

    file_metadata = {
        'name': doc_title,
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(temp_html_path,
                            mimetype='text/html',
                            resumable=True)
    
    # 구글 문서로 업로드
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    link = file.get('webViewLink')

    # 누구나 링크가 있으면 볼 수 있도록 권한 설정
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
    except Exception as perm_ex:
        print(f"Warning: Failed to set permission: {perm_ex}")

    # 임시 HTML 파일 삭제
    try:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
    except Exception as e:
        print(f"Temporary file deletion deferred: {e}")

    return link

def create_report_content():
    # 백엔드 및 프론트엔드 코드 로딩을 통해 보고서에 코드 블록을 정확히 임베딩
    base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    
    try:
        with open(os.path.join(base_dir, 'Code_Literature.gs'), 'r', encoding='utf-8') as f:
            gs_code = f.read()
    except:
        gs_code = "// Code_Literature.gs 파일을 읽을 수 없습니다."

    # 프론트엔드 코드는 너무 기므로 핵심 부분만 발췌하거나 설명으로 대체하여 용량 줄임
    try:
        with open(os.path.join(base_dir, 'index_literature.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
            # 바이트 계산기 및 작은 따옴표 유효성 검사 부분만 슬라이스해서 가져오기
            validation_idx = html_content.find("function validateForm()")
            if validation_idx != -1:
                html_snippet = html_content[validation_idx:validation_idx+1500] + "\n\n  // ... (중략) ..."
            else:
                html_snippet = "validateForm() 함수를 찾을 수 없습니다."
    except:
        html_snippet = "index_literature.html 파일을 읽을 수 없습니다."

    report = f"""# 2026학년도 2학년 문학 수행평가 세특 자동화 시스템 개발 보고서

본 보고서는 진해고등학교 2학년 문학 수행평가(주제: **현대적 관점으로 고전시가 비평하기**)에서 학생 답안 수집, 실시간 글자수 및 조건 만족 유효성 검증, 그리고 Gemini 2.5 Pro 모델을 활용한 생기부 세부능력 및 특기사항(세특) 초안 자동화 시스템 개발 과정과 핵심 기술 사양을 집대성한 문서입니다.

---

## 1. 시스템 개요 및 개발 목적

* **목적**: 
  - 학생들의 현대적 관점 고전시가 비평문 답안을 체계적으로 수집하는 학생용 웹앱 구축.
  - 제출된 학생들의 서술문을 교육과정 성취기준 및 기재 금지 요소를 완벽히 준수하여 350자 내외의 고품질 세특 초안으로 자동 생성하는 자동화 기능 구현.
* **시스템 구성**:
  - **프론트엔드 웹앱 (`index_literature.html`)**: 학생용 모던/프리미엄 반응형 제출 화면.
  - **백엔드 엔진 (`Code_Literature.gs`)**: 구글 스프레드시트 기반의 명렬 관리, 데이터 누적 및 Gemini API 연동.

---

## 2. 프론트엔드 사양 및 핵심 구현 기술 (`index_literature.html`)

### 2.1 프리미엄 디자인 명세
* **색상 시스템**: 하늘색 테마(`#0284c7`, `#e0f2fe`)와 은은한 그라데이션 백그라운드 적용.
* **진해고등학교 교표 최상위 워터마크 배치**:
  - 교표 이미지(`school_logo.png` base64 인코딩)를 `body::before` 의 최상위 레이어(`z-index: 9999`)에 배치하고 **투명도를 `0.08` (8%)**로 조절했습니다.
  - `pointer-events: none` 스타일을 지정하여 로고가 텍스트 위에 얹어져 있어도 하단의 입력창과 버튼 클릭 등의 조작에 전혀 간섭이 없도록(Click-through) 처리했습니다.

### 2.2 실시간 입력값 유효성 검사 (Validation)
* **500자 이상 실시간 카운트**: 글자 수 달성 시 입력 필드 색상 피드백 제공.
* **다양한 작은 따옴표 패턴 정규식 지원**:
  - 학생들의 한글 키보드나 모바일 기기 문서 편집기가 일자형 작은 따옴표(`'`) 대신 자동으로 교체하는 둥근 작은 따옴표(`‘`, `’`)나 전각 기호(`＇`), 조절 기호(`ʼ`) 등 모든 홑따옴표 종류를 인식할 수 있도록 정규식 검사를 강화했습니다.
  - **구현 정규식**: `var quoteRegex = /['‘’’ʼ＇].+?['‘’’ʼ＇]/;`

---

## 3. 백엔드 사양 및 핵심 구현 기술 (`Code_Literature.gs`)

백엔드는 Google Apps Script 기반으로 작동하며 스프레드시트에 내장되어 동작합니다.

### 3.1 가로 명렬부 파싱 및 필터링 (`getRoster`)
* 스프레드시트의 `Sheet1` 시트에서 가로로 길게 연결된 반별 명단(1열: 1반 번호, 2열: 1반 이름...)을 읽어와 JSON 구조로 매핑합니다.
* 나이스 시트에서 2행에 존재하는 학급 총 인원수 요약 행(예: `"31명"`)을 자동 필터링하는 정규식 필터(`!/^\d+\s*명$/.test(name)`)를 탑재하여 학생 이름이 아닌 값이 드롭다운에 출력되는 현상을 원천 방지했습니다.

### 3.2 나이스(NEIS) 규격 부합 바이트 카운터 (`calculateByte`)
* 나이스 생기부 기록 제한(과목별 1,500바이트)을 정확히 모니터링할 수 있도록 교육부 나이스 내부 로직과 소수점 오차도 없이 일치하는 바이트 카운팅 알고리즘을 작성했습니다.
* **산정 기준**: 한글/한자/특수문자/전각기호 = 3바이트, 영문/숫자/공백/ASCII = 1바이트, 줄바꿈(Enter) = 2바이트(CRLF의 CR 무시).

### 3.3 백그라운드 연쇄 자동화 처리 (트리거 연동)
* Gemini Pro급 모델은 실시간 심층 추론(Thinking)을 동반하여 응답 지연(인당 약 17~18초)이 발생합니다. 5명 처리 시 약 1분 40초가 소요됩니다.
* 구글 스크립트 실행 시간 초과(6분 룰)를 예방하기 위해 **5명씩 끊어서 실행하는 배치 처리기**를 도입했습니다.
* 배치 실행 완료 시 대기 중인 학생이 더 남아있으면 **1분 주기 시간 기반 트리거(Time-based Trigger)**를 백그라운드에 자동으로 등록한 뒤 실행을 종료합니다.
* 백엔드가 1분마다 스스로 깨어나 5명씩 연속 처리를 수행하고, 모든 학생의 생기부 초안이 채워지면 **트리거를 자동으로 해제 및 안전 종료**합니다. (수동 중단 메뉴 동시 지원)

---

## 4. Gemini 2.5 Pro 프롬프트 및 API 설정

### 4.1 프롬프트 지침 설계
* **문학 성취기준 맵핑**: `[12문학01-06]`(내용과 형식의 유기성) 및 `[12문학01-10]`(화자의 정서와 자신의 가치관 비교)을 국어과 교과 역량과 연계하여 350자 내외의 밀도 높은 문장으로 완성합니다.
* **생기부 기재 금지 사항 차단**: 부모 직업, 교외 봉사 실적, 교내외 대회/수상, 자격증, 장학금, 사설 기관 상호명 등의 요소가 들어가지 않도록 프롬프트 가이드에 명문화하여 원천 배제했습니다.
* **어조**: 생활기록부 규격에 맞춰 `~함.`, `~임.` 형태의 명사형 및 음절형 어미로 통일성 있게 종결되도록 작성합니다.

### 4.2 API 스키마 및 추론 토큰 제어
* **`responseSchema` 적용**: 무의미한 부연 설명이나 마크다운 기호 없이 순수 JSON 포맷(`{{ "seteuk": "..." }}`)으로만 정확히 반환되도록 강제했습니다.
* **`maxOutputTokens: 8192` 확장**: `gemini-2.5-pro`와 같은 추론형 모델은 스스로 생각하는 단계(Thinking Process)에서 약 1,800개 이상의 토큰을 소모합니다. 생성 한도가 부족해 끊기는 현상(`MAX_TOKENS` 에러)이 없도록 한도를 최대치로 확장해 충분한 여유 공간을 확보했습니다.

---

## 5. 핵심 소스코드

### 5.1 백엔드 Apps Script (`Code_Literature.gs`)

```javascript
{gs_code}
```

### 5.2 프론트엔드 유효성 검사부 스니펫 (`index_literature.html`)

```javascript
{html_snippet}
```

---

## 6. 결론 및 향후 유지보수
* 본 시스템은 교육부의 기재 규정과 나이스 입력 제한 바이트 수를 정밀하게 충족하여 교사의 실제 입력 과정을 극도로 단축할 수 있도록 설계되었습니다.
* 백엔드에 안전 필터링 사유 등으로 생성이 보류되거나 제한될 경우, 에러의 근원(SAFETY, MAX_TOKENS, RECITATION 등)을 짚어주는 예외 처리가 갖춰져 있어 사용자 에러 관리가 용이합니다.
"""
    return report

def main():
    # 폴더가 없으면 생성
    if not os.path.exists(TARGET_DIR):
        try:
            os.makedirs(TARGET_DIR)
            print(f"Directory created: {TARGET_DIR}")
        except Exception as e:
            print(f"Error creating directory {TARGET_DIR}: {e}")
            sys.exit(1)

    md_path = os.path.join(TARGET_DIR, MD_FILE_NAME)
    shortcut_path = os.path.join(TARGET_DIR, SHORTCUT_FILE_NAME)

    print("Generating report markdown content...")
    report_content = create_report_content()
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"Markdown report saved at: {md_path}")

    # 구글 문서 업로드 진행
    print("Uploading markdown to Google Drive as Google Doc...")
    try:
        gdoc_link = upload_as_gdoc(md_path, "2026학년도 2학년 문학 수행평가 세특 자동화 시스템 개발 보고서")
        print(f"Google Doc link successfully created: {gdoc_link}")
        
        # 윈도우 인터넷 단축키(.url) 생성
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write("[InternetShortcut]\n")
            f.write(f"URL={gdoc_link}\n")
        print(f"Shortcut file saved at: {shortcut_path}")
        
    except Exception as e:
        print(f"Error creating Google Doc or shortcut: {e}")

if __name__ == '__main__':
    main()
