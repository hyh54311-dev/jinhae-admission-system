import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def create_form():
    token_path = 'token.json'
    links_path = 'scratch/uploaded_pdf_links.json'
    
    if not os.path.exists(token_path):
        print("Error: token.json does not exist. Please authorize first.")
        return
        
    pdf_links = {}
    if os.path.exists(links_path):
        with open(links_path, 'r', encoding='utf-8') as f:
            pdf_links = json.load(f)
            
    # Default links fallback if json is missing
    link1 = pdf_links.get("1안.pdf", "https://drive.google.com/")
    link2 = pdf_links.get("2안.pdf", "https://drive.google.com/")
    link3 = pdf_links.get("3안.pdf", "https://drive.google.com/")
    link4 = pdf_links.get("4안.pdf", "https://drive.google.com/")

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        # Discover forms API v1
        forms_service = build('forms', 'v1', credentials=creds)
        
        # 1. Create Google Form
        form_title = "2026학년도 입학생 3개년 교육과정 편성표(1학년) 의견 수렴"
        form_body = {
            "info": {
                "title": form_title,
                "documentTitle": form_title
            }
        }
        
        print("Creating Google Form shell...")
        form = forms_service.forms().create(body=form_body).execute()
        form_id = form.get("formId")
        responder_url = form.get("responderUri")
        edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
        
        print(f"Form created. ID: {form_id}")
        
        # 2. Build the questions and descriptions
        description = (
            "본 설문은 2026학년도 입학생 3개년 교육과정 편성표(1학년) 개정 및 편성에 대한 선생님들의 의견을 수렴하기 위한 것입니다.\n\n"
            "아래의 4가지 안을 면밀히 검토하신 후, 가장 적절하다고 판단되는 안을 선택해 주시고 상세 의견을 기재해 주시기 바랍니다.\n\n"
            "■ 각 안의 상세 편성표(PDF 파일) 다운로드 및 확인 링크:\n"
            f"- [1안 상세 보기] 👉 {link1}\n"
            f"- [2안 상세 보기] 👉 {link2}\n"
            f"- [3안 상세 보기] 👉 {link3}\n"
            f"- [4안 상세 보기] 👉 {link4}\n\n"
            "선생님들의 소중한 의견을 모아 교육과정부에 신속히 전달하겠습니다. 참여해 주셔서 감사합니다."
        )
        
        # Build batchUpdate requests
        update_requests = {
            "requests": [
                # 1) Update Form Description
                {
                    "updateFormInfo": {
                        "info": {
                            "description": description
                        },
                        "updateMask": "description"
                    }
                },
                # 2) Question 1: 성명 입력 (Text Question)
                {
                    "createItem": {
                        "item": {
                            "title": "성명을 입력해 주세요.",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "textQuestion": {}
                                }
                            }
                        },
                        "location": {
                            "index": 0
                        }
                    }
                },
                # 3) Question 2: 편성표 선택 (Multiple Choice)
                {
                    "createItem": {
                        "item": {
                            "title": "2026학년도 입학생 3개년 교육과정 편성표(1학년) 중 희망하시는 안을 1개 선택해 주세요.",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "choices": [
                                            {"value": "1안 : 이전과 동일함. 다만, 선택군C의 '언어생활탐구', 선택군E의 '매체의사소통' 과목은 제외. (학생들의 과목 분산으로 인한 폐강을 막기 위함)"},
                                            {"value": "2안 : 이전의 선택군 C, D를 묶은 뒤 3학점씩 4과목을 선택하도록 하는 안."},
                                            {"value": "3안 : 이전의 선택군 C, D 뿐만 아니라 이전의 선택군 E, F도 묶어서 각각 3학점씩 4과목을 선택하도록 하는 안."},
                                            {"value": "4안 : 3학년 1학기 학교지정과목 중 국어, 영어, 수학의 학점을 1학점씩 줄여 3학점을 확보한 뒤, 이전의 선택군 E, F에서 3학점씩 5과목을 선택하도록 하는 안."}
                                        ]
                                    }
                                }
                            }
                        },
                        "location": {
                            "index": 1
                        }
                    }
                },
                # 4) Question 3: 의견 및 건의사항 (Paragraph Question)
                {
                    "createItem": {
                        "item": {
                            "title": "선택하신 안에 대한 상세 사유 및 기타 제안/의견을 자유롭게 기재해 주세요.",
                            "questionItem": {
                                "question": {
                                    "required": False,
                                    "textQuestion": {
                                        "paragraph": True
                                    }
                                }
                            }
                        },
                        "location": {
                            "index": 2
                        }
                    }
                }
            ]
        }
        
        print("Populating questions and descriptions...")
        forms_service.forms().batchUpdate(formId=form_id, body=update_requests).execute()
        print("Form structure created successfully!")
        
        # Save Form information to output
        output_info = {
            "formId": form_id,
            "editUrl": edit_url,
            "responderUrl": responder_url
        }
        with open("scratch/created_form_info.json", "w", encoding="utf-8") as f:
            json.dump(output_info, f, ensure_ascii=False, indent=2)
            
        print(f"\n============================================================")
        print(f" 구글 설문지 생성 완료!")
        print(f"============================================================")
        print(f" 관리자(편집) 주소: {edit_url}")
        print(f" 배포용(학생/교사 응답용) 주소: {responder_url}")
        print(f"============================================================\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    create_form()
