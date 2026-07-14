import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 스프레드시트와 토큰이 있는 워크스페이스
TOKEN_FILE = "token.json"

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                return creds
        except Exception as e:
            print("Error loading credentials:", e)
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No valid credentials found.")
        return
        
    try:
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)
        
        # 1. 구글 문서 양식 생성
        title = "[양식] 문학 교과 심층 탐구 보고서 (진해고등학교)"
        doc = docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc.get("documentId")
        print(f"Created Google Doc with ID: {doc_id}")
        
        # 2. 문서 서식 및 가이드 문구 편집 (batchUpdate)
        # 본문 텍스트 구조 정의
        intro_text = (
            "진해고등학교 2학년 문학 교과 심층 탐구 보고서 양식\n"
            "※ 본 양식은 구글 문서 사본을 복사하거나 다운로드하여 본인의 내용으로 채운 뒤, PDF 또는 한글 파일로 변환하여 문학 탐구 보고서 제출 웹앱을 통해 업로드해 주십시오.\n\n"
            "■ 학생 인적 사항 및 주제\n"
            " - 학년: 2학년\n"
            " - 반 / 번호 / 이름: [   ]반 [   ]번 이름: [       ]\n"
            " - 희망 진로 (또는 관심 분야): [                     ]\n"
            " - 탐구 대상 문학 작품 및 저자: [                     ]\n"
            " - 탐구 주제 (제목): [                                                     ]\n\n"
            "■ 탐구 내용 서술부\n\n"
            "1. 탐구 동기 (수업 시간 배운 내용과의 연계)\n"
            " - 작성 팁: 수업 중 어떤 대목, 개념, 시어 등에서 지적 호기심이 생겼는지 논리적으로 서술해 주세요.\n"
            " [여기에 작성하세요]\n\n"
            "2. 탐구 내용 및 결과\n"
            " - 작성 팁: 주제에 대해 스스로 분석하고 도출해 낸 결과나 현대 사회적 비평 사례를 서술하세요. (관련 통계나 사회 이론 등을 연계하면 신뢰도가 높아집니다.)\n"
            " [여기에 작성하세요]\n\n"
            "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)\n"
            " - 작성 팁: RISS/DBpia에서 실제 검색한 키워드와 찾아본 논문명, 혹은 도서관에서 대출해 깊이 읽은 도서명(저자명)을 구체적인 극복 노력과 함께 서술하세요.\n"
            " [여기에 작성하세요]\n\n"
            "4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)\n"
            " - 작성 팁: 탐구 후 나에게 일어난 문학적 관점의 변화나 진로 분야에서의 성찰적 학업 소명을 정리하세요.\n"
            " [여기에 작성하세요]\n"
        )
        
        requests = [
            {
                "insertText": {
                    "location": {
                        "index": 1
                    },
                    "text": intro_text
                }
            }
        ]
        
        # 문서 텍스트 주입 실행
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
        
        # 3. 문서 공유 권한 설정 (링크가 있는 모든 사용자가 읽기 가능)
        permission = {
            "type": "anyone",
            "role": "reader"
        }
        drive_service.permissions().create(
            fileId=doc_id,
            body=permission
        ).execute()
        print("Set document permission to 'anyone with the link can read'.")
        
        # 4. 웹앱 HTML 파일(Index.html) 내의 CONFIG 변수 자동 업데이트
        hwp_url = f"https://docs.google.com/document/d/{doc_id}/export?format=docx"
        docs_url = f"https://docs.google.com/document/d/{doc_id}/copy"
        
        html_path = "문학_탐구보고서_웹앱_Index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
            
        # 변수 교체
        import re
        html = re.sub(
            r'var CONFIG_TEMPLATE_HWP = "[^"]+";',
            f'var CONFIG_TEMPLATE_HWP = "{hwp_url}";',
            html
        )
        html = re.sub(
            r'var CONFIG_TEMPLATE_DOCS = "[^"]+";',
            f'var CONFIG_TEMPLATE_DOCS = "{docs_url}";',
            html
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Successfully updated CONFIG variables in 문학_탐구보고서_웹앱_Index.html!")
        print(f"Docs Copy URL: {docs_url}")
        print(f"Docs Word Export URL: {hwp_url}")
        
    except Exception as e:
        print("Error during document creation or API call:", e)

if __name__ == "__main__":
    main()
