import os
import json
import requests
import urllib3
import httplib2
import google_auth_httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 경고 메시지 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_TASKS_FILE = "token_tasks_write.json"

def get_credentials():
    if os.path.exists(TOKEN_TASKS_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_TASKS_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
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
        print("No valid credentials found in token_tasks_write.json.")
        return
        
    try:
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        tasks_service = build("tasks", "v1", http=authorized_http)
        
        # 내일 아침 리마인더 날짜 설정 (2026년 7월 10일)
        due_date = "2026-07-10T00:00:00.000Z"
        
        task_data = {
            "title": "[진해고 문학 세특] 내일 아침 탐구보고서 웹앱 배포 및 학생용 양식 최종 점검",
            "notes": "오늘 생성한 구글 문서 양식 및 한글(.hwp) 양식 다운로드 링크가 실제 작동하는지 점검하고, 학생 제출 데이터 기반 AI 세특 초안 자동 작성을 최종 확인합니다.",
            "due": due_date
        }
        
        # 기본 태스크 목록(@default)에 할 일 추가
        result = tasks_service.tasks().insert(tasklist="@default", body=task_data).execute()
        
        print("\n=== Google Tasks Created ===")
        print(f"Title: {result.get('title')}")
        print(f"Notes: {result.get('notes')}")
        print(f"Due Date: {result.get('due')}")
        print(f"Status: {result.get('status')}")
        
    except Exception as e:
        print("Error creating Google Task:", e)

if __name__ == "__main__":
    main()
