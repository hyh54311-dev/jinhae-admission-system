import os
import sys
import io
import requests
import urllib3
import httplib2
import google_auth_httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FILE = "token.json"
DOCUMENT_ID = "1lVu55Wi3ls2IMULdHISH0eYaB9Xxzy0VQAER9QTbyhM"
NEW_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzd3yaezg_qI3sIgFtqMpzNTeHcyVD7A7_J_g_HnFoIHtwTFQnNk-HuYG-tT4_PwSbk/exec"
QR_CODE_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={requests.utils.quote(NEW_WEB_APP_URL)}"

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                session = requests.Session()
                session.verify = False
                creds.refresh(Request(session=session))
                return creds
        except Exception as e:
            print("Error loading credentials:", e)
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No Google credentials found.")
        return

    try:
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        docs_service = build("docs", "v1", http=authorized_http)

        # 1. 문서 가져와서 본문 길이 측정
        print(f"Fetching document {DOCUMENT_ID}...")
        doc = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
        content = doc.get("body").get("content")
        end_index = content[-1].get("endIndex")

        # 2. 본문 내용 청소 (index 1부터 끝까지 지움)
        print("Clearing existing document body content...")
        if end_index > 2:
            docs_service.documents().batchUpdate(
                documentId=DOCUMENT_ID,
                body={
                    "requests": [
                        {
                            "deleteContentRange": {
                                "range": {
                                    "startIndex": 1,
                                    "endIndex": end_index - 1
                                }
                            }
                        }
                    ]
                }
            ).execute()

        # 3. 새로운 텍스트 삽입
        print("Inserting updated notice content...")
        title_text = "2026학년도 2학년 문학 학기말 심층 탐구 보고서 제출 안내\n"
        sub_text = "진해고등학교 2학년 문학 교과 (1~10반 대상)\n\n"
        
        info_text = (
            "학기말 문학 심층 탐구 보고서 제출 시스템 배포 완료에 따른 제출 안내문입니다.\n"
            "학생들은 아래 안내 사항과 절차를 숙지하여 기한 내에 보고서를 제출해 주시기 바랍니다.\n\n"
            "■ 제출 요약\n"
            " 1. 대상 학생: 2학년 1반 ~ 10반 전체 학생\n"
            " 2. 제출 기한: 2026년 2학기 문학 학기말 고사 전 교사 지정일\n"
            " 3. 제출 방법: 문학 탐구 보고서 제출 웹앱을 통한 온라인 제출\n"
            " 4. 제출 형태: 웹 폼 직접 기입 방식 또는 HWP/PDF 파일 업로드 방식 중 택1\n\n"
            "■ 보고서 작성 및 제출 절차\n"
            " 1단계 [양식 다운로드]\n"
            "   - 제출 웹앱에 접속하여 '구글 문서 복사본 만들기' 또는 '한글 양식 받기'를 클릭해 표준 보고서 양식을 내려받습니다.\n"
            " 2단계 [내용 작성 및 심화 독서]\n"
            "   - 나의 희망 진로(전공) 분야와 2학년 문학 교과 수록 작품을 유기적으로 연계한 탐구 주제를 선정합니다.\n"
            "   - 단순 인터넷 검색 수준을 넘어 전문 자료(RISS 논문 등) 및 교양 도서(추천 도서)를 읽고 지적 해결 과정을 서술합니다.\n"
            " 3단계 [AI 실시간 피드백 및 수정]\n"
            "   - 웹앱 하단의 'AI 실시간 첨삭 받기' 단추를 클릭해 실시간 피드백을 받아 내용을 1차 보완 및 수정합니다. (글자 수 자동 집계 지원)\n"
            " 4단계 [최종 제출]\n"
            "   - 최종 완성된 내용을 복사하여 웹 폼에 직접 기입해 제출하거나, 파일로 작성해 PDF/한글 형식으로 업로드하여 제출을 마칩니다.\n\n"
            "■ 탐구 평가 기준 (세특 반영 포인트)\n"
            " - 자기주도성 & 전공 연계성: 문학 작품 속 상황과 진로 학술 개념/이론 간의 융합도\n"
            " - 지적 장벽 극복 노력: 탐구를 깊이 있게 다듬기 위해 RISS 논문이나 참고 도서를 적극적으로 활용한 구체적인 이력\n"
            " - 인식의 변화 및 성장: 배운 후 나에게 일어난 성장 및 미래 학업적 소명 서술\n\n"
            "■ 스마트폰 및 태블릿 간편 접속 (QR 코드)\n"
            " 아래 QR코드를 카메라로 스캔하면 즉시 '문학 탐구 보고서 제출 시스템' 웹페이지로 연결됩니다.\n\n"
            "{{QR_CODE_HERE}}\n\n"
            "※ 웹 주소로 직접 접속할 학생은 아래 주소를 인터넷 창에 입력하세요:\n"
            f"{NEW_WEB_APP_URL}\n"
        )

        docs_service.documents().batchUpdate(
            documentId=DOCUMENT_ID,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": title_text + sub_text + info_text
                        }
                    }
                ]
            }
        ).execute()

        # 4. QR 코드 플레이스홀더 찾아서 이미지 삽입
        print("Searching placeholder and inserting updated QR code image...")
        doc = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
        content = doc.get("body").get("content")
        
        placeholder = "{{QR_CODE_HERE}}"
        placeholder_start = -1
        
        for element in content:
            if "paragraph" in element:
                for run in element["paragraph"]["elements"]:
                    if "textRun" in run:
                        text = run["textRun"]["content"]
                        if placeholder in text:
                            placeholder_start = run["startIndex"] + text.find(placeholder)
                            break
                if placeholder_start != -1:
                    break

        if placeholder_start != -1:
            batch_requests = [
                {
                    "deleteContentRange": {
                        "range": {
                            "startIndex": placeholder_start,
                            "endIndex": placeholder_start + len(placeholder)
                        }
                    }
                },
                {
                    "insertInlineImage": {
                        "uri": QR_CODE_URL,
                        "location": {
                            "index": placeholder_start
                        },
                        "objectSize": {
                            "width": {
                                "magnitude": 300,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 300,
                                "unit": "PT"
                            }
                        }
                    }
                }
            ]
            docs_service.documents().batchUpdate(documentId=DOCUMENT_ID, body={"requests": batch_requests}).execute()
            print("New QR code image inserted successfully.")

        # 5. 서식 및 디자인 재적용
        print("Re-applying document styling...")
        doc = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
        document_end = doc.get("body").get("content")[-1].get("endIndex")
        
        style_requests = [
            # 맑은 고딕 글꼴 지정 (weightedFontFamily 구조 활용)
            {
                "updateTextStyle": {
                    "range": {"startIndex": 1, "endIndex": document_end - 1},
                    "textStyle": {
                        "weightedFontFamily": {
                            "fontFamily": "Malgun Gothic"
                        },
                        "fontSize": {"magnitude": 11, "unit": "PT"},
                        "foregroundColor": {"color": {"rgbColor": {"red": 0.05, "green": 0.09, "blue": 0.16}}}
                    },
                    "fields": "weightedFontFamily,fontSize,foregroundColor"
                }
            },
            # 제목 서식 변경
            {
                "updateTextStyle": {
                    "range": {"startIndex": 1, "endIndex": len(title_text)},
                    "textStyle": {
                        "fontSize": {"magnitude": 22, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {"color": {"rgbColor": {"red": 0.12, "green": 0.23, "blue": 0.54}}} # Navy
                    },
                    "fields": "fontSize,bold,foregroundColor"
                }
            },
            # 부제목 서식 변경
            {
                "updateTextStyle": {
                    "range": {"startIndex": len(title_text), "endIndex": len(title_text + sub_text)},
                    "textStyle": {
                        "fontSize": {"magnitude": 12, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {"color": {"rgbColor": {"red": 0.4, "green": 0.45, "blue": 0.55}}} # Gray-blue
                    },
                    "fields": "fontSize,bold,foregroundColor"
                }
            }
        ]
        docs_service.documents().batchUpdate(documentId=DOCUMENT_ID, body={"requests": style_requests}).execute()
        
        doc_url = f"https://docs.google.com/document/d/{DOCUMENT_ID}/edit"
        print("Document update and styling completed successfully!")
        print(f"Updated Document URL: {doc_url}")

    except Exception as e:
        print("Error during notice document update:", e)

if __name__ == "__main__":
    main()
