import os
import json
import urllib3
import httplib2
import google_auth_httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FILE = "token.json"
TARGET_DOC_ID = "1L7U7S__MwoRStH-vdllIit-FBn8_yoUTnHzBj6QxGWk"

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                import requests
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
        print("No credentials found.")
        return
        
    try:
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        docs_service = build("docs", "v1", http=authorized_http)
        
        # 1. 기존 문서의 길이 획득 및 텍스트 전체 삭제
        print("Fetching existing document to clear...")
        doc = docs_service.documents().get(documentId=TARGET_DOC_ID).execute()
        body = doc.get("body", {})
        content = body.get("content", [])
        end_index = content[-1].get("endIndex")
        
        # 문서 내용 지우기 (startIndex 1부터 end_index-1까지)
        delete_request = []
        if end_index > 2:
            delete_request.append({
                "deleteContentRange": {
                    "range": {
                        "startIndex": 1,
                        "endIndex": end_index - 1
                    }
                }
            })
            docs_service.documents().batchUpdate(
                documentId=TARGET_DOC_ID,
                body={"requests": delete_request}
            ).execute()
            print("Cleared existing content.")

        # 2. 새로운 서식 및 내용 적용을 위한 텍스트 구성
        # 각 색션별로 안내선과 학생 입력칸을 확실히 구별
        text_content = (
            "진해고등학교 문학 심층 탐구 보고서 양식\n"
            "────────────────────────────────────────────────────────\n"
            "※ 본 양식은 구글 문서 사본을 복사하여 작성한 뒤, PDF 또는 한글 파일로 저장하여 문학 탐구 보고서 제출 웹앱을 통해 업로드해 주십시오.\n\n"
            "■ 학생 인적 사항 및 주제\n"
            " - 학년: 2학년\n"
            " - 학반 및 번호: [   ]반 [   ]번\n"
            " - 성명: [       ]\n"
            " - 희망 진로 (또는 관심 분야): [                     ]\n"
            " - 대상 문학 작품 및 저자: [                     ]\n"
            " - 탐구 주제 (제목): [                                                     ]\n"
            "────────────────────────────────────────────────────────\n\n"
            "■ 탐구 내용 서술부\n\n"
            "1. 탐구 동기 (수업 시간 배운 내용과의 연계)\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] 수업 중 어떤 대목, 개념, 시어 등에서 지적 호기심이 생겼는지 논리적으로 서술해 주세요.\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 탐구 동기를 작성해 주세요.\n"
            "\n\n"
            "2. 탐구 내용 및 결과\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] 주제에 대해 스스로 탐구하고 도출해 낸 결과나 현대 사회적 비평 사례를 서술하세요. (관련 보건 통계나 공학 이론 등을 연계하면 신뢰도가 높아집니다.)\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 탐구 내용 및 결과를 작성해 주세요.\n"
            "\n\n"
            "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] RISS/DBpia에서 실제 검색한 키워드와 찾아본 논문명, 혹은 도서관에서 대출해 깊이 읽은 도서명(저자명)을 구체적인 학업적 장벽 극복 노력과 함께 서술하세요.\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 탐구 과정 및 독서 내용을 작성해 주세요.\n"
            "\n\n"
            "4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] 탐구 후 나에게 일어난 문학적 관점의 변화나 진로 분야에서의 성찰적 학업 소명을 정리하세요.\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 결론 및 느낀 점을 작성해 주세요.\n"
            "\n"
        )
        
        insert_request = [
            {
                "insertText": {
                    "location": {
                        "index": 1
                    },
                    "text": text_content
                }
            }
        ]
        
        # 텍스트 주입
        docs_service.documents().batchUpdate(
            documentId=TARGET_DOC_ID,
            body={"requests": insert_request}
        ).execute()
        print("Inserted new formatted text.")

        # 3. 추가적인 가독성 향상 스타일링 적용 (서체 크기, 제목 볼드 등)
        # 구글 문서 다시 가져와서 범위 구하기
        doc = docs_service.documents().get(documentId=TARGET_DOC_ID).execute()
        body = doc.get("body", {})
        content = body.get("content", [])
        
        style_requests = []
        
        # 대제목 스타일링 (맑은고딕 또는 NanumMyeongjo, 16pt, 진한 네이비, 볼드)
        style_requests.append({
            "updateParagraphStyle": {
                "range": {
                    "startIndex": 1,
                    "endIndex": 25
                },
                "paragraphStyle": {
                    "alignment": "CENTER"
                },
                "fields": "alignment"
            }
        })
        style_requests.append({
            "updateTextStyle": {
                "range": {
                    "startIndex": 1,
                    "endIndex": 25
                },
                "textStyle": {
                    "fontSize": {
                        "magnitude": 16,
                        "unit": "PT"
                    },
                    "bold": True,
                    "foregroundColor": {
                        "color": {
                            "rgbColor": {
                                "blue": 0.54,
                                "green": 0.23,
                                "red": 0.12
                            }
                        }
                    }
                },
                "fields": "fontSize,bold,foregroundColor"
            }
        })
        
        # 문서 전체 서체 변경 (Malgun Gothic)
        full_doc_len = content[-1].get("endIndex")
        style_requests.append({
            "updateTextStyle": {
                "range": {
                    "startIndex": 1,
                    "endIndex": full_doc_len - 1
                },
                "textStyle": {
                    "weightedFontFamily": {
                        "fontFamily": "Malgun Gothic"
                    }
                },
                "fields": "weightedFontFamily"
            }
        })
        
        # 안내문구 영역(💡이 들어간 라인들)의 글자 색상을 연하게(회색) 변경하여 구별성 강화
        full_text = ""
        for element in content:
            if "paragraph" in element:
                paragraph = element["paragraph"]
                elements = paragraph.get("elements", [])
                for el in elements:
                    if "textRun" in el:
                        full_text += el["textRun"].get("content", "")
                        
        lines_with_indices = []
        current_idx = 1
        for line in full_text.split("\n"):
            line_len = len(line) + 1  # \n 포함
            if "💡" in line or "안내문" in line:
                lines_with_indices.append((current_idx, current_idx + line_len))
            current_idx += line_len
            
        for start, end in lines_with_indices:
            style_requests.append({
                "updateTextStyle": {
                    "range": {
                        "startIndex": start,
                        "endIndex": end - 1
                    },
                    "textStyle": {
                        "foregroundColor": {
                            "color": {
                                "rgbColor": {
                                    "blue": 0.5,
                                    "green": 0.5,
                                    "red": 0.5
                                }
                            }
                        },
                        "italic": True,
                        "fontSize": {
                            "magnitude": 10,
                            "unit": "PT"
                        }
                    },
                    "fields": "foregroundColor,italic,fontSize"
                }
            })
            
        if style_requests:
            docs_service.documents().batchUpdate(
                documentId=TARGET_DOC_ID,
                body={"requests": style_requests}
            ).execute()
            print("Applied typography and guide text styling.")
            
        print("Document styling completed successfully!")
        
    except Exception as e:
        print("Error during document styling:", e)

if __name__ == "__main__":
    main()
