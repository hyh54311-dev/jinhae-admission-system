import os
import sys
import json
import urllib.request
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

# 1. Setup paths and folder parameters
PARENT_FOLDER_ID = "1L407Q7d36HrcsSPMRWtNJ5b9MufC5k1A" # 2026. 지역 대학 연계 마이크로디그리형 연수 계획
NEW_FOLDER_NAME = "2026_경남대_마이크로디그리_3일차_김경규강사_실습및강의자료"
LOCAL_DOWNLOAD_DIR = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\day3_downloads"
TOKEN_PATH = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\token.json"

os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)

# 2. Files to download
urls_to_download = [
    {
        "name": "01_김경규강사_깃허브_README.md",
        "url": "https://raw.githubusercontent.com/comjoo94/Share/main/README.md"
    },
    {
        "name": "02_유현주교수_AISW기초교육부_강의자료.pdf",
        "url": "https://raw.githubusercontent.com/comjoo94/Share/main/2026%ED%95%98%EA%B3%84%EA%B5%90%EC%9B%90%EB%A7%88%EC%9D%B4%ED%81%AC%EB%A1%9C%EB%94%94%EA%B7%B8%EB%A6%AC%ED%98%95%EC%97%B0%EC%88%98_AISW%EA%B8%B0%EC%B4%88%EA%B5%90%EC%9C%A1%EB%B6%80%EC%9C%A0%ED%98%84%EC%A3%BC_%EA%B0%95%EC%9D%98%EC%9E%90%EB%A3%8C.pdf"
    },
    {
        "name": "03_김경규강사_연수_실습워크북.pdf",
        "url": "https://docs.google.com/document/d/1-azDbmx1tuKvVFXCWaO-v8u0E4Fr7LkbV7wZlLUdOVU/export?format=pdf"
    },
    {
        "name": "04_김경규강사_연수_실습워크북.docx",
        "url": "https://docs.google.com/document/d/1-azDbmx1tuKvVFXCWaO-v8u0E4Fr7LkbV7wZlLUdOVU/export?format=docx"
    }
]

# Write a summary MD file for the Day 3 materials
summary_md_content = """# 2026 경남대학교 마이크로디그리 연수 3일차 자료 정리
- **강사**: 김경규 선생님 (포항제철중)
- **일자**: 2026년 7월 29일(수)

## 📌 주요 서비스 및 링크 정리
1. **김경규 강사 깃허브 저장소**: [https://github.com/comjoo94/Share](https://github.com/comjoo94/Share)
2. **실습 워크북 구글 문서**: [https://docs.google.com/document/d/1-azDbmx1tuKvVFXCWaO-v8u0E4Fr7LkbV7wZlLUdOVU/edit?usp=sharing](https://docs.google.com/document/d/1-azDbmx1tuKvVFXCWaO-v8u0E4Fr7LkbV7wZlLUdOVU/edit?usp=sharing)
3. **오늘자 전용 실습 패들렛**: [https://padlet.com/comjoo/genai260729](https://padlet.com/comjoo/genai260729)
   - **접속 비밀번호**: `260729`
4. **전체 수업 자료 통합 패들렛**: [https://padlet.com/actboy21/ai-n9jluyoqtuszyboy](https://padlet.com/actboy21/ai-n9jluyoqtuszyboy)

## 📄 보관된 파일 목록
- `01_김경규강사_깃허브_README.md`
- `02_유현주교수_AISW기초교육부_강의자료.pdf`
- `03_김경규강사_연수_실습워크북.pdf`
- `04_김경규강사_연수_실습워크북.docx`
- `05_3일차_수업및패들렛_종합안내.md`
"""

summary_file_path = os.path.join(LOCAL_DOWNLOAD_DIR, "05_3일차_수업및패들렛_종합안내.md")
with open(summary_file_path, "w", encoding="utf-8") as f:
    f.write(summary_md_content)

print("=== 1. 다운로드 시작 ===")
downloaded_files = []
for item in urls_to_download:
    save_path = os.path.join(LOCAL_DOWNLOAD_DIR, item["name"])
    print(f"Downloading {item['name']}...")
    try:
        req = urllib.request.Request(item["url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(save_path, 'wb') as out_file:
            out_file.write(resp.read())
        print(f"  -> SUCCESS ({os.path.getsize(save_path)} bytes)")
        downloaded_files.append(save_path)
    except Exception as e:
        print(f"  -> ERROR: {e}")

downloaded_files.append(summary_file_path)

# 3. Google Drive Service Init
creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

# 4. Create new folder under PARENT_FOLDER_ID
print("\n=== 2. 구글 드라이브 새 폴더 생성 ===")
folder_metadata = {
    'name': NEW_FOLDER_NAME,
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [PARENT_FOLDER_ID]
}
new_folder = service.files().create(body=folder_metadata, fields='id, webViewLink').execute()
new_folder_id = new_folder.get('id')
folder_link = new_folder.get('webViewLink')

print(f"새 폴더 생성 완료! (ID: {new_folder_id})")
print(f"폴더 링크: {folder_link}")

# 5. Upload files to new folder
print("\n=== 3. 파일 업로드 시작 ===")
for file_path in downloaded_files:
    file_name = os.path.basename(file_path)
    print(f"Uploading {file_name}...")
    
    # Determine mime type
    mime_type = 'application/octet-stream'
    if file_name.endswith('.pdf'):
        mime_type = 'application/pdf'
        
    elif file_name.endswith('.docx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file_name.endswith('.md'):
        mime_type = 'text/markdown'
        
    file_metadata = {
        'name': file_name,
        'parents': [new_folder_id]
    }
    
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
    
    for attempt in range(3):
        try:
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"  -> SUCCESS! (ID: {uploaded_file.get('id')})")
            break
        except Exception as e:
            print(f"  -> Attempt {attempt+1} failed: {e}")
            time.sleep(2)

print("\n=========================================")
print("PROCESS COMPLETE!")
print(f"NEW FOLDER LINK: {folder_link}")
print("=========================================")
